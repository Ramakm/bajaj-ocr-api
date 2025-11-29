import pytesseract
from PIL import Image

def get_text_from_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)

def get_data_from_image(image: Image.Image):
    return pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
