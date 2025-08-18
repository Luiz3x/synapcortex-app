# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION (v14.3 - CORREÇÃO DE REGISTRO E TEST DRIVE)
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

with app.app_context():
    db.create_all()

# --- FUNÇÃO PARA CRIAR USUÁRIO DEMO (AUTO-CORREÇÃO) ---
@app.before_request
def create_demo_user():
    if not hasattr(app, 'demo_user_created'):
        with app.app_context():
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
            app.demo_user_created = True

# --- DECORADOR DE VERIFICAÇÃO DE ASSINATURA (O "PORTEIRO") ---
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('index'))
        user = AppUser.query.filter_by(email=session['email']).first()
        if not user or user.status_assinatura == 'canceled':
            session.clear()
            flash('Usuário não encontrado ou conta encerrada.', 'error')
            return redirect(url_for('index'))
        if user.status_assinatura in ['active', 'demo']:
            return f(user=user, *args, **kwargs)
        if user.status_assinatura == 'trial':
            if user.trial_end_date and datetime.utcnow() < user.trial_end_date:
                return f(user=user, *args, **kwargs)
            else:
                user.status_assinatura = 'expired_trial'
                db.session.commit()
                flash('Seu período de teste acabou. Para continuar, por favor, realize sua assinatura.', 'info')
                return redirect(url_for('pagamento'))
        flash('Sua assinatura não está ativa. Por favor, regularize para ter acesso.', 'info')
        return redirect(url_for('pagamento'))
    return decorated_function

