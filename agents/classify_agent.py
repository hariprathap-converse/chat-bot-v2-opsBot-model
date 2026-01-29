class ClassifyAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def classify(self, text: str):
        messages = [
            {
                "role": "system",
                "content": (
                    "Classify the given input text into ONE of the following categories ONLY:\n"
                    "sports, politics, technology, business, health, entertainment, unclear.\n\n"
                    "Analyze the key themes and context of the provided text and classify it into "
                    "the most appropriate category from the list above. Take into consideration "
                    "any subcategories, industry-specific terminology, and the possibility of "
                    "ambiguous classification.\n\n"
                    "If the text does not clearly fit into a single category, pick the closest "
                    "category or label it as 'unclear'.\n\n"
                    "Your response must contain ONLY the exact text of one category from the list.\n"
                    "Do NOT explain.\n"
                    "Do NOT add extra words.\n"
                    "Do NOT use categories not listed."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]

        result = self.ai_client.chat(messages)
        return result["choices"][0]["message"]["content"].strip()

 