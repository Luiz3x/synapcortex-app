# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION (v15.1 - BILHETERIA (STRIPE) REFINADA)
# =================================================================================
import os
import json
import secrets
import stripe
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

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'synapcortex_local.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---
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
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True) # APRIMORAMENTO: Ponte para o Stripe
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

# --- COMANDOS DE INICIALIZAÇÃO ---
@app.cli.command("init-db")
def init_db_command():
    """Cria/Atualiza as tabelas e o usuário demo."""
    db.create_all()
    demo_user = AppUser.query.filter_by(email='demo@synapcortex.com').first()
    if not demo_user:
        demo_user = AppUser(
            country='Brasil', company_id='00000000000000', email='demo@synapcortex.com',
            senha_hash=generate_password_hash('demo_password'), nome_empresa='Loja de Demonstração',
            api_key=secrets.token_hex(16), status_assinatura='demo'
        )
        db.session.add(demo_user); db.session.commit()
        print("Usuário de demonstração criado.")
    print("Banco de dados inicializado.")

# --- DECORADOR "PORTEIRO" ---
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error'); return redirect(url_for('index'))
        user = AppUser.query.filter_by(email=session['email']).first()
        if not user or user.status_assinatura == 'canceled':
            session.clear(); flash('Usuário não encontrado ou conta encerrada.', 'error'); return redirect(url_for('index'))
        if user.status_assinatura in ['active', 'demo']:
            return f(user=user, *args, **kwargs)
        if user.status_assinatura == 'trial':
            if user.trial_end_date and datetime.utcnow() < user.trial_end_date:
                return f(user=user, *args, **kwargs)
            else:
                user.status_assinatura = 'expired_trial'
                db.session.commit()
                flash('Seu período de teste acabou. Por favor, realize sua assinatura.', 'info'); return redirect(url_for('pagamento'))
        flash('Sua assinatura não está ativa. Por favor, regularize para ter acesso.', 'info'); return redirect(url_for('pagamento'))
    return decorated_function

# --- ROTAS PRINCIPAIS E DE AUTENTICAÇÃO ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email_form = request.form.get('email'); password_form = request.form.get('password')
    user = AppUser.query.filter_by(email=email_form).first()
    if user and user.status_assinatura != 'canceled' and check_password_hash(user.senha_hash, password_form):
        session['logged_in'] = True; session['email'] = user.email
        return redirect(url_for('dashboard'))
    flash('E-mail ou senha inválidos, ou conta encerrada.', 'error'); return redirect(url_for('index'))

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        email = request.form.get('email'); country = request.form.get('country'); company_id = request.form.get('company_id')
        nome_empresa = request.form.get('nome_empresa'); password = request.form.get('password')
        campos_obrigatorios = {'País': country, 'ID da Empresa (CNPJ)': company_id, 'Nome da Empresa': nome_empresa, 'E-mail Comercial': email, 'Senha': password}
        for nome_campo, valor in campos_obrigatorios.items():
            if not valor:
                flash(f'O campo "{nome_campo}" é obrigatório.', 'error'); return redirect(url_for('index'))
        user_existente = AppUser.query.filter_by(country=country, company_id=company_id).first()
        if user_existente:
            if user_existente.status_assinatura in ['canceled', 'expired_trial']:
                user_existente.nome_empresa = nome_empresa; user_existente.email = email; user_existente.senha_hash = generate_password_hash(password)
                user_existente.status_assinatura = 'trial'; user_existente.trial_end_date = datetime.utcnow() + timedelta(days=7)
                db.session.commit()
                session['logged_in'] = True; session['email'] = user_existente.email
                flash('Que bom te ver de volta! Reativamos sua conta com mais 7 dias de teste.', 'success'); return redirect(url_for('dashboard'))
            else:
                flash('Uma conta com este ID de empresa já existe para o país selecionado.', 'error'); return redirect(url_for('index'))
        senha_hash = generate_password_hash(password)
        data_final_teste = datetime.utcnow() + timedelta(days=30)
        new_user = AppUser(country=country, company_id=company_id, email=email, senha_hash=senha_hash, nome_empresa=nome_empresa, api_key=secrets.token_hex(16), trial_end_date=data_final_teste)
        db.session.add(new_user); db.session.commit()
        session['logged_in'] = True; session['email'] = new_user.email
        flash('Conta criada com sucesso! Você tem 30 dias de teste grátis.', 'success'); return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback(); flash(f'Ocorreu um erro ao registrar: {e}', 'error'); return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('index'))

@app.route('/demo-login')
def demo_login():
    session['logged_in'] = True; session['email'] = 'demo@synapcortex.com'; return redirect(url_for('dashboard'))

# --- ROTAS DO PAINEL (PROTEGIDAS) ---
@app.route('/dashboard')
@subscription_required
def dashboard(user):
    # ... (lógica completa do dashboard) ...

@app.route('/dashboard/visitors')
@subscription_required
def visitors(user):
    # ... (lógica completa de visitors) ...

# --- ROTAS DE PAGAMENTO (FASE 3 - BILHETERIA) ---
@app.route('/pagamento')
def pagamento():
    stripe_public_key = os.environ.get('STRIPE_PUBLIC_KEY')
    return render_template('pagamento_pendente.html', stripe_public_key=stripe_public_key)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    if 'logged_in' not in session:
        return jsonify(error={'message': 'Autenticação necessária.'}), 403
    try:
        intent = stripe.PaymentIntent.create(
            amount=4990, currency='brl',
            automatic_payment_methods={'enabled': True}
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify(error={'message': str(e)}), 500

# --- ROTAS DE GERENCIAMENTO (PROTEGIDAS) ---
@app.route('/salvar-configuracoes', methods=['POST'])
@subscription_required
def salvar_configuracoes(user):
    # ... (lógica completa de salvar) ...

@app.route('/encerrar-conta', methods=['POST'])
@subscription_required
def encerrar_conta(user):
    # ... (lógica completa de encerrar) ...

@app.route('/mudar-email', methods=['POST'])
@subscription_required
def mudar_email(user):
    # ... (lógica completa de mudar email) ...

# --- ROTAS DA API (PARA O spy.js) ---
@app.route('/api/track', methods=['POST'])
def track_event():
    # ... (lógica completa de track) ...

@app.route('/api/get-client-config')
def get_client_config():
    # ... (lógica completa de get-client-config) ...

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)