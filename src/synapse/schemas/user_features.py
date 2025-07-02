"""
Schemas Pydantic para User Features (Subscriptions e Variables)
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
Tabelas: user_subscriptions, user_variables
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import re


# ==================== ENUMS ALINHADOS COM O BANCO ====================


class SubscriptionStatus(str, Enum):
    """Status da subscription - ALINHADO COM O BANCO"""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class BillingCycle(str, Enum):
    """Ciclos de cobrança - ALINHADO COM O BANCO"""

    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    WEEKLY = "weekly"


class PaymentMethod(str, Enum):
    """Métodos de pagamento"""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    FREE = "free"


class PaymentProvider(str, Enum):
    """Provedores de pagamento"""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    PADDLE = "paddle"
    RAZORPAY = "razorpay"
    INTERNAL = "internal"


class VariableCategory(str, Enum):
    """Categorias de variáveis do usuário"""

    API_KEYS = "api_keys"
    CREDENTIALS = "credentials"
    CONFIGURATION = "configuration"
    PREFERENCES = "preferences"
    CUSTOM = "custom"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"


# ==================== USER SUBSCRIPTIONS SCHEMAS ====================


class UserSubscriptionBase(BaseModel):
    """Schema base para subscriptions - ALINHADO COM user_subscriptions TABLE"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    plan_id: uuid.UUID = Field(..., description="ID do plano")
    status: SubscriptionStatus = Field(
        SubscriptionStatus.ACTIVE, description="Status da subscription"
    )

    # Datas importantes
    started_at: datetime = Field(..., description="Data de início")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    cancelled_at: Optional[datetime] = Field(None, description="Data de cancelamento")

    # Informações de pagamento
    payment_method: Optional[PaymentMethod] = Field(
        None, description="Método de pagamento"
    )
    payment_provider: Optional[PaymentProvider] = Field(
        None, description="Provedor de pagamento"
    )
    external_subscription_id: Optional[str] = Field(
        None, max_length=255, description="ID externo da subscription"
    )
    billing_cycle: BillingCycle = Field(
        BillingCycle.MONTHLY, description="Ciclo de cobrança"
    )

    # Período atual
    current_period_start: Optional[datetime] = Field(
        None, description="Início do período atual"
    )
    current_period_end: Optional[datetime] = Field(
        None, description="Fim do período atual"
    )

    # Métricas de uso
    current_workspaces: int = Field(0, ge=0, description="Workspaces atuais")
    current_storage_mb: float = Field(0.0, ge=0, description="Storage atual em MB")
    current_executions_this_month: int = Field(
        0, ge=0, description="Execuções este mês"
    )

    # Metadados
    subscription_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadados da subscription"
    )

    @validator("external_subscription_id")
    def validate_external_id(cls, v):
        """Valida ID externo da subscription"""
        if v and len(v.strip()) == 0:
            raise ValueError("ID externo não pode ser vazio")
        return v.strip() if v else v


class UserSubscriptionCreate(UserSubscriptionBase):
    """Schema para criação de subscriptions"""

    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class UserSubscriptionUpdate(BaseModel):
    """Schema para atualização de subscriptions"""

    plan_id: Optional[uuid.UUID] = Field(None, description="Novo plano")
    status: Optional[SubscriptionStatus] = Field(None, description="Novo status")
    expires_at: Optional[datetime] = Field(None, description="Nova data de expiração")
    cancelled_at: Optional[datetime] = Field(
        None, description="Nova data de cancelamento"
    )
    payment_method: Optional[PaymentMethod] = Field(
        None, description="Novo método de pagamento"
    )
    payment_provider: Optional[PaymentProvider] = Field(
        None, description="Novo provedor"
    )
    external_subscription_id: Optional[str] = Field(
        None, max_length=255, description="Novo ID externo"
    )
    billing_cycle: Optional[BillingCycle] = Field(None, description="Novo ciclo")
    current_period_start: Optional[datetime] = Field(
        None, description="Novo início do período"
    )
    current_period_end: Optional[datetime] = Field(
        None, description="Novo fim do período"
    )
    current_workspaces: Optional[int] = Field(
        None, ge=0, description="Novos workspaces"
    )
    current_storage_mb: Optional[float] = Field(None, ge=0, description="Novo storage")
    current_executions_this_month: Optional[int] = Field(
        None, ge=0, description="Novas execuções"
    )
    subscription_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Novos metadados"
    )


