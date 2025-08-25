# src.synapcortex/blueprints/__init__.py
# =================================================================================
# PONTO DE ENTRADA DOS BLUEPRINTS - VERSÃO CORRIGIDA
# A única função deste arquivo é importar as variáveis dos blueprints
# para que o create_app possa registrá-las facilmente.
# Nenhuma outra lógica ou importação deve estar aqui.
# =================================================================================

from .auth import auth_bp
from .dashboard import dashboard_bp
# from .payments import payments_bp  # <-- AJUSTE AQUI: Comente esta linha por enquanto
from .routes_api import api_bp

# NADA MAIS. O ARQUIVO DEVE TERMINAR AQUI.