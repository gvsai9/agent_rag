# generation/openrouter_generator.py
import os
import json
import requests
from dotenv import load_dotenv
from generation.prompts import SYSTEM_PROMPT
from langsmith import traceable
load_dotenv()

class OpenRouterGenerator:
# This is an API for openrouter
    BASE_URL = (
        "https://openrouter.ai/api/v1/chat/completions"
    )

# Using deepseek model
    MODEL = (
    "deepseek/deepseek-chat-v3-0324" # <--- THE GUI
    )


    def __init__(self):
        # FIXED: Self-contained environment parsing
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is missing")
    @traceable
    def stream(self, query: str, context: str):
        response = requests.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "stream": True,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Question:\n{query}\n\nContext:\n{context}"}
                ]
            },
            stream=True,
            # FIXED: 10 seconds to connect, 300 seconds to completely read long reasoning traces
            timeout=(10, 300)
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            decoded_line = line.decode("utf-8")
            if not decoded_line.startswith("data:"):
                continue

            data = decoded_line[5:].strip()
            if data == "[DONE]":
                break

            try:
                payload = json.loads(data)
                token = payload["choices"][0]["delta"].get("content", "")
                if token:
                    yield token
            except Exception:
                continue
    @traceable
    def generate(
        self,
        query: str,
        context: str
    ) -> str:

        response = requests.post(
            self.BASE_URL,
            headers={
                "Authorization":
                    f"Bearer {self.api_key}",
                "Content-Type":
                    "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content":
                            SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"""
Question:

{query}


Context:

{context}
"""
                    }
                ]
            },
            timeout=120
        )
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        response.raise_for_status()




        data = response.json()

        return (
            data["choices"][0]
            ["message"]
            ["content"]
        )
    
