# src.synapcortex/services/__init__.py
# =================================================================================
# SERVICES - PONTO DE EXPORTAÇÃO
# Este arquivo torna os serviços (lógicas de negócio) facilmente importáveis
# pelo resto da aplicação, como os Blueprints.
# =================================================================================

# Importa as funções/objetos específicos dos seus módulos de serviço
from .analytics import get_active_visitors as analytics_service
# Adicione a importação do seu user_service aqui. Exemplo:
# from .user import get_user_details as user_service

# É uma boa prática, mas se o user_service não estiver pronto,
# você pode comentar a linha acima e a importação no dashboard.py por enquanto.