from dataclasses import dataclass


@dataclass
class IngestionJob:

    chunk_id: str

    status: str

    embedding_model: str

    retry_count: int = 0

    error_message: str | None = None