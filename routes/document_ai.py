from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from agents.extract_document_agent import InvoiceExtractAgent
from ai_client import AzureAIClient
from dotenv import load_dotenv
from utils.pdf_text_extractor import extract_text_from_pdf
from utils.ocr_extractor import extract_text_with_ocr
from utils.image_ocr_extractor import extract_text_from_image

load_dotenv()


router = APIRouter(prefix="/ai", tags=["AI Document Features"])

ai_client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_KEY"),
    model="gpt-4.1-mini"
)

invoice_agent = InvoiceExtractAgent(ai_client)


@router.post("/extract-invoice")
async def extract_invoice(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg")):
        raise HTTPException(status_code=400, detail="Only PDF or image files are supported")

    try:
        # 1️⃣ Save PDF temporarily
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        extracted_text = ""

        # 2️⃣ PDF handling
        if filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(temp_path)
 
            if not extracted_text.strip():
                # 🔁 fallback to OCR
                extracted_text = extract_text_with_ocr(temp_path)

        # 🖼️ Image handling
        else:
            extracted_text = extract_text_from_image(temp_path)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Unable to extract text from document."
            )
        
        # 3️⃣ Call LLM agent
        result = invoice_agent.extract(extracted_text)

        return result  # MUST be JSON only

    finally:
        # 4️⃣ Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)