from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()
URI = os.getenv("NEO4J_URI")
print("URI:", URI)
NEO4J_USERNAME=os.getenv("NEO4J_USERNAME")

PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(NEO4J_USERNAME, PASSWORD))
driver.verify_connectivity()
print("Connected successfully!")

driver.close()