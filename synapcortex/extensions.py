# synapcortex/extensions.py
# =================================================================================
# EXTENSÕES - MÓDULO PURO E CENTRALIZADO
# Este arquivo apenas instancia as extensões.
# =================================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager # Adicionado

# Instancia os objetos aqui, sem nenhuma configuração.
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
login_manager = LoginManager() # Adicionado