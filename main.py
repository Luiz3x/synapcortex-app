# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão Final Estável
# =================================================================================
import os, json, secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from whitenoise import WhiteNoise
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = secrets.token_hex(16)
CORS(app, resources={r"/api/*": {"origins": "*"}})
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"): db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 5
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_PRE_PING'] = True
db = SQLAlchemy(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

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
try:
    with app.app_context():
        db.create_all()
        if not AppUser.query.filter_by(email='demo@synapcortex.com').first():
            demo_user = AppUser(email='demo@synapcortex.com', senha_hash=generate_password_hash('demo'), nome_empresa='Loja de Demonstração', cnpj='00000000000000', api_key='chave_api_demo_123456', configuracoes=json.dumps({'popup_titulo': 'Bem-vindo!', 'popup_mensagem': 'Explore nosso painel.'}))
            db.session.add(demo_user); db.session.commit()
except Exception as e: print(f"!!!!!! ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {e} !!!!!!")
@app.route('/')
def index(): return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = AppUser.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.senha_hash, request.form.get('password')):
            session['logged_in'] = True; session['email'] = user.email; return redirect(url_for('dashboard'))
        else: flash('E-mail ou senha inválidos.', 'error'); return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email')
        if AppUser.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado.', 'error'); return redirect(url_for('registrar'))
        new_user = AppUser(email=email, senha_hash=generate_password_hash(request.form.get('password')), nome_empresa=request.form.get('nome_empresa'), cnpj=request.form.get('cnpj'), api_key=secrets.token_hex(16), configuracoes=json.dumps({'popup_titulo': 'Não vá embora!', 'popup_mensagem': 'Temos uma oferta especial.'}))
        db.session.add(new_user); db.session.commit()
        session['logged_in'] = True; session['email'] = new_user.email; flash('Conta criada com sucesso! Bem-vindo!', 'success'); return redirect(url_for('dashboard'))
    return render_template('registrar.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('login'))
    user = AppUser.query.filter_by(email=session['email']).first()
    if not user: session.clear(); return redirect(url_for('login'))
    popups_exibidos = AnalyticsEvent.query.filter_by(owner_id=user.id, event_name='popup_exibido').count()
    user_config = json.loads(user.configuracoes)
    return render_template('dashboard.html', usuario=user, config=user_config, popups_exibidos=popups_exibidos)
@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    email_na_sessao = session.get('email')
    if not email_na_sessao: return jsonify({'status': 'error', 'message': 'Acesso não autorizado.'}), 403
    if email_na_sessao == 'demo@synapcortex.com': return jsonify({'status': 'info', 'message': 'Na conta de demonstração, as alterações não são salvas.'}), 200
    user = AppUser.query.filter_by(email=email_na_sessao).first()
    if user:
        config_atual = json.loads(user.configuracoes)
        for chave, valor in request.form.items(): config_atual[chave] = True if valor == 'on' else valor
        checkboxes = ['ativar_abandono', 'ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        for check in checkboxes:
            if check not in request.form: config_atual[check] = False
        user.configuracoes = json.dumps(config_atual); db.session.commit()
        return jsonify({'status': 'success', 'message': 'Configurações salvas!'}), 200
    return jsonify({'status': 'error', 'message': 'Usuário não encontrado.'}), 404
@app.route('/api/track', methods=['POST'])
def track_event():
    data = request.get_json();
    if not data: return jsonify({'error': 'Requisição sem dados.'}), 400
    api_key = data.get('apiKey'); visitor_id = data.get('visitorId'); event_name = data.get('eventName')
    if not all([api_key, visitor_id, event_name]): return jsonify({'error': 'Dados incompletos.'}), 400
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user: return jsonify({'error': 'API Key inválida.'}), 403
    new_event = AnalyticsEvent(owner_id=user.id, visitor_id=visitor_id, event_name=event_name, event_data=json.dumps(data.get('eventData', {})))
    db.session.add(new_event); db.session.commit()
    return jsonify({'status': 'ok'}), 200
@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key: return jsonify({'error': 'API Key não fornecida'}), 400
    user = AppUser.query.filter_by(api_key=api_key).first()
    if user: return jsonify(json.loads(user.configuracoes))
    return jsonify({'error': 'API Key inválida'}), 404
if __name__ == '__main__': app.run(debug=True)