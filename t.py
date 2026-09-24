from langsmith import Client

client = Client()

project = client.create_project(
    "agentic-ai-platform"
)

print(project)