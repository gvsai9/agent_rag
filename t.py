import os
from langsmith import Client
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("LANGSMITH_API_KEY"))
# test_langsmith.py


client = Client()


project = client.create_project(
    "agentic-ai-platform"
)
projects = list(
    client.list_projects()
)
print(project)
print(projects)