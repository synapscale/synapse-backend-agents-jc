"""
Schemas para PaymentProvider - provedores de pagamento
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class PaymentProviderBase(BaseModel):
    """Schema base para PaymentProvider"""
    
    name: str = Field(..., description="Nome do provedor")
    provider_type: str = Field(..., description="Tipo do provedor (stripe, paypal, etc)")
    
    # Configurações
    is_active: bool = Field(True, description="Provedor ativo")
    is_default: bool = Field(False, description="Provedor padrão")
    
    # Configuração do provedor
    api_key: Optional[str] = Field(None, description="Chave da API")
    api_secret: Optional[str] = Field(None, description="Segredo da API")
    webhook_secret: Optional[str] = Field(None, description="Segredo do webhook")
    
    # URLs
    base_url: Optional[str] = Field(None, description="URL base da API")
    webhook_url: Optional[str] = Field(None, description="URL do webhook")
    
    # Configurações específicas
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração adicional")
    
    # Metadata
    description: Optional[str] = Field(None, description="Descrição do provedor")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")


class PaymentProviderCreate(PaymentProviderBase):
    """Schema para criação de PaymentProvider"""
    pass


class PaymentProviderUpdate(BaseModel):
    """Schema para atualização de PaymentProvider"""
    
    name: Optional[str] = Field(None, description="Nome do provedor")
    is_active: Optional[bool] = Field(None, description="Provedor ativo")
    is_default: Optional[bool] = Field(None, description="Provedor padrão")
    
    api_key: Optional[str] = Field(None, description="Chave da API")
    api_secret: Optional[str] = Field(None, description="Segredo da API")
    webhook_secret: Optional[str] = Field(None, description="Segredo do webhook")
    
    base_url: Optional[str] = Field(None, description="URL base da API")
    webhook_url: Optional[str] = Field(None, description="URL do webhook")
    
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração adicional")
    description: Optional[str] = Field(None, description="Descrição do provedor")


class PaymentProviderResponse(PaymentProviderBase):
    """Schema para resposta de PaymentProvider"""
    
    id: UUID = Field(..., description="ID único do provedor")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Ocultar dados sensíveis na resposta
    api_key: Optional[str] = Field(None, description="Chave da API (mascarada)")
    api_secret: Optional[str] = Field(None, description="Segredo mascarado")
    webhook_secret: Optional[str] = Field(None, description="Segredo mascarado")
    
    # Status de saúde
    is_healthy: Optional[bool] = Field(None, description="Status de saúde do provedor")
    last_health_check: Optional[datetime] = Field(None, description="Último check de saúde")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentProviderList(BaseModel):
    """Schema para lista de PaymentProvider"""
    
    items: list[PaymentProviderResponse] = Field(..., description="Lista de provedores")
    total: int = Field(..., description="Total de provedores")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentProviderHealth(BaseModel):
    """Schema para status de saúde do provedor"""
    
    provider_id: UUID = Field(..., description="ID do provedor")
    provider_name: str = Field(..., description="Nome do provedor")
    is_healthy: bool = Field(..., description="Status de saúde")
    last_check: datetime = Field(..., description="Último check")
    response_time_ms: Optional[int] = Field(None, description="Tempo de resposta em ms")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    model_config = ConfigDict(from_attributes=True)
