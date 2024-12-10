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
