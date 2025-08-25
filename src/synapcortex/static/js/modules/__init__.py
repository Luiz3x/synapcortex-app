# src.synapcortex/modules/__init__.py
# =================================================================================
# MODULES (MODELS) - PONTO DE EXPORTAÇÃO
# Este arquivo torna os modelos de banco de dados (o "DNA" da aplicação)
# facilmente importáveis pelos Blueprints e Serviços.
# =================================================================================

# Importa as classes dos seus arquivos de modelo que estão nesta pasta
from .user import AppUser, SubscriptionStatus
from .analytics import AnalyticsEvent