import os
import json
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app 
from werkzeug.security import generate_password_hash, check_password_hash # Importações corretas

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
    import stripe # Importa a biblioteca do Stripe (garante que esteja no escopo correto)
    stripe.api_key = app.config['STRIPE_SECRET_KEY_TEST'] # Define a chave secreta do Stripe para a biblioteca
    # ====================================

    # AGORA, TODAS AS ROTAS SÃO REGISTRADAS DENTRO DA FÁBRICA
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        message = request.args.get('message') # Para exibir mensagens de sucesso do registro
        if request.method == 'POST':
            email = request.form.get('email').lower() # Coleta o email (agora é o identificador)
            password = request.form.get('password')
            
            usuarios = carregar_json('users.json', {}) 
            user_data = usuarios.get(email) # Busca pelo email
            
            # Usa check_password_hash do Werkzeug
            if user_data and check_password_hash(user_data['senha'], password):
                session['logged_in'] = True # Usar uma flag booleana é bom
                session['email'] = email    # Armazena o email na sessão
                return redirect(url_for('dashboard'))
            else:
                message = 'E-mail ou senha incorretos.'
        return render_template('login.html', message=message)

    # ... (código anterior do app.py) ...

    @app.route('/registrar', methods=['GET', 'POST'])
    def registrar():
        if request.method == 'POST':
            # Coletar dados do formulário
            email = request.form.get('email').lower() # E-mail será o identificador principal
            password = request.form.get('password')
            cnpj = request.form.get('cnpj') # Novo campo para CNPJ
            nome_empresa = request.form.get('nome_empresa', '') # Novo campo opcional para nome da empresa

            usuarios = carregar_json('users.json', {}) 

            # 1. Verificar se o e-mail já está cadastrado
            if email in usuarios:
                return render_template('registrar.html', error='Este e-mail já está cadastrado. Tente fazer login ou use outro e-mail.')

            # 2. Verificar se o CNPJ já está cadastrado (prevenção de abuso de trial)
            # Percorre os valores (dados de usuário) do dicionário 'usuarios'
            for user_email, user_data in usuarios.items(): # Itera sobre os itens para pegar o email associado
                if user_data.get('cnpj') == cnpj:
                    return render_template('registrar.html', error='Este CNPJ já possui um cadastro. Entre em contato para mais informações.')

            # Hash da senha usando generate_password_hash do Werkzeug
            hashed_password = generate_password_hash(password)

            # 3. Definir o mês grátis: status 'ativo' e data de expiração
            data_inicio_assinatura = datetime.now()
            data_fim_assinatura = data_inicio_assinatura + timedelta(days=30) # Mês grátis

            # Criar novo usuário com a nova estrutura, usando email como chave
            usuarios[email] = {
                'senha': hashed_password,
                'cnpj': cnpj,
                'nome_empresa': nome_empresa,
                'status_assinatura': 'ativo', # Ativado para o período de teste
                'data_inicio_assinatura': data_inicio_assinatura.strftime('%Y-%m-%d'),
                'data_fim_assinatura': data_fim_assinatura.strftime('%Y-%m-%d')
            }
            salvar_json('users.json', usuarios)
            
            print(f"--- Usuário {email} registrado com sucesso! Mês grátis ativado. Redirecionando para login ---")
            return redirect(url_for('login', message='Cadastro realizado com sucesso! Aproveite seu mês grátis.')) 
        return render_template('registrar.html')

    # --- NOVA ROTA: Criar PaymentIntent do Stripe ---
    @app.route('/create-payment-intent', methods=['POST'])
    def create_payment_intent():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Usuário não logado'}), 401

        email_usuario = session.get('email') # Pega o email da sessão
        # Busca o valor da assinatura do seu plano. Por simplicidade, valor fixo em centavos.
        # R$ 29,90 = 2990 centavos. Ajuste para o valor real da sua assinatura.
        amount_in_cents = 2990 

        try:
            # Cria um PaymentIntent no Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='brl', # Moeda brasileira
                metadata={'user_email': email_usuario}, # Para identificar o usuário no Stripe com o email
                payment_method_types=['card'], # Aceita pagamento com cartão
            )
            # Retorna o client_secret para o frontend
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
        session.pop('logged_in', None)
        session.pop('email', None)
        return redirect(url_for('login', error='Sua sessão expirou ou usuário não encontrado.'))

    analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
    config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})

    # NOVO: Lógica de verificação de expiração do trial e mensagens
    status_assinatura = dados_usuario.get('status_assinatura', 'pendente')
    data_fim_str = dados_usuario.get('data_fim_assinatura')
    mensagem_status_assinatura = ""
    dias_restantes = None # Inicializa como None

    if status_assinatura == 'ativo' and data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        hoje = datetime.now()

        if hoje > data_fim:
            # Assinatura expirou
            dados_usuario['status_assinatura'] = 'pendente'
            salvar_json('users.json', usuarios) # Salva a atualização
            status_assinatura = 'pendente' # Atualiza a variável local
            print(f"--- Assinatura de {email_usuario} expirada e atualizada para 'pendente' ---")
            mensagem_status_assinatura = "Sua avaliação gratuita expirou. Por favor, renove sua assinatura para manter o acesso."
        else:
            # Assinatura ainda ativa, calcula dias restantes
            dias_restantes = (data_fim - hoje).days
            if dias_restantes <= 7: # Avisa se faltam 7 dias ou menos
                mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s). Renove agora para não perder o acesso!"
            else:
                mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    elif status_assinatura == 'pendente':
        mensagem_status_assinatura = "Sua assinatura está pendente. Por favor, realize o pagamento para ativar seu acesso."
    # FIM DA LÓGICA DE VERIFICAÇÃO E MENSAGENS

    if status_assinatura == 'ativo':
        return render_template('dashboard.html', 
                               usuario=dados_usuario, 
                               analytics=analytics, 
                               config=config,
                               mensagem_status_assinatura=mensagem_status_assinatura, # Passa a mensagem
                               dias_restantes=dias_restantes # Passa os dias restantes
                              )
    else:
        # Se a assinatura estiver pendente (ou expirou), redireciona para a página de pagamento
        return render_template('pagamento_pendente.html', 
                               stripe_publishable_key=current_app.config['STRIPE_PUBLISHABLE_KEY_TEST'],
                               mensagem_status_assinatura=mensagem_status_assinatura # Passa a mensagem para a tela de pagamento também
                              )

