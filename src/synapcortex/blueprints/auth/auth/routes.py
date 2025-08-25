# src.synapcortex/blueprints/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required
from marshmallow import ValidationError

from .services import AuthService
from .schemas import RegisterSchema, LoginSchema
from ...models import AppUser

auth_bp = Blueprint('auth', __name__, template_folder='../../../templates')

@auth_bp.route('/')
def index():
    """ Rota para a nossa Landing Page. """
    return render_template('auth/index.html')

@auth_bp.route('/demo-login')
def demo_login():
    """ Realiza o login do usuário de demonstração pré-configurado. """
    current_app.logger.info("Tentativa de login de demonstração...")
    try:
        demo_email = current_app.config.get('DEMO_EMAIL')
        if not demo_email:
            current_app.logger.critical("FALHA DE CONFIGURAÇÃO: DEMO_EMAIL não configurado.")
            flash("A funcionalidade de demonstração está temporariamente indisponível.", "danger")
            return redirect(url_for('auth.index'))

        demo_user = AppUser.query.filter_by(email=demo_email).first()

        if not demo_user:
            current_app.logger.error(f"Usuário demo '{demo_email}' não encontrado. Execute 'flask admin create-demo-user'.")
            flash("Ocorreu um erro ao tentar acessar a demonstração.", "warning")
            return redirect(url_for('auth.index'))

        login_user(demo_user, remember=True)
        current_app.logger.info(f"Login de demonstração bem-sucedido para o usuário ID: {demo_user.id}.")
        return redirect(url_for('dashboard.home'))

    except Exception as e:
        current_app.logger.error(f"ERRO CRÍTICO na rota demo_login: {e}", exc_info=True)
        flash("Erro interno do servidor ao processar a demonstração.", "danger")
        return redirect(url_for('auth.index'))

# --- ROTAS DE API PARA O MODAL REACT ---
@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    # ... (código da API de registro que já aprovamos)
    pass # (Mantido como antes)

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    # ... (código da API de login que já aprovamos)
    pass # (Mantido como antes)

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    # ... (código da API de logout que já aprovamos)
    pass # (Mantido como antes)