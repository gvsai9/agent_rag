from database.session import (
    SessionLocal
)

from embeddings.jina_provider import (
    JinaEmbeddingProvider
)

from repositories.chunk_repository import (
    ChunkRepository
)

from vectorstores.pinecone_client import (
    PineconeClient
)

from retrival.retrival import (
    Retriever
)
from retrival.context_builder import (
    ContextBuilder
)

session = SessionLocal()

retriever = Retriever(
    embedding_provider=
        JinaEmbeddingProvider(),

    pinecone_client=
        PineconeClient(),

    chunk_repo=
        ChunkRepository(
            session
        )
)

results = retriever.retrieve(
    "What is agentic memory?",
    top_k=5
)


context = (
    ContextBuilder()
    .build(results)
)

print(context)