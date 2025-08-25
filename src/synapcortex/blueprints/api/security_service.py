from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from ..models import AppUser

# Define que a chave de API virá no cabeçalho 'X-API-Key'
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_current_user(api_key: str = Depends(api_key_header)) -> AppUser:
    """
    Dependência de segurança: valida a API Key e retorna o usuário.
    Esta função será executada automaticamente em todas as rotas protegidas.
    """
    user = AppUser.query.filter_by(api_key=api_key).first()
    if not user or not user.is_subscription_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida ou assinatura inativa.",
        )
    return user