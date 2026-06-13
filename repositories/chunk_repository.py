from sqlalchemy import select

from database.models import ChunkDB

from repositories.base import BaseRepository

from sqlalchemy.orm import joinedload

from sqlalchemy import text
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")
class ChunkRepository(
    BaseRepository
):


# This Function is responsible for inserting or updating multiple chunk records in the database. It takes a list of ChunkDB objects as input. For each chunk, it checks if a record with the same chunk_id already exists in the database. If it does, it updates the existing record's text, word_count, and section_title fields with the new values from the input chunk. If it doesn't exist, it adds the new chunk to the session. Finally, it commits all changes to the database. This method ensures that the database remains up-to-date with the latest information for each chunk while avoiding duplicate entries.
    def upsert_many(
        self,
        chunks: list[ChunkDB]
    ):
        logger.info(f"Upserting {len(chunks)} chunks into the database")
        for chunk in chunks:

            existing = (
                self.session.get(
                    ChunkDB,
                    chunk.chunk_id
                )
            )
        # If a chunk with the same chunk_id already exists in the database, we update its text, word_count, and section_title with the values from the input chunk. If it doesn't exist, we add the new chunk to the session. After processing all chunks, we commit the changes to the database to ensure that all updates and insertions are saved.
            if existing:

                existing.text = (
                    chunk.text
                )

                existing.word_count = (
                    chunk.word_count
                )

                existing.section_title = (
                    chunk.section_title
                )

            else:

                self.session.add(
                    chunk
                )

        self.session.commit()
        logger.info(f"Successfully upserted {len(chunks)} chunks into the database")
    # get chuunks from ids
    def get_chunks_by_ids(
        self,
        chunk_ids: list[str]
    ) -> list[ChunkDB]:
        logger.info(f"Retrieving {len(chunk_ids)} chunks from the database")
        if not chunk_ids:
            return []

        stmt = (
            select(ChunkDB)
            .options(
                joinedload(
                    ChunkDB.paper
                )
            )
            .where(
                ChunkDB.chunk_id.in_(
                    chunk_ids
                )
            )
        )

        result = self.session.execute(stmt)
        logger.info(f"Successfully retrieved {len(chunk_ids)} chunks from the database")

        return list(
            result.scalars().all()
        )
    def keyword_search(self, query: str, limit: int = 20):
        """
        Executes a keyword search, explicitly pulling chunk_id and mapping
        it cleanly so the hybrid blending logic doesn't throw a NoSuchColumnError.
        """
        sql = text(
            """
            SELECT 
                c.chunk_id,
                c.chunk_id AS id,  -- Backup alias for row.id looks
                c.paper_id, 
                c.text, 
                p.title, 
                p.authors, 
                p.year, 
                c.section_title AS section, 
                c.paper_url,
                ts_rank(to_tsvector('english', c.text), plainto_tsquery('english', :query)) AS score
            FROM chunks c
            JOIN papers p ON c.paper_id = p.paper_id
            WHERE to_tsvector('english', c.text) @@ plainto_tsquery('english', :query)
            ORDER BY score DESC
            LIMIT :limit
            """
        )

        result = self.session.execute(
            sql,
            {
                "query": query,
                "limit": limit
            }
        )
        
        return result.fetchall()