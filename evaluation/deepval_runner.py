import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from deepeval import evaluate
from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase

# Core singletons, pipeline components, and datasets
from database.session import SessionLocal
from embeddings.jina_provider import JinaEmbeddingProvider
from vectorstores.pinecone_client import PineconeClient
from repositories.chunk_repository import ChunkRepository
from retrival.retrival import Retriever
from retrival.context_builder import ContextBuilder
from generation.openrouter_generator import OpenRouterGenerator
from generation.rag_pipeline import RAGPipeline
from evaluation.test_cases import TEST_CASES

load_dotenv()

# ==========================================
# 1. Complete Free OpenRouter Judge Model 
# ==========================================
class OpenRouterJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing from environment variables.")
        # Llama-3.3-70B is an exceptional, highly-accurate evaluator judge
        self.model_name = "meta-llama/llama-3.3-70b-instruct:free"

    def load_model(self):
        return self

    def generate(self, prompt: str, schema=None) -> str:
        """Synchronous text generation for evaluation prompts."""
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def a_generate(self, prompt: str, schema=None) -> str:
        """REQUIRED FOR DEEPEVAL: Executes generation inside an async executor loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate, prompt, schema)

    def get_model_name(self):
        return self.model_name

# Initialize the free open-source judge instance
free_judge_llm = OpenRouterJudge()

# ==========================================
# 2. Pipeline Initialization
# ==========================================
db = SessionLocal()
embedding_provider = JinaEmbeddingProvider()
pinecone_client = PineconeClient()
generator = OpenRouterGenerator()

retriever = Retriever(
    embedding_provider=embedding_provider,
    pinecone_client=pinecone_client,
    chunk_repo=ChunkRepository(db)
)

pipeline = RAGPipeline(
    retriever=retriever,
    context_builder=ContextBuilder(),
    generator=generator
)

# ==========================================
# 3. Compile Evaluation Test Cases Array
# ==========================================
evaluation_cases = []

print("⏳ Gathering pipeline context and compiling test queries...")
for question in TEST_CASES:
    # Upfront I/O operations from your clean pipeline split
    context, sources = pipeline.prepare(query=question, top_k=5)
    
    # Generate the baseline summary answer using your regular DeepSeek pipeline model
    answer = generator.generate(query=question, context=context)
    
    # Extract string texts from your database source chunk objects
    chunk_texts = [src.text for src in sources] if hasattr(sources[0], 'text') else [str(src) for src in sources]

    evaluation_cases.append(
        LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=chunk_texts
        )
    )

# Cleanly disconnect your database transaction stream before the judging begins
db.close()

# ==========================================
# 4. Metrics & Execution
# ==========================================
metrics = [
    AnswerRelevancyMetric(threshold=0.5, model=free_judge_llm),
    FaithfulnessMetric(threshold=0.5, model=free_judge_llm),
    ContextualRelevancyMetric(threshold=0.5, model=free_judge_llm)
]

print("🚀 Starting DeepEval evaluation using Llama-3.3-70B on OpenRouter...")
evaluate(
    test_cases=evaluation_cases,
    metrics=metrics
)