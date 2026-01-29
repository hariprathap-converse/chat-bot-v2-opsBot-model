from pydantic import BaseModel

class TextInput(BaseModel):
    text: str


class SummarizeResponse(BaseModel):
    summary: str


class ClassifyResponse(BaseModel):
    category: str


class SentimentResponse(BaseModel):
    sentiment: str