# ... (restante do código do app.py) ...

    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        session.pop('email', None) # Remove o email da sessão
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
            # ATENÇÃO: Verifique se essa URL está correta para seu ambiente PagBank (sandbox/produção)
            url_consulta = f"https://ws.pagseguro.uol.com.br/v3/transactions/notifications/{notification_code}?email={current_app.config['PAGBANK_EMAIL']}&token={current_app.config['PAGBANK_TOKEN']}"
            headers = {'Accept': 'application/xml;charset=ISO-8859-1'}
            response = requests.get(url_consulta, headers=headers)
            response.raise_for_status()
            resposta_texto = response.text
            
            if '<reference>' in resposta_texto and ('<status>3</status>' in resposta_texto or '<status>4</status>' in resposta_texto):
                print("$$$$$$$$$$PAGAMENTO APROVADO!$$$$$$$$$$")
                root = ET.fromstring(resposta_texto)
                # A 'reference' deve ser o EMAIL do usuário para corresponder à chave no users.json
                email_para_atualizar = root.find('reference').text 
                
                print(f"--- Referência encontrada: {email_para_atualizar} ---")
                usuarios = carregar_json('users.json', {})
                if email_para_atualizar in usuarios:
                    print(f"--- Atualizando usuário: {email_para_atualizar} ---")
                    usuarios[email_para_atualizar]['status_assinatura'] = 'ativo'
                    # Ao renovar, adiciona mais 30 dias à data atual (ou à data de fim, se quiser acumular)
                    data_expiracao = datetime.now() + timedelta(days=30) 
                    usuarios[email_para_atualizar]['data_fim_assinatura'] = data_expiracao.strftime('%Y-%m-%d')
                    salvar_json('users.json', usuarios)
                    print("--- Usuário atualizado com sucesso! ---")
                else:
                    print(f"--- Usuário com referência '{email_para_atualizar}' não encontrado no JSON. ---")
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