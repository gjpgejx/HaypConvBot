from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, LabeledPrice, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, \
    PreCheckoutQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User, FileStat, SessionLocal

router = Router()


@router.message(Command("start"))
@router.callback_query(F.data == "start")
async def start_command(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"В статистику",
        callback_data="stats"
    )
    builder.button(
        text=f"О боте",
        callback_data="help"
    )

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username
            )
            session.add(user)
            session.commit()
            await message.answer("Добро пожаловать! Отправьте файл, чтобы конвертировать его в PDF.",
                                 reply_markup=builder.as_markup())
        else:
            await message.answer("Вы уже зарегистрированы в системе.", reply_markup=builder.as_markup())
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        session.close()


# Команда помощи
@router.message(Command("help"))
@router.callback_query(F.data=='help')
async def help_command(message: Message):
    await message.answer(
        "Этот бот конвертирует файлы в формат PDF. Поддерживаются документы (DOCX, ODT, TXT) и изображения (JPG, PNG).\n"
        "Просто отправьте файл, и я обработаю его."
    )


# Покупка подписки
@router.message(Command("buy"))
@router.callback_query(F.data == "buy")
async def buy_command(message: Message, command: CommandObject):
    PAYMENTS_TOKEN = '1744374395:TEST:3af694f7320ae5e79e3b'
    # if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
    # await message.answer(message.chat.id, "Тестовый платеж!!!")

    # Если это команда /donate ЧИСЛО,
    # тогда вытаскиваем число из текста команды
    if command.command != "buy":
        amount = int(command.command.split("_")[1])
    # В противном случае пытаемся парсить пользовательский ввод
    else:
        # Проверка на число и на его диапазон
        if (
                command.args is None
                or not command.args.isdigit()
                or not 1 <= int(command.args) <= 2500
        ):
            amount = 100
        else:
            amount = int(command.args)

    PRICE = LabeledPrice(label="Подписка на 1 месяц", amount=amount * 100)  # в копейках (руб)

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Оплатить {amount} рублей",
        pay=True
    )
    builder.button(
        text="Отменить покупку",
        callback_data="cancel"
    )
    builder.adjust(1)

    await message.answer_invoice(
        title="Подписка на бота",
        description="Активация подписки на бота на 1 месяц",
        provider_token=PAYMENTS_TOKEN,
        currency="rub",
        # photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
        # photo_width=416,
        # photo_height=234,
        # photo_size=416,
        is_flexible=False,
        prices=[PRICE],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload",
        reply_markup=builder.as_markup())

# Обработка пред оплаты - проверка на наличие
@router.pre_checkout_query()
async def on_pre_checkout_query(
        pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)


# Обработка успешной оплаты
@router.message(F.successful_payment)
async def on_successful_payment(
        message: Message
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"В статистику",
        callback_data="stats"
    )
    builder.button(
        text="В начало",
        callback_data="start"
    )
    builder.adjust(1)

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            return
        # Логика засчитывания оплаты
        now = datetime.utcnow()
        if user.subscription_status == 'active' and user.subscription_expiry:
            # Продлить подписку
            user.subscription_expiry += timedelta(days=30)
        else:
            # Новая подписка
            user.subscription_status = 'active'
            user.subscription_expiry = now + timedelta(days=30)

        await message.answer(
            f"Огромное спасибо за оплату! Ваша подписка активна до {user.subscription_expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC.",
            # Это эффект "огонь" из стандартных реакций
            message_effect_id="5104841245755180586",
            reply_markup=builder.as_markup()
        )

        session.commit()

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        session.close()

# Просмотр статистики
@router.message(Command("stats"))
@router.callback_query(F.data == "stats")
async def statistics_command(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"В меню",
        callback_data="start"
    )
    builder.button(
        text=f"Посмотреть файлы",
        callback_data="files"
    )
    builder.button(
        text=f"Удаление данных",
        callback_data="delete"
    )

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start.",
                                 reply_markup=builder.as_markup())
            return

        file_stat = session.query(FileStat).filter_by(user_id=message.from_user.id).first()
        if not file_stat:
            await message.answer("Статистика пока отсутствует. Вы еще не конвертировали ни одного файла.",
                                 reply_markup=builder.as_markup())
        else:
            await message.answer(
                f"Ваш статус подписки: {user.subscription_status}\n"
                f"Количество конвертированных файлов: {file_stat.file_count}\n"
                f"Последнее использование: {file_stat.last_used}",
                reply_markup=builder.as_markup()
            )
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}", reply_markup=builder.as_markup())
    finally:
        session.close()


