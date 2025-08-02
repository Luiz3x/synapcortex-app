import os
import secrets
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
app = Flask(__name__)
CORS(app)

# Carrega as chaves das variáveis de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY_TEST'] = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
app.config['STRIPE_SECRET_KEY_TEST'] = os.environ.get('STRIPE_SECRET_KEY_TEST')
stripe.api_key = app.config.get('STRIPE_SECRET_KEY_TEST')

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Pega a "chave do cofre" que guardamos na Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DO BANCO DE DADOS (A ESTRUTURA DO NOSSO "COFRE") ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    nome_empresa = db.Column(db.String(150))
    status_assinatura = db.Column(db.String(50), default='ativo')
    data_inicio_assinatura = db.Column(db.DateTime(timezone=True), server_default=func.now())
    data_fim_assinatura = db.Column(db.DateTime(timezone=True))
    api_key = db.Column(db.String(100), unique=True, default=lambda: secrets.token_urlsafe(24))
    
    # Configurações agora são colunas individuais para facilitar o acesso
    popup_titulo = db.Column(db.String(100), default="Não vá embora!")
    popup_mensagem = db.Column(db.String(255), default="Temos uma oferta especial para você.")
    ativar_quarto_bem_vindo = db.Column(db.Boolean, default=True)
    msg_bem_vindo = db.Column(db.String(255), default="Que bom te ver de volta!")
    ativar_quarto_interessado = db.Column(db.Boolean, default=True)
    msg_interessado = db.Column(db.String(255), default="Parece que você encontrou algo interessante...")

# --- ROTAS DA APLICAÇÃO (AGORA USANDO O BANCO DE DADOS) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('index'))

    user = User.query.filter_by(email=session['email']).first()

    if not user:
        session.clear()
        return redirect(url_for('index'))
    
    # Lógica de verificação da assinatura
    if user.status_assinatura == 'ativo' and datetime.now().date() > user.data_fim_assinatura.date():
        user.status_assinatura = 'pendente'
        db.session.commit()
    
    if user.status_assinatura == 'pendente':
        return render_template('pagamento_pendente.html', 
                               stripe_publishable_key=app.config['STRIPE_PUBLISHABLE_KEY_TEST'])

    dias_restantes = (user.data_fim_assinatura.date() - datetime.now().date()).days
    mensagem_status = f"Sua avaliação gratuita termina em {dias_restantes} dia(s)."

    # Criamos um dicionário 'config' para manter a compatibilidade com o template
    config = {
        'popup_titulo': user.popup_titulo,
        'popup_mensagem': user.popup_mensagem
    }

    return render_template('dashboard.html', config=config, mensagem_status_assinatura=mensagem_status)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').lower()
    senha = request.form.get('password', '')
    
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.senha, senha):
        session['email'] = user.email
        return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
    
    return jsonify({'success': False, 'message': 'E-mail ou senha inválidos.'}), 401

@app.route('/registrar', methods=['POST'])
def registrar():
    email = request.form.get('email', '').lower()
    senha = request.form.get('password', '')
    nome_empresa = request.form.get('nome_empresa', '')
    cnpj = request.form.get('cnpj', '')

    if not all([email, senha, nome_empresa, cnpj]):
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Este e-mail já está cadastrado.'}), 409

    if User.query.filter_by(cnpj=cnpj).first():
        return jsonify({'success': False, 'message': 'Este CNPJ já está cadastrado.'}), 409

    novo_usuario = User(
        email=email,
        senha=generate_password_hash(senha),
        nome_empresa=nome_empresa,
        cnpj=cnpj,
        data_fim_assinatura=datetime.now() + timedelta(days=30)
    )
    
    db.session.add(novo_usuario)
    db.session.commit()
    
    session['email'] = novo_usuario.email
    return jsonify({'success': True, 'redirect_url': url_for('dashboard')})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/salvar-configuracoes', methods=['POST'])
def salvar_configuracoes():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    user = User.query.filter_by(email=session['email']).first()
    
    if not user:
         return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    user.popup_titulo = request.form.get('popup_titulo')
    user.popup_mensagem = request.form.get('popup_mensagem')
    # Adicionar outras configurações aqui se necessário no futuro
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Configurações salvas!'})

@app.route('/api/get-client-config')
def get_client_config():
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({'error': 'Chave de API não fornecida'}), 400

    user = User.query.filter_by(api_key=api_key).first()

    if user and user.status_assinatura == 'ativo':
        config = {
            "popup_titulo": user.popup_titulo,
            "popup_mensagem": user.popup_mensagem,
            "ativar_quarto_bem_vindo": user.ativar_quarto_bem_vindo,
            "msg_bem_vindo": user.msg_bem_vindo,
            "ativar_quarto_interessado": user.ativar_quarto_interessado,
            "msg_interessado": user.msg_interessado,
        }
        return jsonify(config)

    return jsonify({'error': 'Chave de API inválida ou conta inativa'}), 403

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        intent = stripe.PaymentIntent.create(
            amount=9990, currency='brl',
            automatic_payment_methods={'enabled': True}
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Bloco para criar as tabelas no banco de dados na primeira vez
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)