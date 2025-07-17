import os
import json
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app 
from werkzeug.security import generate_password_hash, check_password_hash
import stripe # Importa a biblioteca do Stripe
import Stripe

# =====================================================================
# FUNÇÕES DE AJUDA (Não mudam)
# =====================================================================
def carregar_json(nome_arquivo, dados_padrao):
    # Define o caminho para o nosso "cofre" na Render
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)

    # Se o arquivo não existir, cria-o com os dados padrão.
    if not os.path.exists(caminho_completo):
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    
    # Abre e retorna os dados do arquivo
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    # Define o caminho para o nosso "cofre" na Render
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)
        # =====================================================================
# A GRANDE MUDANÇA: A FÁBRICA DE APLICATIVOS (Application Factory)
# =====================================================================
def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # === CORREÇÃO CRÍTICA: Garante que o diretório /data exista dentro do projeto ===
    diretorio_de_dados = os.path.join(os.getcwd(), "data") 
    if not os.path.exists(diretorio_de_dados):
        os.makedirs(diretorio_de_dados)
    # ======================================================================
    
    # Configurações e credenciais agora vêm das Variáveis de Ambiente
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
    
    app.config['PAGBANK_EMAIL'] = os.environ.get('PAGBANK_EMAIL')
    app.config['PAGBANK_SANDBOX_TOKEN'] = os.environ.get('PAGBANK_SANDBOX_TOKEN')
    app.config['PAGBANK_TOKEN'] = os.environ.get('PAGBANK_TOKEN') 
    app.config['PAGBANK_CLIENT_ID'] = os.environ.get('PAGBANK_CLIENT_ID') 
    app.config['PAGBANK_CLIENT_SECRET'] = os.environ.get('PAGBANK_CLIENT_SECRET') 

    # --- NOVO: Configurações do Stripe ---
    app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
    app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
    stripe.api_key = app.config['STRIPE_SECRET_KEY_TEST'] # Define a chave secreta do Stripe para a biblioteca
    # ====================================
    # AGORA, TODAS AS ROTAS SÃO REGISTRADAS DENTRO DA FÁBRICA
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            usuarios = carregar_json('users.json', {}) 
            user_data = usuarios.get(username)
            if user_data and check_password_hash(user_data['senha'], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
            return render_template('login.html', error='Credenciais inválidas.')
        return render_template('login.html')

    @app.route('/registrar', methods=['GET', 'POST'])
    def registrar():
        if request.method == 'POST':
            fullname = request.form.get('fullname')
            cpf = request.form.get('cpf')
            ddd = request.form.get('ddd')
            phone = request.form.get('phone')
            username = request.form.get('username')
            password = request.form.get('password')
            
            usuarios = carregar_json('users.json', {}) 
            if username in usuarios:
                return "Usuário já existe!"

            email_comprador = f"cliente_{username}@sandbox.pagbank.com.br"

            usuarios[username] = {
                "email": email_comprador, 
                "senha": generate_password_hash(password),
                "status_assinatura": "pendente", 
                "data_fim_assinatura": None
            }
            salvar_json('users.json', usuarios)
            
            # --- APÓS O REGISTRO, REDIRECIONAMOS PARA O DASHBOARD ---
            # A lógica da API de Pedidos do PagBank foi removida aqui.
            print(f"--- Usuário {username} registrado com sucesso! Redirecionando para dashboard/pagamento pendente ---")
            return redirect(url_for('dashboard')) 
        return render_template('registrar.html')
        # --- NOVA ROTA: Criar PaymentIntent do Stripe ---
    @app.route('/create-payment-intent', methods=['POST'])
    def create_payment_intent():
        if 'username' not in session:
            return jsonify({'error': 'Usuário não logado'}), 401

        username = session['username']
        # Busca o valor da assinatura do seu plano. Por simplicidade, valor fixo em centavos.
        # R$ 29,90 = 2990 centavos. Ajuste para o valor real da sua assinatura.
        amount_in_cents = 2990 

        try:
            # Cria um PaymentIntent no Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='brl', # Moeda brasileira
                metadata={'integration_id': username}, # Para identificar o usuário no Stripe
                payment_method_types=['card'], # Aceita pagamento com cartão
            )
            # Retorna o client_secret para o frontend
            return jsonify(clientSecret=intent.client_secret)
        except stripe.error.StripeError as e:
            print(f"Erro ao criar PaymentIntent: {e}")
            return jsonify(error={'message': str(e)}), 400

    @app.route('/dashboard')
    def dashboard():
        if 'username' not in session:
            return redirect(url_for('login'))

        username = session['username']
        usuarios = carregar_json('users.json', {})
        dados_usuario = usuarios.get(username)

        if dados_usuario and dados_usuario.get('status_assinatura') == 'ativo':
            analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
            config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
            return render_template('dashboard.html', usuario=dados_usuario, analytics=analytics, config=config)
        else:
            # Com a integração do Stripe, esta página de pagamento pendente será modificada
            # para exibir o formulário do Stripe Elements.
            return render_template('pagamento_pendente.html', 
                                    stripe_publishable_key=current_app.config['STRIPE_PUBLISHABLE_KEY_TEST'])
                                    @app.route('/salvar-configuracoes', methods=['POST']) 
    def salvar_configuracoes():
        if 'username' not in session:
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
        session.pop('username', None)
        return redirect(url_for('login'))

    @app.route('/api/get-config')
    def get_config():
        config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
        return jsonify(config)

    @app.route('/api/track-view', methods=['POST']) 
    def track_view():
        try:
            analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
            analytics['visualizacoes_popup'] += 1
            salvar_json('analytics.json', analytics)
            print("--- Visualização de popup registrada com sucesso! ---")
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
            print("--- Clique em popup registrada com sucesso! ---")
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            print(f"!!! Erro ao registrar clique: {e}!!!")
            return jsonify({'status': 'error'}), 500
            
    @app.route('/webhook-pagbank', methods=['POST']) 
    def webhook_pagbank():
        print("!!!!!!!!!! ROTA WEBHOOK FOI ACESSADA!!!!!!!!!!")
        try:
            data = request.form.to_dict()
            notification_code = data.get('notificationCode')
            if not notification_code:
                return jsonify({'status': 'sem codigo'}), 400
            
            print(f"--- Consultando notificação: {notification_code} ---")
            url_consulta = f"https://ws.pagseguro.uol.com.br/v3/transactions/notifications/{notification_code}?email={current_app.config['PAGBANK_EMAIL']}&token={current_app.config['PAGBANK_TOKEN']}"
            headers = {'Accept': 'application/xml;charset=ISO-8859-1'}
            response = requests.get(url_consulta, headers=headers)
            response.raise_for_status()
            resposta_texto = response.text
            
            if '<reference>' in resposta_texto and ('<status>3</status>' in resposta_texto or '<status>4</status>' in resposta_texto):
                print("$$$$$$$$$$PAGAMENTO APROVADO!$$$$$$$$$$")
                root = ET.fromstring(resposta_texto)
                usuario_para_atualizar = root.find('reference').text
                
                print(f"--- Referência encontrada: {usuario_para_atualizar} ---")
                usuarios = carregar_json('users.json', {})
                if usuario_para_atualizar in usuarios:
                    print(f"--- Atualizando usuário: {usuario_para_atualizar} ---")
                    usuarios[usuario_para_atualizar]['status_assinatura'] = 'ativo'
                    data_expiracao = datetime.now() + timedelta(days=30)
                    usuarios[usuario_para_atualizar]['data_fim_assinatura'] = data_expiracao.strftime('%Y-%m-%d')
                    salvar_json('users.json', usuarios)
                    print("--- Usuário atualizado com sucesso! ---")
            else:
                print("--- Pagamento não aprovado ou sem referência na resposta. ---")
                
        except Exception as e:
            print(f"!!! Erro no webhook: {e}!!!")
        return jsonify({'status': 'recebido'}), 200

    # RETORNAMOS O APP CONSTRUÍDO NO FINAL DA FUNÇÃO
    return app

# A SEÇÃO ABAIXO NÃO É MAIS USADA PELO GUNICORN, MAS É ÚTIL PARA TESTES LOCAIS
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)