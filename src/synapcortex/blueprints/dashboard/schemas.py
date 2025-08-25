# =================================================================================
# SYNAPCORTEX - DASHBOARD SCHEMAS (v2.1 - Arquitetura Pydantic V2)
# =================================================================================
# Schemas granulares, seguros e alinhados com as melhores práticas de design de API,
# incluindo validações de negócio e modelos específicos para entrada e saída de dados.
# =================================================================================

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.alias_generators import to_camel
from typing import Optional

# ---------------------------------------------------------------------------------
# 1. SCHEMA BASE: O DNA COMPARTILHADO
# ---------------------------------------------------------------------------------

class UserBase(BaseModel):
    """
    Schema base com configurações e campos compartilhados por outros modelos de usuário.
    Centraliza regras e configurações para evitar repetição de código.
    """
    company_name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100,
        description="Nome da empresa do usuário."
    )
    email: EmailStr = Field(..., description="E-mail de login do usuário, deve ser único.")

    class Config:
        """
        Configurações avançadas do Pydantic V2.
        - anystr_strip_whitespace: Garante dados limpos, sem espaços nas pontas.
        - from_attributes: Permite que o Pydantic leia dados de objetos do SQLAlchemy.
        - alias_generator: Converte snake_case (Python) para camelCase (JSON) automaticamente.
        """
        anystr_strip_whitespace = True
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True

# ---------------------------------------------------------------------------------
# 2. SCHEMAS DE ENTRADA (O que a API recebe)
# ---------------------------------------------------------------------------------

class UserCreateSchema(UserBase):
    """Schema utilizado especificamente para a criação de um novo usuário."""
    password: str = Field(..., min_length=8, description="Senha de acesso do usuário.")

class UserSettingsUpdateSchema(BaseModel):
    """
    Schema específico para ATUALIZAR configurações. Permite atualizações parciais (PATCH/PUT).
    Todos os campos são opcionais.
    """
    company_name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100,
        description="Novo nome da empresa do usuário."
    )
    email: Optional[EmailStr] = Field(None, description="Novo e-mail de login.")

    @validator('company_name', pre=True, always=True)
    def prevent_generic_names(cls, value):
        """Validador customizado que impede o uso de nomes de empresa genéricos."""
        if value and value.lower().strip() in ['empresa', 'company', 'teste', 'test']:
            raise ValueError(f"O nome de empresa '{value}' é genérico demais e não é permitido.")
        return value

# ---------------------------------------------------------------------------------
# 3. SCHEMA DE SAÍDA (O que a API retorna)
# ---------------------------------------------------------------------------------

class UserResponseSchema(UserBase):
    """
    Schema para os dados do usuário que são retornados pela API.
    Garante que dados sensíveis (como senhas) NUNCA sejam expostos.
    """
    id: int
    is_active: bool