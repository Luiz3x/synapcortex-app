# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 2.2 - Com Fundação para o Módulo de Analytics
# =================================================================================

import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = secrets.token_hex(16)

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- MODELOS DO BANCO DE DADOS ---

# Modelo para Usuários do nosso aplicativo
class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    nome_empresa = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_assinatura = db.Column(db.String(20), nullable=False, default='trial')
    configuracoes = db.Column(db.Text, nullable=False, default='{}')
    # Relacionamento com os eventos de analytics
    events = db.relationship('AnalyticsEvent', backref='owner', lazy=True)

# [NOVO] Modelo para a "Sala de Evidências" de Analytics
class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_event'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    visitor_id = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(50), nullable=False) # ex: 'page_view', 'popup_shown'
    event_data = db.Column(db.Text, nullable=True) # JSON com detalhes do evento
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# --- LÓGICA DE INICIALIZAÇÃO DO APP ---
with app.app_context():
    db.create_all() # Cria TODAS as tabelas (AppUser e AnalyticsEvent) se não existirem
    # ... (lógica da conta demo continua a mesma)

# --- ROTAS DE PÁGINAS E AUTENTICAÇÃO ---
# ... (Todas as rotas como /, /login, /registrar, /dashboard, etc. continuam as mesmas)

# --- ROTAS DE API E AÇÕES ---

# [NOVO] O "Ponto de Encontro Secreto" para o Agente Synapse
@app.route('/api/track', methods=['POST'])
def track_event():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Requisição sem dados.'}), 400

    api_key = data.get('apiKey')
    visitor_id = data.get('visitorId')
    event_name = data.get('eventName')
    
    if not all([api_key, visitor_id, event_name]):
        return jsonify({'error': 'Dados incompletos.'}), 400

    # Encontra o dono da API Key
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'API Key inválida.'}), 403

    # Cria o novo evento e salva no banco de dados
    new_event = AnalyticsEvent(
        owner_id=user.id,
        visitor_id=visitor_id,
        event_name=event_name,
        event_data=json.dumps(data.get('eventData', {})) # Salva detalhes extras
    )
    db.session.add(new_event)
    db.session.commit()

    return jsonify({'status': 'ok'}), 200


# (As outras rotas de API como /get-client-config e a rota /salvar-configuracoes continuam as mesmas)

# ... (Resto do seu main.py igual à versão 2.1)
# ... (if __name__ == '__main__': etc.)