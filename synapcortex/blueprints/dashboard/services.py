# =================================================================================
# SYNAPCORTEX - DASHBOARD SERVICES (v2.1 - AI & Event-Driven Architecture)
# =================================================================================
# Esta camada de serviço opera como um microsserviço inteligente, utilizando
# tarefas assíncronas para performance, eventos para escalabilidade e IA para segurança.
# =================================================================================

from typing import Dict, Tuple

# Importa os componentes da nossa aplicação central
from ...extensions import db, celery_app
from ...models import AppUser
# Conceitos de arquitetura avançada (placeholders para implementação futura)
# from ...ai_models import SecurityAnalyzer
# from ...cloud_services import EventPublisher

class UserService:
    """
    Encapsula a lógica de negócio do usuário, agora com capacidades assíncronas,
    orientadas a eventos e com pontos de integração para IA.
    """

    @staticmethod
    def update_user_settings(user: AppUser, settings_data: Dict) -> Tuple[bool, str]:
        """
        Atualiza as configurações de forma segura, publicando um evento ao final.
        """
        # PONTO DE INTEGRAÇÃO COM IA: No futuro, analisaria o risco da requisição.
        # is_secure, risk_reason = SecurityAnalyzer.analyze_request(user, request_metadata)
        # if not is_secure:
        #     return False, f"Ação bloqueada por segurança: {risk_reason}"

        has_changed = False
        # 1. Lógica de atualização completa (reincorporada da v1)
        new_company_name = settings_data.get('company_name')
        if new_company_name and user.company_name != new_company_name:
            user.company_name = new_company_name
            has_changed = True

        new_email = settings_data.get('email')
        if new_email and user.email != new_email:
            existing_user = AppUser.query.filter(AppUser.email == new_email, AppUser.id != user.id).first()
            if existing_user:
                return False, "Este e-mail já está em uso por outra conta."
            user.email = new_email
            has_changed = True

        if not has_changed:
            return True, "Nenhuma alteração foi detectada."

        db.session.commit()

        # 2. ARQUITETURA ORIENTADA A EVENTOS: Notifica outros serviços sobre a mudança.
        # EventPublisher.publish('user.settings.updated', {'user_id': user.id})

        return True, "Configurações atualizadas com sucesso."

    @staticmethod
    def trigger_cancel_account_task(user: AppUser) -> Tuple[bool, str]:
        """
        Método SÍNCRONO que a rota chama. Apenas dispara a tarefa em segundo plano.
        Retorna uma resposta imediata para o usuário.
        """
        # Dispara a tarefa assíncrona, passando apenas o ID do usuário (prática segura)
        _perform_account_cancellation.delay(user_id=user.id)
        
        return True, "O processo de encerramento da sua conta foi iniciado e será concluído em segundo plano."

@celery_app.task(name='tasks.cancel_user_account')
def _perform_account_cancellation(user_id: int) -> Tuple[bool, str]:
    """
    Tarefa ASSÍNCRONA (Celery Task) que executa o processo pesado de cancelamento.
    Roda em um 'worker' separado, sem travar a aplicação principal.
    """
    user = AppUser.query.get(user_id)
    if not user:
        # Idealmente, logaríamos este erro
        return False, "Usuário não encontrado para cancelamento."

    # PONTO DE INTEGRAÇÃO: Chamar serviço de billing para cancelar assinatura no Stripe, etc.
    # billing_service.cancel_subscription(user.stripe_subscription_id)

    # Lógica de anonimização de dados completa (reincorporada da v1)
    user.email = f"deleted_{user.id}@synapcortex.invalid"
    user.company_name = "Conta Encerrada"
    user.password_hash = "disabled"
    user.api_key = None
    user.is_active = False
    user.subscription_status = "canceled"
    
    db.session.commit()
    
    # ARQUITETURA ORIENTADA A EVENTOS: Notifica outros serviços que a conta foi cancelada.
    # EventPublisher.publish('user.account.canceled', {'user_id': user.id})

    return True, f"Processo de encerramento para user_id {user_id} concluído."