import os
import requests

from dotenv import load_dotenv

from embeddings.base import (
    EmbeddingProvider
)

load_dotenv()


class JinaEmbeddingProvider(
    EmbeddingProvider
):

    BASE_URL = (
        "https://api.jina.ai/v1/embeddings"
    )

    MODEL = (
        "jina-embeddings-v3"
    )

    def __init__(self):

        self.api_key = os.getenv(
            "JINA_API_KEY"
        )

        if not self.api_key:

            raise ValueError(
                "JINA_API_KEY missing"
            )

        self.headers = {
            "Authorization":
                f"Bearer {self.api_key}",
            "Content-Type":
                "application/json"
        }
    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        payload = {
            "model":
                self.MODEL,

            "input":
                texts
        }

        response = requests.post(
            self.BASE_URL,
            headers=self.headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return [
            item["embedding"]
            for item in data["data"]
        ]
    

    
    def embed_query(
        self,
        text: str
    ) -> list[float]:

        return self.embed_documents(
            [text]
        )[0]