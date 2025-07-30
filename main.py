# main.py - Versão da Base Estável (Central de Ajuda Funcional)

import os
import json
import secrets
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')
CORS(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

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

@app.route('/')
def index(): return render_template('index.html')

# ... (Cole aqui as suas rotas /login e /registrar completas e funcionais) ...

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
        # ... (lógica de status da assinatura) ...
        dias_restantes = 30 # Exemplo
        mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    if status_assinatura == 'pendente': return render_template('pagamento_pendente.html', usuario=dados_usuario)
    
    insights_exemplo = {'visitantes_unicos': '1,234', 'taxa_recuperacao': '12%', 'top_categoria': 'Camisetas'}
    labels_grafico, dados_visualizacoes, dados_cliques = [], [], []
    
    return render_template(
        'dashboard.html', usuario=dados_usuario, config=dados_usuario.get('configuracoes', {}),
        insights=insights_exemplo, mensagem_status_assinatura=mensagem_status_assinatura,
        labels_do_grafico=labels_grafico, visualizacoes_do_grafico=dados_visualizacoes,
        cliques_do_grafico=dados_cliques
    )

# ... (Cole aqui o resto das suas rotas completas e funcionais) ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)