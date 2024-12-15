from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from database.models import init_db
from handlers import commands, file_handler

# Инициализация базы данных
SessionLocal = init_db()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация маршрутов
dp.include_router(commands.router)
dp.include_router(file_handler.router)

#
# # pre checkout  (must be answered in 10 seconds)
# @dp.pre_checkout_query(lambda query: True)
# async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
#
#
# # successful payment
# @dp.message(F.successful_payment)
# async def successful_payment(message: Message):
#     print("SUCCESSFUL PAYMENT:")
#     payment_info = message.successful_payment.to_python()
#     for k, v in payment_info.items():
#         print(f"{k} = {v}")
#
#     await bot.send_message(message.chat.id,
#                            f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")
#
#


async def set_bot_commands():
    """Установка команд для бота"""
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="help", description="Описание возможностей"),
        BotCommand(command="stats", description="Показать статистику"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await set_bot_commands()

    # Передаем db_session в хранилище TODO fix
    # await storage.set_data(chat=None, user=None, data={"db_session": SessionLocal})

    # Запускаем бота
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
