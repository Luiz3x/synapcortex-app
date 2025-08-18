# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION (v14.5 - ARQUITETURA FINAL REFINADA)
# =================================================================================
import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, UniqueConstraint
from flask_cors import CORS
from collections import defaultdict
from functools import wraps

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
CORS(app, resources={r"/api/*": {"origins": "*"}})

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'synapcortex_local.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS (ARQUITETURA GLOBAL) ---
class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(80), nullable=False)
    company_id = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    nome_empresa = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_assinatura = db.Column(db.String(20), nullable=False, default='trial')
    trial_end_date = db.Column(db.DateTime, nullable=True)
    configuracoes = db.Column(db.Text, nullable=False, default='{}')
    campaign_active = db.Column(db.Boolean, nullable=False, default=False)
    campaign_start_date = db.Column(db.DateTime, nullable=True)
    campaign_end_date = db.Column(db.DateTime, nullable=True)
    campaign_config = db.Column(db.Text, nullable=True, default='{}')
    events = db.relationship('AnalyticsEvent', backref='owner', lazy=True)
    __table_args__ = (UniqueConstraint('company_id', 'country', name='_company_id_country_uc'),)

class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_event'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    visitor_id = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# APRIMORAMENTO 1: Comando para inicializar o DB e criar o usuário demo
@app.cli.command("init-db")
def init_db_command():
    """Cria as tabelas do banco e o usuário de demonstração."""
    db.create_all()
    demo_user = AppUser.query.filter_by(email='demo@synapcortex.com').first()
    if not demo_user:
        demo_user = AppUser(
            country='Brasil',
            company_id='00000000000000',
            email='demo@synapcortex.com',
            senha_hash=generate_password_hash('demo_password'),
            nome_empresa='Loja de Demonstração',
            api_key=secrets.token_hex(16),
            status_assinatura='demo'
        )
        db.session.add(demo_user)
        db.session.commit()
        print("Usuário de demonstração criado.")
    print("Banco de dados inicializado.")

# --- DECORADOR DE VERIFICAÇÃO DE ASSINATURA (O "PORTEIRO") ---
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('index'))
        user = AppUser.query.filter_by(email=session['email']).first()
        if not user or user.status_assinatura == 'canceled':
            session.clear(); flash('Usuário não encontrado ou conta encerrada.', 'error'); return redirect(url_for('index'))
        
        if user.status_assinatura in ['active', 'demo']: # Adicionado 'demo' aqui
            return f(user=user, *args, **kwargs)

        if user.status_assinatura == 'trial':
            if user.trial_end_date and datetime.utcnow() < user.trial_end_date:
                return f(user=user, *args, **kwargs)
            else:
                user.status_assinatura = 'expired_trial'
                db.session.commit()
                flash('Seu período de teste acabou. Por favor, realize sua assinatura.', 'info')
                return redirect(url_for('pagamento'))
        
        flash('Sua assinatura não está ativa. Por favor, regularize para ter acesso.', 'info')
        return redirect(url_for('pagamento'))
    return decorated_function

# --- ROTAS DE AUTENTICAÇÃO E PÁGINAS ---
@app.route('/')
def index():
    # ... (código inalterado) ...

@app.route('/login', methods=['POST'])
def login():
    # ... (código inalterado) ...

@app.route('/registrar', methods=['POST'])
def registrar():
    # ... (Sua excelente lógica de registro com validação continua aqui) ...

@app.route('/logout')
def logout():
    # ... (código inalterado) ...

@app.route('/demo-login')
def demo_login():
    # ... (código inalterado) ...

# --- ROTAS DO PAINEL E GERENCIAMENTO ---
@app.route('/dashboard')
@subscription_required
def dashboard(user):
    # ... (código inalterado) ...

@app.route('/dashboard/visitors')
@subscription_required
def visitors(user):
    # ... (código inalterado) ...

@app.route('/pagamento')
def pagamento():
    # ... (código inalterado) ...

@app.route('/salvar-configuracoes', methods=['POST'])
@subscription_required
def salvar_configuracoes(user):
    # ... (código inalterado) ...

@app.route('/encerrar-conta', methods=['POST'])
@subscription_required
def encerrar_conta(user):
    # ... (código inalterado) ...

@app.route('/mudar-email', methods=['POST'])
@subscription_required
def mudar_email(user):
    # ... (código inalterado) ...

# --- ROTAS DA API ---
@app.route('/api/track', methods=['POST'])
def track_event():
    # ... (código inalterado) ...

# APRIMORAMENTO 2: Resposta da API mais clara e organizada
@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key: return jsonify({'error': 'API Key não fornecida'}), 400
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user: return jsonify({'error': 'API Key inválida'}), 404
    
    try:
        config_geral = json.loads(user.configuracoes or '{}')
    except json.JSONDecodeError:
        config_geral = {}

    agora = datetime.utcnow()
    is_campaign_active = False
    if user.campaign_active and user.campaign_start_date and user.campaign_end_date:
        if user.campaign_start_date <= agora <= user.campaign_end_date:
            is_campaign_active = True
    
    config_geral['is_campaign_active'] = is_campaign_active

    if is_campaign_active:
        try:
            config_geral['campaign_config'] = json.loads(user.campaign_config or '{}')
            config_geral['campaign_end_date'] = user.campaign_end_date.isoformat()
        except json.JSONDecodeError:
            config_geral['campaign_config'] = {}
            
    return jsonify(config_geral)

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)