# synapcortex/__init__.py (v6.0 - Arquitetura Definitiva)
# =================================================================================
# SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO
# Versão final com Application Factory modularizada e aprimoramentos profissionais.
# =================================================================================

import os
import logging
from flask import Flask, Blueprint

# 1. Importações do projeto (Configuração e Extensões)
from .config import config_by_name
from .extensions import db, bcrypt, cors, migrate

def create_app(config_name: str = None) -> Flask:
    """
    Ponto de entrada principal (Application Factory).
    Cria, configura e retorna a instância da aplicação Flask.
    """
    app = Flask(__name__)
    
    # Carrega a configuração a partir da variável de ambiente ou do padrão
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config_by_name[config_name])

    # Registra os componentes da aplicação usando as funções auxiliares
    register_extensions(app)
    register_blueprints(app)
    register_commands_and_shell(app)
    configure_logging(app)

    return app

def register_extensions(app: Flask) -> None:
    """Conecta as extensões Flask à instância da aplicação."""
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)

def register_blueprints(app: Flask) -> None:
    """
    Detecta e registra todas as "alas" (Blueprints) da aplicação.
    """
    with app.app_context():
        from .blueprints import auth, dashboard, payments, routes_api
        
        # APRIMORAMENTO: Lista de blueprints para registro escalável
        blueprints: list[Blueprint] = [
            auth.auth_bp,
            dashboard.dashboard_bp,
            payments.payments_bp,
            routes_api.api_bp
        ]
        
        for bp in blueprints:
            app.register_blueprint(bp)

def register_commands_and_shell(app: Flask) -> None:
    """Registra os comandos CLI customizados e o contexto do shell."""
    from . import commands
    commands.register(app)
    
    @app.shell_context_processor
    def make_shell_context():
        """Pré-importa pacotes para o comando `flask shell` para facilitar o debug."""
        from .models import AppUser, AnalyticsEvent # Adicione outros modelos aqui
        return {'db': db, 'AppUser': AppUser, 'AnalyticsEvent': AnalyticsEvent}

def configure_logging(app: Flask) -> None:
    """Configura o sistema de logging para o ambiente de produção."""
    if not app.debug and not app.testing:
        handler = logging.StreamHandler()
        # APRIMORAMENTO: Formato de log profissional
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('SynapCortex inicializado.')