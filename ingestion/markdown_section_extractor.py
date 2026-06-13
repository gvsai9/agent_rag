import re

from models.section import Section
from models.parsed_paper import ParsedPaper
from models.paper import PaperMetadata
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

def markdown_to_parsed_paper(
    markdown_path: str,
    metadata: PaperMetadata
) -> ParsedPaper:
    logger.info(f"Starting markdown parsing for file: {markdown_path}")
    sections = []

    with open(markdown_path, "r", encoding="utf-8") as f:
            markdown = f.read()
    lines = markdown.splitlines()

    current_title = None

    current_content = []

    abstract_lines = []

    in_abstract = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Detect markdown headers
        if line.startswith("#"):

            # Save previous section
            if (
                current_title is not None
                and current_content
            ):
                sections.append(
                    Section(
                        title=current_title,
                        text="\n".join(
                            current_content
                        )
                    )
                )

            header = re.sub(
                r"^#+\s*",
                "",
                line
            ).strip()

            current_title = header

            current_content = []

            # Detect abstract
            if header.lower() == "abstract":
                in_abstract = True
            else:
                in_abstract = False

            continue

        if in_abstract:
            abstract_lines.append(
                line
            )

        if current_title is not None:
            current_content.append(
                line
            )

    # Save last section
    if (
        current_title is not None
        and current_content
    ):
        sections.append(
            Section(
                title=current_title,
                text="\n".join(
                    current_content
                )
            )
        )

    abstract = "\n".join(
        abstract_lines
    )

    logger.info(f"Completed markdown parsing for file: {markdown_path}")
    return ParsedPaper(
        paper_id=metadata.paper_id,
        title=metadata.title,
        authors=metadata.authors,
        year=int(
    str(metadata.published)[:4]
),
        abstract=abstract,
        sections=sections,
        xml_path=markdown_path,
        paper_url=metadata.paper_url
    )