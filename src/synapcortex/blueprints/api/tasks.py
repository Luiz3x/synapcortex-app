# src.synapcortex/tasks.py
from .extensions import celery_app, db
from .models import AppUser, PaymentEvent, SubscriptionStatus

@celery_app.task(name="webhooks.process_stripe_event")
def process_stripe_event(event_db_id: int):
    """
    Tarefa assíncrona que processa a lógica de negócio de um evento do Stripe.
    """
    event_log = db.session.get(PaymentEvent, event_db_id)
    if not event_log or event_log.status != 'received':
        return # Evento não encontrado ou já processado

    event_log.status = 'processing'
    db.session.commit()

    try:
        event_type = event_log.event_type
        data_object = event_log.payload['data']['object']

        if event_type == 'checkout.session.completed':
            user_id = data_object.get('metadata', {}).get('synapcortex_user_id')
            user = db.session.get(AppUser, user_id)
            if user:
                user.subscription_status = SubscriptionStatus.ACTIVE
                user.stripe_subscription_id = data_object.get('subscription')
        
        elif event_type == 'customer.subscription.deleted':
            stripe_customer_id = data_object.get('customer')
            user = AppUser.query.filter_by(stripe_customer_id=stripe_customer_id).first()
            if user:
                user.subscription_status = SubscriptionStatus.CANCELED
        
        # ... (lógica para outros eventos como 'invoice.payment_failed')
        
        event_log.status = 'completed'
        db.session.commit()

    except Exception as e:
        event_log.status = 'failed'
        db.session.commit()
        # Logar o erro 'e' aqui
        raise