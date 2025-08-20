# synapcortex/services/user_service.py
# =================================================================================
# SERVIÇO DE USUÁRIO - CENTRALIZA A LÓGICA DE NEGÓCIO DO USUÁRIO
# =================================================================================

from ..extensions import db
from ..models import AppUser, SubscriptionStatus

def update_user_settings(user: AppUser, form_data: dict) -> None:
    """
    Atualiza as configurações de um usuário a partir de dados de um formulário.
    """
    try:
        settings = user.settings or {}
        # Mapeia os campos do formulário para as configurações
        settings['ativar_abandono'] = 'ativar_abandono' in form_data
        # Adicione outros campos aqui...
        
        user.settings = settings
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Propaga o erro para a rota poder tratá-lo
        raise e

def cancel_user_account(user: AppUser) -> None:
    """
    Executa os passos para cancelar a conta de um usuário.
    """
    try:
        user.subscription_status = SubscriptionStatus.CANCELED
        # Futuramente, adicione aqui a chamada para cancelar no Stripe
        # stripe.Subscription.delete(user.stripe_subscription_id)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e