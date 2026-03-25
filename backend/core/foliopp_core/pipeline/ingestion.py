import uuid
from datetime import datetime
from backend.clients.minio import minio_client
from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import IngestedBatch
from backend.config import settings

class DataIngestionPipeline:
    def __init__(self, provider: str, fetcher_name: str):
        self.provider = provider
        self.fetcher_name = fetcher_name

    async def ingest(self, query: dict, data: list):
        """
        Phase 1 entry point:
        1. Save raw JSON to MinIO
        2. Create metadata record in Postgres
        """
        # 1. MinIO: Store the RAW response
        batch_id = str(uuid.uuid4())
        object_name = f"{self.provider}/{self.fetcher_name}/{batch_id}.json"
        
        await minio_client.ensure_bucket(settings.MINIO_BUCKET_RAW)
        await minio_client.upload_json(
            settings.MINIO_BUCKET_RAW, 
            object_name, 
            {"query": query, "data": [d.model_dump() if hasattr(d, "model_dump") else d for d in data]}
        )
        
        # 2. Postgres: Track the batch
        async with AsyncSessionLocal() as db:
            batch = IngestedBatch(
                provider=self.provider,
                fetcher_name=self.fetcher_name,
                query_params=query,
                raw_storage_uri=f"s3://{settings.MINIO_BUCKET_RAW}/{object_name}",
                entry_count=len(data)
            )
            db.add(batch)
            await db.commit()
            await db.refresh(batch)
            return batch.id

ingestor = DataIngestionPipeline  # Factory usage
