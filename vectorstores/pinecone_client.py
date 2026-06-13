import os

from dotenv import load_dotenv

from pinecone import Pinecone

from utils.logging_config import setup_pipeline_logger

# Instantiate the module-level logger at the top of the file
logger = setup_pipeline_logger("ingestion_pipeline")

load_dotenv()

# This class is used to interact with Pinecone. It will be used in the embedding worker to upsert the embeddings to Pinecone.
class PineconeClient:

    def __init__(self):

        self.api_key = os.getenv(   #api key for pinecone
            "PINECONE_API_KEY"  
        )

        self.index_name = os.getenv(    #name of the pinecone index to use
            "PINECONE_INDEX_NAME"
        )

        if not self.api_key:
            raise ValueError(
                "Missing PINECONE_API_KEY"
            )

        #run this in the class constructor to initialize the connection to Pinecone
        pc = Pinecone(
            api_key=self.api_key
        )
        # Initialize the index object to interact with the Pinecone index
        self.index = pc.Index(
            self.index_name
        )
    def upsert(
        self,
        vectors: list[dict]
    ):
        logger.info(f"Upserting {len(vectors)} vectors to Pinecone index '{self.index_name}'")
        self.index.upsert(
            vectors=vectors
        )
        logger.info(f"Successfully upserted {len(vectors)} vectors to Pinecone index '{self.index_name}'")
    def query(
        self,
        vector: list[float],
        top_k: int = 5
    ):
        logger.info(f"Querying Pinecone index '{self.index_name}' for top {top_k} results")
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        logger.info(f"Successfully queried Pinecone index '{self.index_name}' for top {top_k} results") 