# --- ROTAS DE AUTENTICAÇÃO E PÁGINAS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email_form = request.form.get('email')
    password_form = request.form.get('password')
    user = AppUser.query.filter_by(email=email_form).first()
    if user and user.status_assinatura != 'canceled' and check_password_hash(user.senha_hash, password_form):
        session['logged_in'] = True
        session['email'] = user.email
        return redirect(url_for('dashboard'))
    flash('E-mail ou senha inválidos, ou conta encerrada.', 'error')
    return redirect(url_for('index'))

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        email = request.form.get('email')
        country = request.form.get('country')
        company_id = request.form.get('company_id')
        nome_empresa = request.form.get('nome_empresa')
        password = request.form.get('password')

        if not all([email, country, company_id, nome_empresa, password]):
            flash('Por favor, preencha todos os campos do cadastro.', 'error')
            return redirect(url_for('index'))
        
        user_existente = AppUser.query.filter_by(country=country, company_id=company_id).first()
        if user_existente:
            if user_existente.status_assinatura in ['canceled', 'expired_trial']:
                user_existente.nome_empresa = nome_empresa
                user_existente.email = email
                user_existente.senha_hash = generate_password_hash(password)
                user_existente.status_assinatura = 'trial'
                user_existente.trial_end_date = datetime.utcnow() + timedelta(days=7)
                db.session.commit()
                session['logged_in'] = True
                session['email'] = user_existente.email
                flash('Que bom te ver de volta! Reativamos sua conta com mais 7 dias de teste.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Uma conta com este ID de empresa já existe para o país selecionado.', 'error')
                return redirect(url_for('index'))
        
        senha_hash = generate_password_hash(password)
        data_final_teste = datetime.utcnow() + timedelta(days=30)
        new_user = AppUser(
            country=country, company_id=company_id, email=email, senha_hash=senha_hash, 
            nome_empresa=nome_empresa, api_key=secrets.token_hex(16), 
            trial_end_date=data_final_teste
        )
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = True
        session['email'] = new_user.email
        flash('Conta criada com sucesso! Você tem 30 dias de teste grátis.', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao registrar: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/demo-login')
def demo_login():
    session['logged_in'] = True
    session['email'] = 'demo@synapcortex.com'
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@subscription_required
def dashboard(user):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    popups_exibidos = AnalyticsEvent.query.filter(AnalyticsEvent.owner_id == user.id, AnalyticsEvent.event_name == 'popup_exibido', AnalyticsEvent.timestamp >= thirty_days_ago).count()
    top_pages_query = db.session.query(AnalyticsEvent.event_data, func.count(AnalyticsEvent.id).label('views')).filter(AnalyticsEvent.owner_id == user.id, AnalyticsEvent.event_name == 'pagina_visitada', AnalyticsEvent.timestamp >= thirty_days_ago).group_by(AnalyticsEvent.event_data).order_by(func.count(AnalyticsEvent.id).desc()).limit(5).all()
    top_pages = [{'title': (json.loads(p.event_data).get('title') or json.loads(p.event_data).get('url', 'N/A')), 'views': p.views} for p in top_pages_query]
    insight_detetive = f"Sua página mais popular é '{top_pages[0]['title']}'. Considere criar uma oferta!" if top_pages else None
    try: user_config = json.loads(user.configuracoes)
    except: user_config = {}
    try: campaign_config_data = json.loads(user.campaign_config or '{}')
    except: campaign_config_data = {}
    return render_template('dashboard.html', usuario=user, config=user_config, popups_exibidos=popups_exibidos, top_pages=top_pages, insight_detetive=insight_detetive, campaign_config_data=campaign_config_data, utcnow=datetime.utcnow)

@app.route('/dashboard/visitors')
@subscription_required
def visitors(user):
    events = AnalyticsEvent.query.filter_by(owner_id=user.id, event_name='pagina_visitada').order_by(AnalyticsEvent.timestamp.desc()).limit(200).all()
    visitors_data = defaultdict(list)
    for event in events:
        try:
            event_details = json.loads(event.event_data)
            event_details['timestamp'] = event.timestamp.strftime('%d/%m/%Y às %H:%M')
            visitors_data[event.visitor_id].append(event_details)
        except: continue
    return render_template('visitors.html', visitors_data=visitors_data, usuario=user)

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento_pendente.html')

@app.route('/salvar-configuracoes', methods=['POST'])
@subscription_required
def salvar_configuracoes(user):
    try:
        config_atual = json.loads(user.configuracoes or '{}')
        campaign_config_atual = json.loads(user.campaign_config or '{}')
        checkboxes_gerais = ['ativar_abandono', 'ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        for check in checkboxes_gerais:
            config_atual[check] = check in request.form
        campos_texto_gerais = ['popup_titulo', 'popup_mensagem', 'msg_bem_vindo', 'msg_interessado', 'abandono_tipo', 'abandono_presente_fechado', 'abandono_presente_aberto', 'abandono_timer_minutos']
        for campo in campos_texto_gerais:
            if request.form.get(campo) is not None:
                config_atual[campo] = request.form.get(campo)
        user.configuracoes = json.dumps(config_atual)
        user.campaign_active = 'campaign_active' in request.form
        start_date_str = request.form.get('campaign_start_date')
        user.campaign_start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M') if start_date_str else None
        end_date_str = request.form.get('campaign_end_date')
        user.campaign_end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') if end_date_str else None
        campaign_config_atual['campaign_bar_active'] = 'campaign_bar_active' in request.form
        campos_texto_campanha = ['campaign_bar_text', 'campaign_bar_position', 'campaign_abandono_tipo', 'campaign_popup_titulo', 'campaign_popup_mensagem', 'campaign_presente_fechado', 'campaign_presente_aberto']
        for campo in campos_texto_campanha:
            if request.form.get(campo) is not None:
                campaign_config_atual[campo] = request.form.get(campo)
        user.campaign_config = json.dumps(campaign_config_atual)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Configurações salvas com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao salvar: {e}'}), 500

@app.route('/encerrar-conta', methods=['POST'])
@subscription_required
def encerrar_conta(user):
    try:
        user.status_assinatura = 'canceled'
        db.session.commit()
        session.clear()
        flash('Sua conta foi encerrada. Agradecemos por testar a SynapCortex.', 'success')
        return jsonify({'status': 'success', 'redirect_url': url_for('index')})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao encerrar a conta: {e}'}), 500

@app.route('/mudar-email', methods=['POST'])
@subscription_required
def mudar_email(user):
    try:
        novo_email = request.form.get('new_email')
        senha_atual = request.form.get('current_password')
        if not novo_email or not senha_atual:
            return jsonify({'status': 'error', 'message': 'Por favor, preencha todos os campos.'}), 400
        if not check_password_hash(user.senha_hash, senha_atual):
            return jsonify({'status': 'error', 'message': 'Senha atual incorreta.'}), 403
        user.email = novo_email
        db.session.commit()
        session['email'] = novo_email
        return jsonify({'status': 'success', 'message': 'E-mail alterado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao alterar o e-mail: {e}'}), 500

# --- ROTAS DA API ---
@app.route('/api/track', methods=['POST'])
def track_event():
    data = request.get_json(silent=True)
    if not data or not data.get('apiKey'):
        return jsonify({'error': 'Dados incompletos ou malformados.'}), 400
    user = AppUser.query.filter_by(api_key=data.get('apiKey')).first()
    if not user:
        return jsonify({'error': 'API Key inválida.'}), 403
    try:
        new_event = AnalyticsEvent(
            owner_id=user.id,
            visitor_id=data.get('visitorId'),
            event_name=data.get('eventName'),
            event_data=json.dumps(data.get('eventData', {}))
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao salvar evento: {e}'}), 500

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({'error': 'API Key não fornecida'}), 400
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'API Key inválida'}), 404
    try:
        config = json.loads(user.configuracoes or '{}')
        campaign_config = json.loads(user.campaign_config or '{}')
    except json.JSONDecodeError:
        config = {}
        campaign_config = {}
    config.update(campaign_config)
    agora = datetime.utcnow()
    is_campaign_active = False
    if user.campaign_active and user.campaign_start_date and user.campaign_end_date:
        if user.campaign_start_date <= agora <= user.campaign_end_date:
            is_campaign_active = True
    config['is_campaign_active'] = is_campaign_active
    if is_campaign_active:
        config['campaign_end_date'] = user.campaign_end_date.isoformat()
    return jsonify(config)

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)