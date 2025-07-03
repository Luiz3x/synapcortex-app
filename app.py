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
        
        usuarios[username] = {
            "email": f"{username}@exemplo.com", 
            "senha": generate_password_hash(password),
            "status_assinatura": "pendente", 
            "data_fim_assinatura": None
        }
        salvar_json('users.json', usuarios)
        
        # --- A VERDADEIRA MÁGICA DA AUTOMAÇÃO ---
        print(f"--- Iniciando criação de pedido para o usuário: {username} ---")
        url_api_pagbank = f"https://ws.pagseguro.uol.com.br/v2/checkout?email={PAGBANK_EMAIL}&token={PAGBANK_TOKEN}"
        
        headers = {"Content-Type": "application/xml; charset=ISO-8859-1"}
        
        dados_pedido_xml = f"""
        <checkout>
            <currency>BRL</currency>
            <reference>{username}</reference>
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
            
            root = ET.fromstring(response.content)
            checkout_code = root.find('code').text
            link_pagamento = f"https://pagseguro.uol.com.br/v2/checkout/payment.html?code={checkout_code}"
            
            print(f"--- Pedido criado com sucesso! Redirecionando para: {link_pagamento} ---")
            return redirect(link_pagamento)

        except requests.exceptions.RequestException as e:
            print(f"!!! Erro de comunicação com o PagBank: {e} !!!")
            return "Ocorreu um erro de comunicação com nosso processador de pagamentos."
        except ET.ParseError as e:
            print(f"!!! Erro ao ler a resposta do PagBank: {e} !!!")
            print(f"Resposta recebida: {response.text}")
            return "Ocorreu um erro ao processar a resposta do pagamento."

    return render_template('registrar.html')