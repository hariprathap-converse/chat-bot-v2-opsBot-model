from PIL import Image
import pytesseract

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


# this will handle ocr for image, png's