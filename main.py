# main.py - Versão 3.5 (Completa e Sincronizada, com cálculo de insights reais)

import os
import json
import secrets
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__, static_folder='static')

# >>> INÍCIO DA MUDANÇA <<<
# Configuração explícita da WhiteNoise para garantir que ela sirva a pasta /static
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')
# >>> FIM DA MUDANÇA <<<

app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
# ... (o resto das configurações)
CORS(app)
# A linha antiga da WhiteNoise que estava aqui foi removida.
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

# --- FUNÇÃO DE CÁLCULO DE INSIGHTS ---
def calcular_insights(dados_analytics):
    total_visualizacoes = 0
    total_cliques = 0
    hoje = datetime.now()
    for i in range(30):
        data_corrente = hoje - timedelta(days=i)
        data_chave = data_corrente.strftime('%Y-%m-%d')
        dados_do_dia = dados_analytics.get(data_chave, {})
        total_visualizacoes += dados_do_dia.get('visualizacoes', 0)
        total_cliques += dados_do_dia.get('cliques', 0)
    if total_visualizacoes == 0:
        taxa_conversao = "0.00%"
    else:
        taxa_conversao = f"{(total_cliques / total_visualizacoes) * 100:.2f}%"
    return {
        'popups_exibidos': total_visualizacoes,
        'clientes_recuperados': total_cliques,
        'taxa_conversao': taxa_conversao
    }

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
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if user_data and check_password_hash(user_data.get('senha', ''), password):
            session['logged_in'] = True
            session['email'] = email
            if is_ajax: return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            message = 'E-mail ou senha incorretos.'
            if is_ajax: return jsonify({'success': False, 'message': message}), 401
            return render_template('login.html', error=message)
    return render_template('login.html', message=request.args.get('message'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if not cnpj or not cnpj.isdigit() or len(cnpj) != 14:
            message = 'CNPJ inválido. Por favor, insira 14 números.'
            if is_ajax: return jsonify({'success': False, 'message': message}), 400
            return render_template('registrar.html', error=message)
        usuarios = carregar_json(CAMINHO_USUARIOS)
        if email in usuarios:
            message = 'Este e-mail já está cadastrado.'
            if is_ajax: return jsonify({'success': False, 'message': message}), 409
            return render_template('registrar.html', error=message)
        for user_data in usuarios.values():
            if user_data.get('cnpj') == cnpj:
                message = 'Este CNPJ já possui um cadastro.'
                if is_ajax: return jsonify({'success': False, 'message': message}), 409
                return render_template('registrar.html', error=message)
        hashed_password = generate_password_hash(password)
        data_inicio = datetime.now()
        data_fim = data_inicio + timedelta(days=30)
        api_key = secrets.token_urlsafe(24)
        usuarios[email] = {
            'senha': hashed_password, 'cnpj': cnpj, 'nome_empresa': nome_empresa,
            'status_assinatura': 'ativo', 'data_inicio_assinatura': data_inicio.strftime('%Y-%m-%d'),
            'data_fim_assinatura': data_fim.strftime('%Y-%m-%d'), 'api_key': api_key,
            'configuracoes': {
                'popup_titulo': 'Não vá embora!', 'popup_mensagem': 'Temos uma oferta especial para você.',
                'tatica_mobile': 'foco', 'ativar_quarto_bem_vindo': False,
                'ativar_quarto_interessado': False, 'msg_bem_vindo': '', 'msg_interessado': ''
            }
        }
        salvar_json(CAMINHO_USUARIOS, usuarios)
        if is_ajax: return jsonify({'success': True, 'redirect_url': url_for('login', message='Cadastro realizado com sucesso!')})
        return redirect(url_for('login', message='Cadastro realizado com sucesso!'))
    return render_template('registrar.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('login'))
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    dados_usuario = usuarios.get(email_usuario)
    if not dados_usuario:
        session.clear(); return redirect(url_for('login'))
    if 'api_key' not in dados_usuario or not dados_usuario['api_key']:
        dados_usuario['api_key'] = secrets.token_urlsafe(24)
        usuarios[email_usuario] = dados_usuario
        salvar_json(CAMINHO_USUARIOS, usuarios)
    status_assinatura = dados_usuario.get('status_assinatura', 'pendente')
    mensagem_status_assinatura = "Sua assinatura está pendente."
    if status_assinatura == 'ativo':
        data_fim_str = dados_usuario.get('data_fim_assinatura')
        if data_fim_str:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            if hoje > data_fim:
                dados_usuario['status_assinatura'] = 'pendente'; salvar_json(CAMINHO_USUARIOS, usuarios); status_assinatura = 'pendente'
            else:
                dias_restantes = (data_fim - hoje).days
                mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    if status_assinatura == 'pendente': return render_template('pagamento_pendente.html', usuario=dados_usuario)
    analytics_data = carregar_json(CAMINHO_ANALYTICS)
    insights_reais = calcular_insights(analytics_data)
    labels_grafico, dados_visualizacoes, dados_cliques = [], [], []
    return render_template(
        'dashboard.html', usuario=dados_usuario, config=dados_usuario.get('configuracoes', {}),
        insights=insights_reais, mensagem_status_assinatura=mensagem_status_assinatura,
        labels_do_grafico=labels_grafico, visualizacoes_do_grafico=dados_visualizacoes,
        cliques_do_grafico=dados_cliques
    )

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session: return redirect(url_for('login'))
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    if email_usuario not in usuarios: return redirect(url_for('login'))
    ativar_bem_vindo = request.form.get('ativar_quarto_bem_vindo') == 'on'
    ativar_interessado = request.form.get('ativar_quarto_interessado') == 'on'
    configuracoes_atuais = usuarios[email_usuario].get('configuracoes', {})
    configuracoes_atuais.update({
        'popup_titulo': request.form.get('popup_titulo', ''), 'popup_mensagem': request.form.get('popup_mensagem', ''),
        'tatica_mobile': request.form.get('tatica_mobile', 'foco'),
        'ativar_quarto_bem_vindo': ativar_bem_vindo, 'ativar_quarto_interessado': ativar_interessado,
        'msg_bem_vindo': request.form.get('msg_bem_vindo', ''), 'msg_interessado': request.form.get('msg_interessado', '')
    })
    usuarios[email_usuario]['configuracoes'] = configuracoes_atuais
    salvar_json(CAMINHO_USUARIOS, usuarios)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROTAS DE API PARA O SPY.JS ---

@app.route('/api/get-client-config')
def get_client_config():
    api_key_recebida = request.args.get('key')
    if not api_key_recebida: return jsonify({'error': 'Chave de API não fornecida.'}), 401
    usuarios = carregar_json(CAMINHO_USUARIOS)
    for usuario in usuarios.values():
        if usuario.get('api_key') == api_key_recebida:
            return jsonify(usuario.get('configuracoes', {}))
    return jsonify({'error': 'Chave de API inválida.'}), 403

@app.route('/api/track-view', methods=['POST']) 
def track_view():
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    analytics = carregar_json(CAMINHO_ANALYTICS); analytics.setdefault(hoje_str, {"visualizacoes": 0, "cliques": 0})
    analytics[hoje_str]['visualizacoes'] += 1; salvar_json(CAMINHO_ANALYTICS, analytics)
    return jsonify({'status': 'success'}), 200

@app.route('/api/track-click', methods=['POST']) 
def track_click():
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    analytics = carregar_json(CAMINHO_ANALYTICS); analytics.setdefault(hoje_str, {"visualizacoes": 0, "cliques": 0})
    analytics[hoje_str]['cliques'] += 1; salvar_json(CAMINHO_ANALYTICS, analytics)
    return jsonify({'status': 'success'}), 200

# --- EXECUÇÃO ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)