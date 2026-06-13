import os

from dotenv import load_dotenv

from knowledge_graph.graph_ingestor import (
    GraphIngestor
)

load_dotenv()


def get_graph_ingestor():

    return GraphIngestor(
        uri=os.getenv(
            "NEO4J_URI"
        ),

        username=os.getenv(
            "NEO4J_USERNAME"
        ),

        password=os.getenv(
            "NEO4J_PASSWORD"
        )
    )