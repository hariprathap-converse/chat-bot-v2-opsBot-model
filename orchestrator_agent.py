import json
from pydantic import BaseModel
from ai_client import AzureAIClient
from typing import Optional ,Dict, Any

# class IntentResponse(BaseModel):                                                    
#     intent: str
class OrchestratorResponse(BaseModel):                                  # This defines what output should look like
    type: str          
    intent: Optional[str] = None
    reply: Optional[str] = None
    tool: Optional[str] = None
    text: Optional[Dict[str, Any]] = None

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
  - apply_leave → user wants to apply for leave, take leave, request leave
  - create_employee → user wants to add or create a new employee
  - get_leave_calendar → user wants to check leave balance, remaining leaves, leave summary, or leave details
  - get_all_employees -> user wants to see all employees, employee list, or employee details
  - send_email → user wants to send an email to someone
  - get_pending_leaves → user wants to see pending leaves, leave requests awaiting approval, approval pending leaves, leaves waiting for approval, my pending leave requests, pending leave applications
  - create_role → user wants to create a role
  - unknown → HR-related but unsupported request

STRICT OUTPUT RULES:
- If it is general conversation, return JSON:
  {{ "type": "chat", "reply": "<your reply>" }}

- If it is an HR-related request, return JSON:
  {{ "type": "intent", "intent": "<intent>" }}

Examples for send_email:
- "send an email to hr about my leave"
- "mail my manager that I will be late today"
- "send email to gokul@gmail.com regarding project update"
- "email hari about today's meeting"

If the user wants to send an email, return JSON ONLY in this format:
{{
  "type": "tool",
  "tool": "send_email",
  "text": {{
    "to": "<email address or person name>",
    "subject": "<email subject>",
    "body": "<email body>"
  }}
}}

Rules:
- Extract recipient, subject, and body from the user message
- If subject is not explicitly mentioned, infer a short subject
- If body is not explicit, rewrite the user message as a polite email

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