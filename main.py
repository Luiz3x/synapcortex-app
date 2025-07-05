import os
import json
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# =====================================================================
# FUNÇÕES DE AJUDA (Não mudam)
# =====================================================================
def carregar_json(nome_arquivo, dados_padrao):
    # Define o caminho para o nosso "cofre" na Render
    diretorio_de_dados = "/data"
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)

    if not os.path.exists(caminho_completo):
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    # Define o caminho para o nosso "cofre" na Render
    diretorio_de_dados = "/data"
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# =====================================================================
# A GRANDE MUDANÇA: A FÁBRICA DE APLICATIVOS (Application Factory)
# =====================================================================
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = 'chave-super-secreta-para-aisynapse-123'

    # SUAS CREDENCIAIS
    PAGBANK_EMAIL = "grupoparceirao@gmail.com"
    PAGBANK_TOKEN = "32ac7134-bf01-4740-a9e3-72983be5d00229e214d74df0b02d523ee864994e43c1a8c4-d445-40ab-8b62-3e2b88b8e429"

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
            # --- NOVOS CAMPOS SENDO COLETADOS DO FORMULÁRIO ---
            fullname = request.form.get('fullname')
            cpf = request.form.get('cpf')
            ddd = request.form.get('ddd')
            phone = request.form.get('phone')
            username = request.form.get('username')
            password = request.form.get('password')
            
            usuarios = carregar_json('users.json', {})

            if username in usuarios:
                return "Usuário já existe!"
            
            # O email do comprador será extraído do nome de usuário por enquanto
            # No futuro, podemos adicionar um campo de email separado
            email_comprador = f"{username}@exemplo.com"

            usuarios[username] = {
                "email": email_comprador, 
                "senha": generate_password_hash(password),
                "status_assinatura": "pendente", 
                "data_fim_assinatura": None
            }
            salvar_json('users.json', usuarios)
            
            print(f"--- Iniciando criação de pedido para o usuário: {username} ---")
            url_api_pagbank = f"https://ws.sandbox.pagseguro.uol.com.br/v2/checkout?email={PAGBANK_EMAIL}&token={PAGBANK_TOKEN}"
            
            headers = {"Content-Type": "application/xml; charset=ISO-8859-1"}
            
            # --- XML AGORA INCLUI OS DADOS DO COMPRADOR (SENDER) ---
            dados_pedido_xml = f"""
            <checkout>
                <currency>BRL</currency>
                <reference>{username}</reference>
                <sender>
                    <name>{fullname}</name>
                    <email>{email_comprador}</email>
                    <phone>
                        <areaCode>{ddd}</areaCode>
                        <number>{phone}</number>
                    </phone>
                    <documents>
                        <document>
                            <type>CPF</type>
                            <value>{cpf}</value>
                        </document>
                    </documents>
                </sender>
                <items>
                    <item>
                        <id>0001</id>
                        <description>Assinatura Mensal Aisynapse</description>
                        <amount>50.00</amount>
                        <quantity>1</quantity>
                    </item>
                </items>
            </checkout>
            """
            
            try:
                response = requests.post(url_api_pagbank, headers=headers, data=dados_pedido_xml.encode('ISO-8859-1'))
                response.raise_for_status()
                
                # Adicionamos uma verificação extra da resposta
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    checkout_code = root.find('code').text
                    link_pagamento = f"https://pagseguro.uol.com.br/v2/checkout/payment.html?code={checkout_code}"
                    
                    print(f"--- Pedido criado com sucesso! Redirecionando para: {link_pagamento} ---")
                    return redirect(link_pagamento)
                else:
                    print(f"!!! PagBank retornou um erro inesperado: {response.text} !!!")
                    return "Ocorreu um erro ao criar seu pedido de pagamento. Tente novamente."

            except requests.exceptions.RequestException as e:
                print(f"!!! Erro de comunicação com o PagBank: {e} !!!")
                return "Ocorreu um erro de comunicação com nosso processador de pagamentos."
            except ET.ParseError as e:
                print(f"!!! Erro ao ler a resposta do PagBank: {e} !!!")
                print(f"Resposta recebida: {response.text}")
                return "Ocorreu um erro ao processar a resposta do pagamento."

        return render_template('registrar.html')

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
            link_pagamento_base = "https://cobranca.pagbank.com/8eeb87d3-50bd-482f-a037-23b28fc42e7a"
            link_com_referencia = f"{link_pagamento_base}?referenceId={username}"
            return render_template('pagamento_pendente.html', link_de_pagamento=link_com_referencia)

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
            print(f"!!! Erro ao registrar visualização: {e} !!!")
            return jsonify({'status': 'error'}), 500

    @app.route('/api/track-click', methods=['POST'])
    def track_click():
        try:
            analytics = carregar_json('analytics.json', {"visualizacoes_popup": 0, "cliques_popup": 0})
            analytics['cliques_popup'] += 1
            salvar_json('analytics.json', analytics)
            print("--- Clique em popup registrado com sucesso! ---")
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            print(f"!!! Erro ao registrar clique: {e} !!!")
            return jsonify({'status': 'error'}), 500
            
    @app.route('/webhook-pagbank', methods=['POST'])
    def webhook_pagbank():
        print("!!!!!!!!!! ROTA WEBHOOK FOI ACESSADA !!!!!!!!!!")
        try:
            data = request.form.to_dict()
            notification_code = data.get('notificationCode')
            if not notification_code:
                return jsonify({'status': 'sem codigo'}), 400
            
            print(f"--- Consultando notificação: {notification_code} ---")
            url_consulta = f"https://ws.pagseguro.uol.com.br/v3/transactions/notifications/{notification_code}?email={PAGBANK_EMAIL}&token={PAGBANK_TOKEN}"
            headers = {'Accept': 'application/xml;charset=ISO-8859-1'}
            response = requests.get(url_consulta, headers=headers)
            response.raise_for_status()
            resposta_texto = response.text
            
            if '<reference>' in resposta_texto and ('<status>3</status>' in resposta_texto or '<status>4</status>' in resposta_texto):
                print("$$$$$$$$$$ PAGAMENTO APROVADO! $$$$$$$$$$")
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
            print(f"!!! Erro no webhook: {e} !!!")
        return jsonify({'status': 'recebido'}), 200

    # RETORNAMOS O APP CONSTRUÍDO NO FINAL DA FUNÇÃO
    return app

# A SEÇÃO ABAIXO NÃO É MAIS USADA PELO GUNICORN, MAS É ÚTIL PARA TESTES LOCAIS
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)