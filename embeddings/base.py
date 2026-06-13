from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """
        Convert multiple texts into embeddings.
        """
        pass

    @abstractmethod
    def embed_query(
        self,
        text: str
    ) -> list[float]:
        """
        Convert a single query into an embedding.
        """
        pass