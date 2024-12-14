import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Document, FSInputFile
from services.document_service import process_document, convert_to_pdf
from services.image_service import process_image
from utils.file_utils import validate_file
from database.db_helper import add_file_record

router = Router()

@router.message(F.document)
# @router.message(F.photo)
async def handle_file(message: Message, state: FSMContext):
    # Получаем db_session из контекста состояния
    data = await state.get_data()
    db_session = data.get("db_session")

    document = message.document


    # Загружаем файл

    # if not db_session:
        # await message.answer("Ошибка: База данных недоступна.")
        # return

    file = message.document
    if(document is None):
        return await message.reply("Error! Not load document.")

    file_id = file.file_id
    file_name = file.file_name if isinstance(file, Document) else "image.jpg"
    file_path = f"temp/{file_name}"

    file_info = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file_info.file_path, destination=file_path)

    await message.answer(f"Файл {document.file_name} успешно сохранен в {file_path}")

    try:
        file_type = validate_file(file_name)
        if file_type == "document":
            output_file = convert_to_pdf(file_path)
        elif file_type == "image":
            output_file = process_image(file_path)

        # Сохраняем информацию в базу данных
        # add_file_record(db_session, message.from_user.id, file_name, file_type, output_file)

        # Отправляем пользователю результат
        pdf_file = FSInputFile(output_file)
        await message.answer_document(pdf_file)
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        print(e)
    finally:
        os.remove(file_path)