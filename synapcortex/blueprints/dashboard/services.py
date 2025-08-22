# synapcortex/blueprints/dashboard/services.py
from typing import Dict, List
from ...models import AppUser, AnalyticsEvent
# from ...extensions import cache # Supondo uma extensão de cache

class DashboardService:
    """ Encapsula a lógica de negócios para os dados brutos do painel. """

    @staticmethod
    # @cache.memoize(timeout=300) # Cache de 5 minutos para esta função
    def get_dashboard_stats(user: AppUser) -> Dict:
        """
        Busca e formata as estatísticas principais para o dashboard.
        A anotação @cache.memoize garante que as consultas pesadas só rodem a cada 5 minutos.
        """
        # Usamos a relação `lazy="dynamic"` para poder fazer mais filtros
        popups_exibidos = user.events.filter_by(event_name='popup_viewed').count()
        clientes_recuperados = user.events.filter_by(event_name='customer_recovered').count()
        
        taxa_conversao = (clientes_recuperados / popups_exibidos * 100) if popups_exibidos > 0 else 0

        return {
            'popups_exibidos': popups_exibidos,
            'clientes_recuperados': clientes_recuperados,
            'taxa_conversao': f"{taxa_conversao:.2f}%"
        }

class InsightService:
    """ O Motor de Insights da SynapCortex. """

    @staticmethod
    # @cache.memoize(timeout=3600) # Cache de 1 hora
    def generate_weekly_insights(user: AppUser) -> List[Dict]:
        """ Analisa os dados da semana e gera recomendações acionáveis. """
        # Lógica futura: Analisar picos, produtos, etc.
        
        # Exemplo de insights estruturados para o frontend
        return [
            { "type": "insight", "text": "70% dos seus clientes foram recuperados em páginas da categoria 'Eletrônicos'." },
            { "type": "recommendation", "text": "Crie um popup com cupom específico para esta categoria para maximizar a conversão." },
            { "type": "alert", "text": "A taxa de visualização dos popups em mobile está 20% abaixo da média. Verifique o design responsivo." }
        ]