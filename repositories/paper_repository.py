from sqlalchemy import select

from database.models import Paper

from repositories.base import BaseRepository
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")


# This is a repository class for managing Paper records in the database. It extends the BaseRepository, which provides a common interface for database interactions. The PaperRepository includes methods for retrieving a paper by its Paper ID and for upserting (inserting or updating) a paper record based on its Paper ID. The upsert method checks if a paper with the given Paper ID already exists; if it does, it updates the existing record's title, year, and XML path. If it doesn't exist, it creates a new paper record and adds it to the session before committing the changes to the database.
class PaperRepository(
    BaseRepository
):


# This retrieves a Paper record from the database based on the provided Paper ID. It constructs a SQLAlchemy select statement to query the Paper table where the paper_id matches the input parameter. The method then executes the statement and returns either the matching Paper object or None if no such record exists in the database.
    def get_by_paper_id(
        self,
        paper_id: str
    ) -> Paper | None:
        logger.info(f"Retrieving paper with Paper ID: {paper_id}")
        stmt = (
            select(Paper)
            .where(
                Paper.paper_id == paper_id
            )
        )

        return (
            self.session
            .execute(stmt)
            .scalar_one_or_none()
        )
    # This method is responsible for inserting or updating a Paper record in the database based on the provided Paper ID. It first checks if a Paper with the given Paper ID already exists by calling the get_by_paper_id method. If a Paper is found, it updates the existing record's title, year, and XML path with the new values provided as parameters. If no Paper is found, it creates a new Paper object with the given Paper ID, title, year, and XML path, and adds it to the session. Finally, it commits the changes to the database and returns the upserted Paper object.
    def upsert(
        self,
        paper_id: str,
        title: str,
        year: int | None,
        xml_path: str,
        authors: str | None,
        paper_url : str|None

    ) -> Paper:

        paper = self.get_by_paper_id(
            paper_id
        )
        logger.info(f"Upserting paper with Paper ID: {paper_id}")
# If a Paper with the specified Paper ID already exists in the database, we update its title, year, and XML path with the new values provided as parameters. If it doesn't exist, we create a new Paper object with the given Paper ID, title, year, and XML path, and add it to the session. After either updating or creating the Paper record, we commit the changes to the database to ensure that the new information is saved. Finally, we return the upserted Paper object.
        if paper:

            paper.title = title
            paper.year = year
            paper.xml_path = xml_path
            paper.authors = authors
            paper.paper_url = paper_url

        else:

            paper = Paper(
                paper_id=paper_id,
                title=title,
                year=year,
                xml_path=xml_path,
                authors=authors,
                paper_url = paper_url
        
            )

            self.session.add(
                paper
            )

        logger.info(f"Successfully upserted paper with Paper ID: {paper_id}")   
        self.session.commit()

        return paper