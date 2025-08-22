# synapcortex/blueprints/api/routes.py
from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, ValidationError, Field
import json

from ...models import AppUser
from ...services.message_queue import publish_to_queue
from ...services.cache import get_cache, set_cache

api_bp = Blueprint('api', __name__, url_prefix='/api/v3')

# --- Schemas de Validação com Pydantic ---
class TrackEventPayload(BaseModel):
    apiKey: str
    eventName: str
    visitorId: str = Field(..., max_length=128)
    eventData: dict = {}

# --- Rotas do Blueprint (Assíncronas) ---
@api_bp.route('/get-client-config')
async def get_client_config():
    """Fornece a configuração do cliente, otimizada com cache-first."""
    api_key = request.args.get('key')
    if not api_key:
        return jsonify(error='API Key não fornecida.'), 400

    cache_key = f"config:{api_key}"
    cached_config = await get_cache(cache_key)
    if cached_config:
        return jsonify(json.loads(cached_config))

    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user or not user.is_subscription_valid:
        return jsonify(error='API Key inválida ou assinatura inativa.'), 403

    config_payload = {'settings': user.settings or {}, 'is_campaign_active': user.is_campaign_active}
    # ... (outra lógica de campanha)

    await set_cache(cache_key, json.dumps(config_payload), expire_seconds=300)
    return jsonify(config_payload)


@api_bp.route('/track', methods=['POST'])
async def track_event():
    """Recebe eventos e os publica em uma fila para processamento assíncrono."""
    try:
        payload = TrackEventPayload(**request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify(error="Dados inválidos.", details=e.errors()), 422

    try:
        await publish_to_queue('analytics_events', payload.dict())
        return jsonify(status='accepted'), 202
    except Exception as e:
        current_app.logger.error(f"Falha ao publicar evento na fila: {e}")
        return jsonify(error='Serviço temporariamente indisponível.'), 503