from ingestion.arxiv_fetcher import (
    search_arxiv
)

from ingestion.pdf_downloader import (
    download_pdf
)

from ingestion.docling_parser import (
    parse_pdf,
    save_markdown
)

from ingestion.markdown_section_extractor import (
    markdown_to_parsed_paper
)

from chunking.chunker import (
    chunk_paper
)
import os
from langsmith import traceable

class IngestionPipeline:
    @traceable(name="arxiv ingestion")
    def ingest_query(
        self,
        query: str,
        limit: int = 10
    ):
        
        papers = search_arxiv(
            query=query,
            limit=limit
        )
        
        parsed_paper_list = []
        for metadata in papers:

            print(
                f"Ingesting {metadata.paper_id}"
            )

            pdf_path = download_pdf(
                metadata.paper_url,
                metadata.paper_id
            )

            markdown = parse_pdf(
                pdf_path
            )

            markdown_path = save_markdown(
                markdown,
                metadata.paper_id
            )

            parsed_paper = (
                markdown_to_parsed_paper(
                    markdown_path=markdown_path,
                    metadata=metadata
                )
            )
            parsed_paper_list.append(
                parsed_paper    
            )
        if os.path.exists(pdf_path):
             os.remove(pdf_path)

        if os.path.exists(markdown_path):
            os.remove(markdown_path)

        return parsed_paper_list    