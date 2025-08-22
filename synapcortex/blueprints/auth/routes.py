# synapcortex/blueprints/auth/routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from marshmallow import ValidationError

from .services import AuthService
from .schemas import RegisterSchema, LoginSchema
# from ...extensions import limiter # Para o Rate Limiting

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
# @limiter.limit("5 per minute")
def register():
    """ Endpoint da API para registrar novos usuários. """
    try:
        data = RegisterSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"status": "error", "errors": err.messages}), 400

    user = AuthService.register_user(data)

    if user is None:
        return jsonify({"status": "error", "errors": {"email": ["Este e-mail já está em uso."]}}), 409

    login_user(user, remember=True)
    return jsonify({
        "status": "success",
        "message": "Conta criada com sucesso!",
        "data": {"redirect_url": "/dashboard"}
    }), 201

@auth_bp.route('/login', methods=['POST'])
# @limiter.limit("10 per minute")
def login():
    """ Endpoint da API para autenticar usuários. """
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"status": "error", "errors": err.messages}), 400

    user = AuthService.verify_credentials(data['email'], data['password'])

    if user:
        login_user(user, remember=True)
        return jsonify({
            "status": "success",
            "message": "Login bem-sucedido!",
            "data": {"redirect_url": "/dashboard"}
        }), 200
    
    return jsonify({"status": "error", "errors": {"general": ["Credenciais inválidas."]}}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """ Endpoint da API para fazer logout. """
    logout_user()
    return jsonify({"status": "success", "message": "Você foi desconectado com sucesso."}), 200

@auth_bp.route('/session')
@login_required
def get_session():
    """ Endpoint para verificar se o usuário tem uma sessão ativa. """
    return jsonify({"status": "success", "is_authenticated": True}), 200