# synapcortex/blueprints/payments/services.py
import os
import stripe
from flask import url_for, current_app
from typing import List, Dict

from ...models import AppUser
from ...extensions import db

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripeService:
    """ Encapsula a lógica de negócios avançada do Stripe. """

    @staticmethod
    def get_or_create_customer(user: AppUser, force_update: bool = False) -> stripe.Customer:
        """ Busca, cria ou atualiza um cliente no Stripe, garantindo a sincronia. """
        customer = None
        if user.stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                if customer.get('deleted'): customer = None
            except stripe.error.InvalidRequestError:
                customer = None

        if customer is None:
            customer = stripe.Customer.create(
                email=user.email, name=user.company_name, metadata={'synapcortex_user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        elif force_update or user.email != customer.email or user.company_name != customer.name:
            stripe.Customer.modify(user.stripe_customer_id, email=user.email, name=user.company_name)
        
        return customer

    @staticmethod
    def get_active_products_with_prices() -> List[Dict]:
        """ Busca produtos e preços ativos do Stripe. Marketing pode gerenciar planos sem tocar no código. """
        products = stripe.Product.list(active=True, expand=['data.default_price'])
        plans = []
        for product in products:
            if product.default_price and product.default_price.type == 'recurring':
                plans.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price_id': product.default_price.id,
                    'price': f"{(product.default_price.unit_amount / 100):.2f}",
                    'currency': product.default_price.currency.upper(),
                    'interval': product.default_price.recurring.interval,
                })
        return sorted(plans, key=lambda p: float(p['price']))

    @staticmethod
    def create_checkout_session(user: AppUser, price_id: str) -> str:
        """ Cria uma Sessão de Checkout do Stripe, preparada para o mercado global com impostos automáticos. """
        customer = StripeService.get_or_create_customer(user)
        try:
            return stripe.checkout.Session.create(
                customer=customer.id,
                line_items=[{'price': price_id, 'quantity': 1}],
                mode='subscription',
                allow_promotion_codes=True,
                automatic_tax={'enabled': True},
                billing_address_collection='required',
                customer_update={'address': 'auto'},
                success_url=url_for('payments.success', _external=True),
                cancel_url=url_for('payments.cancel', _external=True),
                metadata={'synapcortex_user_id': user.id}
            ).url
        except Exception as e:
            current_app.logger.error(f"Erro ao criar Checkout Session: {e}")
            raise e

    @staticmethod
    def create_customer_portal_session(user: AppUser) -> str:
        """ Cria uma sessão do Portal do Cliente Stripe com configurações expandidas. """
        customer = StripeService.get_or_create_customer(user)
        portal_config_id = os.getenv('STRIPE_PORTAL_CONFIGURATION_ID')
        return stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url=url_for('dashboard.home'),
            configuration=portal_config_id
        ).url