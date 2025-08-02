import os
import json
import secrets
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__)
CORS(app)

# É CRUCIAL que você configure estas variáveis de ambiente na Render
app.secret_key = os.environ.get('SECRET_KEY', 'chave-super-secreta-para-desenvolvimento-local')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')

# --- GERENCIAMENTO DE DADOS (Apontando DIRETAMENTE para o Disco) ---

# O caminho do disco é o nosso diretório final. Não precisamos de subpastas.
diretorio_de_dados = '/data' 

CAMINHO_USUARIOS = os.path.join(diretorio_de_dados, "users.json")
# CAMINHO_ANALYTICS = os.path.join(diretorio_de_dados, "analytics.json") # Futura implementação

# A linha "if not os.path.exists..." foi REMOVIDA pois não criamos mais um novo diretório.

def carregar_json(caminho_arquivo, dados_padrao={}):
    """Carrega dados de um arquivo JSON, criando-o se não existir."""
    try:
        if not os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_padrao, f)
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return dados_padrao

def salvar_json(caminho_arquivo, dados):
    """Salva dados em um arquivo JSON."""
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ROTAS PRINCIPAIS E DE AUTENTICAÇÃO ---

@app.route('/')
def index():
    """Renderiza a página inicial."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Renderiza o painel de controle do usuário."""
    if 'email' not in session:
        return redirect(url_for('index'))

    email = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    user_data = usuarios.get(email)

    if not user_data:
        session.pop('email', None)
        return redirect(url_for('index'))
    
    # Lógica para verificar a validade da assinatura
    status_assinatura = user_data.get('status_assinatura', 'pendente')
    mensagem_status = "Sua assinatura está pendente."
    
    if status_assinatura == 'ativo':
        data_fim_str = user_data.get('data_fim_assinatura')
        if data_fim_str:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            if hoje > data_fim:
                user_data['status_assinatura'] = 'pendente'
                usuarios[email] = user_data
                salvar_json(CAMINHO_USUARIOS, usuarios)
                status_assinatura = 'pendente'
            else:
                dias_restantes = (data_fim - hoje).days
                mensagem_status = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."
    
    if status_assinatura == 'pendente':
        return render_template('pagamento_pendente.html', 
                               stripe_publishable_key=app.config['STRIPE_PUBLISHABLE_KEY_TEST'])

    return render_template('dashboard.html', 
                           config=user_data.get('configuracoes', {}),
                           mensagem_status_assinatura=mensagem_status)

@app.route('/login', methods=['POST'])
def login():
    """Processa a tentativa de login via AJAX."""
    email = request.form.get('email', '').lower()
    senha = request.form.get('password', '')
    
    usuarios = carregar_json(CAMINHO_USUARIOS)
    user_data = usuarios.get(email)

    if user_data and check_password_hash(user_data.get('senha', ''), senha):
        session['email'] = email
        return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
    
    return jsonify({'success': False, 'message': 'E-mail ou senha inválidos.'}), 401

@app.route('/registrar', methods=['POST'])
def registrar():
    """Processa um novo registro de usuário via AJAX."""
    email = request.form.get('email', '').lower()
    senha = request.form.get('password', '')
    nome_empresa = request.form.get('nome_empresa', '')
    cnpj = request.form.get('cnpj', '')

    if not all([email, senha, nome_empresa, cnpj]):
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'}), 400

    usuarios = carregar_json(CAMINHO_USUARIOS)

    if email in usuarios:
        return jsonify({'success': False, 'message': 'Este e-mail já está cadastrado.'}), 409
    
    # Criação da nova conta com período de teste de 30 dias
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=30)
    
    usuarios[email] = {
        "senha": generate_password_hash(senha), "cnpj": cnpj, "nome_empresa": nome_empresa,
        "status_assinatura": "ativo", "data_inicio_assinatura": data_inicio.strftime('%Y-%m-%d'),
        "data_fim_assinatura": data_fim.strftime('%Y-%m-%d'), "api_key": secrets.token_urlsafe(24),
        "configuracoes": {
            "popup_titulo": "Não vá embora!", "popup_mensagem": "Temos uma oferta especial para você.",
            "tatica_mobile": "foco", "ativar_quarto_bem_vindo": True, "ativar_quarto_interessado": True,
            "msg_bem_vindo": "Que bom te ver de volta!", "msg_interessado": "Parece que você encontrou algo interessante..."
        }
    }

    salvar_json(CAMINHO_USUARIOS, usuarios)
    session['email'] = email
    
    return jsonify({'success': True, 'redirect_url': url_for('dashboard')})

@app.route('/logout')
def logout():
    """Desloga o usuário."""
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    """Salva as configurações do painel."""
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    email = session['email']
    usuarios = carregar_json(CAMINHO_USUARIOS)
    
    if email not in usuarios:
         return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    for key, value in request.form.items():
        if key in usuarios[email]['configuracoes']:
            usuarios[email]['configuracoes'][key] = value

    salvar_json(usuarios)
    return jsonify({'success': True, 'message': 'Configurações salvas!'})

# --- ROTAS DE API ---

@app.route('/api/get-client-config')
def get_client_config():
    """Fornece os dados de configuração para o script espião."""
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({'error': 'Chave de API não fornecida'}), 400

    usuarios = carregar_json(CAMINHO_USUARIOS)
    for user_data in usuarios.values():
        if user_data.get('api_key') == api_key and user_data.get('status_assinatura') == 'ativo':
            return jsonify(user_data.get('configuracoes', {}))

    return jsonify({'error': 'Chave de API inválida ou conta inativa'}), 403

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    """Cria uma intenção de pagamento no Stripe."""
    try:
        # Preço fixo de R$ 99,90, convertido para centavos
        intent = stripe.PaymentIntent.create(
            amount=9990,
            currency='brl',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

# --- EXECUÇÃO ---
# =============================================================
# ROTA DE DEBUG TEMPORÁRIA - REMOVER DEPOIS
# =============================================================
@app.route('/debug-css')
def debug_css():
    """
    Esta rota serve para testar se o Flask consegue encontrar o arquivo CSS.
    Ela ignora o WhiteNoise e tenta entregar o arquivo diretamente.
    """
    from flask import send_from_directory
    
    try:
        # O caminho para a pasta 'static/css'
        css_dir = os.path.join(app.root_path, 'static', 'css')
        
        # O nome do arquivo que queremos
        filename = 'main_style.css'
        
        print(f"DEBUG: Tentando servir o arquivo '{filename}' do diretório '{css_dir}'")
        
        return send_from_directory(css_dir, filename)

    except Exception as e:
        print(f"DEBUG: Erro ao tentar servir o arquivo: {e}")
        return f"Ocorreu um erro ao tentar encontrar o arquivo: {e}", 500
# =============================================================
if __name__ == '__main__':
    # Bloco para rodar localmente. A Render usará Gunicorn/wsgi.py.
    app.run(host='0.0.0.0', port=5000, debug=True)