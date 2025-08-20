# synapcortex/services/analytics.py
from collections import defaultdict
from ..models import AppUser, AnalyticsEvent
from datetime import datetime, timedelta

def get_active_visitors(user_id: int) -> dict:
    """Busca e agrupa eventos de visitantes das últimas 24 horas."""
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
        # Futuramente, adicionaremos IP e User-Agent aqui
        visitors_data[event.visitor_id].append(event_details)
        
    return dict(visitors_data)