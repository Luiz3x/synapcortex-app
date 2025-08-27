# =================================================================================
# src.SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO (v9.1 - Versão Unificada)
# =================================================================================
import os
import logging
from flask import Flask, g
from flask_login import current_user

from .config import config_by_name
from .extensions import db, bcrypt, cors, migrate, login_manager, csrf, socketio
from .models import AppUser

def create_app(config_name: str = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config_by_name[config_name])

    # --- CORREÇÃO FINAL: O MORDOMO ---
    # Esta função será executada antes de CADA requisição.
    # Ela garante que g.user esteja sempre disponível para os templates.
    @app.before_request
    def before_request_handler():
        """ Disponibiliza o usuário logado globalmente para os templates via g.user. """
        g.user = current_user

    register_extensions(app)
    register_blueprints(app)
    register_commands_and_shell(app)
    configure_logging(app)
    return app

def register_extensions(app: Flask) -> None:
    # ... (esta função continua perfeita, sem alterações) ...
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))
    login_manager.login_view = 'auth.index'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

def register_blueprints(app: Flask) -> None:
    # ... (esta função continua perfeita, com os blueprints desativados) ...
    with app.app_context():
        from .blueprints.auth import auth_bp
        from .blueprints.dashboard import dashboard_bp
        blueprints = [auth_bp, dashboard_bp]
        for bp in blueprints:
            app.register_blueprint(bp)

# Dentro de src/synapcortex/__init__.py

def register_commands_and_shell(app: Flask) -> None:
    # Importa o MÓDULO de comandos inteiro
    from . import commands
    # CHAMA a nossa nova função de registro explícita
    commands.register_commands(app)
    
    @app.shell_context_processor
    def make_shell_context():
        from .models import AppUser, AnalyticsEvent, PaymentEvent
        return {'db': db, 'AppUser': AppUser, 'AnalyticsEvent': AnalyticsEvent, 'PaymentEvent': PaymentEvent}

def configure_logging(app: Flask) -> None:
    # ... (esta função continua perfeita, sem alterações) ...
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(log_format)
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Sistema de logging do SynapCortex configurado com sucesso.')