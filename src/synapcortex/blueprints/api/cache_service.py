import os
import redis.asyncio as redis

class CacheService:
    def __init__(self):
        self.client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost"))

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire_seconds: int):
        await self.client.setex(key, expire_seconds, value)

# Instância única para ser usada na injeção de dependências
_cache_service_instance = CacheService()
def get_cache_service():
    return _cache_service_instance