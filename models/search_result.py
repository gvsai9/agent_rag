from dataclasses import dataclass


# This dataclass helps in retrival results.

@dataclass
class SearchResult:

    chunk_id: str

    paper_id: str

    title: str

    authors: list[str]

    year: int | None

    section: str

    text: str

    score: float

    paper_url : str