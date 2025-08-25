# src/synapcortex/services/cache_service.py
from ..extensions import redis_cache

class CacheService:
    def __init__(self, cache_client):
        self.cache = cache_client

    async def get(self, key: str):
        # Em um app real, aqui teríamos lógica assíncrona
        return self.cache.get(key)

    async def set(self, key: str, value: str, expire_seconds: int):
        return self.cache.set(key, value, ex=expire_seconds)

def get_cache_service() -> CacheService:
    """Fábrica que cria e retorna uma instância do serviço de cache."""
    return CacheService(cache_client=redis_cache)