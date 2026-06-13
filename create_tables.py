from database.session import Base
from database.session import engine

import database.models


Base.metadata.create_all(
    bind=engine
)

print("Tables created successfully")