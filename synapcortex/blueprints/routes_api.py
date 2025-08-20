# =================================================================================
# SYNAPCORTEX - BLUEPRINT DA API (v1.0)
# Ponto de entrada para toda a comunicação machine-to-machine (ex: spy.js).
# Otimizado para alta performance, segurança e validação rigorosa.
# =================================================================================

from flask import Blueprint, request, jsonify, current_app

from ..extensions import db
from ..models import AppUser, AnalyticsEvent

# --- CRIAÇÃO DO BLUEPRINT ---
# Todas as rotas aqui dentro terão o prefixo /api
api_bp = Blueprint('api', __name__, url_prefix='/api')


# --- ROTAS DO BLUEPRINT ---

@api_bp.route('/get-client-config')
def get_client_config():
    """
    Fornece a configuração do cliente para o spy.js.
    Endpoint público, mas que só retorna dados para chaves válidas e assinaturas ativas.
    """
    api_key = request.args.get('key')

    # 1. Validação "Fail-Fast"
    if not api_key:
        return jsonify(error='API Key não fornecida'), 400

    # 2. Busca Otimizada e Validação de Assinatura
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user or not user.is_subscription_valid:
        # Resposta genérica para não informar se a chave existe ou se a assinatura está inativa
        return jsonify(error='API Key inválida ou assinatura inativa'), 403

    # 3. Preparação da Resposta
    config_payload = {
        'settings': user.settings or {},
        'is_campaign_active': False
    }
    
    # Lógica de Campanha
    if user.is_campaign_active and user.campaign_start_date and user.campaign_end_date:
        if user.campaign_start_date <= datetime.utcnow() <= user.campaign_end_date:
            config_payload['is_campaign_active'] = True
            config_payload['campaign_config'] = user.campaign_config or {}
            config_payload['campaign_end_date'] = user.campaign_end_date.isoformat()
            
    return jsonify(config_payload)


@api_bp.route('/track', methods=['POST'])
def track_event():
    """
    Recebe eventos de rastreamento do spy.js e os salva no banco de dados.
    Otimizado para ser extremamente rápido e leve.
    """
    data = request.get_json()

    # 1. Validação "Fail-Fast" e "Zero Confiança"
    if not data:
        return jsonify(error='Requisição sem corpo JSON.'), 400
    
    api_key = data.get('apiKey')
    event_name = data.get('eventName')
    visitor_id = data.get('visitorId')

    if not all([api_key, event_name, visitor_id]):
        return jsonify(error='Campos obrigatórios faltando: apiKey, eventName, visitorId.'), 400

    try:
        # 2. Busca Ultra Otimizada: Buscamos apenas o ID do usuário.
        # Não carregamos colunas pesadas como 'settings' ou 'campaign_config'.
        user_tuple = db.session.query(AppUser.id).filter_by(api_key=api_key).first()

        if not user_tuple:
            return jsonify(error='API Key inválida.'), 403

        # 3. Criação e Salvamento do Evento
        new_event = AnalyticsEvent(
            owner_id=user_tuple[0],
            visitor_id=visitor_id,
            event_name=event_name,
            event_data=data.get('eventData', {})
        )
        db.session.add(new_event)
        db.session.commit()
        
        return jsonify(status='ok'), 200

    except Exception as e:
        db.session.rollback()
        # Logamos o erro no servidor, mas não o expomos para o cliente
        current_app.logger.error(f"Erro ao salvar evento da API para a key {api_key[:5]}...: {e}")
        return jsonify(error='Erro interno ao processar o evento.'), 500