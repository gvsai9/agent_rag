from models.search_result import (
    SearchResult
)

from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

class ContextBuilder:

# this function is used to give the result a good structure.
    def build(
        self,
        results: list[SearchResult]
    ) -> str:
        logger.info(f"Started context building on the results")
        blocks = []

        for idx, result in enumerate(
            results,
            start=1
        ):

            block = f"""
[Source {idx}]

Title:
{result.title}

Authors:
{", ".join(result.authors)}

Year:
{result.year}

Section:
{result.section}

Pdf_URL:
{result.paper_url}

Content:
{result.text}
""".strip()

            blocks.append(
                block
            )
        logger.info(f"Context is built successfully")
        return "\n\n-----------------\n\n".join(
            blocks
        )