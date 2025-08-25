# src.synapcortex/blueprints/payments/webhook_handlers.py
from flask import current_app

from ...extensions import db
from ...models import AppUser, SubscriptionStatus

def handle_checkout_session_completed(event: dict) -> tuple[dict, int]:
    """ Lida com a conclusão bem-sucedida de um checkout. """
    session = event['data']['object']
    user_id = session.get('metadata', {}).get('synapcortex_user_id')
    
    if not user_id:
        current_app.logger.error("Webhook 'checkout.session.completed' sem 'user_id'.")
        return {"error": "user_id faltando"}, 400

    user = db.session.get(AppUser, int(user_id))
    if user:
        user.subscription_status = SubscriptionStatus.ACTIVE
        user.stripe_subscription_id = session.get('subscription')
        db.session.commit()
        current_app.logger.info(f"Assinatura ativada para o usuário {user_id}.")
        # Aqui, poderíamos disparar uma tarefa para enviar um e-mail de boas-vindas.
        # ex: send_welcome_email.delay(user.id)
    
    return {"status": "success"}, 200

def handle_subscription_deleted(event: dict) -> tuple[dict, int]:
    """ Lida com uma assinatura cancelada. """
    subscription = event['data']['object']
    stripe_customer_id = subscription.get('customer')
    
    user = AppUser.query.filter_by(stripe_customer_id=stripe_customer_id).first()
    if user:
        user.subscription_status = SubscriptionStatus.CANCELED
        db.session.commit()
        current_app.logger.info(f"Assinatura cancelada para o usuário {user.id}.")

    return {"status": "success"}, 200

def handle_invoice_payment_failed(event: dict) -> tuple[dict, int]:
    """ Lida com uma falha no pagamento da renovação. """
    invoice = event['data']['object']
    stripe_customer_id = invoice.get('customer')

    user = AppUser.query.filter_by(stripe_customer_id=stripe_customer_id).first()
    if user:
        user.subscription_status = SubscriptionStatus.PAST_DUE
        db.session.commit()
        current_app.logger.warning(f"Pagamento de renovação FALHOU para o usuário {user.id}.")
        # Aqui, dispararíamos uma tarefa para notificar o cliente por e-mail.
        # ex: send_dunning_email.delay(user.id)
        
    return {"status": "success"}, 200

# Adicione outros handlers aqui...