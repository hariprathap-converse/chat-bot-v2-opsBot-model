from pdf2image import convert_from_path
import pytesseract

# 👇 ADD THIS (very important on Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_with_ocr(pdf_path: str) -> str:
    images = convert_from_path(pdf_path)
    full_text = []

    for img in images:
        text = pytesseract.image_to_string(img)
        if text:
            full_text.append(text)

    return "\n".join(full_text)


# Here Scanned pdfs will also work