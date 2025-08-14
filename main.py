# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 9.0 - VERSÃO FINAL, COMPLETA E VERIFICADA
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
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "synapcortex_local.db")
    db_url = f"sqlite:///{db_path}"

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
    trial_end_date = db.Column(db.DateTime, nullable=True)
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

with app.app_context():
    db.create_all()

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email_form = request.form.get('email')
    password_form = request.form.get('password')
    if email_form == 'demo@synapcortex.com':
        session['logged_in'] = True
        session['email'] = 'demo@synapcortex.com'
        return redirect(url_for('dashboard'))
    user = AppUser.query.filter_by(email=email_form).first()
    if user and check_password_hash(user.senha_hash, password_form):
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
            email=email, senha_hash=senha_hash, nome_empresa=request.form.get('nome_empresa'),
            cnpj=request.form.get('cnpj'), api_key=secrets.token_hex(16),
            trial_end_date=data_final_teste, configuracoes='{}', campaign_config='{}')
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = True
        session['email'] = new_user.email
        flash('Conta criada com sucesso! Você tem 30 dias de teste grátis.', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Ocorreu um erro ao registrar: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('index'))
    email = session['email']
    
    if email == 'demo@synapcortex.com':
        user_demo = {'nome_empresa': 'Loja de Demonstração', 'api_key': 'chave_demo', 'campaign_active': False, 'campaign_start_date': None, 'campaign_end_date': None, 'campaign_config': '{}'}
        config_demo = {'ativar_abandono': True, 'popup_titulo': 'Bem-vindo!', 'popup_mensagem': 'Explore o painel.'}
        return render_template('dashboard.html', usuario=user_demo, config=config_demo, popups_exibidos='N/A', top_pages=[], insight_detetive="Este é um exemplo de insight!")

    user = AppUser.query.filter_by(email=email).first()
    if not user: 
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('index'))
    
    if not hasattr(user, 'campaign_active'): user.campaign_active = False
    if not hasattr(user, 'campaign_config') or user.campaign_config is None: user.campaign_config = '{}'
    if not hasattr(user, 'campaign_start_date'): user.campaign_start_date = None
    if not hasattr(user, 'campaign_end_date'): user.campaign_end_date = None
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    popups_exibidos = AnalyticsEvent.query.filter(AnalyticsEvent.owner_id == user.id, AnalyticsEvent.event_name == 'popup_exibido', AnalyticsEvent.timestamp >= thirty_days_ago).count()
    top_pages_query = db.session.query(AnalyticsEvent.event_data, func.count(AnalyticsEvent.id).label('view_count')).filter(AnalyticsEvent.owner_id == user.id, AnalyticsEvent.event_name == 'pagina_visitada', AnalyticsEvent.timestamp >= thirty_days_ago).group_by(AnalyticsEvent.event_data).order_by(func.count(AnalyticsEvent.id).desc()).limit(5).all()
    top_pages = [{'title': (json.loads(p.event_data).get('title') or json.loads(p.event_data).get('url', 'N/A')), 'views': p.view_count} for p in top_pages_query]
    insight_detetive = f"Sua página mais popular é '{top_pages[0]['title']}'. Considere criar uma oferta!" if top_pages else None
    
    try:
        user_config = json.loads(user.configuracoes) if isinstance(user.configuracoes, str) else (user.configuracoes or {})
    except (json.JSONDecodeError, TypeError):
        user_config = {}

    return render_template('dashboard.html', usuario=user, config=user_config, popups_exibidos=popups_exibidos, top_pages=top_pages, insight_detetive=insight_detetive)

@app.route('/dashboard/visitors')
def visitors():
    if 'logged_in' not in session: return redirect(url_for('index'))
    user = AppUser.query.filter_by(email=session['email']).first()
    if not user: return redirect(url_for('index'))
    events = AnalyticsEvent.query.filter_by(owner_id=user.id, event_name='pagina_visitada').order_by(AnalyticsEvent.timestamp.desc()).all()
    visitors_data = defaultdict(list)
    for event in events:
        try:
            event_details = json.loads(event.event_data)
            event_details['timestamp'] = event.timestamp.strftime('%d/%m/%Y às %H:%M')
            visitors_data[event.visitor_id].append(event_details)
        except: continue
    return render_template('visitors.html', visitors_data=visitors_data, usuario=user)

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session: return jsonify({'status': 'error', 'message': 'Acesso não autorizado.'}), 403
    user = AppUser.query.filter_by(email=session['email']).first()
    if not user: return jsonify({'status': 'error', 'message': 'Usuário não encontrado.'}), 404
    if user.email == 'demo@synapcortex.com': return jsonify({'status': 'info', 'message': 'Na conta demo, as alterações não são salvas.'})
    try:
        config_atual = json.loads(user.configuracoes or '{}')
        campaign_config_atual = json.loads(user.campaign_config or '{}')
        checkboxes_normais = ['ativar_abandono', 'ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        for key, value in request.form.items():
            if key in checkboxes_normais or key.startswith('campaign_'): continue
            elif key == 'countdown_bar_text': campaign_config_atual[key] = value
            else: config_atual[key] = value
        for check in checkboxes_normais: config_atual[check] = check in request.form
        user.campaign_active = 'campaign_active' in request.form
        start_date_str = request.form.get('campaign_start_date')
        user.campaign_start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M') if start_date_str else None
        end_date_str = request.form.get('campaign_end_date')
        user.campaign_end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') if end_date_str else None
        user.configuracoes = json.dumps(config_atual)
        user.campaign_config = json.dumps(campaign_config_atual)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Configurações salvas!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao salvar: {e}'}), 500

@app.route('/api/track', methods=['POST'])
def track_event():
    data = request.get_json()
    if not data or not data.get('apiKey'): return jsonify({'error': 'Dados incompletos.'}), 400
    user = AppUser.query.filter_by(api_key=data.get('apiKey')).first()
    if not user: return jsonify({'error': 'API Key inválida.'}), 403
    new_event = AnalyticsEvent(owner_id=user.id, visitor_id=data.get('visitorId'), event_name=data.get('eventName'), event_data=json.dumps(data.get('eventData', {})))
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'status': 'ok'}), 200

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user: return jsonify({'error': 'API Key inválida'}), 404
    config = json.loads(user.configuracoes or '{}')
    agora = datetime.utcnow()
    is_campaign_active = False
    if hasattr(user, 'campaign_active') and user.campaign_active and user.campaign_start_date and user.campaign_end_date:
        if user.campaign_start_date <= agora <= user.campaign_end_date: is_campaign_active = True
    config['is_campaign_active'] = is_campaign_active
    if is_campaign_active:
        config['campaign_config'] = json.loads(user.campaign_config or '{}')
        config['campaign_end_date'] = user.campaign_end_date.isoformat()
    return jsonify(config)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)