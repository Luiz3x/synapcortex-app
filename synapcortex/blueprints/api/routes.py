# =================================================================================
# SYNAPCORTEX - API PÚBLICA (v4.0 - "Olympus")
# Ponto de entrada para a API FastAPI de alta performance.
# =================================================================================

from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import json
import logging
from typing import Dict, Any

# Importa os serviços e modelos da nossa biblioteca 'synapcortex'
from synapcortex.services.cache_service import CacheService, get_cache_service
from synapcortex.services.queue_service import QueueService, get_queue_service
from synapcortex.services.security_service import get_current_user
from synapcortex.models import AppUser

# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---
app = FastAPI(
    title="SynapCortex Public API",
    description="API de alta performance para coleta e configuração de dados em tempo real.",
    version="4.0.0",
    docs_url="/api/v4/docs", # Documentação interativa
    redoc_url="/api/v4/redoc" # Documentação alternativa
)

logging.basicConfig(level=logging.INFO, format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')

# --- DEFINIÇÃO DE SCHEMAS (DTOs - Data Transfer Objects) ---
class TrackEventPayload(BaseModel):
    eventName: str = Field(..., example="page_view")
    visitorId: str = Field(..., max_length=128, description="Identificador único do visitante.", example="vis-12345-abcde")
    eventData: Dict[str, Any] = Field({}, description="Dados adicionais do evento.", example={"url": "/products/synapse-enhancer"})

class ClientConfigResponse(BaseModel):
    settings: Dict[str, Any]
    is_campaign_active: bool

# --- ROTAS DA API ---
@app.get("/api/v4/config", response_model=ClientConfigResponse, tags=["Configuração"])
async def get_client_config(
    user: AppUser = Depends(get_current_user),
    cache: CacheService = Depends(get_cache_service)
):
    """ Fornece a configuração do cliente, otimizada com cache-first. """
    cache_key = f"config:{user.api_key}"
    if cached_config := await cache.get(cache_key):
        return json.loads(cached_config)

    config_payload = {
        'settings': user.settings or {},
        'is_campaign_active': user.is_campaign_active
    }
    await cache.set(cache_key, json.dumps(config_payload), expire_seconds=300)
    return config_payload

@app.post("/api/v4/track", status_code=status.HTTP_202_ACCEPTED, tags=["Eventos"])
async def track_event(
    payload: TrackEventPayload,
    request: Request,
    user: AppUser = Depends(get_current_user),
    queue: QueueService = Depends(get_queue_service)
):
    """ Recebe, valida e enfileira eventos de rastreamento para processamento assíncrono. """
    try:
        event_message = payload.dict()
        event_message.update({
            "apiKey": user.api_key,
            "ip_address": request.client.host,
            "user_agent": request.headers.get("User-Agent")
        })
        
        await queue.publish('analytics_events', event_message)
        return {"status": "accepted"}
    except Exception as e:
        logging.error(f"Falha ao enfileirar evento: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de coleta de eventos temporariamente indisponível."
        )

# Para rodar localmente: uvicorn api:app --reload --port 8000