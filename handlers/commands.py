from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
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
