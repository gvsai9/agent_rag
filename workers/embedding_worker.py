from repositories.ingestion_repository import (
    IngestionRepository
)

from repositories.chunk_repository import (
    ChunkRepository
)

from embeddings.jina_provider import (
    JinaEmbeddingProvider
)

from vectorstores.pinecone_client import (
    PineconeClient 
)

from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")
class EmbeddingWorker:

    def __init__(
        self,
        ingestion_repo: IngestionRepository,
        chunk_repo: ChunkRepository,
        provider: JinaEmbeddingProvider,
        pinecone_client: PineconeClient
    ):
        self.ingestion_repo = ingestion_repo
        self.chunk_repo = chunk_repo
        self.provider = provider
        self.pinecone_client = pinecone_client

    def _build_text(
        self,
        chunk
    ) -> str:

        return f"""
Title:
{chunk.paper.title}

Year:
{chunk.paper.year}

Section:
{chunk.section_title}

Content:
{chunk.text}
""".strip()

    def build_pinecone_payload(
        self,
        chunks,
        vectors
    ):

        payload = []

        for chunk, vector in zip(
            chunks,
            vectors
        ):

            payload.append(
                {
                    "id": chunk.chunk_id,

                    "values": vector,

                    "metadata": {
                        "paper_id":
                            chunk.paper.paper_id,

                        "title":
                            chunk.paper.title,

                        "section":
                            chunk.section_title,

                        "year":
                            chunk.paper.year
                    }
                }
            )

        return payload

    def run_batch(
        self,
        batch_size: int = 5
    ) -> int:
        logger.info(f"Starting embedding worker batch with size: {batch_size}")
        jobs = (
            self.ingestion_repo
            .get_next_queued_jobs(
                batch_size
            )
        )
        if not jobs:
            logger.info(f"No Jobs havr been found")
            return 0
        logger.info(f"Jobs found and started execution:-")

        for job in jobs:
            self.ingestion_repo\
                .mark_processing(
                    job.id
                )

        chunk_ids = [
            job.chunk_id
            for job in jobs
        ]

        chunks = (
            self.chunk_repo
            .get_chunks_by_ids(
                chunk_ids
            )
        )
        logger.info(f"Chunks are created for the job:")

        chunk_map = {
            chunk.chunk_id: chunk
            for chunk in chunks
        }

        ordered_chunks = [
            chunk_map[chunk_id]
            for chunk_id in chunk_ids
        ]

        texts = [
            self._build_text(
                chunk
            )
            for chunk in ordered_chunks
        ]
        logger.info("Text is build for the chunks")
        logger.info(f"Sample text f{texts[0]}")
        try:
            logger.info("vectors are being created")
            vectors = (
                self.provider
                .embed_documents(
                    texts
                )
            )

            if len(vectors) != len(
                ordered_chunks
            ):
                raise ValueError(
                    f"Expected "
                    f"{len(ordered_chunks)} embeddings "
                    f"but received "
                    f"{len(vectors)}"
                )
            logger.info("vectors arecreated")
            logger.info("payloads are being created")

            payload = (
                self.build_pinecone_payload(
                    ordered_chunks,
                    vectors
                )
            )
            logger.info("payloads are created")

            self.pinecone_client.upsert(
                payload
            )
            logger.info("payload is upserted")
            for job in jobs:

                self.ingestion_repo\
                    .mark_completed(
                        job.id
                    )

            return len(jobs)

        except Exception as e:

            for job in jobs:

                self.ingestion_repo\
                    .mark_failed(
                        job.id,
                        str(e)
                    )

            raise
if __name__ == "__main__":
    # 1. Import your database engine/sessionmaker setup
    # (Adjust this import path depending on where your session creator lives)
    from database.session import SessionLocal 
    
    # 2. Spin up an active database session instance
    session = SessionLocal()
    
    # 3. Instantiate your providers/clients
    pinecone_client =  PineconeClient()
    embedding_provider = JinaEmbeddingProvider() # or HuggingFaceEmbeddingProvider, etc.
    
    # 4. Initialize the worker, passing the session into the repositories!
    worker = EmbeddingWorker(
        ingestion_repo=IngestionRepository(session=session),
        chunk_repo=ChunkRepository(session=session),
        provider=embedding_provider,
        pinecone_client=pinecone_client
    )
    
    # 5. Run your batch
    print(worker.run_batch(batch_size=5))