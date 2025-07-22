import os
import json
from flask_cors import CORS
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app 
from werkzeug.security import generate_password_hash, check_password_hash
from whitenoise import WhiteNoise # Importa a biblioteca

# ... (Suas funções carregar_json e salvar_json continuam as mesmas) ...
def carregar_json(nome_arquivo, dados_padrao):
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    if not os.path.exists(caminho_completo):
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, indent=4)
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    diretorio_de_dados = os.path.join(os.getcwd(), "data")
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)


def create_app():
    app = Flask(__name__)
    
    # <<< ALTERAÇÃO FINAL E DEFINITIVA >>>
    # Simplificando a inicialização do WhiteNoise para máxima compatibilidade.
    # Ele agora usará o 'static_folder' padrão do Flask.
    app.wsgi_app = WhiteNoise(app.wsgi_app)
    
    CORS(app)
    
    # ... (o resto do seu código, configurações, rotas, etc., continua exatamente o mesmo) ...

    # Garante que o diretório /data exista
    diretorio_de_dados = os.path.join(os.getcwd(), "data") 
    if not os.path.exists(diretorio_de_dados):
        os.makedirs(diretorio_de_dados)
    
    # Configurações e credenciais
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
    app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
    app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
    import stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY_TEST']

    # --- REGISTRO DAS ROTAS ---
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # ... (código da rota de login)
        message = request.args.get('message')
        if request.method == 'POST':
            email = request.form.get('email').lower()
            password = request.form.get('password')
            usuarios = carregar_json('users.json', {}) 
            user_data = usuarios.get(email)
            if user_data and check_password_hash(user_data['senha'], password):
                session['logged_in'] = True
                session['email'] = email
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
                return redirect(url_for('dashboard'))
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'E-mail ou senha incorretos.'}), 401
                message = 'E-mail ou senha incorretos.'
        return render_template('login.html', message=message)


    @app.route('/registrar', methods=['GET', 'POST'])
    def registrar():
        # ... (código da rota de registro)
        if request.method == 'POST':
            email = request.form.get('email').lower()
            password = request.form.get('password')
            cnpj = request.form.get('cnpj')
            nome_empresa = request.form.get('nome_empresa', '')
            usuarios = carregar_json('users.json', {}) 
            if email in usuarios:
                return jsonify({'success': False, 'message': 'Este e-mail já está cadastrado. Tente fazer login.'}), 409
            for user_data in usuarios.values():
                if user_data.get('cnpj') == cnpj:
                    return jsonify({'success': False, 'message': 'Este CNPJ já possui um cadastro. Entre em contato.'}), 409
            hashed_password = generate_password_hash(password)
            data_inicio_assinatura = datetime.now()
            data_fim_assinatura = data_inicio_assinatura + timedelta(days=30)
            usuarios[email] = {
                'senha': hashed_password, 'cnpj': cnpj, 'nome_empresa': nome_empresa,
                'status_assinatura': 'ativo',
                'data_inicio_assinatura': data_inicio_assinatura.strftime('%Y-%m-%d'),
                'data_fim_assinatura': data_fim_assinatura.strftime('%Y-%m-%d')
            }
            salvar_json('users.json', usuarios)
            return jsonify({'success': True, 'redirect_url': url_for('login', message='Cadastro realizado com sucesso! Aproveite seu mês grátis.')})
        return render_template('registrar.html')


    @app.route('/dashboard')
    def dashboard():
        # ... (código da rota do dashboard)
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        email_usuario = session.get('email')
        usuarios = carregar_json('users.json', {})
        dados_usuario = usuarios.get(email_usuario)
        if not dados_usuario:
            session.clear()
            return redirect(url_for('login', error='Sua sessão expirou ou usuário não encontrado.'))
        status_assinatura = dados_usuario.get('status_assinatura', 'pendente')
        data_fim_str = dados_usuario.get('data_fim_assinatura')
        mensagem_status_assinatura = ""
        dias_restantes = None
        if status_assinatura == 'ativo' and data_fim_str:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            if hoje > data_fim:
                dados_usuario['status_assinatura'] = 'pendente'
                salvar_json('users.json', usuarios)
                status_assinatura = 'pendente'
                mensagem_status_assinatura = "Sua avaliação gratuita expirou. Por favor, renove sua assinatura."
            else:
                dias_restantes = (data_fim - hoje).days
                mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
        elif status_assinatura == 'pendente':
            mensagem_status_assinatura = "Sua assinatura está pendente. Realize o pagamento para ativar."
        if status_assinatura == 'ativo':
            return render_template('dashboard.html', 
                                   usuario=dados_usuario, 
                                   analytics=carregar_json('analytics.json', {}), 
                                   config=carregar_json('config_popup.json', {}),
                                   mensagem_status_assinatura=mensagem_status_assinatura,
                                   dias_restantes=dias_restantes)
        else:
            return render_template('pagamento_pendente.html', 
                                   stripe_publishable_key=current_app.config['STRIPE_PUBLISHABLE_KEY_TEST'],
                                   usuario=dados_usuario,
                                   mensagem_status_assinatura=mensagem_status_assinatura)

    # ... (outras rotas como salvar_configuracoes, logout, create_payment_intent, etc., continuam iguais)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)