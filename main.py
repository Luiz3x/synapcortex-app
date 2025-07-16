import os
import json
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app # current_app importado aqui
from werkzeug.security import generate_password_hash, check_password_hash

# =====================================================================
# FUNÇÕES DE AJUDA (Não mudam)
# =====================================================================
def carregar_json(nome_arquivo, dados_padrao):
    # Define o caminho para o nosso "cofre" no Render
    # O diretório 'data' agora será criado dentro do diretmo do projeto
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)

    # Se o arquivo não existir, cria-o com os dados padrão.
    # O diretório já terá sido garantido por create_app()
    if not os.path.exists(caminho_completo):
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    
    # Abre e retorna os dados do arquivo
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    # Define o caminho para o nosso "cofre" na Render
    # O diretório 'data' agora será criado dentro do diretmo do projeto
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    
    # Abre e salva os dados no arquivo
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
    # ATENÇÃO: Armazene as credenciais em app.config para que sejam acessíveis em todo o aplicativo
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
    
    app.config['PAGBANK_EMAIL'] = os.environ.get('PAGBANK_EMAIL')
    app.config['PAGBANK_SANDBOX_TOKEN'] = os.environ.get('PAGBANK_SANDBOX_TOKEN')
    app.config['PAGBANK_TOKEN'] = os.environ.get('PAGBANK_TOKEN') # Mantendo para o webhook
    app.config['PAGBANK_CLIENT_ID'] = os.environ.get('PAGBANK_CLIENT_ID') # Se for usar
    app.config['PAGBANK_CLIENT_SECRET'] = os.environ.get('PAGBANK_CLIENT_SECRET') # Se for usar

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
            # Coletando todos os dados do formulário
            fullname = request.form.get('fullname')
            cpf = request.form.get('cpf')
            ddd = request.form.get('ddd')
            phone = request.form.get('phone')
            username = request.form.get('username')
            password = request.form.get('password')
            
            usuarios = carregar_json('users.json', {}) # Carrega o JSON vazio ou existente
            if username in usuarios:
                return "Usuário já existe!"

            # Usaremos um e-mail de teste por enquanto, como na documentação
            email_comprador = f"cliente_{username}@sandbox.pagbank.com.br"

            usuarios[username] = {
                "email": email_comprador, 
                "senha": generate_password_hash(password),
                "status_assinatura": "pendente", 
                "data_fim_assinatura": None
            }
            salvar_json('users.json', usuarios)
            
            # --- A NOVA API EM AÇÃO ---
            print(f"--- Iniciando criação de pedido para o usuário: {username} via NOVA API ---")
            url_api_pagbank = "https://sandbox.api.pagseguro.com/checkouts"
            
            # Montamos os novos headers com as credenciais que você conseguiu
            headers = {
                "accept": "application/json",
                # ACESSANDO O TOKEN VIA current_app.config
                "Authorization": current_app.config['PAGBANK_SANDBOX_TOKEN'], 
                "Content-Type": "application/json"
            }
            
            # Montamos o corpo do pedido em JSON, como a documentação pede
            dados_pedido_json = {
                "reference_id": username,
                "customer": {
                    "name": fullname,
                    "email": email_comprador,
                    "tax_id": cpf,
                    "phones": [f"+55-{ddd}-{phone}"], # Use o DDD e o telefone real do formulário
                },
                "items": [{ 
                    "name": "Assinatura Mensal SynapCortex",
                    "quantity": 1,
                    "unit_amount": 1000, # Valor em centavos (ex: R$10,00)
                }],
                "notification_urls": [ 
                    "https://synapcortex-app.onrender.com/webhook-pagbank" # Substitua pelo seu domínio real
                ]
            }

            try:
                response = requests.post(url_api_pagbank, json=dados_pedido_json, headers=headers)
                response.raise_for_status()
                resposta_json = response.json()

                # A nova API retorna uma lista de links de pagamento
                if "links" in resposta_json:
                    link_pagamento = next((link['href'] for link in resposta_json['links'] if link['rel'] == 'PAY'), None)
                    if link_pagamento:
                        print(f"--- Pedido criado com sucesso! Redirecionando para: {link_pagamento} ---")
                        return redirect(link_pagamento)

                print(f"!!! Link de pagamento não encontrado na resposta: {resposta_json}!!!")
                return "Ocorreu um erro ao obter o link de pagamento."

            except requests.exceptions.RequestException as e:
                print(f"!!! Erro de comunicação com o PagBank: {e}!!!")
                print(f"!!! Resposta do servidor: {e.response.text if e.response else 'N/A'}!!!")
                return "Ocorreu um erro de comunicação com nosso processador de pagamentos."

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
            # Este link de pagamento parece ser para a API antiga ou um link fixo
            # Se você estiver usando a nova API para registrar, este link pode precisar ser atualizado
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
            # Este endpoint usa o PAGBANK_EMAIL e PAGBANK_TOKEN (o antigo)
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