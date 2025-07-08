"""
Schemas para Subscription - assinaturas de usuários
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class SubscriptionBase(BaseModel):
    """Schema base para Subscription"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    plan_id: UUID = Field(..., description="ID do plano")
    
    # Status da assinatura
    status: str = Field(..., description="Status da assinatura")
    
    # Datas importantes
    start_date: datetime = Field(..., description="Data de início")
    end_date: Optional[datetime] = Field(None, description="Data de fim")
    next_billing_date: Optional[datetime] = Field(None, description="Próxima cobrança")
    
    # Informações de pagamento
    payment_provider_id: Optional[UUID] = Field(None, description="ID do provedor de pagamento")
    external_subscription_id: Optional[str] = Field(None, description="ID externo da assinatura")
    
    # Preços
    monthly_price: Optional[float] = Field(None, description="Preço mensal")
    yearly_price: Optional[float] = Field(None, description="Preço anual")
    current_price: Optional[float] = Field(None, description="Preço atual")
    
    # Configurações
    is_active: bool = Field(True, description="Assinatura ativa")
    auto_renew: bool = Field(True, description="Renovação automática")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")


class SubscriptionCreate(SubscriptionBase):
    """Schema para criação de Subscription"""
    pass


class SubscriptionUpdate(BaseModel):
    """Schema para atualização de Subscription"""
    
    plan_id: Optional[UUID] = Field(None, description="ID do plano")
    status: Optional[str] = Field(None, description="Status da assinatura")
    
    end_date: Optional[datetime] = Field(None, description="Data de fim")
    next_billing_date: Optional[datetime] = Field(None, description="Próxima cobrança")
    
    payment_provider_id: Optional[UUID] = Field(None, description="ID do provedor de pagamento")
    external_subscription_id: Optional[str] = Field(None, description="ID externo da assinatura")
    
    monthly_price: Optional[float] = Field(None, description="Preço mensal")
    yearly_price: Optional[float] = Field(None, description="Preço anual")
    current_price: Optional[float] = Field(None, description="Preço atual")
    
    is_active: Optional[bool] = Field(None, description="Assinatura ativa")
    auto_renew: Optional[bool] = Field(None, description="Renovação automática")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class SubscriptionResponse(SubscriptionBase):
    """Schema para resposta de Subscription"""
    
    id: UUID = Field(..., description="ID único da assinatura")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas (opcional)
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    plan_name: Optional[str] = Field(None, description="Nome do plano")
    plan_description: Optional[str] = Field(None, description="Descrição do plano")
    
    # Status derivados
    is_expired: Optional[bool] = Field(None, description="Assinatura expirada")
    days_until_expiry: Optional[int] = Field(None, description="Dias até expirar")
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionList(BaseModel):
    """Schema para lista de Subscription"""
    
    items: list[SubscriptionResponse] = Field(..., description="Lista de assinaturas")
    total: int = Field(..., description="Total de assinaturas")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionSummary(BaseModel):
    """Schema para resumo de assinaturas"""
    
    total_active: int = Field(..., description="Total de assinaturas ativas")
    total_expired: int = Field(..., description="Total de assinaturas expiradas")
    total_cancelled: int = Field(..., description="Total de assinaturas canceladas")
    
    monthly_revenue: float = Field(..., description="Receita mensal")
    yearly_revenue: float = Field(..., description="Receita anual")
    
    # Breakdown por plano
    by_plan: Dict[str, int] = Field(..., description="Por plano")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionWithPlan(SubscriptionResponse):
    """Schema para Subscription com detalhes do plano"""
    
    plan_details: Dict[str, Any] = Field(..., description="Detalhes do plano")
    
    model_config = ConfigDict(from_attributes=True)
