from pydantic import BaseModel


class QueryRequest(BaseModel):

    question: str

    top_k: int = 5


class SourceResponse(BaseModel):

    title: str

    authors: list[str]

    year: int | None

    section: str

    score: float

    paper_url: str


class QueryResponse(BaseModel):

    answer: str

    sources: list[SourceResponse]

    
class IngestRequest(
    BaseModel
):

    query: str

    limit: int = 10