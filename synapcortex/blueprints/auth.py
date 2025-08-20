# =================================================================================
# SYNAPCORTEX - BLUEPRINT DE AUTENTICAÇÃO (v2.0)
# Ala responsável por todas as rotas públicas: index, login, registro e logout.
# =================================================================================

import secrets
from datetime import datetime, timedelta

from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app)
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from ..models import AppUser, SubscriptionStatus

TRIAL_DURATION_DAYS = 30
REACTIVATION_TRIAL_DAYS = 7

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard.home'))
    return render_template('index.html')

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
    session.permanent = True
    session['logged_in'] = True
    session['email'] = user.email
    current_app.logger.info(f"Login bem-sucedido para o usuário: {email}")
    next_url = session.pop('next', None)
    return redirect(next_url or url_for('dashboard.home'))

@auth_bp.route('/register', methods=['POST'])
def register():
    form = request.form
    email = form.get('email')
    password = form.get('password')
    company_id = form.get('company_id')
    required_fields = ['country', 'company_id', 'company_name', 'email', 'password']
    if not all(form.get(field) for field in required_fields):
        flash('Todos os campos são obrigatórios para o registro.', 'warning')
        return redirect(url_for('.index'))
    existing_user_by_email = AppUser.query.filter_by(email=email).first()
    if existing_user_by_email and existing_user_by_email.subscription_status != SubscriptionStatus.CANCELED:
        flash('Este e-mail já está em uso por uma conta ativa.', 'error')
        return redirect(url_for('.index'))
    try:
        user_to_reactivate = AppUser.query.filter_by(company_id=company_id, country=form.get('country')).first()
        if user_to_reactivate and user_to_reactivate.subscription_status in [SubscriptionStatus.CANCELED, SubscriptionStatus.EXPIRED_TRIAL]:
            user = user_to_reactivate
            user.email = email
            user.password_hash = generate_password_hash(password)
            user.company_name = form.get('company_name')
            user.subscription_status = SubscriptionStatus.TRIAL
            user.trial_end_date = datetime.utcnow() + timedelta(days=REACTIVATION_TRIAL_DAYS)
            flash(f'Que bom te ver de volta! Reativamos sua conta com mais {REACTIVATION_TRIAL_DAYS} dias de teste.', 'success')
        else:
            user = AppUser(
                country=form.get('country'),
                company_id=company_id, email=email,
                password_hash=generate_password_hash(password),
                company_name=form.get('company_name'),
                api_key=secrets.token_hex(16),
                trial_end_date=datetime.utcnow() + timedelta(days=TRIAL_DURATION_DAYS)
            )
            db.session.add(user)
            flash(f'Conta criada com sucesso! Você tem {TRIAL_DURATION_DAYS} dias de teste grátis.', 'success')
        db.session.commit()
        session['logged_in'] = True
        session['email'] = user.email
        current_app.logger.info(f"Nova conta registrada/reativada para o e-mail: {email}")
        return redirect(url_for('dashboard.home'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro inesperado no registro para {email}: {e}")
        flash('Ocorreu um erro inesperado. Nossa equipe foi notificada.', 'error')
        return redirect(url_for('.index'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta com segurança.', 'info')
    return redirect(url_for('.index'))

@auth_bp.route('/demo-login')
def demo_login():
    session.permanent = True
    session['logged_in'] = True
    session['email'] = 'demo@synapcortex.com'
    return redirect(url_for('dashboard.home'))