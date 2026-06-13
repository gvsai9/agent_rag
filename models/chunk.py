from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str               #A unique identifier for the chunk, which is a string that combines the paper_id, section title, and chunk index. This allows us to easily identify and retrieve specific chunks of text from the database.
    paper_id: str                  #The paper_id of the paper from which the chunk was extracted. This is a string that represents the unique identifier of the paper. It allows us to associate each chunk with its source paper and retrieve all chunks related to a specific paper when needed.
    section_title: str          #The title of the section from which the chunk was extracted. This is a string that represents the heading of the section in the paper. It allows us to identify the main topic or theme of the chunk and retrieve all chunks related to a specific section when needed.
    text: str                   #The text of the chunk, which is a string that contains the content of the chunk. This can be used to extract information and answer questions related to the topic of the chunk.
    chunk_index: int            #The index of the chunk within the section, which is an integer that represents the position of the chunk in the section. This allows us to maintain the order of chunks within a section and retrieve them in the correct sequence when needed.
    word_count: int             #The word count of the chunk, which is an integer that represents the number of words in the chunk. This can be used to filter chunks based on their length or to calculate the total word count of all chunks related to a specific paper or section when needed.
    summary: str | None = None  #An optional summary of the chunk, which is a string that provides a brief overview of the content of the chunk. This can be used to quickly understand the main points of the chunk without having to read the entire text, and can be generated using a summarization algorithm or model when needed.
