# =================================================================================
# SYNAPCORTEX - ARQUIVO DE DECORADORES (v3.1)
# Responsável por criar "guardiões" para as nossas rotas, controlando o acesso.
# Versão com arquitetura "Guard Clause" para máxima clareza e robustez.
# =================================================================================

from functools import wraps
from typing import Callable
from flask import session, flash, redirect, url_for, g, request

# Importa as dependências dos nossos outros módulos
from .models import AppUser, db, SubscriptionStatus

def get_current_user() -> AppUser | None:
    """
    Busca o usuário logado e o armazena no contexto global 'g' da requisição.

    O objeto 'g' é único para cada requisição. Ao armazenar o usuário nele,
    evitamos múltiplas consultas ao banco de dados se precisarmos do usuário
    em diferentes partes do código durante o mesmo request.
    """
    if 'user' not in g and 'email' in session:
        g.user = AppUser.query.filter_by(email=session['email']).first()
    
    return g.get('user')


def subscription_required(f: Callable) -> Callable:
    """
    Decorador "Guardião" para rotas que exigem um usuário logado e com assinatura válida.

    Ele executa as seguintes verificações em uma ordem lógica e segura ("Guard Clause"):
    1.  O usuário está logado? Se não, salva a URL de destino e o envia para o login.
    2.  O usuário existe no banco de dados e sua conta não foi cancelada?
    3.  Se o usuário estava em período de teste (trial), este já expirou?
    4.  A assinatura do usuário é considerada válida (ativa, demo ou trial ainda ativo)?

    Se todas as verificações passarem, a rota é executada.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # --- 1. Guardião: Acesso apenas para usuários logados ---
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            session['next'] = request.url 
            return redirect(url_for('auth.login'))

        user = get_current_user()

        # --- 2. Guardião: Usuário deve existir e não pode ter sido cancelado ---
        if not user or user.subscription_status == SubscriptionStatus.CANCELED:
            session.clear()
            flash('Usuário não encontrado ou sua conta foi encerrada.', 'error')
            return redirect(url_for('auth.login'))

        # --- 3. Guardião: Trata o caso específico de um trial recém-expirado ---
        # Verificamos este caso antes da validação geral para dar a mensagem mais precisa
        # e para atualizar o status do usuário no banco de dados.
        if user.subscription_status == SubscriptionStatus.TRIAL and not user.is_trial_active:
            user.subscription_status = SubscriptionStatus.EXPIRED_TRIAL
            db.session.commit()
            flash('Seu período de teste acabou. Por favor, realize sua assinatura para continuar.', 'info')
            return redirect(url_for('dashboard.pagamento'))

        # --- 4. Guardião: A assinatura deve ser válida ---
        if not user.is_subscription_valid:
            flash('Sua assinatura não está ativa. Por favor, regularize para ter acesso.', 'warning')
            return redirect(url_for('dashboard.pagamento'))

        # --- SUCESSO! ---
        # Se o código chegou até aqui, todos os guardiões foram superados.
        # A rota pode acessar o usuário através de 'g.user' a qualquer momento.
        return f(*args, **kwargs)

    return decorated_function
    # =================================================================================
# SYNAPCORTEX - ARQUIVO DE DECORADORES (v4.0)
# Contém os "guardiões" que protegem as rotas da nossa aplicação.
# =================================================================================

from functools import wraps
from typing import Callable
from flask import session, flash, redirect, url_for, g

from .models import AppUser, SubscriptionStatus

def get_current_user() -> AppUser | None:
    """Busca o usuário logado e o armazena no contexto 'g' da requisição."""
    if 'user' not in g and 'email' in session:
        g.user = AppUser.query.filter_by(email=session['email']).first()
    return g.get('user')


def login_required(f: Callable) -> Callable:
    """
    Decorador "Recepcionista": Garante que o usuário esteja logado.

    É uma versão mais simples do 'subscription_required', ideal para páginas
    como checkout ou gerenciamento de conta, onde o status da assinatura
    não é um impeditivo para acessar, apenas o login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para continuar.', 'warning')
            return redirect(url_for('auth.index'))

        user = get_current_user()

        if not user:
            session.clear()
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'error')
            return redirect(url_for('auth.index'))
        
        # O usuário está disponível para a rota via g.user.
        return f(*args, **kwargs)

    return decorated_function


def subscription_required(f: Callable) -> Callable:
    """
    Decorador "Guardião Premium": Exige login e assinatura válida.
    Protege as áreas principais do dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primeiro, garante que o usuário está logado.
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            session['next'] = request.url 
            return redirect(url_for('auth.login'))

        user = get_current_user()

        # Garante que o usuário existe e não está cancelado.
        if not user or user.subscription_status == SubscriptionStatus.CANCELED:
            session.clear()
            flash('Usuário não encontrado ou sua conta foi encerrada.', 'error')
            return redirect(url_for('auth.login'))

        # Verificação final e mais importante: a assinatura é válida?
        if not user.is_subscription_valid:
            flash('Sua assinatura não está ativa. Por favor, regularize para ter acesso.', 'warning')
            return redirect(url_for('payments.checkout'))

        # Sucesso!
        return f(*args, **kwargs)

    return decorated_function