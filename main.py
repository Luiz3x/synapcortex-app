# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 3.5 - Correção de Conexão SSL para Neon DB
# =================================================================================
import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct
from flask_cors import CORS
from collections import defaultdict

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- CONFIGURAÇÃO DO BANCO DE DADOS (RENDER) ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# --- CORREÇÃO PARA COMPATIBILIDADE COM NEON ---
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}
# --- FIM DA CORREÇÃO ---
db = SQLAlchemy(app)


# --- MODELOS DO BANCO DE DADOS ---
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
    campaign_active = db.Column(db.Boolean, nullable=False, default=False)
    campaign_start_date = db.Column(db.DateTime, nullable=True)
    campaign_end_date = db.Column(db.DateTime, nullable=True)
    campaign_config = db.Column(db.Text, nullable=True, default='{}')
    events = db.relationship('AnalyticsEvent', backref='owner', lazy=True)

class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_event'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    visitor_id = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# --- INICIALIZAÇÃO DO BANCO DE DADOS E USUÁRIO DEMO ---
with app.app_context():
    db.create_all()
    if not AppUser.query.filter_by(email='demo@synapcortex.com').first():
        demo_user = AppUser(email='demo@synapcortex.com', senha_hash=generate_password_hash('demo'), nome_empresa='Loja de Demonstração', cnpj='00000000000000', api_key='chave_api_demo_123456', configuracoes=json.dumps({'ativar_abandono': True, 'popup_titulo': 'Bem-vindo!', 'popup_mensagem': 'Explore nosso painel.'}))
        db.session.add(demo_user)
        db.session.commit()


# --- ROTAS ---
# (Todas as rotas continuam exatamente as mesmas da versão anterior)
@app.route('/')
def index():
    return render_template('index.html')

# ... (todas as outras rotas) ...

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user: return jsonify({'error': 'API Key inválida'}), 404
    
    config = json.loads(user.configuracoes)
    agora = datetime.utcnow()
    is_campaign_active = False
    if user.campaign_active and user.campaign_start_date and user.campaign_end_date:
        if user.campaign_start_date <= agora <= user.campaign_end_date: is_campaign_active = True
    
    config['is_campaign_active'] = is_campaign_active
    if is_campaign_active:
        config['campaign_config'] = json.loads(user.campaign_config or '{}')
        config['campaign_end_date'] = user.campaign_end_date.isoformat()
        
    return jsonify(config)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)