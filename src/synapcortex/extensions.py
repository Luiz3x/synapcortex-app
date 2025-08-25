# =================================================================================
# src.SYNAPCORTEX - EXTENSIONS (v2.1 - Final com SocketIO)
# Centraliza a inicialização de todas as extensões Flask para evitar
# importações circulares e manter o código organizado.
# =================================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO  # <--- CORREÇÃO: Importação adicionada

# Cria instâncias vazias das extensões.
# Elas serão conectadas à nossa aplicação Flask depois, usando o padrão "Application Factory".
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
socketio = SocketIO()  # <--- CORREÇÃO: Instância do SocketIO adicionada