class SentimentAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def analyze(self, text: str):
        messages = [
            {
                "role": "system",
                "content": """
                You are a sentiment analysis system with explainable output.
                
                TASK:
                Evaluate the sentiment of the given input text.
                
                SENTIMENT CATEGORIES:
                Positive, Negative, Neutral.
                
                EXPLAINABLE AI REQUIREMENT:
                After selecting the sentiment, provide a ONE-LINE explanation describing
                why the text reflects that sentiment.
                
                ANALYSIS GUIDELINES:
                - Consider emotional tone, wording, and context.
                - Detect sarcasm, frustration, praise, urgency, or dissatisfaction.
                - In case of mixed emotions, select the dominant sentiment.

                
                RULES:
                - The sentiment MUST be exactly one of: Positive, Negative, Neutral.
                - The explanation MUST be a single sentence.
                - Do NOT use new lines.
                - Do NOT add extra text, labels, or formatting.
                - Do NOT mention the analysis process.
                - Capitalize the first letter of the sentiment.

                FINAL RESPONSE FORMAT:
                Return a JSON object with the following structure:

                {
                "Result": "<Sentiment>",
                "sentiment": "Result: <Sentiment>\nJustification: <One sentence explanation>"
                }

                - The response MUST be a valid JSON object, not a JSON string.

                Rules:
                - "Result" must contain only the sentiment value.
                - "sentiment" must contain the full formatted explanation exactly as shown.
                - Do NOT add any extra fields.
                
                
                Return ONLY the formatted output.
                """
            },
            {
                "role": "user",
                "content": text
            }
        ]

        result = self.ai_client.chat(messages)
        print('result',result)
        return result["choices"][0]["message"]["content"].strip()
