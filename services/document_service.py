from docx import Document

import os
# from unoconv import Unoconv
from fpdf import FPDF

def convert_to_pdf(input_path: str, output_path: str = str()):
    # Получаем расширение файла
    ext = os.path.splitext(input_path)[-1].lower()
    res = str()
    if ext == ".odt":
        res = convert_odt_to_pdf(input_path, output_path)
    elif ext == ".txt":
        res = convert_txt_to_pdf(input_path, output_path)
    elif ext == ".docx":
        res = process_document(input_path)
    else:
        raise ValueError(f"Формат {ext} не поддерживается для конвертации в PDF.")

    return res

def convert_odt_to_pdf(input_path: str, output_path: str):
    """Конвертация ODT в PDF через unoconv."""
    # unoconv = Unoconv()
    # unoconv.convert(input_path, output_path)
    # print(f"Конвертация {input_path} в {output_path} завершена!")
    # return output_path

def convert_txt_to_pdf(input_path: str, output_path: str):
    """Конвертация TXT в PDF через FPDF."""
    try:
        pdf = FPDF()
        pdf.add_page()
        output_path = input_path.replace('.txt', '.pdf')

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 14)

        with open(input_path, "r", encoding="utf-8") as file:
            for line in file:
                pdf.cell(200, 10, txt=line, ln=True)

        pdf.output(output_path)
        return output_path
    except Exception as e:
        print(e)


def process_document(file_path):
    try:
        document = Document(file_path)
        output_file = file_path.replace('.docx', '.pdf')
        pdf = FPDF()
        pdf.add_page()

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 14)

        for paragraph in document.paragraphs:
            pdf.cell(200, 10, txt=paragraph.text, ln=True)

        pdf.output(output_file)
        return output_file
    except Exception as e:
        print(e)
