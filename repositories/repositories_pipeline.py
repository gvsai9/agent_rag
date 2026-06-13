from database.models import ChunkDB
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

class RepositoriesPipeline:

    def __init__(
        self,
        paper_repo,
        chunk_repo,
        ingestion_repo
    ):
        self.paper_repo = paper_repo
        self.chunk_repo = chunk_repo
        self.ingestion_repo = ingestion_repo


    def persist(
    self,
    parsed_paper,
    chunks,
    xml_path: str
            ):

        self.paper_repo.upsert(
    paper_id=parsed_paper.paper_id,
    title=parsed_paper.title,
    authors=";".join(
        parsed_paper.authors
    ),
    year=parsed_paper.year,
    xml_path=xml_path,
    paper_url = parsed_paper.paper_url
)
        chunk_models = []

        for chunk in chunks:

            chunk_models.append(
                ChunkDB(
                    chunk_id=chunk.chunk_id,
                    paper_id=chunk.paper_id,
                    section_title=
                        chunk.section_title,
                    chunk_index=
                        chunk.chunk_index,
                    text=
                        chunk.text,
                    word_count=
                        chunk.word_count,
                    paper_url = 
                        parsed_paper.paper_url
                )
            )


        self.chunk_repo.upsert_many(
        chunk_models
    )
        chunk_ids = [
        chunk.chunk_id
        for chunk in chunks
    ]
        self.ingestion_repo.create_jobs(
        chunk_ids=chunk_ids,
        embedding_model=
            "jina-embeddings-v3",
        embedding_version=1
    )