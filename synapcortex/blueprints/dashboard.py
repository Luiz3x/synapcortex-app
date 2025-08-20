# synapcortex/blueprints/dashboard.py (v4.0 - Arquitetura Profissional)
# =================================================================================
# BLUEPRINT DO DASHBOARD - FOCO EM ROTAS E RENDERIZAÇÃO
# =================================================================================

from flask import (Blueprint, render_template, request, url_for, 
                   flash, jsonify, current_app)
from flask_login import current_user, logout_user

# Importa os decoradores e os novos módulos de serviço
from ..decorators import subscription_required
from ..services import user_service, analytics_service

# --- CRIAÇÃO DO BLUEPRINT ---
# O blueprint agora só gerencia as URLs e a comunicação entre o navegador e os serviços.
dashboard_bp = Blueprint(
    'dashboard', 
    __name__, 
    url_prefix='/dashboard',
    template_folder='templates'
)

# =================================================================================
# ROTAS DE RENDERIZAÇÃO DE PÁGINAS
# =================================================================================

@dashboard_bp.route('/')
@subscription_required
def home():
    """Renderiza a página principal do painel, buscando dados através dos serviços."""
    try:
        dashboard_data = analytics_service.get_home_dashboard_data(current_user)
        return render_template('dashboard/home.html', **dashboard_data)
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar home do dashboard para {current_user.email}: {e}")
        flash("Não foi possível carregar os dados do painel. Tente novamente.", "error")
        return render_template('dashboard/home.html')

@dashboard_bp.route('/visitors')
@subscription_required
def visitors():
    """Renderiza o dossiê de visitantes, com dados já processados pelo serviço."""
    try:
        visitors_data = analytics_service.get_processed_visitors_data(current_user.id)
        return render_template('dashboard/visitors.html', visitors_data=visitors_data)
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar visitantes para {current_user.email}: {e}")
        flash("Ocorreu um erro ao carregar os dados dos visitantes.", "error")
        return render_template('dashboard/visitors.html', visitors_data=[])

# =================================================================================
# ROTAS DE API (AÇÕES DO USUÁRIO)
# =================================================================================

@dashboard_bp.route('/save-settings', methods=['POST'])
@subscription_required
def save_settings_api():
    """Endpoint da API que delega o salvamento de configurações para o user_service."""
    try:
        user_service.update_user_settings(current_user, request.form)
        return jsonify({'status': 'success', 'message': 'Configurações salvas com sucesso!'})
    except Exception as e:
        current_app.logger.error(f"API Erro ao salvar config para {current_user.email}: {e}")
        return jsonify({'status': 'error', 'message': 'Ocorreu um erro interno ao salvar.'}), 500

@dashboard_bp.route('/cancel-account', methods=['POST'])
@subscription_required
def cancel_account_api():
    """Endpoint da API que delega o cancelamento da conta para o user_service."""
    try:
        user_service.cancel_user_account(current_user)
        logout_user() # Forma correta e segura de fazer logout
        return jsonify({'status': 'success', 'redirect_url': url_for('auth.login')})
    except Exception as e:
        current_app.logger.error(f"API Erro ao cancelar conta para {current_user.email}: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao processar o encerramento.'}), 500