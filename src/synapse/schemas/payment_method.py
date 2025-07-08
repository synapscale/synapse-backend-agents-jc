"""
Schemas para PaymentMethod - métodos de pagamento
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class PaymentMethodBase(BaseModel):
    """Schema base para PaymentMethod"""
    
    # Identificação
    name: str = Field(..., description="Nome do método de pagamento")
    
    # Tipo
    method_type: str = Field(..., description="Tipo do método (credit_card, pix, boleto, etc)")
    
    # Dados do método (criptografados/tokenizados)
    payment_data: Dict[str, Any] = Field(..., description="Dados do método de pagamento")
    
    # Status
    is_active: bool = Field(True, description="Método ativo")
    is_default: bool = Field(False, description="Método padrão")
    
    # Relacionamentos
    user_id: UUID = Field(..., description="ID do usuário")
    payment_provider_id: UUID = Field(..., description="ID do provedor de pagamento")
    
    # Token externo
    external_token: Optional[str] = Field(None, description="Token do provedor externo")
    
    # Dados de expiração (para cartões)
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class PaymentMethodCreate(PaymentMethodBase):
    """Schema para criação de PaymentMethod"""
    pass


class PaymentMethodUpdate(BaseModel):
    """Schema para atualização de PaymentMethod"""
    
    name: Optional[str] = Field(None, description="Nome do método de pagamento")
    
    payment_data: Optional[Dict[str, Any]] = Field(None, description="Dados do método de pagamento")
    
    is_active: Optional[bool] = Field(None, description="Método ativo")
    is_default: Optional[bool] = Field(None, description="Método padrão")
    
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class PaymentMethodResponse(PaymentMethodBase):
    """Schema para resposta de PaymentMethod"""
    
    id: UUID = Field(..., description="ID único do método de pagamento")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    payment_provider_name: Optional[str] = Field(None, description="Nome do provedor")
    
    # Dados mascarados para segurança
    masked_payment_data: Optional[Dict[str, Any]] = Field(None, description="Dados mascarados")
    
    # Status de validação
    is_valid: Optional[bool] = Field(None, description="Método válido")
    validation_error: Optional[str] = Field(None, description="Erro de validação")
    
    # Última utilização
    last_used_at: Optional[datetime] = Field(None, description="Última utilização")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodList(BaseModel):
    """Schema para lista de PaymentMethod"""
    
    items: List[PaymentMethodResponse] = Field(..., description="Lista de métodos de pagamento")
    total: int = Field(..., description="Total de métodos")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodValidation(BaseModel):
    """Schema para validação de PaymentMethod"""
    
    method_id: UUID = Field(..., description="ID do método de pagamento")
    
    # Resultado da validação
    is_valid: bool = Field(..., description="Método válido")
    
    # Detalhes da validação
    validation_details: Dict[str, Any] = Field(..., description="Detalhes da validação")
    
    # Erros
    errors: List[str] = Field(..., description="Erros encontrados")
    
    # Timestamp
    validated_at: datetime = Field(..., description="Data da validação")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodToken(BaseModel):
    """Schema para tokenização de PaymentMethod"""
    
    method_type: str = Field(..., description="Tipo do método")
    payment_data: Dict[str, Any] = Field(..., description="Dados do método")
    
    # Configurações de tokenização
    provider_id: UUID = Field(..., description="ID do provedor")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodTokenResult(BaseModel):
    """Schema para resultado da tokenização"""
    
    token: str = Field(..., description="Token gerado")
    
    # Dados mascarados
    masked_data: Dict[str, Any] = Field(..., description="Dados mascarados")
    
    # Validade
    expires_at: Optional[datetime] = Field(None, description="Data de expiração do token")
    
    # Status
    is_valid: bool = Field(..., description="Token válido")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodCharge(BaseModel):
    """Schema para cobrança usando PaymentMethod"""
    
    method_id: UUID = Field(..., description="ID do método de pagamento")
    amount: float = Field(..., description="Valor da cobrança")
    
    # Descrição
    description: str = Field(..., description="Descrição da cobrança")
    
    # Dados adicionais
    charge_data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais da cobrança")
    
    # Contexto
    invoice_id: Optional[UUID] = Field(None, description="ID da fatura")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodChargeResult(BaseModel):
    """Schema para resultado da cobrança"""
    
    charge_id: UUID = Field(..., description="ID da cobrança")
    method_id: UUID = Field(..., description="ID do método de pagamento")
    
    # Status
    status: str = Field(..., description="Status da cobrança")
    amount: float = Field(..., description="Valor cobrado")
    
    # Transação
    transaction_id: Optional[str] = Field(None, description="ID da transação")
    
    # Timestamps
    charged_at: datetime = Field(..., description="Data da cobrança")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodHistory(BaseModel):
    """Schema para histórico de PaymentMethod"""
    
    method_id: UUID = Field(..., description="ID do método de pagamento")
    
    # Histórico de transações
    transactions: List[Dict[str, Any]] = Field(..., description="Transações")
    
    # Estatísticas
    total_transactions: int = Field(..., description="Total de transações")
    total_amount: float = Field(..., description="Valor total")
    successful_transactions: int = Field(..., description="Transações bem-sucedidas")
    failed_transactions: int = Field(..., description="Transações falhadas")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodStatistics(BaseModel):
    """Schema para estatísticas de PaymentMethod"""
    
    # Totais
    total_methods: int = Field(..., description="Total de métodos")
    active_methods: int = Field(..., description="Métodos ativos")
    
    # Por tipo
    by_method_type: Dict[str, int] = Field(..., description="Por tipo de método")
    
    # Por provedor
    by_provider: Dict[str, int] = Field(..., description="Por provedor")
    
    # Uso
    total_transactions: int = Field(..., description="Total de transações")
    successful_transactions: int = Field(..., description="Transações bem-sucedidas")
    failed_transactions: int = Field(..., description="Transações falhadas")
    
    # Valores
    total_amount: float = Field(..., description="Valor total processado")
    average_transaction_amount: float = Field(..., description="Valor médio da transação")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodSecurity(BaseModel):
    """Schema para segurança de PaymentMethod"""
    
    method_id: UUID = Field(..., description="ID do método de pagamento")
    
    # Configurações de segurança
    encryption_level: str = Field(..., description="Nível de criptografia")
    pci_compliant: bool = Field(..., description="Compatível com PCI")
    
    # Validações de segurança
    security_checks: List[Dict[str, Any]] = Field(..., description="Verificações de segurança")
    
    # Score de segurança
    security_score: float = Field(..., description="Score de segurança")
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodExport(BaseModel):
    """Schema para exportação de PaymentMethod"""
    
    format: str = Field(..., description="Formato da exportação")
    
    # Filtros
    method_type: Optional[str] = Field(None, description="Tipo de método")
    is_active: Optional[bool] = Field(None, description="Métodos ativos")
    
    # Configurações de segurança
    include_sensitive_data: bool = Field(False, description="Incluir dados sensíveis")
    mask_payment_data: bool = Field(True, description="Mascarar dados de pagamento")
    
    model_config = ConfigDict(from_attributes=True)
