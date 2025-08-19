# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION (v15.2 - ARQUITETURA OTIMIZADA)
# =================================================================================

# --- MÓDULOS NATIVOS E DE TERCEIROS ---
import os
import json
import secrets
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
import logging

# --- MÓDULOS DO FRAMEWORK E EXTENSÕES ---
import stripe
from flask import (Flask, render_template, request, jsonify, redirect,
                   url_for, session, flash, g)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB # Mais eficiente para PostgreSQL
from flask_cors import CORS

# --- CONSTANTES GLOBAIS ---
TRIAL_DURATION_DAYS = 30
STRIPE_PRICE_IN_CENTS = 4990 # R$ 49,90

class SubscriptionStatus:
    """Centraliza os status de assinatura para evitar erros de digitação."""
    ACTIVE = 'active'
    TRIAL = 'trial'
    EXPIRED_TRIAL = 'expired_trial'
    CANCELED = 'canceled'
    DEMO = 'demo'
    VALID_STATUSES = {ACTIVE, TRIAL, DEMO}

# --- INICIALIZAÇÃO E CONFIGURAÇÃO DA APLICAÇÃO ---
app = Flask(__name__)

# Configuração de logging para facilitar o debug em produção
logging.basicConfig(level=logging.INFO)

# Configuração de Chaves e Segredos
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(24)) # Aumentado para 24 bytes
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')

# Configuração do Banco de Dados (com otimizações)
db_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'synapcortex_local.db')}")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config.update(
    SQLALCHEMY_DATABASE_URI=db_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'sslmode': 'require'}} if 'postgresql' in db_url else {}
)

db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# --- MODELOS DO BANCO DE DADOS (COM MELHORIAS) ---
class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(80), nullable=False)
    company_id = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True) # Adicionado unique e index
    senha_hash = db.Column(db.String(256), nullable=False)
    nome_empresa = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=False, index=True) # Adicionado index
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_assinatura = db.Column(db.String(20), nullable=False, default=SubscriptionStatus.TRIAL)
    trial_end_date = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True)
    
    # Usando JSON/JSONB para melhor performance e manipulação de dados estruturados
    db_json_type = JSONB if 'postgresql' in db_url else db.JSON
    configuracoes = db.Column(db_json_type, nullable=False, default=lambda: {})
    campaign_config = db.Column(db_json_type, nullable=True, default=lambda: {})
    
    campaign_active = db.Column(db.Boolean, nullable=False, default=False)
    campaign_start_date = db.Column(db.DateTime, nullable=True)
    campaign_end_date = db.Column(db.DateTime, nullable=True)
    
    events = db.relationship('AnalyticsEvent', backref='owner', lazy='dynamic') # lazy='dynamic' para queries
    __table_args__ = (UniqueConstraint('company_id', 'country', name='_company_id_country_uc'),)
    
    @property
    def is_trial_active(self):
        """Verifica se o período de teste do usuário ainda está ativo."""
        return self.status_assinatura == SubscriptionStatus.TRIAL and \
               self.trial_end_date and datetime.utcnow() < self.trial_end_date

    @property
    def is_subscription_valid(self):
        """Centraliza a lógica de validação de acesso."""
        return self.status_assinatura in SubscriptionStatus.VALID_STATUSES or self.is_trial_active

class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_event'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False, index=True) # Adicionado index
    visitor_id = db.Column(db.String(100), nullable=False, index=True) # Adicionado index
    event_name = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.JSON, nullable=True) # JSON é mais apropriado
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True) # Adicionado index

# --- FUNÇÕES HELPER E DECORATORS ---

def get_current_user():
    """Busca o usuário logado e armazena no contexto da requisição para evitar queries repetidas."""
    if 'user' not in g and 'email' in session:
        g.user = AppUser.query.filter_by(email=session['email']).first()
    return g.get('user')