class UserSubscriptionResponse(UserSubscriptionBase):
    """Schema de resposta para subscriptions - ALINHADO COM user_subscriptions TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID = Field(..., description="ID único da subscription")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== USER VARIABLES SCHEMAS ====================


class UserVariableBase(BaseModel):
    """Schema base para variables - ALINHADO COM user_variables TABLE"""

    key: str = Field(..., min_length=1, max_length=255, description="Chave da variável")
    value: str = Field(..., description="Valor da variável")
    user_id: uuid.UUID = Field(..., description="ID do usuário")

    # Configurações de segurança
    is_secret: bool = Field(False, description="Se é uma variável secreta")
    is_encrypted: bool = Field(False, description="Se o valor está criptografado")
    is_active: bool = Field(True, description="Se a variável está ativa")

    # Metadados
    category: Optional[VariableCategory] = Field(
        None, description="Categoria da variável"
    )
    description: Optional[str] = Field(None, description="Descrição da variável")

    @validator("key")
    def validate_key(cls, v):
        """Valida formato da chave"""
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError(
                "Chave deve conter apenas letras, números, pontos, hífens e underscores"
            )
        if v.startswith(".") or v.endswith("."):
            raise ValueError("Chave não pode começar ou terminar com ponto")
        return v.strip().upper()

    @validator("value")
    def validate_value(cls, v, values):
        """Valida valor da variável"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Valor da variável é obrigatório")

        # Se for secreta, validar que não está exposta
        if values.get("is_secret") and len(v) < 8:
            raise ValueError("Variáveis secretas devem ter pelo menos 8 caracteres")

        return v


class UserVariableCreate(BaseModel):
    """Schema para criação de variables"""

    key: str = Field(..., min_length=1, max_length=255, pattern=r'^[A-Z][A-Z0-9_]*$')
    value: str = Field(..., min_length=1)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=100)
    is_encrypted: bool = False


class UserVariableUpdate(BaseModel):
    """Schema para atualização de variables"""

    value: str | None = Field(None, min_length=1)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=100)
    is_active: bool | None = None


class UserVariableResponse(UserVariableBase):
    """Schema de resposta para variables - ALINHADO COM user_variables TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID = Field(..., description="ID único da variável")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    @validator("value", pre=True)
    def mask_secret_values(cls, v, values):
        """Mascara valores secretos na resposta"""
        if values.get("is_secret"):
            return "****HIDDEN****"
        return v


class UserVariableSecureResponse(BaseModel):
    """Schema de resposta segura para variables (sem valor)"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID = Field(..., description="ID único da variável")
    key: str = Field(..., description="Chave da variável")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    is_secret: bool = Field(..., description="Se é secreta")
    is_encrypted: bool = Field(..., description="Se está criptografada")
    is_active: bool = Field(..., description="Se está ativa")
    category: Optional[VariableCategory] = Field(None, description="Categoria")
    description: Optional[str] = Field(None, description="Descrição")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Estatísticas de uso
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    usage_count: int = Field(0, description="Número de usos")


# ==================== SCHEMAS EXPANDIDOS ====================


class UserSubscriptionWithPlan(UserSubscriptionResponse):
    """Subscription com informações do plano"""

    plan_name: str = Field(..., description="Nome do plano")
    plan_description: Optional[str] = Field(None, description="Descrição do plano")
    plan_price: float = Field(..., description="Preço do plano")
    plan_currency: str = Field(..., description="Moeda do plano")
    plan_features: List[str] = Field(
        default_factory=list, description="Features do plano"
    )

    # Limites do plano
    plan_workspace_limit: Optional[int] = Field(
        None, description="Limite de workspaces"
    )
    plan_storage_limit_mb: Optional[int] = Field(None, description="Limite de storage")
    plan_execution_limit: Optional[int] = Field(None, description="Limite de execuções")

    # Percentuais de uso
    workspace_usage_percent: float = Field(0.0, description="% uso workspaces")
    storage_usage_percent: float = Field(0.0, description="% uso storage")
    execution_usage_percent: float = Field(0.0, description="% uso execuções")


