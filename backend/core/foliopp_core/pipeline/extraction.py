import uuid
from langchain_openai import OpenAIEmbeddings
from qdrant_client.http import models as qmodels
from backend.clients.qdrant import qdrant_client
from backend.clients.neo4j import neo4j_client
from backend.config import settings

class KnowledgeExtractionPipeline:
    def __init__(self, collection_name: str = "portfolio-knowledge"):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        self.collection_name = collection_name

    async def extract_vector(self, text: str, metadata: dict):
        """
        Phase 2: Generate embeddings and store in Qdrant
        """
        vector = await self.embeddings.aembed_query(text)
        point_id = str(uuid.uuid4())
        
        await qdrant_client.create_collection(self.collection_name, 1536)
        await qdrant_client.upsert(
            self.collection_name, 
            points=[
                qmodels.PointStruct(
                    id=point_id, 
                    vector=vector, 
                    payload=metadata
                )
            ]
        )
        return point_id

    async def extract_graph(self, symbol: str, head: str, relationship: str, tail: str):
        """
        Phase 2: Store relationships in Neo4j
        Example: (Symbol:SBIN)-[:BELONGS_TO]->(Sector:Banking)
        """
        query = f"""
        MERGE (s:Security {{symbol: $symbol}})
        MERGE (h:{head.capitalize()} {{name: $head_val}})
        MERGE (t:{tail.capitalize()} {{name: $tail_val}})
        MERGE (h)-[r:{relationship.upper()}]->(t)
        RETURN count(r)
        """
        params = {
            "symbol": symbol,
            "head_val": head,
            "tail_val": tail
        }
        return await neo4j_client.execute_query(query, params)

extractor = KnowledgeExtractionPipeline()
