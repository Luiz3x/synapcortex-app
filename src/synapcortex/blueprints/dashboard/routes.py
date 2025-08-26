# =================================================================================
# SYNAPCORTEX - BLUEPRINT DO DASHBOARD (v6.0 - Versão Unificada e Inteligente)
# =================================================================================

from flask import (
    Blueprint, render_template, request, jsonify, 
    current_app, url_for, flash, g
)
from flask_login import login_required, logout_user
from pydantic import ValidationError

# Importa os serviços especializados
from ..services.analytics_service import get_analytics_service
from .services import UserService

# Importa os schemas para validação
from .schemas import UserSettingsSchema

# --- CRIAÇÃO DO BLUEPRINT ---
dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    url_prefix='/dashboard',
    template_folder='../../../templates/dashboard'
)

# =================================================================================
# ROTAS DE RENDERIZAÇÃO DE PÁGINAS
# =================================================================================

@dashboard_bp.route('/') # Mudei para a raiz do dashboard
@login_required
def home():
    """
    Renderiza a página principal do painel, buscando os dados através do serviço de analytics.
    """
    try:
        # Agora o painel volta a ser inteligente!
        analytics_service = get_analytics_service()
        # Passamos g.user, que agora sabemos que existe graças ao nosso "mordomo".
        dashboard_data = analytics_service.get_home_dashboard_data(g.user)
        return render_template('home.html', **dashboard_data)
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar home do dashboard para {g.user.email}: {e}", exc_info=True)
        flash("Não foi possível carregar os dados do painel. Tente novamente.", "error")
        # Retorna o template mesmo em caso de erro, para a página não quebrar.
        return render_template('home.html')

@dashboard_bp.route('/visitors')
@login_required
def visitors():
    """Renderiza a página do dossiê de visitantes."""
    return render_template('visitors.html')

@dashboard_bp.route('/settings')
@login_required
def settings():
    """Renderiza a página de configurações da conta."""
    return render_template('settings.html')

# =================================================================================
# ROTAS DE API (O Motor da SynapCortex)
# =================================================================================

@dashboard_bp.route('/api/v1/settings', methods=['PUT'])
@login_required
def save_settings_api():
    """Endpoint para ATUALIZAR as configurações do usuário."""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 'error', 'message': 'Requisição sem dados (JSON).'}), 400

        validated_data = UserSettingsSchema(**json_data)

        # Usamos g.user aqui também para consistência
        success, message = UserService.update_user_settings(
            user=g.user, 
            settings_data=validated_data.dict()
        )

        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message}), 422

    except ValidationError as e:
        current_app.logger.warning(f"API Falha de validação para {g.user.id}: {e.errors()}")
        return jsonify({'status': 'error', 'message': 'Dados inválidos.', 'details': e.errors()}), 400
        
    except Exception as e:
        current_app.logger.error(f"API Erro ao salvar config para {g.user.id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Ocorreu um erro interno no servidor.'}), 500

@dashboard_bp.route('/api/v1/account', methods=['DELETE'])
@login_required
def cancel_account_api():
    """Endpoint para ENCERRAR a conta do usuário."""
    try:
        # Dispara a tarefa assíncrona de cancelamento
        success, message = UserService.trigger_cancel_account_task(g.user)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 422

        logout_user()
        
        return jsonify({
            'status': 'success', 
            'message': 'O processo de encerramento da sua conta foi iniciado.',
            'data': {
                'redirect_url': url_for('auth.index', _external=True)
            }
        })
    except Exception as e:
        current_app.logger.error(f"API Erro ao cancelar conta para {g.user.id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Erro ao processar o encerramento da conta.'}), 500