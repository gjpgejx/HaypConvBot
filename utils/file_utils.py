from config import SUPPORTED_DOCS, SUPPORTED_IMAGES

def validate_file(file_name):
    ext = file_name.split('.')[-1].lower()
    if ext in SUPPORTED_DOCS:
        return "document"
    elif ext in SUPPORTED_IMAGES:
        return "image"
    else:
        raise ValueError("Неподдерживаемый формат файла.")
