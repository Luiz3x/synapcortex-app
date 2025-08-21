# =================================================================================
# DECORATORS - PONTO DE EXPORTAÇÃO
# Este arquivo torna os decoradores customizados da aplicação
# facilmente importáveis pelos Blueprints.
# =================================================================================

# Expõe o decorador 'subscription_required' do módulo 'auth.py' para o resto da app.
from .auth import subscription_required