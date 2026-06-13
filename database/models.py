from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base
from database.enums import JobStatus

class Paper(Base):
    __tablename__ = "papers"

    paper_id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    xml_path: Mapped[str] = mapped_column(
        String
    )
    
    authors: Mapped[str] = mapped_column(
        Text
    )
    
    paper_url: Mapped[str] = mapped_column(
        String,
        unique=True
    ) 

    # FIXED HERE: Explicitly pass foreign_keys as a string matching the child attribute
    chunks = relationship(
        "ChunkDB",
        back_populates="paper",
        foreign_keys="[ChunkDB.paper_id]"
    )


class ChunkDB(Base):
    __tablename__ = "chunks"

    chunk_id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_id")
    )

    section_title: Mapped[str] = mapped_column(
        String
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer
    )

    text: Mapped[str] = mapped_column(
        Text
    )

    word_count: Mapped[int] = mapped_column(
        Integer
    )

    paper_url: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_url")
    )

    jobs = relationship(
        "IngestionJobDB",
        back_populates="chunk"
    )

    # FIXED HERE: Explicitly pass the column object reference
    paper = relationship(
        "Paper",
        back_populates="chunks",
        foreign_keys=[paper_id]
    )


class IngestionJobDB(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("chunks.chunk_id"),
        unique=True  
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus)
    )

    embedding_model: Mapped[str] = mapped_column(
        String
    )

    embedding_version: Mapped[int] = mapped_column(
        Integer
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    chunk = relationship(
        "ChunkDB",
        back_populates="jobs"
    )