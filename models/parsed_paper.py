from dataclasses import dataclass

from models.section import Section


@dataclass
class ParsedPaper:

    paper_id: str

    title: str

    authors: list[str]

    year: int | None

    abstract: str

    sections: list[Section]

    xml_path: str

    paper_url: str