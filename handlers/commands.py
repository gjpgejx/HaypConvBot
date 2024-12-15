from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, LabeledPrice
from database.db_helper import get_user_statistics

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Добро пожаловать! Отправьте файл, чтобы конвертировать его в PDF.")


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Этот бот конвертирует файлы в формат PDF. Поддерживаются документы (DOCX, ODT, TXT) и изображения (JPG, PNG).\n"
        "Просто отправьте файл, и я обработаю его."
    )


# buy
@router.message(Command("buy"))
async def buy_command(message: Message):
    PAYMENTS_TOKEN = '1744374395:TEST:3af694f7320ae5e79e3b'
    # if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        # await message.answer(message.chat.id, "Тестовый платеж!!!")

    PRICE = LabeledPrice(label="Подписка на 1 месяц", amount=500 * 100)  # в копейках (руб)

    await message.answer_invoice(
        title="Подписка на бота",
        description="Активация подписки на бота на 1 месяц",
        provider_token=PAYMENTS_TOKEN,
        currency="rub",
        photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[PRICE],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")


@router.message(Command("stats"))
async def statistics_command(message: Message):
    db_session = message.bot["db_session"]
    stats = get_user_statistics(db_session, message.from_user.id)
    if not stats:
        await message.answer("У вас пока нет конвертированных файлов.")
    else:
        response = "Ваши конвертированные файлы:\n"
        for record in stats:
            response += f"{record.file_name} -> PDF (создано: {record.created_at})\n"
        await message.answer(response)
