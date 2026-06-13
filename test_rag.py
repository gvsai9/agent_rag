from database.session import (
    SessionLocal
)

from embeddings.jina_provider import (
    JinaEmbeddingProvider
)

from repositories.chunk_repository import (
    ChunkRepository
)

# Preserved custom package spelling
from retrival.retrival import (
    Retriever
)

from retrival.context_builder import (
    ContextBuilder
)

from vectorstores.pinecone_client import (
    PineconeClient
)

from generation.openrouter_generator import (
    OpenRouterGenerator
)

from generation.rag_pipeline import (
    RAGPipeline
)
from retrival.hybrid_retrival import HybridRetriever
from reranking.jina_reranker import JinaReranker

session = SessionLocal()

# 1. Instantiate the single, shared database repository
chunk_repo = ChunkRepository(session)

# 2. Build the base vector retriever
base_vector_retriever = Retriever(
    embedding_provider=JinaEmbeddingProvider(),
    pinecone_client=PineconeClient(),
    chunk_repo=chunk_repo
)

# 3. Assemble the full decoupled RAGPipeline pipeline
pipeline = RAGPipeline(
    retriever=HybridRetriever(
        vector_retriever=base_vector_retriever,
        chunk_repo=chunk_repo
    ),
    context_builder=ContextBuilder(),
    generator=OpenRouterGenerator(),
    reranker=JinaReranker()
)

# Execute query
result = pipeline.ask(
    "What is EvoArena?"
)

print()
print(result.answer)
print()
print("Sources:")

for source in result.sources:
    print(
        source.title,
        source.paper_url
    )