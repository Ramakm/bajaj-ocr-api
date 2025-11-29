import pytesseract
from PIL import Image
import numpy as np
import cv2

def get_text_from_image(image: Image.Image) -> str:
    """
    Extracts text from a PIL Image using Tesseract.
    """
    return pytesseract.image_to_string(image)

def get_data_from_image(image: Image.Image):
    """
    Extracts detailed data (boxes, conf, text) from a PIL Image using Tesseract.
    """
    return pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
