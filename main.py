# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 3.2 - Implementação do Dossiê de Visitantes
# =================================================================================
import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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
        # ... (código do usuário demo continua igual)
        pass


# --- ROTAS PRINCIPAIS E DE AUTENTICAÇÃO ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # ... (código de login continua igual)
    pass

@app.route('/registrar', methods=['POST'])
def registrar():
    # ... (código de registrar continua igual)
    pass

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- ROTAS DO PAINEL DE CONTROLE ---
@app.route('/dashboard')
def dashboard():
    # ... (o código da rota dashboard principal continua igual, com a lógica do insight)
    pass

@app.route('/dashboard/visitors')
def visitors():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    
    user = AppUser.query.filter_by(email=session['email']).first()
    if not user:
        return redirect(url_for('index'))

    events = AnalyticsEvent.query.filter_by(owner_id=user.id, event_name='pagina_visitada').order_by(AnalyticsEvent.timestamp.desc()).all()

    visitors_data = defaultdict(list)
    for event in events:
        try:
            event_details = json.loads(event.event_data)
            event_details['timestamp'] = event.timestamp.strftime('%d/%m/%Y às %H:%M')
            visitors_data[event.visitor_id].append(event_details)
        except:
            continue
            
    return render_template('visitors.html', visitors_data=visitors_data, usuario=user)


# --- ROTAS DE API E CONFIGURAÇÃO ---
@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    # ... (código de salvar configurações continua igual)
    pass

@app.route('/api/track', methods=['POST'])
def track_event():
    # ... (código da API track continua igual)
    pass

@app.route('/api/get-client-config')
def get_client_config():
    # ... (código da API get-client-config continua igual)
    pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)