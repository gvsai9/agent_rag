import requests
from pathlib import Path

from ingestion.arxiv_fetcher import search_arxiv
DOWNLOAD_DIR = Path(
    "downloads"
)
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")
DOWNLOAD_DIR.mkdir(
    exist_ok=True
)
def download_pdf(
    pdf_url: str,
    arxiv_id: str
) -> str:
    logger.info(f"Attempting to download PDF for arXiv ID: {arxiv_id} from URL: {pdf_url}")
    filepath = (
        DOWNLOAD_DIR /
        f"{arxiv_id}.pdf"
    )

    response = requests.get(
        pdf_url,
        timeout=60
    )

    response.raise_for_status()
    logger.info(f"Successfully downloaded PDF for arXiv ID: {arxiv_id} from URL: {pdf_url}")
    with open(
        filepath,
        "wb"
    ) as f:

        f.write(
            response.content
        )
    logger.info(f"Saved PDF for arXiv ID: {arxiv_id} to path: {filepath}")
    return str(filepath)
