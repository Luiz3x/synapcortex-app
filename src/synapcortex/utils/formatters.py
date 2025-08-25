# src.synapcortex/utils/formatters.py
from datetime import datetime, timezone

def humanize_time(dt: datetime) -> str:
    """Transforma um datetime em uma string amigável (ex: 'há 2 minutos')."""
    now = datetime.now(timezone.utc)
    dt_utc = dt.replace(tzinfo=timezone.utc)
    diff = now - dt_utc
    
    seconds = diff.total_seconds()
    if seconds < 60: return "agora mesmo"
    minutes = seconds / 60
    if minutes < 60: return f"há {int(minutes)} minuto(s)"
    hours = minutes / 60
    if hours < 24: return f"há {int(hours)} hora(s)"
    days = hours / 24
    return f"há {int(days)} dia(s)"

# As funções abaixo são exemplos que podem ser expandidos no futuro
def get_location_from_ip(ip: str) -> str:
    return "Localização Desconhecida"

def parse_user_agent(ua_string: str) -> dict:
    if 'mobi' in ua_string.lower():
        return {'type': 'Mobile', 'icon': 'fas fa-mobile-alt'}
    return {'type': 'Desktop', 'icon': 'fas fa-desktop'}

def timesince(start_time, end_time) -> str:
    """Calcula a duração da sessão de forma amigável."""
    duration_seconds = (end_time - start_time).total_seconds()
    if duration_seconds < 60:
        return f"{int(duration_seconds)} seg"
    return f"{int(duration_seconds / 60)} min"