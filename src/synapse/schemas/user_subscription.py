from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class SubscriptionStatus(str, Enum):
    """Status possíveis da assinatura."""
    active = "active"
    cancelled = "cancelled"
    expired = "expired"
    trial = "trial"
    # Outros status podem ser aceitos como string

class BillingCycle(str, Enum):
    """Ciclos de cobrança suportados."""
    monthly = "monthly"
    yearly = "yearly"
    custom = "custom"
    # Outros ciclos podem ser aceitos como string

class UserSubscriptionBase(BaseModel):
    """Schema base para assinatura de usuário."""
    user_id: UUID = Field(..., description="ID do usuário assinante")
    plan_id: UUID = Field(..., description="ID do plano assinado")
    status: str = Field(..., description="Status da assinatura")
    billing_cycle: str = Field(..., description="Ciclo de cobrança da assinatura")
    start_date: datetime = Field(..., description="Data de início da assinatura")
    end_date: Optional[datetime] = Field(None, description="Data de término da assinatura")
    subscription_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados adicionais da assinatura")
    is_active: bool = Field(..., description="Indica se a assinatura está ativa")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = {e.value for e in SubscriptionStatus}
        if v not in allowed:
            import warnings
            warnings.warn(f"Status '{v}' não está entre os padrões conhecidos.")
        return v

    @field_validator('billing_cycle')
    @classmethod
    def validate_billing_cycle(cls, v):
        allowed = {e.value for e in BillingCycle}
        if v not in allowed:
            import warnings
            warnings.warn(f"Ciclo de cobrança '{v}' não está entre os padrões conhecidos.")
        return v

class UserSubscriptionCreate(UserSubscriptionBase):
    """Schema para criação de assinatura de usuário."""
    pass

class UserSubscriptionUpdate(BaseModel):
    """Schema para atualização parcial de assinatura de usuário."""
    status: Optional[str] = Field(None, description="Status da assinatura")
    billing_cycle: Optional[str] = Field(None, description="Ciclo de cobrança da assinatura")
    end_date: Optional[datetime] = Field(None, description="Data de término da assinatura")
    subscription_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais da assinatura")
    is_active: Optional[bool] = Field(None, description="Indica se a assinatura está ativa")

class UserSubscriptionResponse(UserSubscriptionBase):
    """Schema de resposta para assinatura de usuário."""
    id: UUID = Field(..., description="ID da assinatura")
    created_at: datetime = Field(..., description="Data de criação da assinatura")
    updated_at: datetime = Field(..., description="Data de atualização da assinatura")
    model_config = ConfigDict(from_attributes=True, use_enum_values=True, validate_assignment=True)

class UserSubscriptionList(BaseModel):
    """Resposta paginada de assinaturas de usuário."""
    items: List[UserSubscriptionResponse]
    total: int = Field(..., ge=0, description="Total de assinaturas encontradas")
    page: int = Field(..., ge=1, description="Página atual")
    per_page: int = Field(..., ge=1, le=100, description="Itens por página")
    pages: int = Field(..., ge=1, description="Total de páginas")
    model_config = ConfigDict(from_attributes=True)

# Exemplo de uso:
# sub = UserSubscriptionCreate(
#     user_id=UUID("..."),
#     plan_id=UUID("..."),
#     status="active",
#     billing_cycle="monthly",
#     start_date=datetime.now(),
#     is_active=True
# ) 