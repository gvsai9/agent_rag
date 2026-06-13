from retrival.hybrid_retrival import HybridRetriever
from retrival.context_builder import ContextBuilder

from reranking.base import Reranker
from generation.base import Generator

from models.generated_answer import (
    GeneratedAnswer
)

from utils.duplicate_sources import (
    deduplicate_sources
)

from langsmith import traceable
class RAGPipeline:

    def __init__(
        self,
        retriever: HybridRetriever,
        context_builder: ContextBuilder,
        generator: Generator,
        reranker: Reranker
    ):
        self.retriever = retriever
        self.context_builder = context_builder
        self.generator = generator
        self.reranker = reranker

    @traceable
    def prepare(
        self,
        query: str,
        top_k: int = 5
    ):
        """
        Retrieval + Reranking only.
        """

        candidates = (
            self.retriever.retrieve(
                query=query,
                top_k=40
            )
        )

        reranked = (
            self.reranker.rerank(
                query=query,
                documents=candidates
            )
        )

        final_results = (
            reranked[:top_k]
        )

        context = (
            self.context_builder.build(
                final_results
            )
        )

        sources = (
            deduplicate_sources(
                final_results
            )
        )

        return context, sources
    @traceable
    def ask(
        self,
        query: str,
        top_k: int = 5
    ) -> GeneratedAnswer:

        context, sources = (
            self.prepare(
                query=query,
                top_k=top_k
            )
        )

        answer = (
            self.generator.generate(
                query=query,
                context=context
            )
        )

        return GeneratedAnswer(
            answer=answer,
            sources=sources
        )
    @traceable
    def stream(
        self,
        query: str,
        context: str
    ):

        return self.generator.stream(
            query=query,
            context=context
        )