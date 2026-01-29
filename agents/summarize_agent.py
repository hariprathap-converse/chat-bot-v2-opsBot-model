class SummarizeAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def summarize(self, text: str):
        messages = [
            {
                "role": "system",
                "content": (
                    "Summarize the given input text into clear, concise bullet points. "
                    "Identify the key ideas, important facts, and main conclusions while "
                    "removing unnecessary details and repetition. Ensure that each bullet "
                    "point conveys a distinct and meaningful insight from the text.\n\n"
                    "Formatting rules:\n"
                    "- Use bullet points only\n"
                    "- Each bullet must start with a hyphen (-)\n"
                    "- Keep bullet points short and readable\n"
                    "- Do NOT include headings or titles\n"
                    "- Do NOT add explanations or commentary\n"
                    "- Do NOT rewrite the original text verbatim\n\n"
                    "Return ONLY the bullet points and nothing else."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]

        result = self.ai_client.chat(messages)
        return result["choices"][0]["message"]["content"].strip()
