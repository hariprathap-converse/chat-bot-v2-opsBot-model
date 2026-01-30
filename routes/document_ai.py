from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from utils.pdf_text_extractor import extract_text_from_pdf
from agents.extract_document_agent import InvoiceExtractAgent
from ai_client import AzureAIClient
from dotenv import load_dotenv
from utils.ocr_extractor import extract_text_with_ocr

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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # 1️⃣ Save PDF temporarily
        temp_filename = f"/tmp/{uuid.uuid4()}.pdf"

        with open(temp_filename, "wb") as f:
            f.write(await file.read())

        # 2️⃣ Extract text from PDF
        extracted_text = extract_text_from_pdf(temp_filename)
 
        if not extracted_text.strip():
            # 🔁 fallback to OCR
            extracted_text = extract_text_with_ocr(temp_filename)

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
        if os.path.exists(temp_filename):
            os.remove(temp_filename)