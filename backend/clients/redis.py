import redis.asyncio as aioredis
from backend.config import settings

class RedisClient:
    def __init__(self, url: str):
        self.url = url
        self.redis = None

    async def connect(self):
        if self.redis is None:
            self.redis = aioredis.from_url(
                self.url, 
                encoding="utf-8", 
                decode_responses=False
            )
        return self.redis

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        return await self.redis.set(key, value, ex=ex)

    async def close(self):
        if self.redis:
            await self.redis.close()

redis_client = RedisClient(settings.REDIS_URL)
