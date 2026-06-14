from neo4j import GraphDatabase

from utils.logging_config import (
    setup_pipeline_logger
)

logger = setup_pipeline_logger(
    "graph_ingestor"
)

from langsmith import traceable

class GraphIngestor:

    def __init__(
        self,
        uri: str,
        username: str,
        password: str
    ):

        self.driver = (
            GraphDatabase.driver(
                uri,
                auth=(
                    username,
                    password
                )
            )
        )
    @traceable(name="Close")
    def close(self):

        self.driver.close()
    @traceable(name="ingestion into neo4j")
    def ingest_paper(
        self,
        paper
    ):

        try:

            with self.driver.session() as session:

                session.run(
                    """
                    MERGE (
                        p:Paper {
                            paper_id:$paper_id
                        }
                    )

                    SET
                        p.title = $title,
                        p.year = $year,
                        p.paper_url = $paper_url
                    """,

                    paper_id=paper.paper_id,
                    title=paper.title,
                    year=paper.year,
                    paper_url=paper.paper_url
                )

                for author in paper.authors:

                    session.run(
                        """
                        MERGE (
                            a:Author {
                                name:$author
                            }
                        )

                        WITH a

                        MATCH (
                            p:Paper {
                                paper_id:$paper_id
                            }
                        )

                        MERGE
                        (
                            a
                        )-[:AUTHORED]->
                        (
                            p
                        )
                        """,

                        author=author,
                        paper_id=paper.paper_id
                    )

            logger.info(
                f"Graph paper inserted: "
                f"{paper.paper_id}"
            )

        except Exception as e:

            logger.exception(
                f"Graph ingestion failed "
                f"for paper "
                f"{paper.paper_id}: {e}"
            )
    @traceable(name="ingestion of neo4j entities")
    def ingest_entities(
        self,
        paper,
        entities
    ):

        try:

            with self.driver.session() as session:

                for method in entities.get(
                    "methods",
                    []
                ):

                    session.run(
                        """
                        MERGE (
                            m:Method {
                                name:$name
                            }
                        )

                        WITH m

                        MATCH (
                            p:Paper {
                                paper_id:$paper_id
                            }
                        )

                        MERGE
                        (
                            p
                        )-[:USES_METHOD]->
                        (
                            m
                        )
                        """,

                        name=method,
                        paper_id=paper.paper_id
                    )

                for dataset in entities.get(
                    "datasets",
                    []
                ):

                    session.run(
                        """
                        MERGE (
                            d:Dataset {
                                name:$name
                            }
                        )

                        WITH d

                        MATCH (
                            p:Paper {
                                paper_id:$paper_id
                            }
                        )

                        MERGE
                        (
                            p
                        )-[:EVALUATED_ON]->
                        (
                            d
                        )
                        """,

                        name=dataset,
                        paper_id=paper.paper_id
                    )

                for benchmark in entities.get(
                    "benchmarks",
                    []
                ):

                    session.run(
                        """
                        MERGE (
                            b:Benchmark {
                                name:$name
                            }
                        )

                        WITH b

                        MATCH (
                            p:Paper {
                                paper_id:$paper_id
                            }
                        )

                        MERGE
                        (
                            p
                        )-[:TESTED_ON]->
                        (
                            b
                        )
                        """,

                        name=benchmark,
                        paper_id=paper.paper_id
                    )

            logger.info(
                f"Entities inserted for "
                f"{paper.paper_id}"
            )

        except Exception as e:

            logger.exception(
                f"Entity ingestion failed "
                f"for {paper.paper_id}: {e}"
            )

    def create_indexes(self):

        with self.driver.session() as session:

            session.run(
                """
                CREATE CONSTRAINT paper_id_unique
                IF NOT EXISTS

                FOR (p:Paper)

                REQUIRE p.paper_id IS UNIQUE
                """
            )

            session.run(
                """
                CREATE INDEX author_name_idx
                IF NOT EXISTS

                FOR (a:Author)

                ON (a.name)
                """
            )

            session.run(
                """
                CREATE INDEX method_name_idx
                IF NOT EXISTS

                FOR (m:Method)

                ON (m.name)
                """
            )

            session.run(
                """
                CREATE INDEX dataset_name_idx
                IF NOT EXISTS

                FOR (d:Dataset)

                ON (d.name)
                """
            )

            session.run(
                """
                CREATE INDEX benchmark_name_idx
                IF NOT EXISTS

                FOR (b:Benchmark)

                ON (b.name)
                """
            )

            logger.info(
                "Neo4j indexes created"
            )