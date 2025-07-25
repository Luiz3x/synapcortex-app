# --- Importações Essenciais ---
import os
import json
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
from flask_cors import CORS

# --- INICIALIZAÇÃO DO APP FLASK ---
app = Flask(__name__, static_folder='static')

# --- CONFIGURAÇÕES DO APLICATIVO ---
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-synapcortex-padrao')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')

# Configura o Stripe globalmente para a aplicação iniciar corretamente
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')

# --- MIDDLEWARE (Bloco Único e Correto) ---
CORS(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')


# --- GERENCIAMENTO DE DIRETÓRIO DE DADOS ---
diretorio_de_dados = os.path.join(os.getcwd(), "data")
if not os.path.exists(diretorio_de_dados):
    os.makedirs(diretorio_de_dados)

# --- FUNÇÕES AUXILIARES PARA MANIPULAÇÃO DE JSON ---
def carregar_json(nome_arquivo, dados_padrao):
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    try:
        if not os.path.exists(caminho_completo):
            with open(caminho_completo, 'w', encoding='utf-8') as f:
                json.dump(dados_padrao, f, indent=4)
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return dados_padrao

def salvar_json(nome_arquivo, dados):
    caminho_completo = os.path.join(diretorio_de_dados, nome_arquivo)
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ROTAS PRINCIPAIS DO APLICATIVO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        usuarios = carregar_json('users.json', {})
        user_data = usuarios.get(email)
        if user_data and check_password_hash(user_data.get('senha', ''), password):
            session['logged_in'] = True
            session['email'] = email
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
            else:
                return redirect(url_for('dashboard'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'E-mail ou senha incorretos.'}), 401
            else:
                return render_template('login.html', error='E-mail ou senha incorretos.')
    message = request.args.get('message')
    return render_template('login.html', message=message)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')
        usuarios = carregar_json('users.json', {})
        if email in usuarios:
            message = 'Este e-mail já está cadastrado.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': message}), 409
            return render_template('registrar.html', error=message)
        for user_data in usuarios.values():
            if user_data.get('cnpj') == cnpj:
                message = 'Este CNPJ já possui um cadastro.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': message}), 409
                return render_template('registrar.html', error=message)
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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'redirect_url': url_for('login', message='Cadastro realizado com sucesso!')})
        # Linha que estava cortada, agora completa
        return redirect(url_for('login', message='Cadastro realizado com sucesso!'))
    return render_template('registrar.html')

@app.route('/test_css')
def test_css_route():
    return render_template('test_css.html')
    
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email_usuario = session.get('email')
    usuarios = carregar_json('users.json', {})
    dados_usuario = usuarios.get(email_usuario)

    if not dados_usuario:
        session.clear()
        return redirect(url_for('login', error='Sua sessão expirou.'))

    # Lógica de status da assinatura (continua a mesma)
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
            mensagem_status_assinatura = "Sua avaliação gratuita expirou."
        else:
            dias_restantes = (data_fim - hoje).days
            mensagem_status_assinatura = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    elif status_assinatura == 'pendente':
        mensagem_status_assinatura = "Sua assinatura está pendente. Regularize para continuar."
    
    # Renderiza a página correta baseada no status
    if status_assinatura == 'ativo':
        # --- LÓGICA DO GRÁFICO REAL ---
        analytics_por_dia = carregar_json('analytics.json', {})
        
        # Prepara as listas para os últimos 7 dias
        labels_grafico = []
        dados_visualizacoes = []
        dados_cliques = []
        
        hoje = datetime.now()
        for i in range(7):
            # Pega a data dos últimos 7 dias, começando por hoje e voltando para trás
            data_corrente = hoje - timedelta(days=i)
            # Formata a data como "dd/mm" para os rótulos do gráfico
            labels_grafico.append(data_corrente.strftime('%d/%m'))
            # Formata a data como "YYYY-MM-DD" para buscar no JSON
            data_chave = data_corrente.strftime('%Y-%m-%d')
            
            # Pega os dados do dia, ou 0 se o dia não tiver registro
            dados_do_dia = analytics_por_dia.get(data_chave, {"visualizacoes": 0, "cliques": 0})
            dados_visualizacoes.append(dados_do_dia.get('visualizacoes', 0))
            dados_cliques.append(dados_do_dia.get('cliques', 0))
            
        # Inverte as listas para o gráfico mostrar do dia mais antigo para o mais novo
        labels_grafico.reverse()
        dados_visualizacoes.reverse()
        dados_cliques.reverse()

        config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
        
        return render_template('dashboard.html', 
                               usuario=dados_usuario, 
                               config=config,
                               mensagem_status_assinatura=mensagem_status_assinatura,
                               dias_restantes=dias_restantes,
                               # Enviando os dados do gráfico para a página
                               labels_do_grafico=labels_grafico,
                               visualizacoes_do_grafico=dados_visualizacoes,
                               cliques_do_grafico=dados_cliques)
    else: # Status 'pendente'
        return render_template('pagamento_pendente.html', 
                               stripe_publishable_key=app.config.get('STRIPE_PUBLISHABLE_KEY_TEST'),
                               usuario=dados_usuario,
                               mensagem_status_assinatura=mensagem_status_assinatura)
                               
@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    novo_titulo = request.form.get('popup_titulo')
    nova_mensagem = request.form.get('popup_mensagem')
    config_atual = carregar_json('config_popup.json', {})
    config_atual['titulo'] = novo_titulo
    config_atual['mensagem'] = nova_mensagem
    salvar_json('config_popup.json', config_atual)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROTAS DE API ---

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    if 'logged_in' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    if not stripe.api_key:
        return jsonify(error={'message': 'Chave do Stripe não configurada no servidor.'}), 500
    email_usuario = session.get('email')
    amount_in_cents = 2990
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents, 
            currency='brl',
            metadata={'user_email': email_usuario},
            payment_method_types=['card'],
        )
        return jsonify(clientSecret=intent.client_secret)
    except Exception as e:
        return jsonify(error={'message': str(e)}), 400

@app.route('/api/get-config')
def get_config():
    config = carregar_json('config_popup.json', {"titulo": "", "mensagem": ""})
    return jsonify(config)

@app.route('/api/track-view', methods=['POST']) 
def track_view():
    try:
        hoje_str = datetime.now().strftime('%Y-%m-%d')
        analytics = carregar_json('analytics.json', {})
        if hoje_str not in analytics:
            analytics[hoje_str] = {"visualizacoes": 0, "cliques": 0}
        analytics[hoje_str]['visualizacoes'] += 1
        salvar_json('analytics.json', analytics)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/track-click', methods=['POST']) 
def track_click():
    try:
        hoje_str = datetime.now().strftime('%Y-%m-%d')
        analytics = carregar_json('analytics.json', {})
        if hoje_str not in analytics:
            analytics[hoje_str] = {"visualizacoes": 0, "cliques": 0}
        analytics[hoje_str]['cliques'] += 1
        salvar_json('analytics.json', analytics)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Bloco de Execução para Ambiente Local ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)