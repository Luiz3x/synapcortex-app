# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 5.8 (Correção Definitiva da Criação de Usuário Demo)
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
    if not os.path.exists(caminho):
        return {}
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# --- [CORREÇÃO] LÓGICA DE CRIAÇÃO DO USUÁRIO DEMO ---
# Movida para o escopo global para garantir que seja executada quando o servidor iniciar
def inicializar_conta_demo():
    print(">>> Verificando/Criando conta de demonstração...")
    users = carregar_json(CAMINHO_USUARIOS)
    if 'demo@synapcortex.com' not in users:
        print(">>> Conta demo não encontrada. Criando agora...")
        users['demo@synapcortex.com'] = {
            'senha_hash': generate_password_hash('demo'),
            'nome_empresa': 'Loja de Demonstração',
            'api_key': 'chave_api_demo_123456',
            'data_registro': datetime.now().isoformat(),
            'status_assinatura': 'trial',
            'configuracoes': {
                'popup_titulo': 'Bem-vindo à Demo!',
                'popup_mensagem': 'Explore nosso painel. As alterações não são salvas.',
                'ativar_quarto_bem_vindo': True, 'msg_bem_vindo': 'Que bom te ver de novo!',
                'ativar_quarto_interessado': True, 'msg_interessado': 'Parece que você encontrou algo interessante!'
            }
        }
        salvar_json(CAMINHO_USUARIOS, users)
        print(">>> Conta demo criada com sucesso!")
    else:
        print(">>> Conta demo já existe.")

inicializar_conta_demo() # Executa a função na inicialização do app

# --- ROTAS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('password')
    usuarios = carregar_json(CAMINHO_USUARIOS)

    if email in usuarios and check_password_hash(usuarios[email].get('senha_hash', ''), senha):
        session['logged_in'] = True
        session['email'] = email
        return jsonify({'redirect_url': url_for('dashboard')})
    
    return jsonify({'message': 'E-mail ou senha inválidos.'}), 401

# (As outras rotas como /registrar, /logout, /dashboard continuam iguais...)
@app.route('/registrar', methods=['POST'])
def registrar():
    email = request.form.get('email')
    senha = request.form.get('password')
    nome_empresa = request.form.get('nome_empresa')
    usuarios = carregar_json(CAMINHO_USUARIOS)

    if email in usuarios:
        return jsonify({'message': 'Este e-mail já está cadastrado.'}), 400

    usuarios[email] = {
        'senha_hash': generate_password_hash(senha),
        'nome_empresa': nome_empresa,
        'data_registro': datetime.now().isoformat(),
        'api_key': secrets.token_hex(16),
        'status_assinatura': 'trial',
        'configuracoes': {}
    }
    salvar_json(CAMINHO_USUARIOS, usuarios)

    session['logged_in'] = True
    session['email'] = email
    return jsonify({'redirect_url': url_for('dashboard')})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('index'))
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    dados_usuario = usuarios.get(email_usuario)
    if not dados_usuario:
        session.clear(); return redirect(url_for('index'))
    return render_template('dashboard.html', usuario=dados_usuario, config=dados_usuario.get('configuracoes', {}))


@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    # LANTERNA DE DIAGNÓSTICO
    email_na_sessao = session.get('email')
    print("--- INICIANDO ROTA /salvar-configuracoes ---")
    print(f"EMAIL NA SESSÃO É: '{email_na_sessao}'")
    print("---------------------------------------------")

    if not email_na_sessao: return jsonify({'status': 'error', 'message': 'Acesso não autorizado.'}), 403

    if email_na_sessao == 'demo@synapcortex.com':
        return jsonify({'status': 'info', 'message': 'Na conta de demonstração, as alterações não são salvas.'}), 200
    
    usuarios = carregar_json(CAMINHO_USUARIOS)
    if email_na_sessao in usuarios:
        if 'configuracoes' not in usuarios[email_na_sessao]: usuarios[email_na_sessao]['configuracoes'] = {}
        for chave, valor in request.form.items():
            usuarios[email_na_sessao]['configuracoes'][chave] = True if valor == 'on' else valor
        checkboxes = ['ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        for check in checkboxes:
            if check not in request.form: usuarios[email_na_sessao]['configuracoes'][check] = False
        salvar_json(CAMINHO_USUARIOS, usuarios)
        return jsonify({'status': 'success', 'message': 'Configurações salvas!'}), 200

    return jsonify({'status': 'error', 'message': 'Usuário não encontrado.'}), 404

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key: return jsonify({'error': 'API Key não fornecida'}), 400
    usuarios = carregar_json(CAMINHO_USUARIOS)
    for email, dados in usuarios.items():
        if dados.get('api_key') == api_key:
            return jsonify(dados.get('configuracoes', {}))
    return jsonify({'error': 'API Key inválida'}), 404

# O bloco __main__ agora é usado apenas para testes locais
if __name__ == '__main__':
    app.run(debug=True, port=5001)