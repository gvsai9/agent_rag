from embeddings.jina_provider import (
    JinaEmbeddingProvider
)

provider = (
    JinaEmbeddingProvider()
)

vector = provider.embed_query(
    "What is LangGraph?"
)

print(len(vector))