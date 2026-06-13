from sqlalchemy import select

from database.models import (
    IngestionJobDB
)

from database.enums import (
    JobStatus
)

from repositories.base import (
    BaseRepository
)

# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")
class IngestionRepository(
    BaseRepository
):

# This function is responsible for creating ingestion jobs in the database.

    def create_jobs(
        self,
        chunk_ids: list[str],
        embedding_model: str,
        embedding_version: int
    ):
        logger.info(f"Creating ingestion jobs for {len(chunk_ids)} chunks") 
        for chunk_id in chunk_ids:

            existing_job = (
                self.session.execute(
                    select(IngestionJobDB)
                    .where(
                        IngestionJobDB.chunk_id
                        == chunk_id
                    )
                )
                .scalar_one_or_none()
            )

            if existing_job:

                if (
                    existing_job.status
                    == JobStatus.FAILED
                ):

                    existing_job.status = (
                        JobStatus.QUEUED
                    )

                    existing_job.retry_count += 1

                    existing_job.error_message = None

                continue

            self.session.add(
                IngestionJobDB(
                    chunk_id=chunk_id,

                    status=
                        JobStatus.QUEUED,

                    embedding_model=
                        embedding_model,

                    embedding_version=
                        embedding_version,

                    retry_count=0
                )
            )

        self.session.commit()
        logger.info(f"Successfully created ingestion jobs for {len(chunk_ids)} chunks")
    def mark_processing(
        self,
        job_id: int
    ) -> bool:
        """
        Flips a specific job's status to PROCESSING using its unique Job ID.
        """
        # session.get is much faster here because we are looking up by Primary Key directly
        job = self.session.get(IngestionJobDB, job_id)
        logger.info(f"Marking job {job_id} as processing")
        if job:
            job.status = JobStatus.PROCESSING
            self.session.commit()
            return True
        return False

    def mark_completed(
        self,
        job_id: int
    ) -> bool:
        """
        Marks a specific job as completely finished using its unique Job ID.
        """
        job = self.session.get(IngestionJobDB, job_id)
        logger.info(f"Marking job {job_id} as completed")
        if job:
            job.status = JobStatus.COMPLETED
            job.error_message = None  # Clear past errors upon success
            self.session.commit()
            return True
        return False

    def mark_failed(
        self,
        job_id: int,
        error_message: str
    ) -> bool:
        """
        Marks a specific job as FAILED and logs the error using its unique Job ID.
        """
        job = self.session.get(IngestionJobDB, job_id)
        logger.info(f"Marking job {job_id} as failed")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = error_message
            job.retry_count += 1
            self.session.commit()
            return True
        return False
    def get_next_queued_jobs(
            self,
            limit: int = 100
        ) -> list[IngestionJobDB]:

            logger.info(f"Retrieving next {limit} queued jobs")
            stmt = (
                select(IngestionJobDB)
                .where(
                    IngestionJobDB.status == JobStatus.QUEUED
                ).order_by(
                    IngestionJobDB.id
                )
                .limit(limit)
            )

            result = self.session.execute(stmt)
            
            # FIX: Extract the jobs into a stable list variable first
            jobs_list = list(result.scalars().all())

            # Now you can safely check the length without destroying the data
            logger.info(f"Successfully retrieved {len(jobs_list)} queued jobs")
            
            # Return the saved variable
            return jobs_list