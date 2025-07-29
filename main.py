# main.py - Versão 3.3 (Completa, com salvamento das mensagens personalizadas)

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
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
# ... (o resto das suas configurações continua igual) ...

# --- GERENCIAMENTO DE DADOS ---
diretorio_de_dados = "data"
CAMINHO_USUARIOS = os.path.join(diretorio_de_dados, "users.json")
# ... (o resto das suas variáveis de caminho e a função de criar diretório)

def carregar_json(caminho_arquivo, dados_padrao={}):
    # ... (a função carregar_json continua igual)
def salvar_json(caminho_arquivo, dados):
    # ... (a função salvar_json continua igual)

# --- ROTAS PRINCIPAIS ---

# (A rota '/' e '/login' continuam as mesmas)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        # ... (coleta e validação de dados continua a mesma)
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')

        hashed_password = generate_password_hash(password)
        data_inicio = datetime.now()
        data_fim = data_inicio + timedelta(days=30)
        api_key = secrets.token_urlsafe(24)
        
        usuarios = carregar_json(CAMINHO_USUARIOS)
        usuarios[email] = {
            'senha': hashed_password, 'cnpj': cnpj, 'nome_empresa': nome_empresa,
            'status_assinatura': 'ativo', 'data_inicio_assinatura': data_inicio.strftime('%Y-%m-%d'),
            'data_fim_assinatura': data_fim.strftime('%Y-%m-%d'), 'api_key': api_key,
            'configuracoes': {
                'popup_titulo': 'Não vá embora!', 'popup_mensagem': 'Temos uma oferta especial para você.',
                'tatica_mobile': 'foco', 'ativar_quarto_bem_vindo': False,
                'ativar_quarto_interessado': False,
                'msg_bem_vindo': '', # >>> MUDANÇA: Campo padrão para nova mensagem
                'msg_interessado': ''  # >>> MUDANÇA: Campo padrão para nova mensagem
            }
        }
        salvar_json(CAMINHO_USUARIOS, usuarios)

        # ... (o resto da lógica de resposta ajax/redirect continua a mesma)
    return render_template('registrar.html')

# (A rota '/dashboard' continua a mesma, ela já está pronta para receber os dados)

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session: return redirect(url_for('login'))
    email_usuario = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    if email_usuario not in usuarios: return redirect(url_for('login'))

    ativar_bem_vindo = request.form.get('ativar_quarto_bem_vindo') == 'on'
    ativar_interessado = request.form.get('ativar_quarto_interessado') == 'on'
    
    configuracoes_atuais = usuarios[email_usuario].get('configuracoes', {})
    
    # >>> INÍCIO DA MUDANÇA <<<
    # Atualiza o dicionário com os novos campos de mensagem
    configuracoes_atuais.update({
        'popup_titulo': request.form.get('popup_titulo', ''), 
        'popup_mensagem': request.form.get('popup_mensagem', ''),
        'tatica_mobile': request.form.get('tatica_mobile', 'foco'),
        'ativar_quarto_bem_vindo': ativar_bem_vindo, 
        'ativar_quarto_interessado': ativar_interessado,
        'msg_bem_vindo': request.form.get('msg_bem_vindo', ''),
        'msg_interessado': request.form.get('msg_interessado', '')
    })
    # >>> FIM DA MUDANÇA <<<

    usuarios[email_usuario]['configuracoes'] = configuracoes_atuais
    
    salvar_json(CAMINHO_USUARIOS, usuarios)
    return redirect(url_for('dashboard'))

# (A rota '/logout' e as rotas de API continuam as mesmas)

# --- EXECUÇÃO ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)