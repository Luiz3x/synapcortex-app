import os
import json
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app 
from werkzeug.security import generate_password_hash, check_password_hash
from whitenoise import WhiteNoise # <<< ADICIONADO >>> Importa a biblioteca WhiteNoise

# =====================================================================
# Funções para carregar e salvar JSON
# =====================================================================
# Definindo o caminho para o arquivo de usuários
USERS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')
ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'analytics.json')
CONFIG_POPUP_FILE = os.path.join(os.path.dirname(__file__), 'data', 'config_popup.json')

def carregar_json(nome_arquivo, dados_padrao):
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)

    if not os.path.exists(caminho_completo):
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# =====================================================================
# A FÁBRICA DE APLICATIVOS (Application Factory)
# =====================================================================
def create_app():
    app = Flask(__name__)
    
    # <<< ADICIONADO >>> Integração do WhiteNoise para servir arquivos estáticos em produção.
    # Ele irá procurar arquivos na pasta 'static' e os servirá com o prefixo '/static/'.
    # Isso corrige o problema do CSS/JS não carregar no Render.com.
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')
    
    CORS(app)
    
    # Garante que o diretório /data exista
    diretorio_de_dados = os.path.join(os.getcwd(), "data") 
    if not os.path.exists(diretorio_de_dados):
        os.makedirs(diretorio_de_dados)
    
    # Configurações e credenciais
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
    
    app.config['PAGBANK_EMAIL'] = os.environ.get('PAGBANK_EMAIL')
    app.config['PAGBANK_SANDBOX_TOKEN'] = os.environ.get('PAGBANK_SANDBOX_TOKEN')
    app.config['PAGBANK_TOKEN'] = os.environ.get('PAGBANK_TOKEN') 
    app.config['PAGBANK_CLIENT_ID'] = os.environ.get('PAGBANK_CLIENT_ID') 
    app.config['PAGBANK_CLIENT_SECRET'] = os.environ.get('PAGBANK_CLIENT_SECRET') 

    # Configurações do Stripe
    app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
    app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
    import stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY_TEST']


    # --- REGISTRO DAS ROTAS ---

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('dashboard'))
            else:
                # Retornando uma resposta JSON para o AJAX no frontend
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify(message='E-mail ou senha incorretos.'), 401
                message = 'E-mail ou senha incorretos.'
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
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify(message='Este e-mail já está cadastrado.'), 409
                return render_template('registrar.html', error='Este e-mail já está cadastrado. Tente fazer login ou use outro e-mail.')

            for user_data in usuarios.values():
                if user_data.get('cnpj') == cnpj:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify(message='Este CNPJ já possui um cadastro.'), 409
                    return render_template('registrar.html', error='Este CNPJ já possui um cadastro. Entre em contato para mais informações.')

            hashed_password = generate_password_hash(password)
            data_inicio_assinatura = datetime.now()
            data_fim_assinatura = data_inicio_assinatura + timedelta(days=30)

            usuarios[email] = {
                'senha': hashed_password,
                'cnpj': cnpj,
                'nome_empresa': nome_empresa,
                'status_assinatura': 'ativo',
                'data_inicio_assinatura': data_inicio_assinatura.strftime('%Y-%m-%d'),
                'data_fim_assinatura': data_fim_assinatura.strftime('%Y-%m-%d')
            }
            salvar_json('users.json', usuarios)
            
            print(f"--- Usuário {email} registrado com sucesso! Mês grátis ativado. ---")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=True, redirect_url=url_for('login', message='Cadastro realizado com sucesso! Aproveite seu mês grátis.'))
                
            return redirect(url_for('login', message='Cadastro realizado com sucesso! Aproveite seu mês grátis.')) 
        return render_template('registrar.html')

    @app.route('/create-payment-intent', methods=['POST'])
    def create_payment_intent():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Usuário não logado'}), 401

        email_usuario = session.get('email')
        amount_in_cents = 2990 # Ex: R$ 29,90

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='brl',
                metadata={'user_email': email_usuario},
                payment_method_types=['card'],
            )
            return jsonify(clientSecret=intent.client_secret)
        except stripe.error.StripeError as e:
            print(f"Erro ao criar PaymentIntent: {e}")
            return jsonify(error={'message': str(e)}), 400

    @app.route('/dashboard')
    def dashboard():
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))

        email_usuario = session.get('email')
        usuarios = carregar_json('users.json', {})
        dados_usuario = usuarios.get(email_usuario)

        if not dados_usuario:
            session.clear()
            return redirect(url_for('login', error='Sua sessão expirou ou usuário não encontrado.'))

        analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
        config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})

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
                print(f"--- Assinatura de {email_usuario} expirada e atualizada para 'pendente' ---")
                mensagem_status_assinatura = "Sua avaliação gratuita expirou. Por favor, renove sua assinatura para manter o acesso."
            else:
                dias_restantes = (data_fim - hoje).days
                if dias_restantes <= 7:
                    mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s). Renove agora para não perder o acesso!"
                else:
                    mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
        
        elif status_assinatura == 'pendente':
            mensagem_status_assinatura = "Sua assinatura está pendente. Por favor, realize o pagamento para ativar seu acesso."

        if status_assinatura == 'ativo':
            return render_template('dashboard.html', 
                                   usuario=dados_usuario, 
                                   analytics=analytics, 
                                   config=config,
                                   mensagem_status_assinatura=mensagem_status_assinatura,
                                   dias_restantes=dias_restantes)
        else:
            return render_template('pagamento_pendente.html', 
                                   stripe_publishable_key=current_app.config['STRIPE_PUBLISHABLE_KEY_TEST'],
                                   mensagem_status_assinatura=mensagem_status_assinatura)

    @app.route('/salvar-configuracoes', methods=['POST']) 
    def salvar_configuracoes():
        if 'logged_in' not in session or not session['logged_in']:
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
        config = carregar_json('config_popup.json', {"titulo": "Não vá embora!", "mensagem": "Temos uma oferta especial para você."})
        return jsonify(config)

    @app.route('/api/track-view', methods=['POST']) 
    def track_view():
        try:
            analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
            analytics['visualizacoes_popup'] += 1
            salvar_json('analytics.json', analytics)
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            print(f"!!! Erro ao registrar visualização: {e}!!!")
            return jsonify({'status': 'error'}), 500

    @app.route('/api/track-click', methods=['POST']) 
    def track_click():
        try:
            analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
            analytics['cliques_popup'] += 1
            salvar_json('analytics.json', analytics)
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            print(f"!!! Erro ao registrar clique: {e}!!!")
            return jsonify({'status': 'error'}), 500
            
    # --- ROTA DE WEBHOOK DO PAGSEGURO (LEGADO) ---
    # Manter ou remover dependendo da sua necessidade
    @app.route('/webhook-pagbank', methods=['POST']) 
    def webhook_pagbank():
        print("!!!!!!!!!! ROTA WEBHOOK PAGBANK FOI ACESSADA !!!!!!!!!!")
        try:
            data = request.form.to_dict()
            notification_code = data.get('notificationCode')
            if not notification_code:
                return jsonify({'status': 'sem codigo'}), 400
            
            print(f"--- Consultando notificação PagBank: {notification_code} ---")
            # ... Lógica de consulta do PagBank ...

        except Exception as e:
            print(f"!!! Erro no webhook PagBank: {e}!!!")
        return jsonify({'status': 'recebido'}), 200

    # RETORNAMOS O APP CONSTRUÍDO NO FINAL DA FUNÇÃO
    return app

# Seção para execução local (para testes)
if __name__ == '__main__':
    app = create_app()
    # Para testes locais, o debug=True já serve os arquivos estáticos.
    # A mudança do WhiteNoise é para o ambiente de produção (Gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)