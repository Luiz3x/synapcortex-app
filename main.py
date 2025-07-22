import os
import json
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app 
from werkzeug.security import generate_password_hash, check_password_hash
from whitenoise import WhiteNoise

# --- INICIALIZAÇÃO DIRETA E SIMPLIFICADA DO APP ---
app = Flask(__name__)

# --- CONFIGURAÇÕES APLICADAS DIRETAMENTE ---
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
app.config = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config = os.environ.get('STRIPE_SECRET_KEY_TEST')

import stripe
stripe.api_key = app.config

# --- WHITE NOISE (A FORMA MAIS ROBUSTA) ---
app.wsgi_app = WhiteNoise(app.wsgi_app)

CORS(app)

# Garante que o diretório /data exista
diretorio_de_dados = os.path.join(os.getcwd(), "data") 
if not os.path.exists(diretorio_de_dados):
    os.makedirs(diretorio_de_dados)

# --- FUNÇÕES AUXILIARES ---
def carregar_json(nome_arquivo, dados_padrao):
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    if not os.path.exists(caminho_completo):
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# --- ROTAS DO APLICATIVO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=)
def login():
    message = request.args.get('message')
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        usuarios = carregar_json('users.json', {}) 
        user_data = usuarios.get(email)
        if user_data and check_password_hash(user_data['senha'], password):
            session['logged_in'] = True
            session['email'] = email
            return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'E-mail ou senha incorretos.'}), 401
    return render_template('login.html', message=message)

@app.route('/registrar', methods=)
def registrar():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')
        usuarios = carregar_json('users.json', {}) 
        if email in usuarios:
            return jsonify({'success': False, 'message': 'Este e-mail já está cadastrado.'}), 409
        for user_data in usuarios.values():
            if user_data.get('cnpj') == cnpj:
                return jsonify({'success': False, 'message': 'Este CNPJ já possui um cadastro.'}), 409
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
        return jsonify({'success': True, 'redirect_url': url_for('login', message='Cadastro realizado com sucesso!')})
    return render_template('registrar.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    email_usuario = session.get('email')
    usuarios = carregar_json('users.json', {})
    dados_usuario = usuarios.get(email_usuario)
    if not dados_usuario:
        session.clear()
        return redirect(url_for('login', error='Sua sessão expirou.'))
    
    status_assinatura = dados_usuario.get('status_assinatura', 'pendente')
    data_fim_str = dados_usuario.get('data_fim_assinatura')
    mensagem_status_assinatura = ""
    dias_restantes = None

    if status_assinatura == 'ativo' and data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        hoje = datetime.now().date()
        if hoje > data_fim:
            dados_usuario['status_assinatura'] = 'pendente'
            salvar_json('users.json', usuarios)
            status_assinatura = 'pendente'
            mensagem_status_assinatura = "Sua avaliação gratuita expirou."
        else:
            dias_restantes = (data_fim - hoje).days
            mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    elif status_assinatura == 'pendente':
        mensagem_status_assinatura = "Sua assinatura está pendente."

    if status_assinatura == 'ativo':
        analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
        config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
        return render_template('dashboard.html', 
                               usuario=dados_usuario, 
                               analytics=analytics, 
                               config=config,
                               mensagem_status_assinatura=mensagem_status_assinatura,
                               dias_restantes=dias_restantes)
    else:
        # <<< BUG CORRIGIDO AQUI >>> Adicionado 'usuario=dados_usuario'
        return render_template('pagamento_pendente.html', 
                               stripe_publishable_key=current_app.config,
                               usuario=dados_usuario,
                               mensagem_status_assinatura=mensagem_status_assinatura)

@app.route('/create-payment-intent', methods=)
def create_payment_intent():
    if 'logged_in' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    email_usuario = session.get('email')
    amount_in_cents = 2990
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents, currency='brl',
            metadata={'user_email': email_usuario},
            payment_method_types=['card'],
        )
        return jsonify(clientSecret=intent.client_secret)
    except Exception as e:
        return jsonify(error={'message': str(e)}), 400

@app.route('/salvar-configuracoes', methods=) 
def salvar_configuracoes():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    novo_titulo = request.form.get('popup_titulo')
    nova_mensagem = request.form.get('popup_mensagem')
    config_atual = carregar_json('config_popup.json', {})
    config_atual['titulo'] = novo_titulo
    config_atual['mensagem'] = nova_mensagem
    salvar_json('config_popup.json', config_atual)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/get-config')
def get_config():
    config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
    return jsonify(config)

#... (outras rotas de API como track_view e track_click continuam aqui)...
@app.route('/api/track-view', methods=) 
def track_view():
    try:
        analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
        analytics['visualizacoes_popup'] += 1
        salvar_json('analytics.json', analytics)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error'}), 500

@app.route('/api/track-click', methods=) 
def track_click():
    try:
        analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
        analytics['cliques_popup'] += 1
        salvar_json('analytics.json', analytics)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error'}), 500

# --- PARA EXECUÇÃO LOCAL ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)