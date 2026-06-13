from neo4j import GraphDatabase


class GraphIngestor:

    def __init__(
        self,
        uri,
        username,
        password
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

    def close(self):
        self.driver.close()

    def ingest_paper(
        self,
        paper
    ):

        with self.driver.session() as session:

            session.run(
                """
                MERGE (
                    p:Paper {
                        paper_id:$paper_id
                    }
                )

                SET
                    p.title=$title,
                    p.year=$year,
                    p.paper_url=$paper_url
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
                            name:$author_name
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
                        p
                    )-[:AUTHORED_BY]->
                    (
                        a
                    )
                    """,

                    author_name=author,
                    paper_id=paper.paper_id
                )

    def ingest_entities(
        self,
        paper,
        entities
    ):

        with self.driver.session() as session:

            # your methods code here
            pass