def subscription_required(f):
    """Decorator "Porteiro" refatorado para maior clareza e eficiência."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('index'))

        user = get_current_user()

        if not user or user.status_assinatura == SubscriptionStatus.CANCELED:
            session.clear()
            flash('Usuário não encontrado ou conta encerrada.', 'error')
            return redirect(url_for('index'))

        if user.is_subscription_valid:
            return f(user=user, *args, **kwargs)

        if user.status_assinatura == SubscriptionStatus.TRIAL and not user.is_trial_active:
            user.status_assinatura = SubscriptionStatus.EXPIRED_TRIAL
            db.session.commit()
            flash('Seu período de teste acabou. Por favor, realize sua assinatura.', 'info')
            return redirect(url_for('pagamento'))

        flash('Sua assinatura não está ativa. Por favor, regularize para ter acesso.', 'info')
        return redirect(url_for('pagamento'))
    return decorated_function

# --- ROTAS PRINCIPAIS E DE AUTENTICAÇÃO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('E-mail e senha são obrigatórios.', 'error')
        return redirect(url_for('index'))

    user = AppUser.query.filter_by(email=email).first()

    if user and user.status_assinatura != SubscriptionStatus.CANCELED and check_password_hash(user.senha_hash, password):
        session.permanent = True  # Torna a sessão mais duradoura
        session['logged_in'] = True
        session['email'] = user.email
        app.logger.info(f"Login bem-sucedido para o usuário {email}")
        return redirect(url_for('dashboard'))
    
    flash('E-mail ou senha inválidos, ou conta encerrada.', 'error')
    return redirect(url_for('index'))

@app.route('/registrar', methods=['POST'])
def registrar():
    form_data = request.form
    required_fields = {
        'País': 'country', 'ID da Empresa (CNPJ)': 'company_id',
        'Nome da Empresa': 'nome_empresa', 'E-mail Comercial': 'email', 'Senha': 'password'
    }

    # Validação de campos
    for field_name, key in required_fields.items():
        if not form_data.get(key):
            flash(f'O campo "{field_name}" é obrigatório.', 'error')
            return redirect(url_for('index'))

    try:
        user = AppUser.query.filter_by(country=form_data['country'], company_id=form_data['company_id']).first()

        if user:
            # Reativação de conta
            if user.status_assinatura in [SubscriptionStatus.CANCELED, SubscriptionStatus.EXPIRED_TRIAL]:
                user.nome_empresa = form_data['nome_empresa']
                user.email = form_data['email']
                user.senha_hash = generate_password_hash(form_data['password'])
                user.status_assinatura = SubscriptionStatus.TRIAL
                user.trial_end_date = datetime.utcnow() + timedelta(days=7) # Reativação com 7 dias
                message = 'Que bom te ver de volta! Reativamos sua conta com mais 7 dias de teste.'
            else:
                flash('Uma conta com este ID de empresa já existe para o país selecionado.', 'error')
                return redirect(url_for('index'))
        else:
            # Novo usuário
            new_user = AppUser(
                country=form_data['country'], company_id=form_data['company_id'], email=form_data['email'],
                senha_hash=generate_password_hash(form_data['password']), nome_empresa=form_data['nome_empresa'],
                api_key=secrets.token_hex(16),
                trial_end_date=datetime.utcnow() + timedelta(days=TRIAL_DURATION_DAYS)
            )
            db.session.add(new_user)
            user = new_user
            message = f'Conta criada com sucesso! Você tem {TRIAL_DURATION_DAYS} dias de teste grátis.'
            
        db.session.commit()
        session['logged_in'] = True
        session['email'] = user.email
        flash(message, 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro no registro de usuário: {e}")
        flash('Ocorreu um erro inesperado ao registrar. Tente novamente.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

@app.route('/demo-login')
def demo_login():
    session['logged_in'] = True
    session['email'] = 'demo@synapcortex.com'
    return redirect(url_for('dashboard'))

# --- ROTAS DO PAINEL (PROTEGIDAS) ---

@app.route('/dashboard')
@subscription_required
def dashboard(user):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Usando lazy='dynamic' no modelo para poder adicionar filtros
    popups_exibidos = user.events.filter(
        AnalyticsEvent.event_name == 'popup_exibido',
        AnalyticsEvent.timestamp >= thirty_days_ago
    ).count()

    top_pages_query = db.session.query(
        AnalyticsEvent.event_data, func.count(AnalyticsEvent.id).label('views')
    ).filter(
        AnalyticsEvent.owner_id == user.id,
        AnalyticsEvent.event_name == 'pagina_visitada',
        AnalyticsEvent.timestamp >= thirty_days_ago
    ).group_by(AnalyticsEvent.event_data).order_by(func.count(AnalyticsEvent.id).desc()).limit(5).all()

    top_pages = [{'title': (p.event_data.get('title') or p.event_data.get('url', 'N/A')), 'views': p.views} for p in top_pages_query]
    
    insight_detetive = f"Sua página mais popular é '{top_pages[0]['title']}'. Considere criar uma oferta!" if top_pages else "Ainda não há dados suficientes para insights."

    dias_restantes = None
    if user.is_trial_active:
        delta = user.trial_end_date - datetime.utcnow()
        dias_restantes = max(0, delta.days)

    return render_template('dashboard.html', usuario=user, popups_exibidos=popups_exibidos,
                           top_pages=top_pages, insight_detetive=insight_detetive,
                           dias_restantes=dias_restantes)

@app.route('/dashboard/visitors')
@subscription_required
def visitors(user):
    events = user.events.filter_by(event_name='pagina_visitada') \
                       .order_by(AnalyticsEvent.timestamp.desc()).limit(200).all()
    
    visitors_data = defaultdict(list)
    for event in events:
        event_details = event.event_data or {}
        event_details['timestamp'] = event.timestamp.strftime('%d/%m/%Y às %H:%M')
        visitors_data[event.visitor_id].append(event_details)

    return render_template('visitors.html', visitors_data=dict(visitors_data), usuario=user)

# --- ROTAS DE PAGAMENTO ---

@app.route('/pagamento')
def pagamento():
    if not STRIPE_PUBLIC_KEY:
        app.logger.error("STRIPE_PUBLIC_KEY não está configurada!")
        flash("A configuração de pagamento está indisponível no momento. Contate o suporte.", "error")
        return redirect(url_for('dashboard'))
    return render_template('pagamento_pendente.html', stripe_public_key=STRIPE_PUBLIC_KEY)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    if 'logged_in' not in session:
        return jsonify(error={'message': 'Autenticação necessária.'}), 403
    try:
        intent = stripe.PaymentIntent.create(
            amount=STRIPE_PRICE_IN_CENTS,
            currency='brl',
            automatic_payment_methods={'enabled': True}
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        app.logger.error(f"Erro ao criar PaymentIntent no Stripe: {e}")
        return jsonify(error={'message': "Não foi possível iniciar o pagamento."}), 500

# --- ROTAS DE GERENCIAMENTO (PROTEGIDAS) ---

@app.route('/salvar-configuracoes', methods=['POST'])
@subscription_required
def salvar_configuracoes(user):
    try:
        form = request.form
        
        # Agrupando campos para facilitar a manutenção
        general_checkboxes = ['ativar_abandono', 'ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        general_fields = ['popup_titulo', 'popup_mensagem', 'msg_bem_vindo', 'msg_interessado', 'abandono_tipo', 'abandono_presente_fechado', 'abandono_presente_aberto', 'abandono_timer_minutos']
        campaign_checkboxes = ['campaign_bar_active']
        campaign_fields = ['campaign_bar_text', 'campaign_bar_position', 'campaign_abandono_tipo', 'campaign_popup_titulo', 'campaign_popup_mensagem', 'campaign_presente_fechado', 'campaign_presente_aberto']

        # Atualiza dicionários de configuração de forma mais limpa
        config_geral = user.configuracoes or {}
        for key in general_checkboxes: config_geral[key] = key in form
        for key in general_fields: config_geral[key] = form.get(key)
        
        config_campanha = user.campaign_config or {}
        for key in campaign_checkboxes: config_campanha[key] = key in form
        for key in campaign_fields: config_campanha[key] = form.get(key)

        user.configuracoes = config_geral
        user.campaign_config = config_campanha

        # Atualiza status e datas da campanha
        user.campaign_active = 'campaign_active' in form
        
        def parse_datetime(date_str):
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if date_str else None
        
        user.campaign_start_date = parse_datetime(form.get('campaign_start_date'))
        user.campaign_end_date = parse_datetime(form.get('campaign_end_date'))
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Configurações salvas com sucesso!'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao salvar configurações para o usuário {user.email}: {e}")
        return jsonify({'status': 'error', 'message': 'Ocorreu um erro interno ao salvar.'}), 500

@app.route('/encerrar-conta', methods=['POST'])
@subscription_required
def encerrar_conta(user):
    try:
        user.status_assinatura = SubscriptionStatus.CANCELED
        db.session.commit()
        session.clear()
        flash('Sua conta foi encerrada. Agradecemos por testar a SynapCortex.', 'success')
        return jsonify({'status': 'success', 'redirect_url': url_for('index')})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao encerrar conta para o usuário {user.email}: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao encerrar a conta.'}), 500

# --- ROTAS DA API (PARA O spy.js) ---

@app.route('/api/track', methods=['POST'])
def track_event():
    data = request.get_json()
    api_key = data.get('apiKey')
    if not api_key:
        return jsonify({'error': 'API Key é obrigatória.'}), 400

    user = AppUser.query.filter_by(api_key=api_key).options(db.defer('configuracoes')).first() # Otimização
    if not user:
        return jsonify({'error': 'API Key inválida.'}), 403
    
    try:
        new_event = AnalyticsEvent(
            owner_id=user.id,
            visitor_id=data.get('visitorId'),
            event_name=data.get('eventName'),
            event_data=data.get('eventData', {})
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao salvar evento da API para a key {api_key[:5]}...: {e}")
        return jsonify({'error': 'Erro interno ao salvar evento.'}), 500

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({'error': 'API Key não fornecida'}), 400

    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user or not user.is_subscription_valid:
        return jsonify({'error': 'API Key inválida ou assinatura inativa'}), 404

    config_geral = user.configuracoes or {}
    agora = datetime.utcnow()
    is_campaign_active = user.campaign_active and user.campaign_start_date and \
                         user.campaign_end_date and user.campaign_start_date <= agora <= user.campaign_end_date

    config_geral['is_campaign_active'] = is_campaign_active
    if is_campaign_active:
        config_geral['campaign_config'] = user.campaign_config or {}
        config_geral['campaign_end_date'] = user.campaign_end_date.isoformat()
        
    return jsonify(config_geral)

# --- COMANDOS CLI E INICIALIZAÇÃO DO SERVIDOR ---

@app.cli.command("init-db")
def init_db_command():
    """Cria/Atualiza as tabelas e o usuário demo."""
    db.create_all()
    if not AppUser.query.filter_by(email='demo@synapcortex.com').first():
        demo_user = AppUser(
            country='Brasil', company_id='00000000000000',
            email='demo@synapcortex.com',
            senha_hash=generate_password_hash('demo_password'),
            nome_empresa='Loja de Demonstração',
            api_key=secrets.token_hex(16),
            status_assinatura=SubscriptionStatus.DEMO
        )
        db.session.add(demo_user)
        db.session.commit()
        print("Usuário de demonstração criado.")
    print("Banco de dados inicializado.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)