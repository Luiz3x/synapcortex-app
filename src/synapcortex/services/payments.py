# src.synapcortex/blueprints/payments.py
# =================================================================================
# SYNAPCORTEX - BLUEPRINT DE PAGAMENTOS (v2.1)
# A "Ala da Bilheteria", com arquitetura de serviços e rota de sucesso.
# =================================================================================

from flask import (Blueprint, render_template, redirect,
                   url_for, flash, g, jsonify, current_app)

# Importa as ferramentas, o DNA e os guardiões do nosso projeto
from ..decorators import login_required
from ..models import SubscriptionStatus
from ..services import payments as payment_service

# --- CRIAÇÃO DO BLUEPRINT ---
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


# --- ROTAS DO BLUEPRINT ---

@payments_bp.route('/checkout')
@login_required 
def checkout():
    """Exibe a página de finalização de assinatura, já com o PaymentIntent criado."""
    user = g.user

    if user.is_subscription_valid and user.subscription_status != 'trial':
        flash('Você já possui uma assinatura ativa!', 'info')
        return redirect(url_for('dashboard.home'))
    
    try:
        # A lógica agora chama nosso serviço, mantendo o blueprint limpo
        client_secret = payment_service.create_stripe_payment_intent(user)
        
        return render_template(
            'payments/checkout.html', 
            stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'],
            client_secret=client_secret
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao preparar checkout para {g.user.email}: {e}")
        flash("Não foi possível iniciar o processo de pagamento. Tente novamente.", "error")
        return redirect(url_for('dashboard.home'))


@payments_bp.route('/success')
@login_required
def success():
    """
    Rota de retorno do Stripe após pagamento bem-sucedido.
    Ativa a assinatura do usuário em nosso sistema.
    """
    user = g.user
    try:
        payment_service.activate_subscription_for_user(user)
        flash('Pagamento aprovado! Sua assinatura está ativa. Bem-vindo à elite!', 'success')
    except Exception as e:
        current_app.logger.error(f"Erro ao ativar assinatura para {user.email} pós-pagamento: {e}")
        flash('Seu pagamento foi aprovado, mas tivemos um problema ao ativar sua conta. Por favor, contate o suporte.', 'error')
    
    return redirect(url_for('dashboard.home')))