from models.search_result import (
    SearchResult
)
# ingestion/ingestion_pipeline.py
from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

class GraphRetriever:

    def __init__(
        self,
        neo4j_driver
    ):
        self.driver = (
            neo4j_driver
        )

    def retrieve(
        self,
        query: str,
        limit: int = 20
    ):
        logger.info("retriving from graph database")
        cypher = """
        MATCH
        (p:Paper)-[:USES_METHOD]->(m)

        WHERE
        toLower(m.name)
        CONTAINS
        toLower($query)

        RETURN
        p.paper_id as paper_id,
        p.title as title,
        p.paper_url as paper_url
        LIMIT $limit
        """

        results = []
        print(type(self.driver))
        with self.driver.session() as session:

            records = session.run(
                cypher,
                parameters={
                    "query": query,
                    "limit": limit
                }
            )

            for record in records:

                results.append(
                    SearchResult(
                        chunk_id="graph",
                        paper_id=record[
                            "paper_id"
                        ],
                        title=record[
                            "title"
                        ],
                        authors=[],
                        year=None,
                        section="Graph",
                        text="",
                        score=1.0,
                        paper_url=record[
                            "paper_url"
                        ]
                    )
                )

        return results