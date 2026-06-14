import json

from generation.openrouter_generator import (
    OpenRouterGenerator
)
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

class EntityExtractor:

    def __init__(self):

        self.generator = (
            OpenRouterGenerator()
        )

    def extract(
        self,
        paper
    ):

        prompt = f"""
Extract important entities from this paper.

Return ONLY JSON.

Format:

{{
    "methods": [],
    "datasets": [],
    "benchmarks": []
}}

Title:
{paper.title}

Abstract:
{paper.abstract}
"""

        response = (
            self.generator.generate(
                query="entity extraction",
                context=prompt
            )
        )

        try:

            start = response.find("{")
            end = response.rfind("}") + 1
            logger.info(f"found entites")
            return json.loads(
                response[start:end]
            )

        except Exception:

            return {
                "methods": [],
                "datasets": [],
                "benchmarks": []
            }