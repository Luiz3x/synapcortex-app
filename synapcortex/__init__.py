# synapcortex/__init__.py (v4.0 - Arquitetura Blindada para Produção)
# =================================================================================
# SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO
# Versão final com Application Factory, logging para produção e otimizações.
# =================================================================================

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from .config import config_by_name
from .extensions import db, bcrypt, cors, migrate

def create_app(config_name: str = None) -> Flask:
    """Cria, configura e retorna a instância da aplicação Flask."""
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config_by_name[config_name])

    # Registra as extensões, a configuração de logging e os blueprints.
    register_extensions(app)
    register_blueprints(app)
    register_commands_and_shell(app)
    configure_logging(app)

    return app

def register_extensions(app: Flask):
    """Conecta as extensões Flask à aplicação."""
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)

def register_blueprints(app: Flask):
    """Registra todas as "alas" (Blueprints) da aplicação."""
    with app.app_context():
        from .blueprints import auth, dashboard, payments, routes_api
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(dashboard.dashboard_bp)
        app.register_blueprint(payments.payments_bp)
        app.register_blueprint(routes_api.api_bp)

def register_commands_and_shell(app: Flask):
    """Registra os comandos CLI e o contexto do shell."""
    from . import commands
    from .models import AppUser, AnalyticsEvent
    
    commands.register(app)
    
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'AppUser': AppUser, 'AnalyticsEvent': AnalyticsEvent}

def configure_logging(app: Flask):
    """Configura o sistema de logging para produção."""
    if not app.debug and not app.testing:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('SynapCortex inicializado.')