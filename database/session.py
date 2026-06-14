import os

from dotenv import load_dotenv

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


# This file sets up the database connection and session management for the application. It uses SQLAlchemy to create an engine and a session factory, which can be used to interact with the database throughout the application. The database URL is loaded from an environment variable, allowing for flexibility in different deployment environments.
load_dotenv()


# The DATABASE_URL environment variable is used to specify the database connection string.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///medical_rag.db"
)

# The create_engine function is used to create a SQLAlchemy engine, which is the starting point for any SQLAlchemy application. 
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=180
)


# The sessionmaker function is used to create a session factory, which can be used to create new sessions for interacting with the database.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# The declarative_base function is used to create a base class for declarative class definitions. This base class will be used to define the models for the database tables.
Base = declarative_base()