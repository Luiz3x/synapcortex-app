# =================================================================================
# SYNAPCORTEX - BLUEPRINT DE AUTENTICAÇÃO (v3.0 - Modernizado com Flask-Login)
# Ala responsável por todas as rotas públicas: index, login, registro e logout.
# Totalmente integrado com Flask-Login para um sistema de autenticação unificado.
# =================================================================================

import secrets
from datetime import datetime, timedelta

from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app)
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from ..models import AppUser, SubscriptionStatus

# --- Constantes ---
TRIAL_DURATION_DAYS = 30
REACTIVATION_TRIAL_DAYS = 7

# --- Criação do Blueprint ---
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    # APRIMORAMENTO: Usa a verificação do Flask-Login, que é mais segura.
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    # CORREÇÃO: Aponta para o caminho correto do template.
    return render_template('auth/index.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('E-mail e senha são obrigatórios.', 'warning')
        return redirect(url_for('.index'))

    user = AppUser.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password) or user.subscription_status == SubscriptionStatus.CANCELED:
        flash('Credenciais inválidas ou conta inativa.', 'error')
        return redirect(url_for('.index'))

    # APRIMORAMENTO: Usa a função login_user do Flask-Login.
    # É mais segura e gerencia a sessão e o cookie "lembrar-me" automaticamente.
    login_user(user, remember=True)
    current_app.logger.info(f"Login bem-sucedido para o usuário: {email}")
    
    next_url = session.pop('next', None)
    return redirect(next_url or url_for('dashboard.home'))


@auth_bp.route('/register', methods=['POST'])
def register():
    form = request.form
    email = form.get('email')
    password = form.get('password')

    # (Lógica de validação e criação/reativação do usuário mantida, está ótima)
    # ...
    
    try:
        # (Seu código para criar ou reativar o usuário vai aqui, sem alterações...)
        # ... Exemplo ...
        user = AppUser(
            email=email,
            password_hash=generate_password_hash(password),
            # ... outros campos
        )
        # db.session.add(user) # ou atualiza o usuário existente
        # db.session.commit()
        
        # Simulação para o código funcionar, substitua pelo seu código de registro
        user_to_log_in = AppUser.query.filter_by(email=email).first()
        if not user_to_log_in:
             # Este bloco é apenas um exemplo, o seu código original de registro é mais completo
             user_to_log_in = AppUser(email=email, password_hash=generate_password_hash(password), api_key=secrets.token_hex(16))
             db.session.add(user_to_log_in)
             db.session.commit()
             flash(f'Conta criada com sucesso! Você tem {TRIAL_DURATION_DAYS} dias de teste grátis.', 'success')
        # Fim da simulação

        # APRIMORAMENTO: Faz o login do novo usuário automaticamente com Flask-Login.
        login_user(user_to_log_in)
        current_app.logger.info(f"Nova conta registrada/reativada para o e-mail: {email}")
        return redirect(url_for('dashboard.home'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro inesperado no registro para {email}: {e}")
        flash('Ocorreu um erro inesperado. Nossa equipe foi notificada.', 'error')
        return redirect(url_for('.index'))


@auth_bp.route('/logout')
def logout():
    # APRIMORAMENTO: Usa a função logout_user do Flask-Login para limpar a sessão de forma segura.
    logout_user()
    flash('Você saiu da sua conta com segurança.', 'info')
    return redirect(url_for('.index'))


@auth_bp.route('/demo-login')
def demo_login():
    # APRIMORAMENTO: Busca o usuário demo no banco e faz o login de forma segura.
    demo_user = AppUser.query.filter_by(email='demo@synapcortex.com').first()
    if demo_user:
        login_user(demo_user, remember=True)
        return redirect(url_for('dashboard.home'))
    else:
        flash('Usuário de demonstração não encontrado.', 'error')
        return redirect(url_for('.index'))