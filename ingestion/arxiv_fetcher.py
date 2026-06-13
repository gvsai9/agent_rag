import arxiv

from models.paper import (
    PaperMetadata
)

# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

# This function performs a search on the arXiv platform using the provided query and limit parameters. It utilizes the arxiv library to interact with the arXiv API, retrieves search results, and constructs a list of PaperMetadata objects containing relevant information about each paper, such as its unique identifier, title, summary, authors, publication date, and PDF URL.
def search_arxiv(
    query: str,
    limit: int = 10
) -> list[PaperMetadata]:

    client = arxiv.Client()

    search = arxiv.Search(
        query=query,
        max_results=limit,
        sort_by=
            arxiv.SortCriterion.SubmittedDate
    )

    papers = []
    logger.info(f"Searching arXiv for query: '{query}' with limit: {limit}")
    for result in client.results(
        search
    ):

        papers.append(
            PaperMetadata(
                paper_id=
                    result.entry_id.split(
                        "/abs/"
                    )[-1],

                title=
                    result.title,

                summary=
                    result.summary,

                authors=[
                    author.name
                    for author
                    in result.authors
                ],

                published=
                    str(
                        result.published.date()
                    ),

                paper_url=
                    result.pdf_url
            )
        )
    logger.info(f"Found {len(papers)} papers on arXiv for query: '{query}'")
    return papers
