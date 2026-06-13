from abc import ABC
from abc import abstractmethod


class Reranker(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list
    ):
        pass