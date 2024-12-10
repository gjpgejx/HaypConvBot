from docx import Document
from fpdf import FPDF

def process_document(file_path):
    document = Document(file_path)
    output_file = file_path.replace('.docx', '.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for paragraph in document.paragraphs:
        pdf.multi_cell(0, 10, paragraph.text)

    pdf.output(output_file)
    return output_file
