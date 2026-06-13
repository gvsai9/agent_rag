from sqlalchemy.orm import Session

# This is a base repository class that other repository classes can inherit from. It provides a common interface for interacting with the database session. Each specific repository (e.g., PaperRepository, ChunkRepository, IngestionRepository) will extend this base class and implement methods for specific database operations related to their respective models.
class BaseRepository:

    def __init__(
        self,
        session: Session
    ):
        self.session = session