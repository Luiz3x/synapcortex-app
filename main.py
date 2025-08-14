# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 4.3 - CORREÇÃO FINAL DA ROTA DE REGISTRO
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
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}
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
    trial_end_date = db.Column(db.DateTime, nullable=True)
    campaign_active = db.Column(db.Boolean, nullable=False, default=False)
    campaign_start_date = db.Column(db.DateTime, nullable=True)
    campaign_end_date = db.Column(db.DateTime, nullable=True)
    campaign_config = db.Column(db.Text, nullable=True, default='{}')
    events = db.relationship('AnalyticsEvent', backref='owner', lazy=True)

class AnalyticsEvent(db.Model):
    # ... (modelo AnalyticsEvent continua o mesmo)
    pass

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
with app.app_context():
    db.create_all()

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Lógica para o botão Test Drive
    if request.form.get('email') == 'demo@synapcortex.com':
        # Simula um usuário demo estático para evitar falhas de banco
        user_demo = {'nome_empresa': 'Loja de Demonstração'}
        config_demo = {'ativar_abandono': True, 'popup_titulo': 'Bem-vindo!', 'popup_mensagem': 'Explore o painel.'}
        return render_template('dashboard.html', usuario=user_demo, config=config_demo, popups_exibidos=0, top_pages=[], insight_detetive=None)

    user = AppUser.query.filter_by(email=request.form.get('email')).first()
    if user and check_password_hash(user.senha_hash, request.form.get('password')):
        session['logged_in'] = True
        session['email'] = user.email
        return redirect(url_for('dashboard'))
    flash('E-mail ou senha inválidos.', 'error')
    return redirect(url_for('index'))

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        email = request.form.get('email')
        if AppUser.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado.', 'error')
            return redirect(url_for('index'))
        
        senha_hash = generate_password_hash(request.form.get('password'))
        data_final_teste = datetime.utcnow() + timedelta(days=30)
        
        new_user = AppUser(
            email=email,
            senha_hash=senha_hash,
            nome_empresa=request.form.get('nome_empresa'),
            cnpj=request.form.get('cnpj'),
            api_key=secrets.token_hex(16),
            trial_end_date=data_final_teste
        )
        db.session.add(new_user)
        db.session.commit()
        
        session['logged_in'] = True
        session['email'] = new_user.email
        flash('Conta criada com sucesso! Você tem 30 dias de teste grátis.', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        # Em caso de qualquer erro, não quebra a aplicação, apenas avisa.
        flash(f'Ocorreu um erro ao registrar: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ROTAS DO PAINEL ---
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('index'))
    user = AppUser.query.filter_by(email=session['email']).first()
    if not user: 
        flash('Usuário não encontrado. Por favor, faça o login novamente.', 'error')
        return redirect(url_for('index'))
    # ... (o resto da lógica do dashboard continua aqui)
    return render_template('dashboard.html', usuario=user, config=json.loads(user.configuracoes or '{}'), popups_exibidos=0, top_pages=[], insight_detetive=None)

# ... (outras rotas e o final do arquivo continuam os mesmos) ...