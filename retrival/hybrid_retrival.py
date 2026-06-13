from models.search_result import SearchResult
from langsmith import traceable
class HybridRetriever:
    def __init__(
        self,
        vector_retriever,
        chunk_repo
    ):
        self.vector_retriever = vector_retriever
        self.chunk_repo = chunk_repo

    @traceable
    def retrieve(self, query: str, top_k: int):
        # 1. Fetch from vector retriever (Returns list of clean SearchResult models)
        vector_results = self.vector_retriever.retrieve(
            query,
            top_k=20
        )

        # 2. Fetch from Postgres keyword search (Returns list of raw database row tuples)
        keyword_rows = self.chunk_repo.keyword_search(
            query,
            limit=20
        )

        combined = {}

        # 3. Add vector results to dictionary (r is a SearchResult model, so .chunk_id works)
        for r in vector_results:
            combined[r.chunk_id] = r

        # 4. Convert and add keyword rows safely to dictionary
        for row in keyword_rows:
            # Check if we already have this chunk from vector search to prevent overwriting clean objects
            if row.chunk_id in combined:
                continue

            # Convert row on-the-fly to a mutable SearchResult model so the reranker can add attributes
            combined[row.chunk_id] = SearchResult(
                chunk_id=row.chunk_id,
                paper_id=getattr(row, 'paper_id', None),
                title=getattr(row, 'title', 'Unknown Title'),
                authors=row.authors.split(";") if isinstance(row.authors, str) else (row.authors or []),
                year=getattr(row, 'year', None),
                section=getattr(row, 'section', 'Unknown'),
                text=row.text,
                score=getattr(row, 'score', 0.0),
                paper_url=getattr(row, 'paper_url', None)
            )

        # 5. Return the list up to top_k (which goes straight to the reranker!)
        return list(combined.values())[:top_k]