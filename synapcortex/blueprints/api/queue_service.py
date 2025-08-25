import json
from .cache_service import redis_client # Reutilizando a conexão Redis para Pub/Sub

class QueueService:
    async def publish(self, queue_name: str, message: dict):
        await redis_client.publish(queue_name, json.dumps(message))

_queue_service_instance = QueueService()
def get_queue_service():
    return _queue_service_instance