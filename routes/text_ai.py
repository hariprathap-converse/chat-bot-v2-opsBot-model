from fastapi import APIRouter
from schemas import TextInput, SummarizeResponse, ClassifyResponse, SentimentResponse
from agents.summarize_agent import SummarizeAgent
from agents.classify_agent import ClassifyAgent
from agents.sentiment_agent import SentimentAgent
from ai_client import AzureAIClient
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI Features"])

# Init LLM once
ai_client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_KEY"),
    model="gpt-4.1-mini"
)

summarizer = SummarizeAgent(ai_client)
classifier = ClassifyAgent(ai_client)
sentimenter = SentimentAgent(ai_client)


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_text(payload: TextInput):
    result = summarizer.summarize(payload.text)
    return {"summary": result}


@router.post("/classify", response_model=ClassifyResponse)
def classify_text(payload: TextInput):
    result = classifier.classify(payload.text)
    return {"category": result}


@router.post("/sentiment", response_model=SentimentResponse)
def analyze_sentiment(payload: TextInput):
    result = sentimenter.analyze(payload.text)
    return {"sentiment": result}

