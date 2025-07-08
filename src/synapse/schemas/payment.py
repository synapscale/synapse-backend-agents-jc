"""
Schemas Pydantic para Payment/Billing system
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# ==================== PAYMENT PROVIDER SCHEMAS ====================

class PaymentProviderCreate(BaseModel):
    """Schema para criação de provedor de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="Nome do provedor")
    display_name: str = Field(..., description="Nome de exibição")
    is_active: bool = Field(True, description="Se está ativo")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuração")
    webhook_secret: Optional[str] = Field(None, description="Segredo do webhook")
    api_version: Optional[str] = Field(None, description="Versão da API")


class PaymentProviderResponse(BaseModel):
    """Schema de resposta para provedor de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do provedor")
    name: str = Field(..., description="Nome")
    display_name: str = Field(..., description="Nome de exibição")
    is_active: bool = Field(..., description="Se está ativo")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuração")
    webhook_secret: Optional[str] = Field(None, description="Segredo do webhook")
    api_version: Optional[str] = Field(None, description="Versão da API")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


# ==================== PAYMENT CUSTOMER SCHEMAS ====================

class PaymentCustomerCreate(BaseModel):
    """Schema para criação de customer de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    provider_id: uuid.UUID = Field(..., description="ID do provedor")
    external_customer_id: str = Field(..., description="ID externo do customer")
    customer_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados do customer")
    is_active: bool = Field(True, description="Se está ativo")


class PaymentCustomerResponse(BaseModel):
    """Schema de resposta para customer de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do customer")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    provider_id: uuid.UUID = Field(..., description="ID do provedor")
    external_customer_id: str = Field(..., description="ID externo")
    customer_data: Optional[Dict[str, Any]] = Field(None, description="Dados do customer")
    is_active: bool = Field(..., description="Se está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== PAYMENT METHOD SCHEMAS ====================

class PaymentMethodCreate(BaseModel):
    """Schema para criação de método de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: str = Field(..., description="Tipo do método")
    external_method_id: str = Field(..., description="ID externo do método")
    provider_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados do provedor")
    is_default: bool = Field(False, description="Se é padrão")
    is_active: bool = Field(True, description="Se está ativo")


class PaymentMethodUpdate(BaseModel):
    """Schema para atualização de método de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: Optional[str] = Field(None, description="Tipo do método")
    external_method_id: Optional[str] = Field(None, description="ID externo")
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Dados do provedor")
    is_default: Optional[bool] = Field(None, description="Se é padrão")
    is_active: Optional[bool] = Field(None, description="Se está ativo")


class PaymentMethodResponse(BaseModel):
    """Schema de resposta para método de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do método")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    type: str = Field(..., description="Tipo")
    external_method_id: str = Field(..., description="ID externo")
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Dados do provedor")
    is_default: bool = Field(..., description="Se é padrão")
    is_active: bool = Field(..., description="Se está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


class PaymentMethodListResponse(BaseModel):
    """Schema de resposta para listagem de métodos de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[PaymentMethodResponse] = Field(..., description="Lista de métodos")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# ==================== INVOICE SCHEMAS ====================

class InvoiceCreate(BaseModel):
    """Schema para criação de invoice"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    amount: float = Field(..., description="Valor total")
    currency: str = Field(..., description="Moeda")
    description: Optional[str] = Field(None, description="Descrição")
    due_date: Optional[datetime] = Field(None, description="Data de vencimento")
    invoice_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados da invoice")


class InvoiceUpdate(BaseModel):
    """Schema para atualização de invoice"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    amount: Optional[float] = Field(None, description="Valor total")
    currency: Optional[str] = Field(None, description="Moeda")
    description: Optional[str] = Field(None, description="Descrição")
    due_date: Optional[datetime] = Field(None, description="Data de vencimento")
    invoice_data: Optional[Dict[str, Any]] = Field(None, description="Dados da invoice")
    status: Optional[str] = Field(None, description="Status")


class InvoiceResponse(BaseModel):
    """Schema de resposta para invoice"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID da invoice")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    amount: float = Field(..., description="Valor total")
    currency: str = Field(..., description="Moeda")
    status: str = Field(..., description="Status")
    description: Optional[str] = Field(None, description="Descrição")
    due_date: Optional[datetime] = Field(None, description="Data de vencimento")
    invoice_data: Optional[Dict[str, Any]] = Field(None, description="Dados da invoice")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


class InvoiceListResponse(BaseModel):
    """Schema de resposta para listagem de invoices"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[InvoiceResponse] = Field(..., description="Lista de invoices")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


class PaginatedResponse(BaseModel):
    """Schema base para respostas paginadas"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")
