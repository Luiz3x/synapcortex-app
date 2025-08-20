# synapcortex/extensions.py
# =================================================================================
# EXTENSÕES - MÓDULO PURO (v2.0)
# Este arquivo apenas instancia as extensões. Não importa nada do resto da app.
# Isso é crucial para evitar erros de importação circular.
# =================================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate

# Instancia os objetos aqui, sem nenhuma configuração.
# A configuração será feita depois, dentro da factory 'create_app'.
db: SQLAlchemy = SQLAlchemy()
bcrypt: Bcrypt = Bcrypt()
cors: CORS = CORS()
migrate: Migrate = Migrate()