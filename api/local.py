import time
import traceback
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from database.session import SessionLocal
from api.schemas import QueryRequest, QueryResponse, SourceResponse
from fastapi.middleware.cors import CORSMiddleware
from langsmith import traceable

# FIXED TYPOS: Corrected 'retrival' to 'retrieval' package paths
from embeddings.jina_provider import JinaEmbeddingProvider
from vectorstores.pinecone_client import PineconeClient
from repositories.chunk_repository import ChunkRepository
from retrival.retrival import Retriever
from retrival.context_builder import ContextBuilder
from generation.openrouter_generator import OpenRouterGenerator
from generation.rag_pipeline import RAGPipeline
from fastapi.responses import (
    StreamingResponse
)
from retrival.graph_retrival import GraphRetriever
from reranking.jina_reranker import JinaReranker
import json
from knowledge_graph.entity_extractor import EntityExtractor

app = FastAPI(title="local", version="1.0.0")

from retrival.hybrid_retrival import HybridRetriever
from embeddings.jina_provider import JinaEmbeddingProvider
from ingestion.ingestion_pipeline import IngestionPipeline
from repositories.repositories_pipeline import RepositoriesPipeline
from repositories.paper_repository import PaperRepository
from repositories.ingestion_repository import IngestionRepository
from workers.embedding_worker import EmbeddingWorker
from api.schemas import (
    IngestRequest
)

from chunking.chunker import (
    chunk_paper
)

from knowledge_graph.neo4j_client import (
    get_graph_ingestor
)
# -----------------------------
# Global singletons (Thread-Safe)
# -----------------------------
embedding_provider = JinaEmbeddingProvider()
pinecone_client = PineconeClient()
generator = OpenRouterGenerator()
reranker = JinaReranker()
graph_retriever = GraphRetriever(
    get_graph_ingestor().driver
)
entity_extractor = EntityExtractor()
# -----------------------------
# Database dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}

# -----------------------------
# Standard Query Endpoint (Unified Setup)
# -----------------------------
@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, db: Session = Depends(get_db)):
    chunk_repo = ChunkRepository(db)
    try:
        start = time.time()

        # 1. Instantiate the identical retrieval matching stack
        base_vector_retriever = Retriever(
            embedding_provider=embedding_provider,
            pinecone_client=pinecone_client,
            chunk_repo=chunk_repo
        )

        hybrid_engine = HybridRetriever(
            vector_retriever=base_vector_retriever,
            chunk_repo=chunk_repo,
            graph_retriever=graph_retriever
        )

        # 2. Inject requirements via constructor parameters
        pipeline = RAGPipeline(
            retriever=hybrid_engine,
            context_builder=ContextBuilder(),
            generator=generator,
            reranker=reranker
        )

        # 3. Fire full pass (Deduplication occurs natively inside prepare)
        context, sources = pipeline.prepare(
            query=request.question,
            top_k=request.top_k
        )
        
        # Use your dedicated .ask component fallback mapping if required, or direct generate:
        answer = generator.generate(query=request.question, context=context)

        # 4. Consistent, type-safe mapping loop
        serialized_sources = [
            SourceResponse(
                title=src.title,
                authors=src.authors if isinstance(src.authors, list) else src.authors.split(";"),
                year=src.year,
                section=getattr(src, 'section_title', getattr(src, 'section', 'Unknown')),
                score=getattr(src, 'score', 0.0),
                paper_url=src.paper_url
            )
            for src in sources
        ]

        elapsed = time.time() - start
        print(f"🚀 Standard query completed in {elapsed:.2f}s")

        return QueryResponse(
            answer=answer,
            sources=serialized_sources
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/stream")
def stream_query(request: QueryRequest, db: Session = Depends(get_db)):
    chunk_repo = ChunkRepository(db)
    try:
        base_vector_retriever = Retriever(
            embedding_provider=embedding_provider,
            pinecone_client=pinecone_client,
            chunk_repo=chunk_repo
        )

        hybrid_engine = HybridRetriever(
            vector_retriever=base_vector_retriever,
            chunk_repo=chunk_repo,
            graph_retriever=graph_retriever
        )

        pipeline = RAGPipeline(
            retriever=hybrid_engine,
            context_builder=ContextBuilder(),
            generator=generator,
            reranker=reranker
        )
        # Execute upfront heavy I/O operations cleanly before streaming loop starts
        context, sources = pipeline.prepare(
            query=request.question,
            top_k=request.top_k
        )
        serialized_sources = [
            {
                "title": src.title,
                "authors": src.authors if isinstance(src.authors, list) else src.authors.split(";"),
                "year": src.year,
                "section": getattr(src, 'section_title', getattr(src, 'section', 'Unknown')),
                "score": getattr(src, 'score', 0.0),
                "paper_url": src.paper_url ,
    
            }
            for src in sources
        ]

        def event_stream():
            try:
                # FIXED: Structured initial sources packet
                yield f"data: {json.dumps({'type': 'sources', 'data': serialized_sources})}\n\n"

                # Stream out individual text updates
                for token in pipeline.stream(query=request.question, context=context):
                    yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

                # FIXED: Explicit completion signal for frontend event triggers
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as stream_err:
                yield f"data: {json.dumps({'type': 'error', 'data': str(stream_err)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/ingest")
@traceable(name="ingest")
def ingest(
    request: IngestRequest,
    db: Session = Depends(
        get_db
    )
):

    graph_ingestor = None

    try:

        ingestion_pipeline = (
            IngestionPipeline()
        )

        parsed_papers = (
            ingestion_pipeline.ingest_query(
                query=request.query,
                limit=request.limit
            )
        )

        repositories_pipeline = (
            RepositoriesPipeline(
                paper_repo=
                    PaperRepository(db),

                chunk_repo=
                    ChunkRepository(db),

                ingestion_repo=
                    IngestionRepository(db)
            )
        )

        graph_ingestor = (
            get_graph_ingestor()
        )

        total_chunks = 0

        for parsed_paper in parsed_papers:

            chunks = chunk_paper(
                parsed_paper
            )

            total_chunks += len(
                chunks
            )

            repositories_pipeline.persist(
                parsed_paper=
                    parsed_paper,

                chunks=
                    chunks,

                xml_path=
                    parsed_paper.xml_path
            )

            # keeping your commit
            db.commit()

            graph_ingestor.ingest_paper(
                parsed_paper
            )

            entities = (
                entity_extractor.extract(
                    parsed_paper
                )
            )

            graph_ingestor.ingest_entities(
                parsed_paper,
                entities
            )

        return {
            "status":
                "success",

            "papers_processed":
                len(parsed_papers),

            "chunks_created":
                total_chunks
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if graph_ingestor:

            graph_ingestor.close()
@app.post("/process-jobs")
def process_jobs(
    db: Session = Depends(get_db)
):

    try:

        worker = EmbeddingWorker(
            ingestion_repo=
                IngestionRepository(db),

            chunk_repo=
                ChunkRepository(db),

            provider=
                embedding_provider,

            pinecone_client=
                pinecone_client
        )

        total_processed = 0

        while True:

            processed = worker.run_batch(
                batch_size=100
            )

            total_processed += processed

            if processed == 0:
                break

        return {
            "status": "success",
            "vectors_uploaded":
                total_processed
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )