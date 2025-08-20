# =================================================================================
# SYNAPCORTEX - BLUEPRINT DO DASHBOARD (v3.0 - Unificado e Aprimorado)
# Responsável por todas as rotas e lógicas do painel do usuário,
# desde a visão geral até a análise detalhada de visitantes.
# =================================================================================

from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, g, jsonify, current_app)
from datetime import datetime, timedelta, timezone

# Importa as ferramentas, o DNA e os guardiões do nosso projeto
from ..extensions import db
from ..models import AppUser, AnalyticsEvent, SubscriptionStatus
from ..decorators import subscription_required
# Helpers para lógicas de negócio e formatação (essencial para a rota /visitors)
from .utils import analytics_service, format_helpers

# --- CRIAÇÃO DO BLUEPRINT ---
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# =================================================================================
# ROTAS DE RENDERIZAÇÃO DE PÁGINAS
# =================================================================================

@dashboard_bp.route('/')
@subscription_required
def home():
    """Renderiza a página principal do painel de controle."""
    user = g.user
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    popups_exibidos = user.events.filter(
        AnalyticsEvent.event_name == 'popup_exibido',
        AnalyticsEvent.timestamp >= thirty_days_ago
    ).count()
    
    dias_restantes = None
    if user.is_trial_active:
        delta = user.trial_end_date - datetime.utcnow()
        dias_restantes = max(0, delta.days)

    return render_template('dashboard/home.html', 
                           dias_restantes=dias_restantes,
                           popups_exibidos=popups_exibidos)


@dashboard_bp.route('/visitors')
@subscription_required
def visitors():
    """
    Renderiza o dossiê de visitantes ativos, enriquecendo os dados brutos
    com informações contextuais para uma análise mais profunda.
    """
    try:
        raw_visitor_events = analytics_service.get_active_visitors(user_id=g.user.id)
        visitors_data = _process_visitor_data(raw_visitor_events)
        return render_template('dashboard/visitors.html', visitors_data=visitors_data)
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar dados dos visitantes para {g.user.email}: {e}")
        flash("Ocorreu um erro ao carregar os dados dos visitantes. Tente novamente mais tarde.", "error")
        return render_template('dashboard/visitors.html', visitors_data=[])


# =================================================================================
# ROTAS DE API (AÇÕES DO USUÁRIO)
# =================================================================================

@dashboard_bp.route('/save-settings', methods=['POST'])
@subscription_required
def save_settings():
    """Recebe e salva TODAS as configurações do painel via AJAX (fetch)."""
    user = g.user
    form = request.form

    try:
        # --- Lógica para Gatilhos Gerais ---
        settings = user.settings or {}
        settings['ativar_abandono'] = 'ativar_abandono' in form
        # Adicione outros campos de gatilhos aqui conforme o form evoluir
        user.settings = settings

        db.session.commit()
        current_app.logger.info(f"Configurações salvas com sucesso para o usuário: {user.email}")
        return jsonify({'status': 'success', 'message': 'Configurações salvas com sucesso!'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao salvar configurações para {user.email}: {e}")
        return jsonify({'status': 'error', 'message': 'Ocorreu um erro interno. Nossa equipe foi notificada.'}), 500


@dashboard_bp.route('/cancel-account', methods=['POST'])
@subscription_required
def cancel_account():
    """Encerra a conta do usuário de forma segura."""
    user = g.user
    try:
        user.subscription_status = SubscriptionStatus.CANCELED
        # Adicionar aqui a lógica para cancelar a assinatura no Stripe, se aplicável
        db.session.commit()
        
        email = user.email # Salva o e-mail antes de limpar a sessão
        session.clear()
        
        current_app.logger.info(f"Conta encerrada com sucesso pelo usuário: {email}")
        flash('Sua conta foi encerrada. Agradecemos por usar a SynapCortex.', 'info')
        return jsonify({'status': 'success', 'redirect_url': url_for('auth.index')})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao encerrar conta para {user.email}: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao processar o encerramento da conta.'}), 500


# =================================================================================
# FUNÇÕES AUXILIARES (LÓGICA INTERNA)
# =================================================================================

def _process_visitor_data(raw_events: dict) -> list:
    """
    Função auxiliar para agrupar, ordenar e enriquecer os dados dos visitantes.
    É o cérebro por trás da inteligência da página de visitantes.
    """
    if not raw_events:
        return []

    processed_list = []
    
    for visitor_id, events in raw_events.items():
        sorted_events = sorted(events, key=lambda e: e['timestamp'], reverse=True)
        
        first_event_time = min(e['timestamp'] for e in events)
        last_event_time = max(e['timestamp'] for e in events)
        session_duration = format_helpers.timesince(first_event_time, last_event_time)
        
        # Mock de dados contextuais (isso viria de uma análise de IP ou User-Agent)
        location = format_helpers.get_location_from_ip(events[0].get('ip_address', ''))
        device_info = format_helpers.parse_user_agent(events[0].get('user_agent', ''))

        visitor_details = {
            'id': visitor_id,
            'location': location,
            'device_type': device_info['type'],
            'device_icon': device_info['icon'],
            'session_duration': session_duration,
            'events': [
                {
                    'title': event['title'],
                    'timestamp': format_helpers.humanize_time(event['timestamp']),
                    'full_timestamp': event['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                }
                for event in sorted_events
            ]
        }
        processed_list.append(visitor_details)

    # Ordena a lista final de visitantes pelo mais recente
    if processed_list:
        processed_list.sort(key=lambda v: max(e['full_timestamp'] for e in v['events']), reverse=True)
    
    return processed_list