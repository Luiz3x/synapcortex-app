# main.py - Versão 3.0 (Consolidada e Completa)

import os
import json
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')
CORS(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# --- GERENCIAMENTO DE DADOS ---
diretorio_de_dados = "data"
CAMINHO_USUARIOS = os.path.join(diretorio_de_dados, "users.json")
CAMINHO_ANALYTICS = os.path.join(diretorio_de_dados, "analytics.json")

if not os.path.exists(diretorio_de_dados):
    os.makedirs(diretorio_de_dados)

def carregar_json(caminho_arquivo, dados_padrao={}):
    try:
        if not os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_padrao, f)
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return dados_padrao

def salvar_json(caminho_arquivo, dados):
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        usuarios = carregar_json(CAMINHO_USUARIOS)
        user_data = usuarios.get(email)
        if user_data and check_password_hash(user_data.get('senha', ''), password):
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='E-mail ou senha incorretos.')
    return render_template('login.html', message=request.args.get('message'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')
        usuarios = carregar_json(CAMINHO_USUARIOS)

        if email in usuarios:
            return render_template('registrar.html', error='Este e-mail já está cadastrado.')
        
        for user_data in usuarios.values():
            if user_data.get('cnpj') == cnpj:
                return render_template('registrar.html', error='Este CNPJ já possui um cadastro.')

        hashed_password = generate_password_hash(password)
        data_inicio = datetime.now()
        data_fim = data_inicio + timedelta(days=30)
        
        usuarios[email] = {
            'senha': hashed_password,
            'cnpj': cnpj,
            'nome_empresa': nome_empresa,
            'status_assinatura': 'ativo',
            'data_inicio_assinatura': data_inicio.strftime('%Y-%m-%d'),
            'data_fim_assinatura': data_fim.strftime('%Y-%m-%d'),
            'configuracoes': {
                'popup_titulo': 'Não vá embora!',
                'popup_mensagem': 'Temos uma oferta especial para você.',
                'tatica_mobile': 'foco',
                'ativar_quarto_bem_vindo': False,
                'ativar_quarto_interessado': False
            }
        }
        salvar_json(CAMINHO_USUARIOS, usuarios)
        return redirect(url_for('login', message='Cadastro realizado com sucesso!'))
    return render_template('registrar.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    dados_usuario = usuarios.get(email_usuario)

    if not dados_usuario:
        session.clear()
        return redirect(url_for('login'))

    # Lógica de status de assinatura
    status_assinatura = dados_usuario.get('status_assinatura', 'pendente')
    mensagem_status_assinatura = "Sua assinatura está pendente."
    if status_assinatura == 'ativo':
        data_fim_str = dados_usuario.get('data_fim_assinatura')
        if data_fim_str:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            if hoje > data_fim:
                dados_usuario['status_assinatura'] = 'pendente'
                salvar_json(CAMINHO_USUARIOS, usuarios)
                status_assinatura = 'pendente'
            else:
                dias_restantes = (data_fim - hoje).days
                mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    
    if status_assinatura == 'pendente':
        return render_template('pagamento_pendente.html', usuario=dados_usuario)

    # Lógica dos Insights e Gráfico
    insights = {'visitantes_unicos': 1234, 'taxa_recuperacao': '12%', 'top_categoria': 'Camisetas'}
    labels_grafico, dados_visualizacoes, dados_cliques = [], [], [] # Adicione sua lógica de gráfico aqui

    return render_template(
        'dashboard.html',
        usuario=dados_usuario,
        config=dados_usuario.get('configuracoes', {}),
        insights=insights,
        mensagem_status_assinatura=mensagem_status_assinatura,
        labels_do_grafico=labels_grafico,
        visualizacoes_do_grafico=dados_visualizacoes,
        cliques_do_grafico=dados_cliques
    )

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    
    if email_usuario not in usuarios:
        return redirect(url_for('login'))

    ativar_bem_vindo = request.form.get('ativar_quarto_bem_vindo') == 'on'
    ativar_interessado = request.form.get('ativar_quarto_interessado') == 'on'
    
    configuracoes_atuais = usuarios[email_usuario].get('configuracoes', {})
    configuracoes_atuais.update({
        'popup_titulo': request.form.get('popup_titulo', ''),
        'popup_mensagem': request.form.get('popup_mensagem', ''),
        'tatica_mobile': request.form.get('tatica_mobile', 'foco'),
        'ativar_quarto_bem_vindo': ativar_bem_vindo,
        'ativar_quarto_interessado': ativar_interessado
    })
    usuarios[email_usuario]['configuracoes'] = configuracoes_atuais
    
    salvar_json(CAMINHO_USUARIOS, usuarios)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROTAS DE API (devem ser adicionadas/revisadas depois) ---

# ... Suas rotas /api/get-config, /api/track-view, etc. ...

# --- EXECUÇÃO ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)