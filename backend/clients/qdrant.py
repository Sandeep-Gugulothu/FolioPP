from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from backend.config import settings

class QdrantClientWrapper:
    def __init__(self):
        if settings.QDRANT_API_KEY:
            endpoint = settings.QDRANT_HOST
            if not endpoint.startswith("http"):
                endpoint = f"https://{endpoint}"
            self.client = AsyncQdrantClient(
                url=endpoint,
                api_key=settings.QDRANT_API_KEY
            )
        else:
            self.client = AsyncQdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )

    async def create_collection(self, collection_name: str, vector_size: int):
        try:
            await self.client.get_collection(collection_name)
        except Exception:
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                ),
            )

    async def upsert(self, collection_name: str, points: list):
        return await self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    async def search(self, collection_name: str, vector: list, limit: int = 5):
        return await self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

qdrant_client = QdrantClientWrapper()
