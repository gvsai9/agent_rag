# This module contains the logic for chunking the parsed papers into smaller pieces of text that can be used for retrieval and question answering. The main function in this module is chunk_paper, which takes a ParsedPaper object as input and returns a list of Chunk objects. Each Chunk object represents a chunk of text extracted from the paper, along with metadata such as the PMCID, section title, and chunk index. The chunking process is designed to create chunks of approximately 400 words, while ensuring that each chunk contains complete paragraphs and does not split sentences in the middle. This allows us to maintain the coherence and context of the text within each chunk, which is important for accurate retrieval and question answering.
import logging

from models import paper
from models.chunk import Chunk
from models.parsed_paper import ParsedPaper
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")
# We define some constants for the target number of words per chunk and the minimum number of words required for a chunk. These constants can be adjusted based on the desired chunk size and the characteristics of the papers being processed.
TARGET_WORDS = 400
MIN_WORDS = 200

# This function takes a ParsedPaper object as input and returns a list of Chunk objects. It iterates through each section of the paper, splits the section text into paragraphs, and then groups the paragraphs into chunks based on the target word count. The function ensures that each chunk contains complete paragraphs and does not split sentences in the middle. It also assigns a unique chunk ID to each chunk, which combines the PMCID, section title, and chunk index. This allows us to easily identify and retrieve specific chunks of text from the database when needed.
def chunk_paper(
    paper: ParsedPaper
) -> list[Chunk]:
    logger.info(f"Chunking paper {paper.paper_id} with title: '{paper.title}'")
    chunks = []
# We initialize a global chunk index that is used to assign unique chunk IDs across all sections of the paper. This ensures that each chunk has a unique identifier that can be used to retrieve it from the database, even if multiple chunks are extracted from the same section or from different sections of the same paper.
    global_chunk_index = 0

    for section in paper.sections:

        paragraphs = _split_paragraphs(
            section.text
        )

        current_chunk = []
        current_word_count = 0
# We iterate through each paragraph in the section and count the number of words in the paragraph. If adding the current paragraph to the current chunk would exceed the target word count and the current chunk is not empty, we create a new Chunk object with the current chunk text and metadata, and append it to the list of chunks. We then reset the current chunk and word count to start building the next chunk. If adding the current paragraph does not exceed the target word count, we simply add it to the current chunk and update the word count. After processing all paragraphs in the section, if there is any remaining text in the current chunk, we create a final Chunk object for that text and append it to the list of chunks.
        for paragraph in paragraphs:

            paragraph_words = len(
                paragraph.split()
            )
# We check if adding the current paragraph to the current chunk would exceed the target word count and if the current chunk is not empty. If both conditions are true, we create a new Chunk object with the current chunk text and metadata, and append it to the list of chunks. We then reset the current chunk and word count to start building the next chunk.
            if (
                current_word_count + paragraph_words
                > TARGET_WORDS
                and current_chunk
            ):

                chunk_text = "\n\n".join(
                    current_chunk
                )

                chunks.append(
                    Chunk(
                        chunk_id=(
                            f"{paper.paper_id}_"
                            f"{global_chunk_index}"
                        ),
                        paper_id=paper.paper_id,
                        section_title=section.title,
                        text=chunk_text,
                        chunk_index=global_chunk_index,
                        word_count=len(chunk_text.split())
                    )
                )

                global_chunk_index += 1
# We reset the current chunk and word count to start building the next chunk.
                current_chunk = []
                current_word_count = 0
# If adding the current paragraph does not exceed the target word count, we simply add it to the current chunk and update the word count.
            current_chunk.append(
                paragraph
            )

            current_word_count += (
                paragraph_words
            )
# After processing all paragraphs in the section, if there is any remaining text in the current chunk, we create a final Chunk object for that text and append it to the list of chunks.
        if current_chunk:

            chunk_text = "\n\n".join(
                current_chunk
            )

            chunks.append(
                Chunk(
                    chunk_id=(
                        f"{paper.paper_id}_"
                        f"{global_chunk_index}"
                    ),
                    paper_id=paper.paper_id,
                    section_title=section.title,
                    text=chunk_text,
                    chunk_index=global_chunk_index,
                    word_count=len(chunk_text.split())
                )
            )

            global_chunk_index += 1
    logger.info(f"Created {len(chunks)} chunks for paper {paper.paper_id}")
    return chunks


# This is a helper function that splits a block of text into paragraphs. It takes a string of text as input and returns a list of paragraphs. The function splits the text by newline characters, strips any leading or trailing whitespace from each paragraph, and filters out any empty paragraphs. This allows us to work with clean, well-defined paragraphs when creating chunks from the section text.
def _split_paragraphs(
    text: str
) -> list[str]:

    paragraphs = [
        p.strip()
        for p in text.split("\n")
        if p.strip()
    ]

    return paragraphs