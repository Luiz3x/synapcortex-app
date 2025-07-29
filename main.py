# main.py - Versão com lógica para a nova Sala de Comando

import os
import json
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO E CONFIGURAÇÃO (sem alterações) ---
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
# ... (o resto das suas configurações do Stripe, etc.)

# >>> MUDANÇA: Vamos usar um único arquivo de dados para simplificar
diretorio_de_dados = "data"
CAMINHO_USUARIOS = os.path.join(diretorio_de_dados, "users.json")

if not os.path.exists(diretorio_de_dados):
    os.makedirs(diretorio_de_dados)

def carregar_usuarios():
    try:
        if not os.path.exists(CAMINHO_USUARIOS):
            with open(CAMINHO_USUARIOS, 'w') as f:
                json.dump({}, f)
        with open(CAMINHO_USUARIOS, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def salvar_usuarios(dados):
    with open(CAMINHO_USUARIOS, 'w') as f:
        json.dump(dados, f, indent=4)

# --- ROTAS DE AUTENTICAÇÃO (sem grandes alterações) ---
# As rotas /login, /registrar, /logout continuam praticamente as mesmas.
# Apenas a rota de registro agora cria uma sub-chave para as configurações.
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        # ... (toda a sua lógica de pegar email, senha, etc.)
        email = request.form.get('email').lower()
        password = request.form.get('password')
        # ...
        
        usuarios = carregar_usuarios()
        # ... (toda a sua lógica de verificação se o usuário já existe)
        
        # >>> MUDANÇA: Ao criar um novo usuário, já criamos a estrutura de configurações
        usuarios[email] = {
            'senha': generate_password_hash(password),
            # ... (outros campos: cnpj, nome_empresa, status_assinatura, etc.)
            'configuracoes': {
                'popup_titulo': 'Não vá embora!',
                'popup_mensagem': 'Temos uma oferta especial para você.',
                'tatica_mobile': 'foco',
                'ativar_quarto_bem_vindo': False,
                'ativar_quarto_interessado': False
            }
        }
        salvar_usuarios(usuarios)
        return redirect(url_for('login', message='Cadastro realizado com sucesso!'))
    return render_template('registrar.html')

# As outras rotas de autenticação (/login, /logout) não precisam de mudança.

# --- ROTA DO PAINEL DE CONTROLE (Atualizada) ---
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email_usuario = session['email']
    usuarios = carregar_usuarios()
    dados_usuario = usuarios.get(email_usuario)

    if not dados_usuario:
        session.clear()
        return redirect(url_for('login'))

    # ... (Sua lógica de verificação de status da assinatura continua aqui)
    
    # >>> MUDANÇA: Carregamos as configurações do usuário ou usamos valores padrão
    configuracoes_usuario = dados_usuario.get('configuracoes', {})

    # >>> MUDANÇA: Carregamos os dados para os insights (aqui ainda com exemplos)
    insights = {
        'visitantes_unicos': 1234,
        'taxa_recuperacao': '12%',
        'top_categoria': 'Camisetas'
    }

    return render_template(
        'dashboard.html',
        usuario=dados_usuario,
        config=configuracoes_usuario, # Passa o dicionário de configurações para o template
        insights=insights
        # ... (suas outras variáveis como mensagem_status_assinatura e dados do gráfico)
    )

# --- ROTA PARA SALVAR CONFIGURAÇÕES (Totalmente Reformulada) ---
@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email_usuario = session['email']
    usuarios = carregar_usuarios()
    
    if email_usuario not in usuarios:
        return redirect(url_for('login'))

    # >>> MUDANÇA: Capturamos todos os novos dados do formulário
    # Para checkboxes, se não estiverem marcados, não são enviados. Usamos .get()
    ativar_bem_vindo = request.form.get('ativar_quarto_bem_vindo') == 'on'
    ativar_interessado = request.form.get('ativar_quarto_interessado') == 'on'

    # >>> MUDANÇA: Atualizamos o dicionário de configurações do usuário
    usuarios[email_usuario]['configuracoes'] = {
        'popup_titulo': request.form.get('popup_titulo', ''),
        'popup_mensagem': request.form.get('popup_mensagem', ''),
        'tatica_mobile': request.form.get('tatica_mobile', 'foco'),
        'ativar_quarto_bem_vindo': ativar_bem_vindo,
        'ativar_quarto_interessado': ativar_interessado
    }
    
    salvar_usuarios(usuarios)
    
    return redirect(url_for('dashboard'))

# ... (o resto do seu main.py, como as rotas de API, pode continuar o mesmo por agora)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)