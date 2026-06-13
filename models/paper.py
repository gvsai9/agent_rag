from dataclasses import dataclass


@dataclass
class PaperMetadata:

    paper_id: str       #this is the unique identifier for the paper on arxiv.

    title: str          #the titlye of the paper.     

    summary: str        #a brief summary of the paper, which is usually the abstract.

    authors: list[str]   #a list of author names for the paper.

    published: str      #the date when the paper was published.

    paper_url: str        #the URL to the PDF version of the paper.