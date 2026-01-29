class SentimentAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def analyze(self, text: str):
        messages = [
            {
                "role": "system",
                "content": (
                    "Evaluate the sentiment of the given input text, taking into account its "
                    "emotional tone, subtle language cues, and cultural or contextual factors. "
                    "Classify the tone of the text into one of the following categories: "
                    "Positive, Negative, or Neutral. "
                    "Look for sarcasm, emoticons, or specialized terminology that could affect "
                    "the sentiment reading. In cases of mixed emotions, identify the most "
                    "dominant sentiment. Analyze neutral phrases that may have positive or "
                    "negative undertones, and gauge the message's urgency or significance. "
                    "Your response must be ONLY ONE WORD. "
                    "Capitalize the first letter. "
                    "Do NOT add any explanations."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]

        result = self.ai_client.chat(messages)
        return result["choices"][0]["message"]["content"].strip()
