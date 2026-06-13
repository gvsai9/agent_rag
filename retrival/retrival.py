from embeddings.base import (
    EmbeddingProvider
)

from repositories.chunk_repository import (
    ChunkRepository
)

from vectorstores.pinecone_client import (
    PineconeClient
)

from models.search_result import (
    SearchResult
)

from utils.logging_config import setup_pipeline_logger
from langsmith import traceable
# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

class Retriever:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        pinecone_client: PineconeClient,
        chunk_repo: ChunkRepository
    ):
        self.embedding_provider = (
            embedding_provider
        )

        self.pinecone_client = (
            pinecone_client
        )

        self.chunk_repo = (
            chunk_repo
        )


# This functions takes user queries and gives the search result from the pinecone
    @traceable
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> list[SearchResult]:

        logger.info(f"Retrival started on the query - {query}")
# Embedd the query vector with same embedding provider
        query_vector = (
            self.embedding_provider
            .embed_query(query)
        )

        logger.info(f"Query is embedded as {query_vector}")

#This is the respone from pinecone
        response = (
            self.pinecone_client
            .query(
                vector=query_vector,
                top_k=top_k
            )
        )

        matches = response.matches
        logger.info(f"The response is feteched from the pincone")
        chunk_ids = [
            match.id
            for match in matches
        ]

# Retrive Chunks From Database using chunk_ids
        chunks = (
            self.chunk_repo
            .get_chunks_by_ids(
                chunk_ids
            )
        )

        chunk_map = {
            chunk.chunk_id: chunk
            for chunk in chunks
        }
        logger.info(f"Chunks are fetched from the ChunkDB")

        results = []
        logger.info(f"Buidling the search results")

        for match in matches:
            
            chunk = chunk_map.get( #To preserve Pinecone rankings
                match.id
            )

            if not chunk:
                continue

# Result is list of SearchResult DataModel
            results.append(
                SearchResult(
                    chunk_id=
                        chunk.chunk_id,

                    paper_id=
                        chunk.paper.paper_id,

                    title=
                        chunk.paper.title,

                    authors=
                        chunk.paper.authors.split(";"),

                    year=
                        chunk.paper.year,

                    section=
                        chunk.section_title,

                    text=
                        chunk.text,

                    score=
                        match.score,
                    paper_url =
                            chunk.paper_url
                )
            )
        logger.info(f"Search Results have been builted")

        return results