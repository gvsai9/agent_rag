import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database.models import Base, Paper, ChunkDB, IngestionJobDB

# Force connection explicitly to the local file to audit the data landing zone
SQLLITE_PATH = "sqlite:///medical_rag.db"
engine = create_engine(SQLLITE_PATH)
SessionClass = sessionmaker(bind=engine)
session = SessionClass()

print("--- AUDITING SYSTEM LOCAL FALLBACK STORAGE ---")
if os.path.exists("medical_rag.db"):
    paper_count = session.query(Paper).count()
    chunk_count = session.query(ChunkDB).count()
    job_count = session.query(IngestionJobDB).count()
    
    print(f"File Status: 'medical_rag.db' exists!")
    print(f"Captured Papers: {paper_count}")
    print(f"Captured Text Chunks: {chunk_count}")
    print(f"Queued Worker Tasks: {job_count}")
else:
    print("No local SQLite tracking file detected.")
    
session.close()