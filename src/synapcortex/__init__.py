# =================================================================================
# src.SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO (v8.2 - Deploy Estável)
# Versão focada nos blueprints essenciais para o deploy inicial.
# =================================================================================

import os
import logging
from flask import Flask

# 1. Importações centrais da nossa arquitetura
from .config import config_by_name
from .extensions import db, bcrypt, cors, migrate, login_manager, csrf, socketio
from .models import AppUser

def create_app(config_name: str = None) -> Flask:
    """
    Ponto de entrada principal (Application Factory).
    Cria, configura e retorna a instância da aplicação Flask.
    """
    app = Flask(__name__.split('.')[0], instance_relative_config=True)
    
    # Carrega a configuração a partir do ambiente
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
    socketio.init_app(app)

    # --- Configuração do Sistema de Login ---
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))
    
    login_manager.login_view = 'auth.index'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

# --- FUNÇÃO CORRIGIDA PARA O DEPLOY ---
def register_blueprints(app: Flask) -> None:
    """Registra apenas os blueprints essenciais para o primeiro deploy."""
    with app.app_context():
        from .blueprints.auth import auth_bp
        from .blueprints.dashboard import dashboard_bp
        # from .blueprints.api import api_bp          # Desativado para o deploy inicial
        # from .blueprints.payments import payments_bp # Desativado para o deploy inicial
        from .blueprints.dashboard.routes import dashboard_api_bp
        
        # Lista apenas com os blueprints ativos
        blueprints = [
            auth_bp,
            dashboard_bp,
            dashboard_api_bp,
            # api_bp,      # Desativado
            # payments_bp, # Desativado
        ]
        
        for bp in blueprints:
            app.register_blueprint(bp)

def register_commands_and_shell(app: Flask) -> None:
    """Registra comandos CLI e o contexto do `flask shell`."""
    # A importação deve ser local para evitar importação circular
    from .commands import admin_cli 
    app.cli.add_command(admin_cli)
    
    @app.shell_context_processor
    def make_shell_context():
        """Pré-importa pacotes para facilitar o debug via `flask shell`."""
        from .models import AppUser, AnalyticsEvent, PaymentEvent
        return {
            'db': db, 
            'AppUser': AppUser, 
            'AnalyticsEvent': AnalyticsEvent,
            'PaymentEvent': PaymentEvent
        }

def configure_logging(app: Flask) -> None:
    """Configura o sistema de logging da aplicação para ser visível nos logs da Render."""
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(log_format)
    
    app.logger.handlers.clear()
    
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info('Sistema de logging do SynapCortex configurado com sucesso.')