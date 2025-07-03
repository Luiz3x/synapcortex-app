import sys
print("--- TESTANDO A IMPORTACAO DO APP.PY ---", file=sys.stderr)
# =====================================================================
# 1. IMPORTAÇÕES
# =====================================================================
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import requests # <--- Ferramenta para falar com a API
import xml.etree.ElementTree as ET # <--- Ferramenta para ler a resposta do PagBank
from datetime import datetime, timedelta

# =====================================================================
# 2. CONFIGURAÇÃO DO APP E CREDENCIAIS
# =====================================================================
app = Flask(__name__)
app.secret_key = 'chave-super-secreta-para-aisynapse-123'

# SUAS CREDENCIAIS - VERIFIQUE SE ESTÃO CORRETAS
PAGBANK_EMAIL = "grupoparceirao@gmail.com"
PAGBANK_TOKEN = "446b98d3-4db7-40ac-9a53-34de98bfdf3448d0e1d74ef58b28e808b89539974e053afc-624d-4284-808a-14e703c1e413"

# =====================================================================
# 3. FUNÇÕES DE AJUDA (Não mudam)
# =====================================================================
def carregar_json(nome_arquivo, dados_padrao):
    if not os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# =====================================================================
# 4. ROTAS DA APLICAÇÃO
# =====================================================================

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
        username = request.form.get('username')
        password = request.form.get('password')
        usuarios = carregar_json('users.json', {})

        if username in usuarios:
            return "Usuário já existe!"
        
        # Salva o usuário primeiro com status pendente
        usuarios[username] = {
            "email": f"{username}@exemplo.com",
            "senha": generate_password_hash(password),
            "status_assinatura": "pendente",
            "data_fim_assinatura": None
        }
        salvar_json('users.json', usuarios)
        
        # --- A NOVA MÁGICA COMEÇA AQUI ---
        # Redireciona para o link de pagamento simples, mas com a referência
        link_pagamento_base = "https://cobranca.pagbank.com/8eeb87d3-50bd-482f-a037-23b28fc42e7a"
        link_com_referencia = f"{link_pagamento_base}?referenceId={username}"
        
        print(f"--- Redirecionando usuário '{username}' para o pagamento ---")
        return redirect(link_com_referencia)
        
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
        link_base_pagamento = "https://cobranca.pagbank.com/8eeb87d3-50bd-482f-a037-23b28fc42e7a"
        link_com_referencia = f"{link_base_pagamento}?referenceId={username}"
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

# --- ROTA WEBHOOK ATUALIZADA PARA AUTOMAÇÃO TOTAL ---
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
        response.raise_for_status() # Isso vai gerar um erro se a consulta falhar
        resposta_texto = response.text
        
        # Verifica se o pagamento foi aprovado (status 3 ou 4)
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

# =====================================================================
# 5. "MOTOR DE ARRANQUE"
# =====================================================================
if __name__ == '__main__':
    app.run(port=5000, debug=True)