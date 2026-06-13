import os
import requests
from dotenv import load_dotenv
from reranking.base import Reranker
from langsmith import traceable
load_dotenv()

class JinaReranker(Reranker):
    BASE_URL = "https://api.jina.ai/v1/rerank"
    MODEL = "jina-reranker-v2-base-multilingual"

    def __init__(self):
        self.api_key = os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("💥 JINA_API_KEY is missing from environment variables.")
        

    @traceable
    def rerank(self, query: str, documents: list) -> list:
        # Edge Case Safeguard: Return empty list instantly if no chunks were retrieved
        if not documents:
            return []

        MAX_CHARS = 4000

        docs_payload = [
            (
                doc.text[:MAX_CHARS]
                if hasattr(doc, "text")
                else str(doc)[:MAX_CHARS]
            )
            for doc in documents
        ]

        # Explicit payload POST request
        response = requests.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "query": query,
                "documents": docs_payload
            },
            timeout=(10, 120)  # 10s connection timeout, 120s deep cross-attention compute timeout
        )
        
        response.raise_for_status()
        data = response.json()

        reranked_documents = []
        
        # Build your sorted list using Jina's alignment indices
        for item in data.get("results", []):
            original_index = item["index"]
            chunk_object = documents[original_index]
            
            # Inject score metrics dynamically into the object for debugging/ui reference
            setattr(chunk_object, "rerank_score", item.get("relevance_score", 0.0))
            setattr(chunk_object, "rerank_rank", len(reranked_documents) + 1)
            
            reranked_documents.append(chunk_object)

        return reranked_documents