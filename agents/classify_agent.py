class ClassifyAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def classify(self, text: str):
        messages = [
            {
                "role": "system",
                "content": """
            You are a text classification system with explainable output.
            
            TASK:
            Classify the given input text into ONE of the following categories ONLY:
            sports, politics, technology, business, health, entertainment, Education, Finance, Lifestyle, unclear, etc...
            
            EXPLAINABLE AI REQUIREMENT:
            Provide a one line justification explaining why the text belongs to that category.
            
            STRICT OUTPUT FORMAT (MUST FOLLOW EXACTLY):
            Classification: <Category>
            Justification: <One or two sentence explanation>

            RULES:
            - The category MUST be exactly one from the allowed list.
            - The explanation MUST be a single sentence.
            - Do NOT use new lines.
            - Do NOT add extra text, labels, or formatting.
            - Do NOT mention the classification process or the word 'category'.
            - If classification is ambiguous, use 'unclear' with a reason.
            
            EXAMPLES:
            sports | The text focuses on players, matches, and competitive sporting events.
            technology | The text discusses software, systems, or technological advancements.
            
            Return ONLY the formatted output.
            """
            },
            {
                "role": "user",
                "content": text
            }
        ]

        result = self.ai_client.chat(messages)
        return result["choices"][0]["message"]["content"].strip()

 