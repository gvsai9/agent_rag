from bs4 import BeautifulSoup

from models.section import Section
from models.parsed_paper import ParsedPaper

# This function takes the XML content of a paper as input and parses it to extract the PMCID, title, abstract, and sections of the paper. It returns a ParsedPaper object that contains this information. The function uses BeautifulSoup to navigate the XML structure of the paper and extract the relevant information from the appropriate tags.
def parse_xml(xml_content: str) -> ParsedPaper:

    # We use BeautifulSoup to parse the XML content of the paper. We specify the parser as "xml" to ensure that the XML is parsed correctly. The resulting soup object allows us to navigate and extract information from the XML structure of the paper.
    soup = BeautifulSoup(
        xml_content,
        "xml"
    )

    # ---------- PMCID ----------
    pmcid_tag = soup.find(
        "article-id",
        {"pub-id-type": "pmcid"}
    )

    pmcid = (
        pmcid_tag.get_text(strip=True)
        if pmcid_tag
        else ""
    )

    # ---------- TITLE ----------

    title_tag = soup.find(
        "article-title"
    )

    title = (
        title_tag.get_text(
            " ",
            strip=True
        )
        if title_tag
        else ""
    )

    # ---------- ABSTRACT ----------

    abstract = ""

    abstract_tag = soup.find(
        "abstract",
        attrs={
            "abstract-type": False
        }
    )

    if abstract_tag:

        paragraphs = abstract_tag.find_all(
            "p"
        )

        abstract = "\n".join(
            p.get_text(
                " ",
                strip=True
            )
            for p in paragraphs
        )

    # ---------- BODY ----------

    body = soup.find("body")

    sections = []

    if body:

        top_level_sections = body.find_all(
            "sec",
            recursive=False
        )
# We then find any child sections that are direct children of the current section element. We call the _extract_sections function recursively for each child section, passing the full title of the current section as the new parent path. This allows us to build up the full hierarchy of sections in the paper, with each section's title reflecting its position within the overall structure.
        for sec in top_level_sections:

            _extract_sections(
                sec,
                sections,
                parent_path=""
            )

    return ParsedPaper(
        pmcid=pmcid,
        title=title,
        abstract=abstract,
        sections=sections
    )


# This is a helper function that recursively extracts sections from the XML structure of the paper. It takes a section element, a list to store the extracted sections, and a parent path string to keep track of the hierarchy of sections. The function extracts the title and text of the section, creates a Section object, and appends it to the sections list. It then finds any child sections and calls itself recursively to extract those as well, building up the full hierarchy of sections in the paper.
def _extract_sections(
    sec,
    sections: list[Section],
    parent_path: str
):

# We find the title of the section by looking for a "title" tag that is a direct child of the section element. If a title tag is found, we extract its text content and use it as the title of the section. If no title tag is found, we skip this section and do not extract it.
    title_tag = sec.find(
        "title",
        recursive=False
    )

    if not title_tag:
        return
# If a title tag is found, we extract its text content and use it as the title of the section. We also construct the full title of the section by combining it with the parent path, which represents the hierarchy of sections. For example, if the parent path is "Introduction" and the current section title is "Background", the full title would be "Introduction > Background". This helps to maintain the context of each section within the overall structure of the paper.
    title = title_tag.get_text(
        " ",
        strip=True
    )

# We construct the full title of the section by combining it with the parent path, which represents the hierarchy of sections. For example, if the parent path is "Introduction" and the current section title is "Background", the full title would be "Introduction > Background". This helps to maintain the context of each section within the overall structure of the paper.
    full_title = (
        title
        if not parent_path
        else f"{parent_path} > {title}"
    )
# We extract the text of the section by finding all "p" tags that are direct children of the section element. We then join the text content of these paragraphs together to form the full text of the section. This allows us to capture all the content within the section, even if it is divided into multiple paragraphs.
    paragraphs = sec.find_all(
        "p",
        recursive=False
    )

    text = "\n".join(
        p.get_text(
            " ",
            strip=True
        )
        for p in paragraphs
    )

    sections.append(
        Section(
            title=full_title,
            text=text
        )
    )
# We then find any child sections that are direct children of the current section element. We call the _extract_sections function recursively for each child section, passing the full title of the current section as the new parent path. This allows us to build up the full hierarchy of sections in the paper, with each section's title reflecting its position within the overall structure.
    child_sections = sec.find_all(
        "sec",
        recursive=False
    )

# We then find any child sections that are direct children of the current section element. We call the _extract_sections function recursively for each child section, passing the full title of the current section as the new parent path. This allows us to build up the full hierarchy of sections in the paper, with each section's title reflecting its position within the overall structure.
    for child in child_sections:

        _extract_sections(
            child,
            sections,
            full_title
        )


# This is a simple test case to verify that the XML parsing is working correctly. We read an XML file of a paper, parse it using the parse_xml function, and print the title, abstract, and the titles of the first few sections to check if the information is extracted correctly.

if __name__ == "__main__":

    with open(
        "data/raw/PMC13252007.xml",
        encoding="utf-8"
    ) as f:

        xml = f.read()

    paper = parse_xml(xml)

    from chunking.chunker import chunk_paper

    chunks = chunk_paper(paper)

    print(
        f"Generated {len(chunks)} chunks"
    )

    print()

    first = chunks[0]

    print(first.chunk_id)

    print(first.section_title)

    print(len(first.text.split()))

    print(first.text[:500])