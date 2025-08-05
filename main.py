# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão com Modo de Demonstração Seguro
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
app.secret_key = secrets.token_hex(16) # Chave secreta para a sessão

# Configuração para servir arquivos estáticos em produção (Render)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# Habilita o CORS para a API, permitindo que outros sites a acessem
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- GERENCIAMENTO DE DADOS (JSON) ---
CAMINHO_USUARIOS = 'usuarios.json'

def carregar_json(caminho):
    if not os.path.exists(caminho):
        return {}
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# --- ROTAS DO SITE PRINCIPAL E AUTENTICAÇÃO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('password')
    usuarios = carregar_json(CAMINHO_USUARIOS)

    if email in usuarios and check_password_hash(usuarios[email]['senha_hash'], senha):
        session['logged_in'] = True
        session['email'] = email
        return jsonify({'redirect_url': url_for('dashboard')})
    
    return jsonify({'message': 'E-mail ou senha inválidos.'}), 401

@app.route('/registrar', methods=['POST'])
def registrar():
    email = request.form.get('email')
    senha = request.form.get('password')
    nome_empresa = request.form.get('nome_empresa')
    cnpj = request.form.get('cnpj')
    usuarios = carregar_json(CAMINHO_USUARIOS)

    if email in usuarios:
        return jsonify({'message': 'Este e-mail já está cadastrado.'}), 400

    usuarios[email] = {
        'senha_hash': generate_password_hash(senha),
        'nome_empresa': nome_empresa,
        'cnpj': cnpj,
        'data_registro': datetime.now().isoformat(),
        'api_key': secrets.token_hex(16),
        'status_assinatura': 'trial', # 'trial', 'ativo', 'pendente'
        'configuracoes': {
            'popup_titulo': 'Não vá embora!',
            'popup_mensagem': 'Temos uma oferta especial para você.',
            'ativar_quarto_bem_vindo': False,
            'msg_bem_vindo': '',
            'ativar_quarto_interessado': False,
            'msg_interessado': ''
        }
    }
    salvar_json(CAMINHO_USUARIOS, usuarios)

    session['logged_in'] = True
    session['email'] = email
    return jsonify({'redirect_url': url_for('dashboard')})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ROTAS DO PAINEL DO CLIENTE ---

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    dados_usuario = usuarios.get(email_usuario)

    if not dados_usuario:
        session.clear()
        return redirect(url_for('index'))

    # Lógica simples de expiração do Trial (30 dias)
    data_registro = datetime.fromisoformat(dados_usuario['data_registro'])
    dias_restantes = 30 - (datetime.now() - data_registro).days
    mensagem_status = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    if dias_restantes < 0:
        mensagem_status = "Seu período de avaliação terminou."
        # Aqui você pode adicionar a lógica para mudar o status para 'pendente'

    return render_template('dashboard.html', 
                           usuario=dados_usuario, 
                           config=dados_usuario.get('configuracoes', {}),
                           mensagem_status_assinatura=mensagem_status)

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    # ======================================================
    #               LANTERNA DE DIAGNÓSTICO
    # ======================================================
    email_na_sessao = session.get('email')
    print("--- INICIANDO ROTA /salvar-configuracoes ---")
    print(f"EMAIL NA SESSÃO É: '{email_na_sessao}'")
    print(f"O TIPO DO DADO É: {type(email_na_sessao)}")
    print(f"A comparação (email == 'demo@synapcortex.com') resulta em: {email_na_sessao == 'demo@synapcortex.com'}")
    print("---------------------------------------------")
    # ======================================================

    # O resto da lógica continua
    if not email_na_sessao:
        return jsonify({'status': 'error', 'message': 'Acesso não autorizado.'}), 403

    if email_na_sessao == 'demo@synapcortex.com':
        return jsonify({
            'status': 'info', 
            'message': 'Na conta de demonstração, as alterações não são salvas.'
        }), 200
    
    usuarios = carregar_json(CAMINHO_USUARIOS)
    if email_na_sessao in usuarios:
        if 'configuracoes' not in usuarios[email_na_sessao]:
            usuarios[email_na_sessao]['configuracoes'] = {}

        for chave, valor in request.form.items():
            if valor == 'on':
                usuarios[email_na_sessao]['configuracoes'][chave] = True
            else:
                usuarios[email_na_sessao]['configuracoes'][chave] = valor
        
        checkboxes = ['ativar_quarto_bem_vindo', 'ativar_quarto_interessado']
        for check in checkboxes:
            if check not in request.form:
                usuarios[email_na_sessao]['configuracoes'][check] = False
        
        salvar_json(CAMINHO_USUARIOS, usuarios)
        return jsonify({'status': 'success', 'message': 'Configurações salvas!'}), 200

    return jsonify({'status': 'error', 'message': 'Usuário não encontrado.'}), 404

# --- API PARA O SCRIPT ESPIÃO ---

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({'error': 'API Key não fornecida'}), 400

    usuarios = carregar_json(CAMINHO_USUARIOS)
    for email, dados in usuarios.items():
        if dados.get('api_key') == api_key:
            return jsonify(dados.get('configuracoes', {}))
    
    return jsonify({'error': 'API Key inválida'}), 404

# --- EXECUÇÃO DO APP ---
if __name__ == '__main__':
    # Cria uma conta demo se ela não existir
    users = carregar_json(CAMINHO_USUARIOS)
    if 'demo@synapcortex.com' not in users:
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
    
    app.run(debug=True, port=5001)