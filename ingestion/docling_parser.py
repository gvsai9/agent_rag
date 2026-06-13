import os
# Force lightweight thread limits to prevent background memory spikes
os.environ["DOCLING_NUM_THREADS"] = "1"
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")
# Configure options: Keep tables active, but process 1 page at a time to save RAM
pipeline_options = PdfPipelineOptions(
    do_ocr=False,
    do_table_structure=True,  # Keeps advanced table layout parsing turned on!
    table_batch_size=1,        # Hard limit to single-page assembly line processing
    layout_batch_size=1
)
from models.parsed_paper import ParsedPaper

# Build the converter using the memory-efficient PyPdfium engine
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
            backend=PyPdfiumDocumentBackend  # Streams pages sequentially to protect RAM
        )
    }
)

def parse_pdf(pdf_path: str) -> str:
    logger.info(f"Starting PDF parsing for file: {pdf_path} using Docling with PyPdfium backend")
    result = converter.convert(pdf_path)
    document = result.document
    markdown = document.export_to_markdown()
    logger.info(f"Completed PDF parsing for file: {pdf_path}. Generated markdown length: {len(markdown)} characters")
    return markdown
def save_markdown(
    markdown: str,
    arxiv_id: str
) -> str:
    logger.info(f"Saving markdown for arXiv ID: {arxiv_id} to disk. Markdown length: {len(markdown)} characters")
    output_dir = Path(
        "parsed"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    filepath = (
        output_dir /
        f"{arxiv_id}.md"
    )

    filepath.write_text(
        markdown,
        encoding="utf-8"
    )
    logger.info(f"Markdown for arXiv ID: {arxiv_id} saved to path: {filepath}")
    return str(filepath)

