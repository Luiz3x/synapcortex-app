# synapcortex/__init__.py (v6.2 - Com Flask-Login Integrado)
# =================================================================================
# SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO
# Versão final com Application Factory e sistema de login configurado.
# =================================================================================

import os
import logging
from flask import Flask, Blueprint

# 1. Importações do projeto (Configuração e Extensões)
from .config import config_by_name
# A importação agora inclui o novo login_manager
from .extensions import db, bcrypt, cors, migrate, login_manager
# Importa o modelo de usuário para o user_loader
from .models import AppUser

def create_app(config_name: str = None) -> Flask:
    """
    Ponto de entrada principal (Application Factory).
    Cria, configura e retorna a instância da aplicação Flask.
    """
    app = Flask(__name__)
    
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config_by_name[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands_and_shell(app)
    configure_logging(app)

    return app

def register_extensions(app: Flask) -> None:
    """Conecta as extensões Flask e configura o LoginManager."""
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)
    
    # --- LIGA E CONFIGURA O SISTEMA DE LOGIN ---
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        # Esta função diz ao Flask-Login como encontrar um usuário a partir do ID na sessão
        return AppUser.query.get(int(user_id))
    
    # Se um usuário não logado tentar acessar uma página protegida, ele será
    # redirecionado para a rota 'auth.index' (sua página de login).
    login_manager.login_view = 'auth.index'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'


def register_blueprints(app: Flask) -> None:
    """Detecta e registra todas as "alas" (Blueprints) da aplicação."""
    with app.app_context():
        from .blueprints import auth, dashboard, routes_api
        
        blueprints: list[Blueprint] = [
            auth.auth_bp,
            dashboard.dashboard_bp,
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