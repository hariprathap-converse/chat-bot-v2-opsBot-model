class SummarizeAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def summarize(self, text: str):
        messages = [
            {
                "role": "system",
                "content": ("""
                You are an assistant that formats responses for a UI.
                
                STRICT OUTPUT FORMAT (MUST FOLLOW EXACTLY):
                
                1. The output MUST start with exactly TWO plain text lines.
                   - Each line should be a short sentence.
                   - Do NOT use bullets for these two lines.
                   - Do NOT add headings or labels.
                
                2. After the two lines, output EXACTLY FOUR bullet points.
                   - Each bullet MUST start with an asterisk followed by a space: "* "
                   - Each bullet must be on its own line.
                   - Do NOT use hyphens (-), numbers, or any other symbols.
                   - Do NOT add extra bullets.
                
                3. Do NOT include explanations, commentary, or extra text.
                4. Do NOT wrap the output in code blocks or quotes.
                5. Follow this structure strictly; any deviation is incorrect.
                
                The goal is to make the output directly renderable in a UI with round bullet points.
                """
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]

        result = self.ai_client.chat(messages)
        return result["choices"][0]["message"]["content"].strip()
