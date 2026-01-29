import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    full_text = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text.append(f"\n--- Page {page_number} ---\n{text}")

    return "\n".join(full_text)


"""
Opens PDF

Loops all pages

Extracts text page by page

Adds page separators (helps LLM context)

Returns one string
"""