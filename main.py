# --- Importações Essenciais ---
import os
import json
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO DO APP FLASK ---
# Sendo explícito sobre a pasta static, ajudamos o Flask em ambientes de deploy
app = Flask(__name__, static_folder='static')

# --- CONFIGURAÇÕES DO APLICATIVO ---
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')

# Adicione esta linha de volta para configurar o Stripe globalmente
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')

# --- MIDDLEWARE (APENAS UM BLOCO) ---
CORS(app)
# ... resto do código ...

# --- MIDDLEWARE (APENAS UM BLOCO) ---
CORS(app)
# Configuração SIMPLIFICADA do WhiteNoise. Ele apenas 'melhora' o sistema do Flask.
app.wsgi_app = WhiteNoise(app.wsgi_app)


# --- GERENCIAMENTO DE DIRETÓRIO DE DADOS ---
diretorio_de_dados = os.path.join(os.getcwd(), "data")
if not os.path.exists(diretorio_de_dados):
    os.makedirs(diretorio_de_dados)

# --- FUNÇÕES AUXILIARES PARA MANIPULAÇÃO DE JSON ---
def carregar_json(nome_arquivo, dados_padrao):
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    try:
        if not os.path.exists(caminho_completo):
            with open(caminho_completo, 'w', encoding='utf-8') as f:
                json.dump(dados_padrao, f, indent=4)
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return dados_padrao

def salvar_json(nome_arquivo, dados):
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ROTAS PRINCIPAIS DO APLICATIVO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        usuarios = carregar_json('users.json', {})
        user_data = usuarios.get(email)
        if user_data and check_password_hash(user_data.get('senha', ''), password):
            session['logged_in'] = True
            session['email'] = email
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
            else:
                return redirect(url_for('dashboard'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'E-mail ou senha incorretos.'}), 401
            else:
                return render_template('login.html', error='E-mail ou senha incorretos.')
    message = request.args.get('message')
    return render_template('login.html', message=message)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')
        usuarios = carregar_json('users.json', {})
        if email in usuarios:
            message = 'Este e-mail já está cadastrado.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': message}), 409
            return render_template('registrar.html', error=message)
        for user_data in usuarios.values():
            if user_data.get('cnpj') == cnpj:
                message = 'Este CNPJ já possui um cadastro.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': message}), 409
                return render_template('registrar.html', error=message)
        hashed_password = generate_password_hash(password)
        data_inicio_assinatura = datetime.now()
        data_fim_assinatura = data_inicio_assinatura + timedelta(days=30)
        usuarios[email] = {
            'senha': hashed_password, 'cnpj': cnpj, 'nome_empresa': nome_empresa,
            'status_assinatura': 'ativo',
            'data_inicio_assinatura': data_inicio_assinatura.strftime('%Y-%m-%d'),
            'data_fim_assinatura': data_fim_assinatura.strftime('%Y-%m-%d')
        }
        salvar_json('users.json', usuarios)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'redirect_url': url_for('login', message='Cadastro realizado com sucesso!')})
        return redirect(url_