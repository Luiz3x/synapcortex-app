# =================================================================================
# SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO (v7.0 - Final)
# Versão final com Application Factory, login, CSRF, Sockets e todos os blueprints.
# =================================================================================

import os
import logging
from flask import Flask

# 1. Importações do projeto
from .config import config_by_name
from .extensions import db, bcrypt, cors, migrate, login_manager, csrf, socketio
from .models import AppUser

def create_app(config_name: str = None) -> Flask:
    """
    Ponto de entrada principal (Application Factory).
    Cria, configura e retorna a instância da aplicação Flask.
    """
    app = Flask(__name__)
    
    # Carrega a configuração a partir do ambiente (development/production)
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config_by_name[config_name])

    # Registra todos os componentes da aplicação
    register_extensions(app)
    register_blueprints(app)
    register_commands_and_shell(app)
    configure_logging(app)

    return app

def register_extensions(app: Flask) -> None:
    """Conecta e configura todas as extensões Flask."""
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app) # <-- SocketIO ativado aqui

    # --- Configuração do Sistema de Login ---
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))
    
    login_manager.login_view = 'auth.index' # Rota para redirecionar não-logados
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

def register_blueprints(app: Flask) -> None:
    """Detecta e registra todos os Blueprints da aplicação."""
    with app.app_context():
        from .blueprints.auth.routes import auth_bp
        from .blueprints.dashboard.routes import dashboard_bp, dashboard_api_bp
        from .blueprints.api.routes import api_bp
        
        # Lista central de todos os blueprints a serem registrados
        blueprints = [
            auth_bp,
            dashboard_bp,
            dashboard_api_bp,
            api_bp
        ]
        
        for bp in blueprints:
            app.register_blueprint(bp)

def register_commands_and_shell(app: Flask) -> None:
    """Registra comandos CLI e o contexto do `flask shell`."""
    # from . import commands
    # commands.register(app)
    
    @app.shell_context_processor
    def make_shell_context():
        """Pré-importa pacotes para facilitar o debug via `flask shell`."""
        from .models import AppUser, AnalyticsEvent
        return {'db': db, 'AppUser': AppUser, 'AnalyticsEvent': AnalyticsEvent}

def configure_logging(app: Flask) -> None:
    """Configura o sistema de logging para o ambiente de produção."""
    if not app.debug and not app.testing:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('SynapCortex inicializado.')