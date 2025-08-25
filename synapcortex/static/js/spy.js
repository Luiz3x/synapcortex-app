# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION (v14.5 - ARQUITETURA FINAL)
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
    # ... (Seu modelo global está perfeito) ...
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
    # ... (Seu modelo de evento está perfeito) ...
    __tablename__ = 'analytics_event'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    visitor_id = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- FUNÇÃO PARA CRIAR USUÁRIO DEMO (SUA LÓGICA BRILHANTE) ---
@app.before_first_request
def create_demo_user():
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

# --- DECORADOR DE VERIFICAÇÃO DE ASSINATURA (O "PORTEIRO") ---
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ... (Sua lógica perfeita do Porteiro) ...
        return f(user=user, *args, **kwargs) # Simplifiquei para brevidade, a sua está ótima
    return decorated_function

# --- ROTAS DE AUTENTICAÇÃO E PÁGINAS ---
# ... (Suas rotas de index, login, registrar, logout e demo_login estão ótimas) ...

# --- ROTAS DO PAINEL (PROTEGIDAS PELO "PORTEIRO") ---
@app.route('/dashboard')
@subscription_required
def dashboard(user):
    # ... (Sua lógica do dashboard está ótima) ...

@app.route('/dashboard/visitors')
@subscription_required
def visitors(user):
    # ... (Sua lógica de visitors está ótima) ...

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento_pendente.html')

@app.route('/salvar-configuracoes', methods=['POST'])
@subscription_required
def salvar_configuracoes(user):
    # ... (Sua lógica de salvar está ótima) ...

# --- ROTAS DE GERENCIAMENTO DE CONTA ---
@app.route('/encerrar-conta', methods=['POST'])
@subscription_required
def encerrar_conta(user):
    # ... (Sua lógica de encerrar conta está ótima) ...

@app.route('/mudar-email', methods=['POST'])
@subscription_required
def mudar_email(user):
    # ... (Sua lógica de mudar e-mail está ótima) ...

# --- ROTAS DA API ---
@app.route('/api/track', methods=['POST'])
def track_event():
    # ... (Sua lógica de track está ótima) ...

# =========================================================
# ROTA DA API APRIMORADA
# =========================================================
@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({'error': 'API Key não fornecida'}), 400
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'API Key inválida'}), 404
    
    try:
        config_geral = json.loads(user.configuracoes or '{}')
    except json.JSONDecodeError:
        config_geral = {}

    agora = datetime.utcnow()
    is_campaign_active = False
    if user.campaign_active and user.campaign_start_date and user.campaign_end_date:
        if user.campaign_start_date <= agora <= user.campaign_end_date:
            is_campaign_active = True
    
    # Adicionamos a flag de campanha ativa ao objeto principal
    config_geral['is_campaign_active'] = is_campaign_active

    # Se a campanha estiver ativa, adicionamos um objeto separado para as configs da campanha
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