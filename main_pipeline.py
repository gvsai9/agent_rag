from ingestion.ingestion_pipeline import IngestionPipeline
from chunking.chunker import chunk_paper
from repositories import repositories_pipeline
from repositories.paper_repository import PaperRepository
from repositories.chunk_repository import ChunkRepository
from repositories.ingestion_repository import IngestionRepository
from knowledge_graph.neo4j_client import (
    get_graph_ingestor
)

graph_ingestor = (
    get_graph_ingestor()
)

from database.session import SessionLocal  # Import your SQLAlchemy session maker
if __name__ == "__main__":
    pipeline = IngestionPipeline()
    session = SessionLocal()

    repositories_pipeline = (
        repositories_pipeline.RepositoriesPipeline(
            paper_repo=PaperRepository(session),
            chunk_repo=ChunkRepository(session),
            ingestion_repo=IngestionRepository(session)
        )
    )
    parsed_paper_list = pipeline.ingest_query(
        "agentic ai",
        limit=1
    )
    for parsed_paper in parsed_paper_list:
        chunks = chunk_paper(
            parsed_paper
        )
        repositories_pipeline.persist(
            parsed_paper=parsed_paper,
            chunks=chunks,
            xml_path=parsed_paper.xml_path
        ) 

        graph_ingestor.ingest_paper(
            parsed_paper
        )
