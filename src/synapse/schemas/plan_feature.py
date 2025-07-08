"""
Schemas para PlanFeature - associação entre planos e features
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class PlanFeatureBase(BaseModel):
    """Schema base para PlanFeature"""
    
    # Relacionamentos
    plan_id: UUID = Field(..., description="ID do plano")
    feature_id: UUID = Field(..., description="ID da feature")
    
    # Configurações da feature no plano
    is_enabled: bool = Field(True, description="Feature habilitada")
    limit_value: Optional[int] = Field(None, description="Valor limite da feature")
    
    # Configuração específica da feature para este plano
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração específica")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class PlanFeatureCreate(PlanFeatureBase):
    """Schema para criação de PlanFeature"""
    pass


class PlanFeatureUpdate(BaseModel):
    """Schema para atualização de PlanFeature"""
    
    is_enabled: Optional[bool] = Field(None, description="Feature habilitada")
    limit_value: Optional[int] = Field(None, description="Valor limite da feature")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração específica")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class PlanFeatureResponse(PlanFeatureBase):
    """Schema para resposta de PlanFeature"""
    
    id: UUID = Field(..., description="ID único da associação")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    plan_name: Optional[str] = Field(None, description="Nome do plano")
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")
    feature_category: Optional[str] = Field(None, description="Categoria da feature")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureList(BaseModel):
    """Schema para lista de PlanFeature"""
    
    items: List[PlanFeatureResponse] = Field(..., description="Lista de associações")
    total: int = Field(..., description="Total de associações")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureMatrix(BaseModel):
    """Schema para matrix de features por plano"""
    
    plans: List[Dict[str, Any]] = Field(..., description="Lista de planos")
    features: List[Dict[str, Any]] = Field(..., description="Lista de features")
    
    # Matrix de features
    matrix: Dict[str, Dict[str, Any]] = Field(..., description="Matrix plan_id -> feature_key -> config")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureUsage(BaseModel):
    """Schema para uso de feature em plano"""
    
    plan_feature_id: UUID = Field(..., description="ID da associação plan-feature")
    subscription_id: UUID = Field(..., description="ID da assinatura")
    
    # Uso atual
    current_usage: int = Field(..., description="Uso atual")
    limit_value: Optional[int] = Field(None, description="Valor limite")
    
    # Estatísticas
    usage_percentage: Optional[float] = Field(None, description="Porcentagem de uso")
    remaining_quota: Optional[int] = Field(None, description="Quota restante")
    
    # Timestamps
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    reset_at: Optional[datetime] = Field(None, description="Reset do contador")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureBulkOperation(BaseModel):
    """Schema para operações em lote"""
    
    plan_id: UUID = Field(..., description="ID do plano")
    operation: str = Field(..., description="Tipo de operação")
    
    # Dados da operação
    feature_operations: List[Dict[str, Any]] = Field(..., description="Operações das features")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureComparison(BaseModel):
    """Schema para comparação de features entre planos"""
    
    plan_ids: List[UUID] = Field(..., description="IDs dos planos a comparar")
    
    # Resultado da comparação
    plans_info: List[Dict[str, Any]] = Field(..., description="Informações dos planos")
    features_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Comparação de features")
    
    # Análise
    unique_features: Dict[str, List[str]] = Field(..., description="Features únicas por plano")
    common_features: List[str] = Field(..., description="Features comuns")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureTemplate(BaseModel):
    """Schema para template de features de plano"""
    
    template_name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    
    # Features do template
    features: List[Dict[str, Any]] = Field(..., description="Features do template")
    
    # Categoria
    category: str = Field(..., description="Categoria do template")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureStatistics(BaseModel):
    """Schema para estatísticas de PlanFeature"""
    
    plan_id: UUID = Field(..., description="ID do plano")
    
    # Features
    total_features: int = Field(..., description="Total de features")
    enabled_features: int = Field(..., description="Features habilitadas")
    limited_features: int = Field(..., description="Features com limite")
    
    # Por categoria
    features_by_category: Dict[str, int] = Field(..., description="Features por categoria")
    
    # Uso
    most_used_features: List[Dict[str, Any]] = Field(..., description="Features mais usadas")
    least_used_features: List[Dict[str, Any]] = Field(..., description="Features menos usadas")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureValidation(BaseModel):
    """Schema para validação de features de plano"""
    
    plan_id: UUID = Field(..., description="ID do plano")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    
    # Validações
    is_valid: bool = Field(..., description="Configuração válida")
    errors: List[str] = Field(..., description="Erros encontrados")
    warnings: List[str] = Field(..., description="Avisos")
    
    # Validações específicas
    missing_features: List[str] = Field(..., description="Features obrigatórias faltantes")
    conflicting_features: List[str] = Field(..., description="Features conflitantes")
    invalid_limits: List[str] = Field(..., description="Limites inválidos")
    
    model_config = ConfigDict(from_attributes=True)


class PlanFeatureAudit(BaseModel):
    """Schema para auditoria de features de plano"""
    
    plan_id: UUID = Field(..., description="ID do plano")
    
    # Histórico de mudanças
    changes: List[Dict[str, Any]] = Field(..., description="Histórico de mudanças")
    
    # Análise
    added_features: List[str] = Field(..., description="Features adicionadas")
    removed_features: List[str] = Field(..., description="Features removidas")
    modified_features: List[str] = Field(..., description="Features modificadas")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)
