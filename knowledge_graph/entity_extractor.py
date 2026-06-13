import json

from generation.openrouter_generator import (
    OpenRouterGenerator
)


class EntityExtractor:

    def __init__(
        self,
        generator: OpenRouterGenerator
    ):
        self.generator = generator

    def extract(
        self,
        paper
    ) -> dict:

        prompt = f"""
Extract the following from this research paper.

Return JSON ONLY.

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

        response = self.generator.generate(
            query="Extract entities",
            context=prompt
        )

        try:
            return json.loads(
                response
            )

        except Exception:

            return {
                "methods": [],
                "datasets": [],
                "benchmarks": []
            }