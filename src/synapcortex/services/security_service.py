# src/synapcortex/services/security_service.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from ..models import AppUser

# Define o esquema de segurança para a chave de API
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_current_user(api_key: str = Depends(api_key_header)) -> AppUser:
    """
    Valida a chave de API e retorna o objeto do usuário correspondente.
    Usado como uma dependência do FastAPI para proteger rotas.
    """
    user = AppUser.query.filter_by(api_key=api_key, is_active=True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida ou ausente.",
            headers={"WWW-Authenticate": "Header"},
        )
    return user