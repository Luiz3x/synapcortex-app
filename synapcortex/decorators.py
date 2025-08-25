# src.synapcortex/decorators.py
# =================================================================================
# DECORATORS - VERSÃO FINAL E MODERNIZADA
# Módulo centralizado que usa flask-login para proteger as rotas,
# eliminando conflitos e erros de importação circular.
# =================================================================================

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def subscription_required(f):
    """
    Decorador Guardião que utiliza o sistema flask-login.

    Verifica em duas etapas:
    1. O usuário está autenticado via flask-login?
    2. O usuário autenticado tem uma assinatura ativa?
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Guardião de Autenticação: Usa a verificação padrão do flask-login.
        # É mais seguro e integrado que checar a sessão manualmente.
        if not current_user.is_authenticated:
            flash("Por favor, faça login para acessar esta página.", "warning")
            return redirect(url_for('auth.login'))

        # 2. Guardião de Assinatura: Verifica se o usuário tem uma assinatura válida.
        # Isso depende de um método/propriedade no seu modelo AppUser.
        # Garanta que seu modelo AppUser tenha essa lógica (ex: `has_active_subscription`).
        if not current_user.has_active_subscription():
            flash("Você precisa de uma assinatura ativa para acessar esta funcionalidade.", "warning")
            return redirect(url_for('payments.pricing')) # Leva para a página de planos/pagamentos

        # SUCESSO: Se passou pelas duas verificações, a rota é liberada.
        return f(*args, **kwargs)

    return decorated_function