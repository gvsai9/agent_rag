from abc import ABC
from abc import abstractmethod


class Generator(ABC):

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str
    ) -> str:
        pass

    @abstractmethod
    def stream(
        self,
        query: str,
        context: str
    ):
        pass