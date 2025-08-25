# Onde salvar: src.synapcortex/services/analytics.py (Substituir o conteúdo)
# =================================================================================
# SERVIÇO DE ANÁLISE (v2.0 - Unificado e Completo)
# Centraliza toda a lógica de busca e processamento de dados de análise.
# =================================================================================

from collections import defaultdict
from datetime import datetime, timedelta

# Importa os models e helpers necessários
from ..models import AppUser, AnalyticsEvent
from ..utils import format_helpers # Verifique se o caminho está correto

# ---------------------------------------------------------------------------------
# FUNÇÕES DE BUSCA DE DADOS BRUTOS (RAW DATA)
# ---------------------------------------------------------------------------------

def get_active_visitors(user_id: int) -> dict:
    """
    Busca e agrupa eventos de visitantes das últimas 24 horas.
    (Esta é a sua função original, integrada aqui).
    """
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    
    events = AnalyticsEvent.query.filter(
        AnalyticsEvent.owner_id == user_id,
        AnalyticsEvent.event_name == 'pagina_visitada',
        AnalyticsEvent.timestamp >= twenty_four_hours_ago
    ).order_by(AnalyticsEvent.timestamp.desc()).limit(200).all()
    
    visitors_data = defaultdict(list)
    for event in events:
        event_details = event.event_data or {}
        event_details['timestamp'] = event.timestamp
        event_details['ip_address'] = event.ip_address
        event_details['user_agent'] = event.user_agent
        visitors_data[event.visitor_id].append(event_details)
        
    return dict(visitors_data)

# ---------------------------------------------------------------------------------
# FUNÇÕES DE LÓGICA DE NEGÓCIO (PROCESSAMENTO)
# ---------------------------------------------------------------------------------

def get_home_dashboard_data(user: AppUser) -> dict:
    """Busca e calcula os dados para a página principal do dashboard."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    popups_exibidos = user.events.filter(
        AnalyticsEvent.event_name == 'popup_exibido',
        AnalyticsEvent.timestamp >= thirty_days_ago
    ).count()
    
    dias_restantes = None
    if user.is_trial_active and user.trial_end_date:
        delta = user.trial_end_date - datetime.utcnow()
        dias_restantes = max(0, delta.days)
        
    return {
        'dias_restantes': dias_restantes,
        'popups_exibidos': popups_exibidos
    }

def get_processed_visitors_data(user_id: int) -> list:
    """
    Orquestra a busca e o processamento dos dados dos visitantes para exibição.
    """
    raw_visitor_events = get_active_visitors(user_id=user_id)
    if not raw_visitor_events:
        return []

    processed_list = []
    for visitor_id, events in raw_visitor_events.items():
        sorted_events = sorted(events, key=lambda e: e['timestamp'], reverse=True)
        
        first_event_time = min(e['timestamp'] for e in events)
        last_event_time = max(e['timestamp'] for e in events)
        session_duration = format_helpers.timesince(first_event_time, last_event_time)
        
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
                    'title': event.get('title', 'Página Desconhecida'),
                    'timestamp': format_helpers.humanize_time(event['timestamp']),
                    'full_timestamp': event['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                }
                for event in sorted_events
            ]
        }
        processed_list.append(visitor_details)

    # Ordena a lista final pelo visitante mais recente
    if processed_list:
        processed_list.sort(key=lambda v: max(e['full_timestamp'] for e in v['events']), reverse=True)
    
    return processed_list