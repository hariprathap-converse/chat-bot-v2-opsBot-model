import requests
import json

class AzureAIClient:                                                    # to store all, and reuse it
    def __init__(self, endpoint: str, api_key: str, model: str):  
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model

    # 🔹 NORMAL (NON-STREAMING) — for JSON responses
    def chat(self, messages: list):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 5000
        }

        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()
    

    # def chat_stream(self, messages: list):                                     # sends messages to Azure and gets reply
    #     headers = {                                                     # I am sending JSON data, and secret key
    #         "Content-Type": "application/json",
    #         "api-key": self.api_key
    #     }

    #     payload = {                                                     # the message to model(actual data sent to Azure)
    #         "model": self.model,
    #         "messages": messages,
    #         "temperature": 0.1,
    #         "max_tokens": 5000,
    #         "stream": True
    #     }

    #     response = requests.post(                                       # sending req to ai foundry
    #         self.endpoint,
    #         headers=headers,
    #         json=payload,
    #         timeout=30,
    #         stream=True
    #     )

    #     response.raise_for_status()
    #     # return response.json()
    #     for line in response.iter_lines():
    #         if not line:
    #             continue

    #         decoded = line.decode("utf-8")

    #         # Azure streams lines starting with "data:"
    #         if decoded.startswith("data: "):
    #             data = decoded.replace("data: ", "")

    #             if data == "[DONE]":
    #                 break

    #             chunk = json.loads(data)
    #             delta = chunk["choices"][0]["delta"]

    #             if "content" in delta:
    #                 yield delta["content"]