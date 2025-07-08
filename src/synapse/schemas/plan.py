"""
Schemas para Plan - planos de assinatura
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal


class PlanBase(BaseModel):
    """Schema base para Plan"""
    
    # Identificação
    name: str = Field(..., description="Nome do plano")
    description: Optional[str] = Field(None, description="Descrição do plano")
    
    # Código único
    plan_code: str = Field(..., description="Código único do plano")
    
    # Preços
    monthly_price: Decimal = Field(..., description="Preço mensal")
    yearly_price: Optional[Decimal] = Field(None, description="Preço anual")
    
    # Configurações
    is_active: bool = Field(True, description="Plano ativo")
    is_public: bool = Field(True, description="Plano público")
    is_featured: bool = Field(False, description="Plano em destaque")
    
    # Limites
    user_limit: Optional[int] = Field(None, description="Limite de usuários")
    workspace_limit: Optional[int] = Field(None, description="Limite de workspaces")
    agent_limit: Optional[int] = Field(None, description="Limite de agentes")
    storage_limit_gb: Optional[int] = Field(None, description="Limite de armazenamento em GB")
    
    # Configuração de features
    features_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de features")
    
    # Trial
    trial_days: Optional[int] = Field(None, description="Dias de trial")
    
    # Contexto
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant (null para planos globais)")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Visual
    color: Optional[str] = Field(None, description="Cor do plano")
    icon: Optional[str] = Field(None, description="Ícone do plano")


class PlanCreate(PlanBase):
    """Schema para criação de Plan"""
    pass


class PlanUpdate(BaseModel):
    """Schema para atualização de Plan"""
    
    name: Optional[str] = Field(None, description="Nome do plano")
    description: Optional[str] = Field(None, description="Descrição do plano")
    
    monthly_price: Optional[Decimal] = Field(None, description="Preço mensal")
    yearly_price: Optional[Decimal] = Field(None, description="Preço anual")
    
    is_active: Optional[bool] = Field(None, description="Plano ativo")
    is_public: Optional[bool] = Field(None, description="Plano público")
    is_featured: Optional[bool] = Field(None, description="Plano em destaque")
    
    user_limit: Optional[int] = Field(None, description="Limite de usuários")
    workspace_limit: Optional[int] = Field(None, description="Limite de workspaces")
    agent_limit: Optional[int] = Field(None, description="Limite de agentes")
    storage_limit_gb: Optional[int] = Field(None, description="Limite de armazenamento")
    
    features_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de features")
    trial_days: Optional[int] = Field(None, description="Dias de trial")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    color: Optional[str] = Field(None, description="Cor do plano")
    icon: Optional[str] = Field(None, description="Ícone do plano")


class PlanResponse(PlanBase):
    """Schema para resposta de Plan"""
    
    id: UUID = Field(..., description="ID único do plano")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Estatísticas
    subscribers_count: Optional[int] = Field(None, description="Número de assinantes")
    revenue_monthly: Optional[Decimal] = Field(None, description="Receita mensal")
    revenue_yearly: Optional[Decimal] = Field(None, description="Receita anual")
    
    # Features incluídas
    features: Optional[List[Dict[str, Any]]] = Field(None, description="Features incluídas")
    
    model_config = ConfigDict(from_attributes=True)


class PlanList(BaseModel):
    """Schema para lista de Plan"""
    
    items: List[PlanResponse] = Field(..., description="Lista de planos")
    total: int = Field(..., description="Total de planos")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class PlanComparison(BaseModel):
    """Schema para comparação de planos"""
    
    plans: List[PlanResponse] = Field(..., description="Planos a comparar")
    
    # Comparação de features
    feature_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Comparação de features")
    
    # Comparação de limites
    limits_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Comparação de limites")
    
    model_config = ConfigDict(from_attributes=True)


class PlanUsage(BaseModel):
    """Schema para uso do plano"""
    
    plan_id: UUID = Field(..., description="ID do plano")
    subscription_id: UUID = Field(..., description="ID da assinatura")
    
    # Uso atual
    users_used: int = Field(..., description="Usuários utilizados")
    workspaces_used: int = Field(..., description="Workspaces utilizados")
    agents_used: int = Field(..., description="Agentes utilizados")
    storage_used_gb: float = Field(..., description="Armazenamento utilizado em GB")
    
    # Limites do plano
    user_limit: Optional[int] = Field(None, description="Limite de usuários")
    workspace_limit: Optional[int] = Field(None, description="Limite de workspaces")
    agent_limit: Optional[int] = Field(None, description="Limite de agentes")
    storage_limit_gb: Optional[int] = Field(None, description="Limite de armazenamento")
    
    # Porcentagens de uso
    users_usage_percentage: Optional[float] = Field(None, description="Porcentagem de uso de usuários")
    workspaces_usage_percentage: Optional[float] = Field(None, description="Porcentagem de uso de workspaces")
    agents_usage_percentage: Optional[float] = Field(None, description="Porcentagem de uso de agentes")
    storage_usage_percentage: Optional[float] = Field(None, description="Porcentagem de uso de armazenamento")
    
    model_config = ConfigDict(from_attributes=True)


class PlanRecommendation(BaseModel):
    """Schema para recomendação de plano"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Plano recomendado
    recommended_plan_id: UUID = Field(..., description="ID do plano recomendado")
    recommended_plan_name: str = Field(..., description="Nome do plano recomendado")
    
    # Motivo da recomendação
    reason: str = Field(..., description="Motivo da recomendação")
    confidence_score: float = Field(..., description="Score de confiança")
    
    # Análise de uso
    usage_analysis: Dict[str, Any] = Field(..., description="Análise de uso")
    
    # Benefícios da mudança
    benefits: List[str] = Field(..., description="Benefícios da mudança")
    
    model_config = ConfigDict(from_attributes=True)


