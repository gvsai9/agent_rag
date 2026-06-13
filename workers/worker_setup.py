from database.session import SessionLocal 
from repositories.base import BaseRepository
from repositories.chunk_repository import ChunkRepository
from repositories.ingestion_repository import IngestionRepository
from embeddings.jina_provider import JinaEmbeddingProvider
from vectorstores.pinecone_client import PineconeClient
from workers.embedding_worker import EmbeddingWorker

def setup_worker():
# 2. Spin up an active database session instance
    session = SessionLocal()

    # 3. Instantiate your providers/clients
    pinecone_client = PineconeClient() # your pinecone setup code
    embedding_provider = JinaEmbeddingProvider() # or HuggingFaceEmbeddingProvider, etc.

    # 4. Initialize the worker, passing the session into the repositories!
    worker = EmbeddingWorker(
        ingestion_repo=IngestionRepository(session=session),
        chunk_repo=ChunkRepository(session=session),
        provider=embedding_provider,
        pinecone_client=pinecone_client

    )
    return worker