class UserSubscriptionUsage(BaseModel):
    """Uso atual da subscription"""

    subscription_id: uuid.UUID = Field(..., description="ID da subscription")
    user_id: uuid.UUID = Field(..., description="ID do usuário")

    # Uso atual vs limites
    workspaces_used: int = Field(0, description="Workspaces em uso")
    workspaces_limit: Optional[int] = Field(None, description="Limite de workspaces")
    storage_used_mb: float = Field(0.0, description="Storage usado em MB")
    storage_limit_mb: Optional[int] = Field(None, description="Limite de storage")
    executions_this_month: int = Field(0, description="Execuções este mês")
    executions_limit: Optional[int] = Field(None, description="Limite de execuções")

    # Status de limites
    is_workspace_limit_reached: bool = Field(
        False, description="Limite de workspaces atingido"
    )
    is_storage_limit_reached: bool = Field(
        False, description="Limite de storage atingido"
    )
    is_execution_limit_reached: bool = Field(
        False, description="Limite de execuções atingido"
    )

    # Próximas datas importantes
    next_billing_date: Optional[datetime] = Field(None, description="Próxima cobrança")
    expiration_date: Optional[datetime] = Field(None, description="Data de expiração")
    days_until_expiration: Optional[int] = Field(None, description="Dias até expiração")


class UserVariableGroup(BaseModel):
    """Grupo de variáveis por categoria"""

    category: VariableCategory = Field(..., description="Categoria das variáveis")
    variables: List[UserVariableSecureResponse] = Field(
        ..., description="Variáveis da categoria"
    )
    total_count: int = Field(..., description="Total de variáveis")
    active_count: int = Field(..., description="Variáveis ativas")
    secret_count: int = Field(..., description="Variáveis secretas")


# ==================== SCHEMAS DE BILLING ====================


class SubscriptionBillingInfo(BaseModel):
    """Informações de cobrança da subscription"""

    subscription_id: uuid.UUID = Field(..., description="ID da subscription")

    # Valores
    current_amount: float = Field(..., description="Valor atual")
    currency: str = Field(..., description="Moeda")
    next_billing_amount: Optional[float] = Field(None, description="Próximo valor")

    # Datas
    next_billing_date: Optional[datetime] = Field(None, description="Próxima cobrança")
    last_billing_date: Optional[datetime] = Field(None, description="Última cobrança")

    # Status
    payment_status: str = Field(..., description="Status do pagamento")
    auto_renew: bool = Field(True, description="Renovação automática")

    # Informações do pagamento
    payment_method_type: Optional[str] = Field(
        None, description="Tipo do método de pagamento"
    )
    payment_method_last4: Optional[str] = Field(None, description="Últimos 4 dígitos")
    payment_method_expires: Optional[str] = Field(
        None, description="Expiração do método"
    )


class SubscriptionInvoice(BaseModel):
    """Fatura da subscription"""

    invoice_id: str = Field(..., description="ID da fatura")
    subscription_id: uuid.UUID = Field(..., description="ID da subscription")

    # Valores
    amount: float = Field(..., description="Valor da fatura")
    currency: str = Field(..., description="Moeda")
    tax_amount: float = Field(0.0, description="Valor do imposto")
    total_amount: float = Field(..., description="Valor total")

    # Datas
    invoice_date: datetime = Field(..., description="Data da fatura")
    due_date: datetime = Field(..., description="Data de vencimento")
    paid_date: Optional[datetime] = Field(None, description="Data do pagamento")

    # Status
    status: str = Field(..., description="Status da fatura")

    # Itens
    line_items: List[Dict[str, Any]] = Field(
        default_factory=list, description="Itens da fatura"
    )


# ==================== SCHEMAS DE BUSCA E FILTROS ====================


class UserSubscriptionSearchRequest(BaseModel):
    """Schema para busca de subscriptions"""

    user_ids: Optional[List[uuid.UUID]] = Field(None, description="IDs dos usuários")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    plan_ids: Optional[List[uuid.UUID]] = Field(None, description="IDs dos planos")
    statuses: Optional[List[SubscriptionStatus]] = Field(None, description="Status")
    payment_providers: Optional[List[PaymentProvider]] = Field(
        None, description="Provedores"
    )
    billing_cycles: Optional[List[BillingCycle]] = Field(
        None, description="Ciclos de cobrança"
    )

    # Filtros por data
    started_after: Optional[datetime] = Field(None, description="Iniciado após")
    started_before: Optional[datetime] = Field(None, description="Iniciado antes")
    expires_after: Optional[datetime] = Field(None, description="Expira após")
    expires_before: Optional[datetime] = Field(None, description="Expira antes")

    # Filtros por uso
    min_workspaces: Optional[int] = Field(
        None, ge=0, description="Mínimo de workspaces"
    )
    max_workspaces: Optional[int] = Field(
        None, ge=0, description="Máximo de workspaces"
    )
    min_storage_mb: Optional[float] = Field(None, ge=0, description="Mínimo de storage")
    max_storage_mb: Optional[float] = Field(None, ge=0, description="Máximo de storage")

    # Paginação
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(50, ge=1, le=200, description="Tamanho da página")


