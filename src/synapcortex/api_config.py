# /src/synapcortex/api_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class ApiSettings(BaseSettings):
    """
    Configurações para a API FastAPI.
    Pydantic lê e valida automaticamente as variáveis do nosso arquivo .env.
    """
    # Exemplo de variáveis que a API precisa
    REDIS_URL: str = "redis://localhost:6379"
    QUEUE_URL: str = "amqp://guest:guest@localhost:5672/" # Para RabbitMQ
    
    # Chave de segurança para os tokens de autenticação da API (JWT)
    API_JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instância única que será usada em toda a API
settings = ApiSettings()