# =================================================================================
# SYNAPCORTEX - BLUEPRINT DO DASHBOARD (v5.0 - Arquitetura Enterprise Grade)
# =================================================================================

from flask import (
    Blueprint, render_template, request, jsonify, 
    current_app, url_for
)
from flask_login import login_required, current_user, logout_user
from pydantic import ValidationError

# Importa os serviços especializados que contêm a lógica de negócio
from .services import UserService # <-- ADICIONADO DE VOLTA

# Importa os schemas para validação e serialização de dados (Pydantic)
from .schemas import UserSettingsSchema

# --- CRIAÇÃO DO BLUEPRINT ---
# O blueprint atua como o maestro, orquestrando as requisições para os serviços.
dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    url_prefix='/dashboard',
    # O caminho aponta para a pasta de templates na raiz do projeto.
    # Ex: /templates/dashboard/home.html
    template_folder='../../../templates/dashboard'
)

# =================================================================================
# ROTAS DE RENDERIZAÇÃO DE PÁGINAS (Interface com o Frontend Moderno)
# =================================================================================
# As rotas de renderização são mantidas simples, pois o frontend (React/Vue/etc.)
# cuidará da maior parte da lógica de UI, consumindo nossa API.

@dashboard_bp.route('/home')
@login_required
def home():
    """Renderiza a página principal (a 'casca') do painel."""
    return render_template('home.html')

@dashboard_bp.route('/visitors')
@login_required
def visitors():
    """Renderiza a página do dossiê de visitantes."""
    return render_template('visitors.html')

@dashboard_bp.route('/settings')
@login_required
def settings():
    """Renderiza a página de configurações da conta."""
    return render_template('settings.html')

# =================================================================================
# ROTAS DE API (O Motor da SynapCortex)
# =================================================================================

@dashboard_bp.route('/api/v1/settings', methods=['PUT']) # Padrão RESTful: PUT para atualizar
@login_required
def save_settings_api():
    """
    Endpoint para ATUALIZAR as configurações do usuário.
    Valida os dados de entrada usando Pydantic antes de passá-los para o serviço.
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 'error', 'message': 'Requisição sem dados (JSON).'}), 400

        # 1. Valida e converte os dados com o schema Pydantic
        validated_data = UserSettingsSchema(**json_data)

        # 2. Passa os dados já validados para o serviço
        success, message = UserService.update_user_settings(
            user=current_user, 
            settings_data=validated_data.dict() # Converte para dicionário
        )

        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            # Erros de negócio (ex: e-mail já existe) tratados pelo serviço
            return jsonify({'status': 'error', 'message': message}), 422 # Unprocessable Entity

    except ValidationError as e:
        # Erro de validação dos dados de entrada (ex: e-mail inválido, campo faltando)
        current_app.logger.warning(f"API Falha de validação para {current_user.id}: {e.errors()}")
        return jsonify({'status': 'error', 'message': 'Dados inválidos.', 'details': e.errors()}), 400
        
    except Exception as e:
        # Erro genérico e inesperado no servidor
        current_app.logger.error(f"API Erro ao salvar config para {current_user.id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Ocorreu um erro interno no servidor.'}), 500

@dashboard_bp.route('/api/v1/account', methods=['DELETE']) # Padrão RESTful: DELETE para remover
@login_required
def cancel_account_api():
    """
    Endpoint para ENCERRAR a conta do usuário.
    A lógica de negócio (ex: cancelar assinatura, anonimizar dados) é encapsulada no serviço.
    """
    try:
        # A lógica mais complexa é encapsulada no serviço
        success, message = UserService.cancel_user_account(current_user)
        
        if not success:
            # Se o serviço retornar um erro (ex: não foi possível cancelar a assinatura)
            return jsonify({'status': 'error', 'message': message}), 422

        logout_user()
        
        # Resposta padronizada e informativa para a API
        return jsonify({
            'status': 'success', 
            'message': 'Conta encerrada com sucesso.',
            'data': {
                'redirect_url': url_for('auth.index', _external=True)
            }
        })
    except Exception as e:
        current_app.logger.error(f"API Erro ao cancelar conta para {current_user.id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Erro ao processar o encerramento da conta.'}), 500