class UserVariableSearchRequest(BaseModel):
    """Schema para busca de variables"""

    query: str = Field(..., min_length=1, max_length=100)
    category: str | None = None
    is_active: bool | None = None


# ==================== SCHEMAS DE LISTAGEM ====================


class UserSubscriptionListResponse(BaseModel):
    """Schema para listagem de subscriptions"""

    subscriptions: List[UserSubscriptionResponse] = Field(
        ..., description="Lista de subscriptions"
    )
    total: int = Field(..., description="Total de subscriptions")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")

    # Estatísticas
    active_count: int = Field(0, description="Subscriptions ativas")
    expired_count: int = Field(0, description="Subscriptions expiradas")
    trial_count: int = Field(0, description="Subscriptions em trial")


class UserVariableListResponse(BaseModel):
    """Schema para listagem de variables"""

    variables: List[UserVariableSecureResponse] = Field(
        ..., description="Lista de variáveis"
    )
    total: int = Field(..., description="Total de variáveis")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")

    # Agrupamento por categoria
    by_category: List[UserVariableGroup] = Field(
        default_factory=list, description="Agrupado por categoria"
    )

    # Estatísticas
    active_count: int = Field(0, description="Variáveis ativas")
    secret_count: int = Field(0, description="Variáveis secretas")
    encrypted_count: int = Field(0, description="Variáveis criptografadas")


# ==================== SCHEMAS DE BULK OPERATIONS ====================


class BulkVariableCreate(BaseModel):
    """Schema para criação em lote de variáveis"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    variables: List[Dict[str, Any]] = Field(
        ..., min_items=1, description="Lista de variáveis"
    )
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    default_category: Optional[VariableCategory] = Field(
        None, description="Categoria padrão"
    )


class BulkVariableUpdate(BaseModel):
    """Schema para atualização em lote de variáveis"""

    variable_ids: List[uuid.UUID] = Field(
        ..., min_items=1, description="IDs das variáveis"
    )
    updates: Dict[str, Any] = Field(..., description="Atualizações a aplicar")


class BulkVariableResult(BaseModel):
    """Resultado de operação em lote de variáveis"""

    created: int = Field(0, description="Quantidade criada")
    updated: int = Field(0, description="Quantidade atualizada")
    errors: List[str] = Field(default_factory=list, description="Erros encontrados")
    variables: List[UserVariableSecureResponse] = Field(
        default_factory=list, description="Variáveis processadas"
    )


# ==================== SCHEMAS DE IMPORTAÇÃO/EXPORTAÇÃO ====================


class VariableExportRequest(BaseModel):
    """Schema para exportação de variáveis"""

    format: str = Field(..., pattern=r'^(env|json|yaml)$')
    include_inactive: bool = False
    category: str | None = None


class VariableImportRequest(BaseModel):
    """Schema para importação de variáveis"""

    source: str = Field(..., pattern=r'^(env_file|text|json)$')
    content: str = Field(..., min_length=1)
    replace_existing: bool = False
    category: str | None = Field(None, max_length=100)


class VariableImportResult(BaseModel):
    """Resultado da importação de variáveis"""

    imported: int
    skipped: int
    errors: list[str]
    warnings: list[str]
    created_variables: List[UserVariableSecureResponse] = Field(
        default_factory=list, description="Variáveis criadas"
    )


# ==================== VARIABLE SCHEMAS ====================

class UserVariableStats(BaseModel):
    total_variables: int
    active_variables: int
    inactive_variables: int
    sensitive_variables: int
    categories_count: dict[str, int]
    last_updated: datetime | None = None

class UserVariableValidation(BaseModel):
    key: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggestions: list[str]
