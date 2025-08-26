# =================================================================================
# SYNAPCORTEX - BLUEPRINT DO DASHBOARD (v6.3 - Arquitetura Padronizada)
# Análise: Sócio.ai
# =================================================================================

from flask import Blueprint, render_template, current_app, flash, g
from flask_login import login_required
from typing import cast

# Importações padronizadas com a nossa arquitetura
from synapcortex.services.analytics_service import get_analytics_service
from synapcortex.models import AppUser # PADRONIZADO: Usando AppUser

# ---------------------------------------------------------------------------------
# Configuração do Blueprint
# ---------------------------------------------------------------------------------
# url_prefix='/dashboard' torna as rotas mais limpas e intuitivas.
# Ex: /dashboard/, /dashboard/visitors, /dashboard/settings
# ---------------------------------------------------------------------------------
dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    url_prefix='/dashboard', # OTIMIZADO
    template_folder='../../../templates'
)

# =================================================================================
# ROTAS DO DASHBOARD
# =================================================================================

@dashboard_bp.route('/') # OTIMIZADO: Rota principal do dashboard
@login_required
def home() -> str:
    """
    Renderiza a página principal do painel (home), buscando os dados
    analíticos essenciais através do analytics_service.
    """
    user = cast(AppUser, g.user) # PADRONIZADO: Usando AppUser
    context = {} 

    try:
        analytics_service = get_analytics_service()
        dashboard_data = analytics_service.get_home_dashboard_data(user)
        context.update(dashboard_data)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar home do dashboard para {user.email}: {e}", exc_info=True)
        flash("Não foi possível carregar os dados do painel. Por favor, tente novamente mais tarde.", "error")
        
    return render_template('dashboard/home.html', **context)


@dashboard_bp.route('/visitors')
@login_required
def visitors() -> str:
    """Renderiza a página do dossiê de visitantes."""
    user = cast(AppUser, g.user) # PADRONIZADO: Usando AppUser
    context = {'visitors_data': []}

    try:
        # LÓGICA FUTURA: Chamar o analytics_service para buscar dados dos visitantes
        pass
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar dados de visitantes para {user.email}: {e}", exc_info=True)
        flash("Não foi possível carregar os dados dos visitantes.", "error")

    return render_template('dashboard/visitors.html', **context)


@dashboard_bp.route('/settings')
@login_required
def settings() -> str:
    """Renderiza a página de configurações da conta do usuário."""
    user = cast(AppUser, g.user) # PADRONIZADO: Usando AppUser
    context = {}

    try:
        # Passa os dados existentes do usuário para preencher o formulário
        context['user_settings'] = {
            'email': user.email,
            'company_name': user.nome_empresa # PADRONIZADO: Usando o campo correto do modelo
        }
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar página de configurações para {user.email}: {e}", exc_info=True)
        flash("Não foi possível carregar suas configurações.", "error")

    return render_template('dashboard/settings.html', **context)