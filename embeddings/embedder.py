from models.chunk import Chunk
from models.paper import PaperMetadata

# This function takes a PaperMetadata object and a Chunk object as input and returns a formatted string that combines the title, authors, year, section title, and content of the chunk. The resulting string is structured in a way that provides context for the chunk, making it easier to understand the information contained in the chunk when it is used for embedding or retrieval purposes. The format includes clear labels for each piece of information, which can help improve the quality of embeddings and the relevance of retrieved chunks when answering questions or providing information based on the paper's content.
def build_embedding_text(
    paper: PaperMetadata,
    chunk: Chunk
) -> str:

    return f"""
Title: {paper.title}

Authors: {", ".join(paper.authors)}

Year: {paper.year}

Section:
{chunk.section_title}

Content:
{chunk.text}
""".strip()