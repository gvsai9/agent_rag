import os
import json
import time
import traceback
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database.session import SessionLocal
from api.schemas import QueryRequest, QueryResponse, SourceResponse

# Core cloud AI providers & clients
from embeddings.jina_provider import JinaEmbeddingProvider
from vectorstores.pinecone_client import PineconeClient
from reranking.jina_reranker import JinaReranker
from generation.openrouter_generator import OpenRouterGenerator

# Retrieval and Orchestration components
from repositories.chunk_repository import ChunkRepository
from retrival.retrival import Retriever
from retrival.hybrid_retrival import HybridRetriever
from retrival.context_builder import ContextBuilder
from generation.rag_pipeline import RAGPipeline

app = FastAPI(
    title="Agentic AI Research Platform",
    version="1.0.0"
)

# Enable CORS so your hosted Lovable frontend can talk to Render safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread-safe cloud gateway singletons
embedding_provider = JinaEmbeddingProvider()
pinecone_client = PineconeClient()
generator = OpenRouterGenerator()
reranker = JinaReranker()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, db: Session = Depends(get_db)):
    chunk_repo = ChunkRepository(db)
    try:
        start = time.time()

        base_vector_retriever = Retriever(
            embedding_provider=embedding_provider,
            pinecone_client=pinecone_client,
            chunk_repo=chunk_repo
        )

        hybrid_engine = HybridRetriever(
            vector_retriever=base_vector_retriever,
            chunk_repo=chunk_repo
        )

        pipeline = RAGPipeline(
            retriever=hybrid_engine,
            context_builder=ContextBuilder(),
            generator=generator,
            reranker=reranker
        )

        context, sources = pipeline.prepare(
            query=request.question,
            top_k=request.top_k
        )
        
        answer = generator.generate(query=request.question, context=context)

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

        print(f"🚀 Standard query completed in {time.time() - start:.2f}s")
        return QueryResponse(answer=answer, sources=serialized_sources)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
            chunk_repo=chunk_repo
        )

        pipeline = RAGPipeline(
            retriever=hybrid_engine,
            context_builder=ContextBuilder(),
            generator=generator,
            reranker=reranker
        )

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
                "paper_url": src.paper_url 
            }
            for src in sources
        ]

        def event_stream():
            try:
                yield f"data: {json.dumps({'type': 'sources', 'data': serialized_sources})}\n\n"

                for token in pipeline.stream(query=request.question, context=context):
                    yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as stream_err:
                yield f"data: {json.dumps({'type': 'error', 'data': str(stream_err)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))