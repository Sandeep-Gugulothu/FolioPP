import aioboto3
from backend.config import settings

class MinIOClient:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.secure = settings.MINIO_SECURE

    async def get_client(self):
        return self.session.client(
            "s3",
            endpoint_url=f"http{'s' if self.secure else ''}://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    async def ensure_bucket(self, bucket_name: str):
        async with self.session.client(
            "s3",
            endpoint_url=f"http{'s' if self.secure else ''}://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as s3:
            try:
                await s3.head_bucket(Bucket=bucket_name)
            except:
                await s3.create_bucket(Bucket=bucket_name)

    async def upload_json(self, bucket: str, object_name: str, data: dict):
        import json
        async with self.session.client(
            "s3",
            endpoint_url=f"http{'s' if self.secure else ''}://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as s3:
            await s3.put_object(
                Bucket=bucket,
                Key=object_name,
                Body=json.dumps(data),
                ContentType="application/json"
            )

minio_client = MinIOClient()
