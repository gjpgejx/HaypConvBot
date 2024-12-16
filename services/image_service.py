from PIL import Image

def process_image(file_path):
    image = Image.open(file_path).convert("RGB")
    output_file = file_path.replace('.jpg', '.pdf')
    image.save(output_file)
    return output_file