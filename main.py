# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 6.1 (com Lanterna de Diagnóstico no Login E no Cadastro)
# =================================================================================

import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = secrets.token_hex(16)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- GERENCIAMENTO DE DADOS (JSON) ---
CAMINHO_USUARIOS = 'usuarios.json'

def carregar_json(caminho):
    if not os.path.exists(caminho): return {}
    try:
        with open(caminho, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# --- LÓGICA DE CRIAÇÃO DO USUÁRIO DEMO ---
def inicializar_conta_demo():
    print(">>> Verificando/Criando conta de demonstração...")
    users = carregar_json(CAMINHO_USUARIOS)
    if 'demo@synapcortex.com' not in users:
        print(">>> Conta demo não encontrada. Criando agora...")
        users['demo@synapcortex.com'] = {
            'senha_hash': generate_password_hash('demo'), 'nome_empresa': 'Loja de Demonstração',
            'cnpj': '00000000000000', 'api_key': 'chave_api_demo_123456',
            'data_registro': datetime.now().isoformat(), 'status_assinatura': 'trial',
            'configuracoes': {}
        }
        salvar_json(CAMINHO_USUARIOS, users)
        print(">>> Conta demo criada com sucesso!")
    else:
        print(">>> Conta demo já existe.")

inicializar_conta_demo()

# --- ROTAS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # ... (código do login com a lanterna continua o mesmo)
    email = request.form.get('email'); senha = request.form.get('password'); usuarios = carregar_json(CAMINHO_USUARIOS)
    print("\n--- TENTATIVA DE LOGIN ---"); print(f"E-mail recebido: '{email}'")
    if email in usuarios:
        print(f"Usuário '{email}' ENCONTRADO."); senha_hash_armazenada = usuarios[email].get('senha_hash', ''); senha_correta = check_password_hash(senha_hash_armazenada, senha); print(f"A senha está correta? -> {senha_correta}")
        if senha_correta:
            print(">>> SUCESSO: Login autorizado."); session['logged_in'] = True; session['email'] = email; return jsonify({'redirect_url': url_for('dashboard')})
    else: print(f"Usuário '{email}' NÃO ENCONTRADO.")
    print(">>> FALHA: Login negado."); return jsonify({'message': 'E-mail ou senha inválidos.'}), 401

@app.route('/registrar', methods=['POST'])
def registrar():
    # --- LANTERNA DE DIAGNÓSTICO DO REGISTRO ---
    print("\n--- TENTATIVA DE CADASTRO ---")
    try:
        email = request.form.get('email')
        senha = request.form.get('password')
        nome_empresa = request.form.get('nome_empresa')
        cnpj = request.form.get('cnpj')
        
        print(f"Dados recebidos -> E-mail: {email}, Nome: {nome_empresa}, CNPJ: {cnpj}")

        usuarios = carregar_json(CAMINHO_USUARIOS)
        print("Arquivo de usuários carregado com sucesso.")

        if email in usuarios:
            print(f"ERRO: E-mail '{email}' já existe.")
            return jsonify({'message': 'Este e-mail já está cadastrado.'}), 400

        print("E-mail é novo. Criando novo usuário...")
        usuarios[email] = {
            'senha_hash': generate_password_hash(senha),
            'nome_empresa': nome_empresa,
            'cnpj': cnpj,
            'data_registro': datetime.now().isoformat(),
            'api_key': secrets.token_hex(16),
            'status_assinatura': 'trial',
            'configuracoes': {}
        }
        
        print("Preparando para salvar o novo usuário no arquivo JSON...")
        salvar_json(CAMINHO_USUARIOS, usuarios)
        print(">>> SUCESSO: Novo usuário salvo no arquivo JSON.")

        session['logged_in'] = True
        session['email'] = email
        print("Sessão criada. Redirecionando para o dashboard.")
        print("-----------------------------\n")
        return jsonify({'redirect_url': url_for('dashboard')})

    except Exception as e:
        print(f"!!!!!! ERRO INESPERADO NO CADASTRO: {e} !!!!!!")
        print("-----------------------------\n")
        return jsonify({'message': 'Ocorreu um erro interno no servidor.'}), 500


# (O resto das rotas, como /logout, /dashboard, etc., continuam iguais)
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('index'))
    email_usuario = session['email']; usuarios = carregar_json(CAMINHO_USUARIOS); dados_usuario = usuarios.get(email_usuario)
    if not dados_usuario: session.clear(); return redirect(url_for('index'))
    return render_template('dashboard.html', usuario=dados_usuario, config=dados_usuario.get('configuracoes', {}))
# (As rotas /salvar-configuracoes e /api/get-client-config também continuam as mesmas)
@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    email_na_sessao = session.get('email')
    if not email_na_sessao: return jsonify({'status': 'error', 'message': 'Acesso não autorizado.'}), 403
    if email_na_sessao == 'demo@synapcortex.com': return jsonify({'status': 'info', 'message': 'Na conta de demonstração, as alterações não são salvas.'}), 200
    usuarios = carregar_json(CAMINHO_USUARIOS)
    if email_na_sessao in usuarios:
        if 'configuracoes' not in usuarios[email_na_sessao]: usuarios[email_na_sessao]['configuracoes'] = {}
        for chave, valor in request.form.items(): usuarios[email_na_sessao]['configuracoes'][chave] = True if valor == 'on' else valor
        checkboxes = ['ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        for check in checkboxes:
            if check not in request.form: usuarios[email_na_sessao]['configuracoes'][check] = False
        salvar_json(CAMINHO_USUARIOS, usuarios)
        return jsonify({'status': 'success', 'message': 'Configurções salvas!'}), 200
    return jsonify({'status': 'error', 'message': 'Usuário não encontrado.'}), 404
@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key: return jsonify({'error': 'API Key não fornecida'}), 400
    usuarios = carregar_json(CAMINHO_USUARIOS)
    for email, dados in usuarios.items():
        if dados.get('api_key') == api_key: return jsonify(dados.get('configuracoes', {}))
    return jsonify({'error': 'API Key inválida'}), 404

# O bloco __main__ agora é usado apenas para testes locais
if __name__ == '__main__':
    app.run(debug=True, port=5001)