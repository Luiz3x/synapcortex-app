# =================================================================================
# SYNAPCORTEX - DASHBOARD SCHEMAS (v2.2 - Final Corrigido)
# =================================================================================

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.alias_generators import to_camel
from typing import Optional

class UserBase(BaseModel):
    # ... (esta parte já está perfeita, sem alterações)
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: EmailStr = Field(...)

    class Config:
        anystr_strip_whitespace = True
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True

class UserCreateSchema(UserBase):
    password: str = Field(..., min_length=8)

# --- CORREÇÃO ESTÁ AQUI ---
class UserSettingsSchema(BaseModel): # NOME CORRIGIDO: Removido o "Update"
    """
    Schema específico para ATUALIZAR configurações. Permite atualizações parciais.
    """
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None)

    @validator('company_name', pre=True, always=True)
    def prevent_generic_names(cls, value):
        if value and value.lower().strip() in ['empresa', 'company', 'teste', 'test']:
            raise ValueError(f"O nome de empresa '{value}' é genérico demais.")
        return value

class UserResponseSchema(UserBase):
    # ... (esta parte já está perfeita, sem alterações)
    id: int
    is_active: bool