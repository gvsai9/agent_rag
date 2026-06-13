# test_db.py

from database.session import engine

with engine.connect() as conn: # This will print the name of the database dialect being used (e.g., 'postgresql', 'sqlite', etc.)
    print("Connected successfully!")