# Обработчики для кнопок
@router.callback_query(lambda callback_query: callback_query.data.startswith("reset_stats"))
async def handle_reset_stats(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        if callback_query.data == "reset_stats_self":
            user = session.query(User).filter_by(telegram_id=user_id).first()
            if user:
                file_stat = session.query(FileStat).filter_by(user_id=user.id).first()
                if file_stat:
                    file_stat.file_count = 0
                    session.commit()
                    await callback_query.message.answer("Ваша статистика обнулена.")
                else:
                    await callback_query.message.answer("Статистика отсутствует.")
    except Exception as e:
        await callback_query.message.answer(f"Произошла ошибка: {e}")
    finally:
        session.close()


# Удаление аккаунта.
@router.callback_query(lambda callback_query: callback_query.data.startswith("delete"))
async def handle_delete_user(callback_query: CallbackQuery):
    session = SessionLocal()
    try:
        user_id = callback_query.from_user.id
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if not user:
            await callback_query.message.answer("Вы не зарегистрированы в системе.")
            return

        # Обработка каждого варианта кнопок
        if callback_query.data == "delete_self":
            session.delete(user)
            session.commit()
            await callback_query.message.answer("Ваши данные были удалены из системы.")

        elif callback_query.data == "delete_admin":
            # Реализация удаления для админов
            await callback_query.message.answer("Удаление для админов еще не реализовано.")

        elif callback_query.data == "delete_test":
            # Тестовая логика удаления
            await callback_query.message.answer("Удаление (тест) завершено.")

        # Уведомляем пользователя о завершении
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"Произошла ошибка: {e}")
    finally:
        session.close()


# Создаем клавиатуру
def create_keyboard():
    keyboard = ()

    # Кнопки "Обнуление статистики"
    keyboard.add(
        InlineKeyboardButton(text="Обнулить статистику (текущий)", callback_data="reset_stats_self"),
        InlineKeyboardButton(text="Обнулить статистику (админ)", callback_data="reset_stats_admin"),
        InlineKeyboardButton(text="Обнулить статистику (тест)", callback_data="reset_stats_test"),
    )

    # Кнопки "Удаление из системы"
    keyboard.add(
        InlineKeyboardButton(text="Удалить из системы (текущий)", callback_data="delete_self"),
        InlineKeyboardButton(text="Удалить из системы (админ)", callback_data="delete_admin"),
        InlineKeyboardButton(text="Удалить из системы (тест)", callback_data="delete_test"),
    )

    return keyboard


# Использование клавиатуры в команде
@router.message(Command('menu'))
async def show_menu(message: Message):
    keyboard = create_keyboard()
    await message.answer("Выберите действие:", reply_markup=keyboard)


# Просмотр файлов.
@router.message(Command('files'))
@router.callback_query(lambda callback_query: callback_query.data.startswith("files"))
async def list_converted_files(message: Message):
    builder = InlineKeyboardBuilder()

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if not user:
            await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start.")
            return

        files = session.query(FileStat).filter_by(user_id=message.from_user.id).all()
        if not files:
            await message.answer("У вас пока нет конвертированных файлов.")
        else:
            for file in files:
                builder.button(
                    text=f"Скачать {file.file_name}",
                    callback_data=f"download {file.id}"
                )
                builder.adjust(1)

            file_list = "\n".join([f"{file.id}. {file.file_name}" for file in files])

            await message.answer(
                f"Ваши файлы:\n{file_list}\n\nДля скачивания файла используйте кнопку или команду /download <ID файла>.",
                reply_markup=builder.as_markup())
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        session.close()

# Скачивание файла.
@router.message(Command('download'))
@router.callback_query(lambda callback_query: callback_query.data.startswith("download"))
async def download_file(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Использование команды: /download <id>\nПример: /download 1")

    file_id = int(args[1])

    session = SessionLocal()
    try:
        file_stat = session.query(FileStat).filter_by(id=file_id).first()
        if not file_stat:
            await message.answer("Файл с указанным ID не найден.")
            return

        pdf_file = FSInputFile(file_stat.file_path)

        await message.answer_document(pdf_file, caption=f"Ваш файл: {file_stat.file_name}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        session.close()
