# src/synapcortex/extensions.py
import os
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from celery import Celery

# Cria instâncias vazias das extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
socketio = SocketIO()

# --- Conexão Central com o Celery (Tarefas Assíncronas) ---
celery_app = Celery(__name__, broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'))

# --- CONEXÃO FINAL: Conexão Central com o Cache (Redis) ---
redis_url = os.getenv('REDIS_URL')
if not redis_url:
    print("AVISO CRÍTICO: A variável de ambiente REDIS_URL não foi definida. O cache não funcionará.")
    redis_cache = None
else:
    redis_cache = redis.from_url(redis_url)

# Criamos um apelido 'cache' para garantir compatibilidade com todos os serviços
cache = redis_cache