class PlanMigration(BaseModel):
    """Schema para migração de plano"""
    
    from_plan_id: UUID = Field(..., description="ID do plano atual")
    to_plan_id: UUID = Field(..., description="ID do plano de destino")
    subscription_id: UUID = Field(..., description="ID da assinatura")
    
    # Configurações da migração
    migration_type: str = Field(..., description="Tipo de migração (immediate, scheduled)")
    scheduled_date: Optional[datetime] = Field(None, description="Data agendada")
    
    # Cálculos de preço
    prorated_amount: Optional[Decimal] = Field(None, description="Valor proporcional")
    new_monthly_amount: Decimal = Field(..., description="Novo valor mensal")
    
    model_config = ConfigDict(from_attributes=True)


class PlanStatistics(BaseModel):
    """Schema para estatísticas de Plan"""
    
    total_plans: int = Field(..., description="Total de planos")
    active_plans: int = Field(..., description="Planos ativos")
    public_plans: int = Field(..., description="Planos públicos")
    
    # Assinantes
    total_subscribers: int = Field(..., description="Total de assinantes")
    subscribers_by_plan: Dict[str, int] = Field(..., description="Assinantes por plano")
    
    # Receita
    total_monthly_revenue: Decimal = Field(..., description="Receita mensal total")
    total_yearly_revenue: Decimal = Field(..., description="Receita anual total")
    revenue_by_plan: Dict[str, Decimal] = Field(..., description="Receita por plano")
    
    # Crescimento
    monthly_growth_rate: float = Field(..., description="Taxa de crescimento mensal")
    churn_rate: float = Field(..., description="Taxa de cancelamento")
    
    model_config = ConfigDict(from_attributes=True)


class PlanPricing(BaseModel):
    """Schema para precificação de plano"""
    
    plan_id: UUID = Field(..., description="ID do plano")
    
    # Preços base
    base_monthly_price: Decimal = Field(..., description="Preço base mensal")
    base_yearly_price: Optional[Decimal] = Field(None, description="Preço base anual")
    
    # Descontos
    monthly_discount_percentage: Optional[float] = Field(None, description="Desconto mensal")
    yearly_discount_percentage: Optional[float] = Field(None, description="Desconto anual")
    
    # Preços finais
    final_monthly_price: Decimal = Field(..., description="Preço final mensal")
    final_yearly_price: Optional[Decimal] = Field(None, description="Preço final anual")
    
    # Válido até
    valid_until: Optional[datetime] = Field(None, description="Válido até")
    
    model_config = ConfigDict(from_attributes=True)
