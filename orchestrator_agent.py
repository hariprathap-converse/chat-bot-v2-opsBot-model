import json
from pydantic import BaseModel
from ai_client import AzureAIClient
from typing import Optional

# class IntentResponse(BaseModel):                                                    
#     intent: str
class OrchestratorResponse(BaseModel):                                  # This defines what output should look like
    type: str          
    intent: Optional[str] = None
    reply: Optional[str] = None

class OrchestratorAgent:
    def __init__(self, ai_client: AzureAIClient):
        self.ai_client = ai_client

    def process(self, user_message: str) -> OrchestratorResponse:
        prompt = f"""
You are an enterprise HR assistant.

Your task:
- If the user message is a greeting, small talk, or general conversation,
  respond normally like a friendly chatbot.
- If the user message is related to HR actions, classify it into one of the intents below.
  - apply_leave
  - create_employee
  - get_leave_calendar → user wants to check leave balance, remaining leaves, leave summary, or leave details
  - get_all_employees -> user wants to see all employees, employee list, or employee details
  - create_role → user wants to create a role
  - unknown → HR-related but unsupported request

STRICT OUTPUT RULES:
- If it is general conversation, return JSON:
  {{ "type": "chat", "reply": "<your reply>" }}

- If it is an HR-related request, return JSON:
  {{ "type": "intent", "intent": "<intent>" }}

- Return JSON ONLY.
- Do NOT include explanations.

User message:
{user_message}
"""

        messages = [
            {"role": "system", "content": "You are an enterprise HR assistant."},
            {"role": "user", "content": prompt}
        ]

        result = self.ai_client.chat(messages)
        # print(result)
        content = result["choices"][0]["message"]["content"]

        print(content)
        print(type(content))
        data = json.loads(content)
        print(data)
        print(type(data))
        return OrchestratorResponse(**data)



# - check_leave_balance
# - get_attendance
# - Leave Policies