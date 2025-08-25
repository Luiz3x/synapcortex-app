# src/synapcortex/services/queue_service.py
from ..extensions import celery_app

class QueueService:
    def __init__(self, task_queue):
        self.queue = task_queue

    async def publish(self, queue_name: str, message: dict):
        # Publica uma tarefa na fila especificada
        self.queue.send_task(name=queue_name, kwargs=message)

def get_queue_service() -> QueueService:
    """Fábrica que cria e retorna uma instância do serviço de fila."""
    return QueueService(task_queue=celery_app)