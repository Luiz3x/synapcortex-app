# =================================================================================
# SYNAPCORTEX - ANALYTICS SERVICES (v2.1 - Predictive Intelligence Engine)
# =================================================================================
# O cérebro de inteligência da SynapCortex. Enriquece dados com IA, classifica
# comportamentos e utiliza cache de alta performance para uma experiência instantânea.
# Arquitetura inspirada em sistemas de Big Data e Machine Learning.
# =================================================================================

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

from sqlalchemy import func, case
from sqlalchemy.orm import Session

# Importa os componentes da nossa aplicação
from ..extensions import db, cache
from ..models import AppUser, AnalyticsEvent

class AnalyticsService:
    """
    Encapsula a lógica para análise preditiva e processamento de dados.
    Utiliza injeção de dependência para o banco de dados e cache, promovendo
    alta testabilidade e desacoplamento.
    """

    def __init__(self, db_session: Session, cache_client):
        """
        Inicializa o serviço com as dependências necessárias.
        
        :param db_session: A sessão do SQLAlchemy para interagir com o DB.
        :param cache_client: O cliente de cache (ex: Redis) para performance.
        """
        self.db = db_session
        self.cache = cache_client
        self.cache_ttl_seconds = 300  # 5 minutos

    def get_home_dashboard_data(self, user: AppUser) -> Dict[str, Any]:
        """
        Busca, processa e enriquece os dados para a home do dashboard, com estratégia cache-first.
        
        :param user: O objeto do usuário logado.
        :return: Dicionário com dados para o painel principal, incluindo insights de IA.
        """
        cache_key = f"dashboard:home:{user.id}"
        if cached_data := self.cache.get(cache_key):
            return json.loads(cached_data)

        start_date = datetime.utcnow() - timedelta(days=30)
        
        # Query de agregação principal: calcula múltiplos KPIs em uma única passagem
        kpis = self.db.query(
            func.count(func.distinct(AnalyticsEvent.visitor_id)).label('total_visitors'),
            func.sum(case((AnalyticsEvent.event_name == 'purchase', AnalyticsEvent.event_data['value'].as_float()), else_=0)).label('total_revenue'),
            func.count(func.distinct(case((AnalyticsEvent.event_name == 'purchase', AnalyticsEvent.visitor_id), else_=None))).label('unique_purchasers')
        ).filter(
            AnalyticsEvent.user_id == user.id,
            AnalyticsEvent.timestamp >= start_date
        ).one()

        total_visitors = kpis.total_visitors or 0
        conversion_rate = (kpis.unique_purchasers / total_visitors * 100) if total_visitors > 0 else 0

        # Query para as páginas mais visitadas
        top_pages_query = self.db.query(
            AnalyticsEvent.event_data['url'].astext.label('page_name'),
            func.count(AnalyticsEvent.id).label('views')
        ).filter(
            AnalyticsEvent.user_id == user.id,
            AnalyticsEvent.event_name == 'page_view',
            AnalyticsEvent.timestamp >= start_date
        ).group_by('page_name').order_by(func.count(AnalyticsEvent.id).desc()).limit(5).all()

        top_pages = [{'name': page.page_name, 'views': page.views} for page in top_pages_query]
        
        dashboard_data = {
            'totalVisitors': total_visitors,
            'totalRevenue': round(float(kpis.total_revenue or 0), 2),
            'conversionRate': round(conversion_rate, 2),
            'topPages': top_pages,
            'userName': user.company_name,
            'cortexInsight': self._generate_ai_insight(conversion_rate, top_pages)
        }

        self.cache.set(cache_key, json.dumps(dashboard_data), ex=self.cache_ttl_seconds)
        return dashboard_data

    def get_enriched_visitors_dossier(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Busca e enriquece os dados para o dossiê de visitantes, classificando personas.
        """
        persona_classifier = case(
            (func.sum(case((AnalyticsEvent.event_name == 'purchase', AnalyticsEvent.event_data['value'].as_float()), else_=0)) > 500, 'Comprador Fiel'),
            (func.count(func.distinct(AnalyticsEvent.session_id)) > 3, 'Cliente em Potencial'),
            (func.sum(case((AnalyticsEvent.event_name == 'add_to_cart', 1), else_=0)) > 0, 'Interesse Elevado'),
            else_='Navegador Casual'
        ).label('persona')

        visitors_raw = self.db.query(
            AnalyticsEvent.visitor_id,
            func.max(AnalyticsEvent.timestamp).label('last_seen'),
            func.count(func.distinct(AnalyticsEvent.session_id)).label('session_count'),
            func.sum(case((AnalyticsEvent.event_name == 'purchase', AnalyticsEvent.event_data['value'].as_float()), else_=0)).label('total_spent'),
            persona_classifier
        ).filter(AnalyticsEvent.user_id == user_id).group_by(AnalyticsEvent.visitor_id).order_by(func.max(AnalyticsEvent.timestamp).desc()).limit(100).all()

        return [
            {
                'id': v.visitor_id,
                'lastSeen': v.last_seen.isoformat() + 'Z',
                'sessionCount': v.session_count,
                'totalSpent': round(float(v.total_spent or 0), 2),
                'persona': v.persona
            } for v in visitors_raw
        ]

    def _generate_ai_insight(self, conversion_rate: float, top_pages: List[Dict]) -> str:
        """[SIMULAÇÃO DE IA] Gera uma análise em linguagem natural baseada nos KPIs."""
        if not top_pages:
            return "Ainda não há dados suficientes para gerar um insight. Continue capturando eventos!"
        top_page_name = top_pages[0]['name']
        if conversion_rate > 5.0:
            return f"Parabéns! Sua taxa de conversão está excelente ({conversion_rate}%). A página '{top_page_name}' é uma verdadeira máquina de vendas!"
        elif conversion_rate > 2.0:
            return f"Bom trabalho! Sua conversão de {conversion_rate}% está sólida. Considere otimizar '{top_page_name}' com um teste A/B para potencializar ainda mais."
        else:
            return f"Sua conversão está em {conversion_rate}%. Um ponto de partida é analisar o funil de usuários que visitam '{top_page_name}' para identificar gargalos."

# --- FÁBRICA DO SERVIÇO (Padrão de Injeção de Dependência) ---

def get_analytics_service() -> AnalyticsService:
    """Fábrica que cria e retorna uma instância do serviço com as dependências atuais."""
    return AnalyticsService(db_session=db.session, cache_client=cache)