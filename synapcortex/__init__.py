# =================================================================================
# SYNAPCORTEX - O CORAÇÃO DA MANSÃO (v2.0)
# Arquitetura revisada para maior modularidade, testabilidade e robustez.
# =================================================================================

import os
from flask import Flask, jsonify

# Importa as nossas peças pré-construídas
from .config import config_by_name
from .extensions import db, bcrypt, cors, migrate

# Importa os registros das nossas "alas" (Blueprints)
# from .blueprints.auth import auth_bp
# from .blueprints.api import api_bp
# ... (outros blueprints)

def create_app(config_name: str = None) -> Flask:
    """
    Cria, configura e retorna uma instância otimizada da aplicação Flask.
    Este é o coração da nossa arquitetura, seguindo o padrão Application Factory.

    Args:
        config_name (str, optional): O nome da configuração a ser usada
                                     ('development', 'testing', 'production').
                                     Se não for fornecido, usa a variável de
                                     ambiente FLASK_CONFIG ou 'development'.

    Returns:
        Flask: A instância configurada da aplicação, pronta para operar.
    """
    # --- Passo 1: A Fundação da Sala de Máquinas ---
    app = Flask(__name__)

    # --- Passo 2: Ligar o Quadro de Força Inteligente ---
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config_by_name[config_name])

    # --- Passo 3: Conectar as Ferramentas de Forma Organizada ---
    register_extensions(app)

    # --- Passo 4: Abrir as Portas das Alas (Blueprints) ---
    register_blueprints(app)

    # --- Passo 5: Definir os Comandos Especiais ---
    # Registro dos nossos comandos de terminal (ex: flask init-db).

    from . import commands
    commands.register(app)

    # --- Passo 6: Adicionar um "Sensor de Vitalidade" ---
    # Uma rota simples para verificar se o coração da mansão está batendo.
    @app.route("/health")
    def health_check():
        return jsonify(status="UP"), 200

    # --- Passo 7: Entregar a Chave Mestra ---
    return app

def register_extensions(app: Flask):
    """Conecta as extensões Flask à aplicação."""
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    # Futuramente, o logger da aplicação seria configurado aqui.

def register_blueprints(app: Flask):
    """Registra os blueprints (as alas da mansão) na aplicação."""
    # Exemplo de como registrar uma ala:
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(api_bp, url_prefix='/api/v1')
    pass

def register_shell_context(app: Flask):
    """
    Registra um contexto de shell para facilitar o desenvolvimento e debugging.
    Permite acesso direto ao 'db' e aos modelos no `flask shell`.
    """
    @app.shell_context_processor
    def make_shell_context():
        # Importe seus modelos aqui para que fiquem disponíveis no shell
        # from .models.user import User
        return {'db': db} #, 'User': User}

def register_commands(app: Flask):
    """Registra comandos de CLI personalizados para a aplicação."""
    # from . import commands
    # commands.register(app)
    pass