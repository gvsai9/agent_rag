from dataclasses import dataclass

from models.search_result import (
    SearchResult
)

# This is dataclass that helps for UI answer structure
@dataclass
class GeneratedAnswer:

    answer: str

    sources: list[SearchResult]