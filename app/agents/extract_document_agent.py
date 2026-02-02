import json
import re

class InvoiceExtractAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def extract(self, document_text: str) -> dict:
            messages = [
                {"role": "system", 
                 "content": """
                Extract invoice details, including customer and vendor information, totals,
                and line items, from all pages of the document, ensuring that all relevant
                information is captured, even if it spans multiple pages.

                Identify and extract data from tables, including those containing checkboxes.
                If a checkbox is unchecked, return "Not checked"; otherwise, extract the information.

                Respond only with the results in JSON format.

                The JSON object should include the following fields:
                 'InvoiceId', 'InvoiceDate', 'DueDate', 'CustomerName', 'CustomerAddress', 'CustomerAddressRecipient','VendorName', 'VendorAddress', 'VendorAddressRecipient',  
                 'SubTotal', 'TotalDiscount', 'TotalTax', 'InvoiceTotal', 'AmountDue', 'Items', 'Items(Amount)',  'Items(Description)', 'Items(Quantity)' and 'Items(UnitPrice)'.

                Rules:
                Rules:
                - Ignore blank fields from the response
                - Items must be inside an array with key "Items"
                - Dates must be in MM/DD/YYYY format
                - Currency symbol must appear before values
                - Return JSON ONLY
                - No explanations

                FINAL RESPONSE FORMAT:
                Wrap the extracted JSON inside an outer object as shown below.
                
                {
                  "type": "json",
                  "text": <extracted_invoice_json>
                }
                
                Rules:
                - The value of "text" MUST be the extracted invoice JSON object.
                - Do NOT change any field names or structure inside "text".
                - Do NOT add explanations.
                - Return JSON ONLY.
                """
                },
                {"role": "user", 
                 "content": document_text
                 }
            ]
    
            result = self.ai_client.chat(messages)
            content = result["choices"][0]["message"]["content"]

            print("RAW LLM OUTPUT:")
            print(repr(content))
    
            return self._clean_llm_json(content)
    
    def _clean_llm_json(self, content: str) -> dict:
        if not content or not content.strip():
            raise ValueError("LLM returned empty response")

        content = re.sub(r"```json", "", content, flags=re.IGNORECASE)
        content = re.sub(r"```", "", content)
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON returned by LLM:\n{content}"
            ) from e