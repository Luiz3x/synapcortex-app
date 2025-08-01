import os
import json
import secrets
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# A CORREÇÃO ESTÁ AQUI: Voltamos ao normal. O Flask precisa saber onde fica a pasta static.
app = Flask(__name__)

# --- Configurações Essenciais ---
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-desenvolvimento-local')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# A configuração do WhiteNoise continua explícita, que é o ideal.
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/", prefix="/static/")


# --- O resto do arquivo está 100% correto e não muda ---
diretorio_de_dados = "data"
CAMINHO_USUARIOS = os.path.join(diretorio_de_dados, "users.json")
CAMINHO_ANALYTICS = os.path.join(diretorio_de_dados, "analytics.json")

def inicializar_arquivos_json():
    if not os.path.exists(diretorio_de_dados):
        os.makedirs(diretorio_de_dados)
    if not os.path.exists(CAMINHO_USUARIOS):
        with open(CAMINHO_USUARIOS, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists(CAMINHO_ANALYTICS):
        with open(CAMINHO_ANALYTICS, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def carregar_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def salvar_json(caminho_arquivo, dados):
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        usuarios = carregar_json(CAMINHO_USUARIOS)
        user_data = usuarios.get(email)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if user_data and check_password_hash(user_data.get('senha', ''), password):
            session['logged_in'] = True
            session['email'] = email
            if is_ajax:
                return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            message = 'E-mail ou senha incorretos.'
            if is_ajax:
                return jsonify({'success': False, 'message': message}), 401
            return render_template('login.html', error=message)
    return render_template('login.html', message=request.args.get('message'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        cnpj = request.form.get('cnpj', '')
        nome_empresa = request.form.get('nome_empresa', '')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if not all([email, password, cnpj, nome_empresa]):
            message = 'Todos os campos são obrigatórios.'
            if is_ajax: return jsonify({'success': False, 'message': message}), 400
            return render_template('registrar.html', error=message)
        if not cnpj.isdigit() or len(cnpj) != 14:
            message = 'CNPJ inválido. Por favor, insira 14 números.'
            if is_ajax: return jsonify({'success': False, 'message': message}), 400
            return render_template('registrar.html', error=message)
        usuarios = carregar_json(CAMINHO_USUARIOS)
        if email in usuarios or any(u.get('cnpj') == cnpj for u in usuarios.values()):
            message = 'E-mail ou CNPJ já cadastrado.'
            if is_ajax: return jsonify({'success': False, 'message': message}), 409
            return render_template('registrar.html', error=message)
        hashed_password = generate_password_hash(password)
        data_inicio = datetime.now()
        data_fim = data_inicio + timedelta(days=30)
        usuarios[email] = {
            'senha': hashed_password, 'cnpj': cnpj, 'nome_empresa': nome_empresa,
            'status_assinatura': 'ativo',
            'data_inicio_assinatura': data_inicio.strftime('%Y-%m-%d'),
            'data_fim_assinatura': data_fim.strftime('%Y-%m-%d'),
            'api_key': secrets.token_urlsafe(24),
            'configuracoes': {
                'popup_titulo': 'Não vá embora!', 'popup_mensagem': 'Temos uma oferta especial para você.',
                'tatica_mobile': 'foco', 'ativar_quarto_bem_vindo': False,
                'ativar_quarto_interessado': False, 'msg_bem_vindo': '', 'msg_interessado': ''
            }
        }
        salvar_json(CAMINHO_USUARIOS, usuarios)
        message = 'Cadastro realizado com sucesso! Faça o login.'
        if is_ajax:
            return jsonify({'success': True, 'redirect_url': url_for('login', message=message)})
        return redirect(url_for('login', message=message))
    return render_template('registrar.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    dados_usuario = usuarios.get(email_usuario)
    if not dados_usuario:
        session.clear()
        return redirect(url_for('login'))
    data_fim_str = dados_usuario.get('data_fim_assinatura')
    hoje = datetime.now().date()
    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    if hoje > data_fim:
        dados_usuario['status_assinatura'] = 'pendente'
        salvar_json(CAMINHO_USUARIOS, usuarios)
        return render_template('pagamento_pendente.html', 
                               stripe_publishable_key=app.config['STRIPE_PUBLISHABLE_KEY_TEST'],
                               usuario=dados_usuario)
    dias_restantes = (data_fim - hoje).days
    mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    analytics_data = carregar_json(CAMINHO_ANALYTICS)
    insights_reais = {'popups_exibidos': 0, 'clientes_recuperados': 0, 'taxa_conversao': "0.00%"}
    return render_template('dashboard.html', 
                           usuario=dados_usuario, 
                           config=dados_usuario.get('configuracoes', {}),
                           insights=insights_reais,
                           mensagem_status_assinatura=mensagem_status_assinatura)

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    if email_usuario not in usuarios:
        return redirect(url_for('login'))
    configuracoes_atuais = usuarios[email_usuario].get('configuracoes', {})
    configuracoes_atuais.update({
        'popup_titulo': request.form.get('popup_titulo'),
        'popup_mensagem': request.form.get('popup_mensagem'),
    })
    usuarios[email_usuario]['configuracoes'] = configuracoes_atuais
    salvar_json(CAMINHO_USUARIOS, usuarios)
    return redirect(url_for('dashboard'))

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    if 'logged_in' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    try:
        intent = stripe.PaymentIntent.create(
            amount=9990,
            currency='brl',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/api/get-client-config')
def get_client_config():
    api_key_recebida = request.args.get('key')
    if not api_key_recebida:
        return jsonify({'error': 'Chave de API não fornecida.'}), 401
    usuarios = carregar_json(CAMINHO_USUARIOS)
    for usuario in usuarios.values():
        if usuario.get('api_key') == api_key_recebida:
            return jsonify(usuario.get('configuracoes', {}))
    return jsonify({'error': 'Chave de API inválida.'}), 403
    