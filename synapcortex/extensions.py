# =================================================================================
# SYNAPCORTEX - EXTENSÕES - MÓDULO PURO E CENTRALIZADO
# Este arquivo apenas instancia as extensões para serem usadas em toda a aplicação.
# =================================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

# Instancia os objetos aqui, sem nenhuma configuração.
# A configuração será feita na nossa Application Factory (__init__.py).
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
socketio = SocketIO()