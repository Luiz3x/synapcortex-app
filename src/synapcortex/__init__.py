# =================================================================================
# src.SYNAPCORTEX - O CORAÇÃO DA APLICAÇÃO (v8.0 - Arquitetura Final)
# Versão final com Application Factory, login, CSRF, Sockets e blueprints corrigidos.
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
    socketio.init_app(app)

    # --- Configuração do Sistema de Login ---
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))
    
    login_manager.login_view = 'auth.index'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

# --- FUNÇÃO CORRIGIDA ---
def register_blueprints(app: Flask) -> None:
    """Registra todos os Blueprints da aplicação de forma moderna e correta."""
    with app.app_context():
        # --- MODO CORRETO DE IMPORTAR BLUEPRINTS ---
        # Nós importamos do "pacote" do blueprint (graças aos __init__.py que corrigimos)
        # em vez de ir diretamente no arquivo de rotas.
        from .blueprints.auth import auth_bp
        from .blueprints.dashboard import dashboard_bp
        from .blueprints.api import api_bp
        from .blueprints.payments import payments_bp
        
        # O dashboard tem um segundo blueprint para a API interna, que não está no __init__.py
        # então a importação dele continua específica
        from .blueprints.dashboard.routes import dashboard_api_bp
        
        # Lista de todos os blueprints a serem registrados
        blueprints = [
            auth_bp,
            dashboard_bp,
            dashboard_api_bp,
            api_bp,
            payments_bp
        ]
        
        for bp in blueprints:
            app.register_blueprint(bp)

def register_commands_and_shell(app: Flask) -> None:
    """Registra comandos CLI e o contexto do `flask shell`."""
    from .commands import admin_cli # Supondo que seus comandos estão em commands.py
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
    