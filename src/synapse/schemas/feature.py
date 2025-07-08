"""
Schemas Pydantic para Features, PlanFeatures, TenantFeatures e WorkspaceFeatures
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# ==================== FEATURE SCHEMAS ====================

class FeatureCreate(BaseModel):
    """Schema para criação de feature"""

    model_config = ConfigDict(str_strip_whitespace=True)

    key: str = Field(..., max_length=100, description="Chave única da feature")
    name: str = Field(..., max_length=200, description="Nome da feature")
    description: Optional[str] = Field(None, description="Descrição da feature")
    category: Optional[str] = Field(None, max_length=100, description="Categoria")
    is_active: bool = Field(True, description="Se a feature está ativa")


class FeatureUpdate(BaseModel):
    """Schema para atualização de feature"""

    model_config = ConfigDict(str_strip_whitespace=True)

    key: Optional[str] = Field(None, max_length=100, description="Nova chave")
    name: Optional[str] = Field(None, max_length=200, description="Novo nome")
    description: Optional[str] = Field(None, description="Nova descrição")
    category: Optional[str] = Field(None, max_length=100, description="Nova categoria")
    is_active: Optional[bool] = Field(None, description="Novo status")


class FeatureResponse(BaseModel):
    """Schema de resposta para feature"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da feature")
    key: str = Field(..., description="Chave da feature")
    name: str = Field(..., description="Nome da feature")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    is_active: bool = Field(..., description="Se está ativa")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


class FeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features"""

    model_config = ConfigDict(from_attributes=True)

    features: List[FeatureResponse] = Field(..., description="Lista de features")
    total_count: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Tamanho da página")
    has_next: bool = Field(..., description="Se há próxima página")


# ==================== PLAN FEATURE SCHEMAS ====================

class PlanFeatureCreate(BaseModel):
    """Schema para criação de feature de plano"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se está habilitada")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração"
    )


class PlanFeatureResponse(BaseModel):
    """Schema de resposta para feature de plano"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da plan feature")
    plan_id: uuid.UUID = Field(..., description="ID do plano")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    config: Dict[str, Any] = Field(..., description="Configuração")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Campos do relacionamento
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")


class PlanFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do plano"""

    model_config = ConfigDict(from_attributes=True)

    items: List[PlanFeatureResponse] = Field(
        ..., description="Lista de features do plano"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# ==================== TENANT FEATURE SCHEMAS ====================

class TenantFeatureCreate(BaseModel):
    """Schema para criação de feature de tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se está habilitada")
    usage_count: Optional[int] = Field(0, description="Contagem de uso")
    limit_value: Optional[int] = Field(None, description="Limite de valor")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração"
    )
    expires_at: Optional[datetime] = Field(
        None, description="Data de expiração"
    )


class TenantFeatureResponse(BaseModel):
    """Schema de resposta para feature de tenant"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da tenant feature")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    usage_count: int = Field(..., description="Contagem de uso")
    limit_value: Optional[int] = Field(None, description="Limite de valor")
    config: Dict[str, Any] = Field(..., description="Configuração")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Campos do relacionamento
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")


class TenantFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do tenant"""

    model_config = ConfigDict(from_attributes=True)

    items: List[TenantFeatureResponse] = Field(
        ..., description="Lista de features do tenant"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# ==================== WORKSPACE FEATURE SCHEMAS ====================

class WorkspaceFeatureCreate(BaseModel):
    """Schema para criação de feature de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se está habilitada")
    usage_count: Optional[int] = Field(0, description="Contagem de uso")
    limit_value: Optional[int] = Field(None, description="Limite de valor")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração"
    )
    expires_at: Optional[datetime] = Field(
        None, description="Data de expiração"
    )


class WorkspaceFeatureResponse(BaseModel):
    """Schema de resposta para feature de workspace"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da workspace feature")
    workspace_id: uuid.UUID = Field(..., description="ID do workspace")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    usage_count: int = Field(..., description="Contagem de uso")
    limit_value: Optional[int] = Field(None, description="Limite de valor")
    config: Dict[str, Any] = Field(..., description="Configuração")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Campos do relacionamento
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")


class WorkspaceFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do workspace"""

    model_config = ConfigDict(from_attributes=True)

    items: List[WorkspaceFeatureResponse] = Field(
        ..., description="Lista de features do workspace"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")
