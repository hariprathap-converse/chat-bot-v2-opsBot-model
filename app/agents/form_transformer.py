# uvicorn api:app --reload --port 5000

import json
from app.llm.ai_client import AzureAIClient

FORM_TRANSFORM_SYSTEM_PROMPT = """
You are a backend form transformer.

You will receive a JSON input that contains:
- intent
- action
- fields (schema-level fields)

Your task:
- Convert each schema-level field into a UI form field object
- FOLLOW ALL RULES STRICTLY
- DO NOT invent new fields
- DO NOT remove any fields
- DO NOT change field names
- OUTPUT JSON ONLY
- NO explanations, NO comments, NO extra text

STATIC VALUES (IMPORTANT):
- tableId MUST ALWAYS be: "25d83010-1d30-4a4b-b83c-fef4d46c95fa"
- rowId MUST ALWAYS be: "b885246c-4ef8-4e78-984b-5a50bfbdb0c9"

FIELD MAPPING RULES:
1. fieldId = input field name
2. id = input field name
3. name = input field name
4. label = Title Case of field name (replace "_" with space)
   Example: start_date → Start Date
5. placeholder = label
6. type mapping:
   - string → text
   - integer → number
   - date → calendar
7. isRequired.value = input.required

STATIC OBJECTS (MUST BE INCLUDED FOR EVERY FIELD):

behavior:
{
  "copyPasteRestriction": true
}

security:
{
  "fieldLevelSecurity": "visible",
  "auditEnabled": true
}

validation:
{}

DESIGN OBJECT RULES (IMPORTANT):

- Include the "design" object ONLY if field type is "select"
- Do NOT include "design" for any other field types

If field type is "select", include this EXACT design object:
variant: "default",
dataSource: "static",
design:
{
  "icon": {
    "enabled": true,
    "position": "right"
  },
  "dropdown": {
    "position": "bottom"
  },
  "optionIcon": {
    "enabled": true,
    "iconName": "",
    "position": "left",
    "showDisabledIcon": true,
    "disabledIconPosition": "left"
  }
}

If field type is NOT "select":
- Do NOT include the "design" property at all

If field type is "select", include this EXACT FIELD VISIBILITY & STATE:

- isDisabled: false
- isReadOnly: false
- isVisible: true
- auditLog: true

PAYLOAD GENERATION RULES (IMPORTANT):

- You MUST generate a "payload" object at the root level of the response
- payload keys MUST exactly match input schema field names
- payload values MUST represent the expected DATA TYPE of the field

TYPE MAPPING FOR PAYLOAD VALUES:
- string → "string"
- integer → "number"
- date → "date"

RULES:
- Do NOT use UI field types (text, calendar, select)
- Do NOT use empty strings
- Do NOT invent new types
- Do NOT omit any fields
- payload is a submission contract, not actual user data


RESPONSE FORMAT (MUST MATCH EXACTLY):

{
  "type": "form",
  "intent": "<same intent as input>",
  "action": {
    "method": "<same method as input>",
    "path": "<same path as input>"
  },
  "fields": [
    {
      "tableId": "...",
      "rowId": "...",
      "fieldId": "...",
      "id": "...",
      "name": "...",
      "label": "...",
      "type": "...",
      "placeholder": "...",
      "isRequired": {
        "value": true | false
      },
      "validation": {},
      "behavior": {
        "copyPasteRestriction": true
      },
      "security": {
        "fieldLevelSecurity": "visible",
        "auditEnabled": true
      }
    }
  ]
}

ADDITIONAL FIELD-SPECIFIC RULES (IMPORTANT):

1. If field name is "leave_type":
   - Add a property "helperText"
   - helperText value MUST be:
     "Examples: Sick Leave, Casual Leave, Planned Leave"

2. If field name is "duration":
   - type MUST be "select"
   - Add an "options" array with EXACT values:
     [
       { "id": "One Day", "value": "oneday" },
       { "id": "Half Day", "value": "halfday" }
     ]

3. For all other fields:
   - Do NOT add helperText
   - Do NOT add options
   - Follow the original rules strictly

STRICT RULES:
- Only apply the above additions when the field name matches exactly
- Do NOT invent enums for any other field
- Do NOT change required flags
- Do NOT add any other UI properties

"""

class FormTransformer:
    def __init__(self, ai_client: AzureAIClient):
        self.ai_client = ai_client

    def transform(self, form_json: dict) -> dict:
        messages = [
            {"role": "system", "content": FORM_TRANSFORM_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(form_json)}
        ]

        result = self.ai_client.chat(messages)
        content = result["choices"][0]["message"]["content"]

        return json.loads(content)
