"""
Schemas Pydantic para Tenants e Tenant Features
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
Tabelas: tenants, tenant_features
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import re


# ==================== ENUMS ALINHADOS COM O BANCO ====================


class TenantStatus(str, Enum):
    """Status do tenant - ALINHADO COM O BANCO"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class TenantTheme(str, Enum):
    """Temas disponíveis para tenants"""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class BillingCycle(str, Enum):
    """Ciclos de cobrança"""

    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"


# ==================== TENANT SCHEMAS ====================


class TenantBase(BaseModel):
    """Schema base para tenants - ALINHADO COM tenants TABLE"""

    name: str = Field(..., min_length=1, max_length=255, description="Nome do tenant")
    slug: str = Field(
        ..., min_length=3, max_length=100, description="Slug único do tenant"
    )
    domain: Optional[str] = Field(
        None, max_length=255, description="Domínio personalizado"
    )
    status: TenantStatus = Field(TenantStatus.ACTIVE, description="Status do tenant")

    # Configurações de aparência
    theme: TenantTheme = Field(TenantTheme.LIGHT, description="Tema da interface")
    default_language: str = Field("en", max_length=10, description="Idioma padrão")
    timezone: str = Field("UTC", max_length=50, description="Fuso horário padrão")

    # Configurações de segurança
    mfa_required: bool = Field(False, description="Se MFA é obrigatório")
    session_timeout: int = Field(
        3600, ge=300, le=86400, description="Timeout da sessão em segundos"
    )
    ip_whitelist: List[str] = Field(
        default_factory=list, description="Lista de IPs permitidos"
    )

    # Limites de recursos
    max_storage_mb: Optional[int] = Field(
        None, ge=0, description="Limite de armazenamento em MB"
    )
    max_workspaces: Optional[int] = Field(
        None, ge=0, description="Limite de workspaces"
    )
    max_api_calls_per_day: Optional[int] = Field(
        None, ge=0, description="Limite de chamadas API por dia"
    )
    max_members_per_workspace: Optional[int] = Field(
        None, ge=1, description="Limite de membros por workspace"
    )

    # Features habilitadas
    enabled_features: List[str] = Field(
        default_factory=list, description="Features habilitadas"
    )

    @validator("slug")
    def validate_slug(cls, v):
        """Valida formato do slug"""
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug deve conter apenas letras minúsculas, números e hífens"
            )
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug não pode começar ou terminar com hífen")
        if "--" in v:
            raise ValueError("Slug não pode ter hífens consecutivos")
        return v

    @validator("domain")
    def validate_domain(cls, v):
        """Valida formato do domínio"""
        if v:
            # Regex básica para validação de domínio
            if not re.match(
                r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.([a-zA-Z]{2,})+$", v
            ):
                raise ValueError("Formato de domínio inválido")
        return v

    @validator("ip_whitelist")
    def validate_ip_whitelist(cls, v):
        """Valida lista de IPs"""
        if v:
            import ipaddress

            for ip in v:
                try:
                    ipaddress.ip_network(ip, strict=False)
                except ValueError:
                    raise ValueError(f"IP inválido na whitelist: {ip}")
        return v


class TenantCreate(TenantBase):
    """Schema para criação de tenants"""

    plan_id: uuid.UUID = Field(..., description="ID do plano do tenant")


class TenantUpdate(BaseModel):
    """Schema para atualização de tenants"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    domain: Optional[str] = Field(None, max_length=255, description="Novo domínio")
    status: Optional[TenantStatus] = Field(None, description="Novo status")
    plan_id: Optional[uuid.UUID] = Field(None, description="Novo plano")

    # Configurações de aparência
    theme: Optional[TenantTheme] = Field(None, description="Novo tema")
    default_language: Optional[str] = Field(
        None, max_length=10, description="Novo idioma padrão"
    )
    timezone: Optional[str] = Field(
        None, max_length=50, description="Novo fuso horário"
    )

    # Configurações de segurança
    mfa_required: Optional[bool] = Field(None, description="Novo status MFA")
    session_timeout: Optional[int] = Field(
        None, ge=300, le=86400, description="Novo timeout"
    )
    ip_whitelist: Optional[List[str]] = Field(None, description="Nova whitelist de IPs")

    # Limites de recursos
    max_storage_mb: Optional[int] = Field(
        None, ge=0, description="Novo limite de storage"
    )
    max_workspaces: Optional[int] = Field(
        None, ge=0, description="Novo limite de workspaces"
    )
    max_api_calls_per_day: Optional[int] = Field(
        None, ge=0, description="Novo limite de API calls"
    )
    max_members_per_workspace: Optional[int] = Field(
        None, ge=1, description="Novo limite de membros"
    )

    # Features habilitadas
    enabled_features: Optional[List[str]] = Field(
        None, description="Novas features habilitadas"
    )


class TenantResponse(TenantBase):
    """Schema de resposta para tenants - ALINHADO COM tenants TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID = Field(..., description="ID único do tenant")
    plan_id: uuid.UUID = Field(..., description="ID do plano")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== TENANT FEATURES SCHEMAS ====================


class TenantFeatureBase(BaseModel):
    """Schema base para tenant features - ALINHADO COM tenant_features TABLE"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se a feature está habilitada")
    usage_count: int = Field(0, ge=0, description="Contador de uso")
    limit_value: Optional[int] = Field(None, ge=0, description="Limite de uso")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Configurações da feature"
    )
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")


class TenantFeatureCreate(TenantFeatureBase):
    """Schema para criação de tenant features"""

    pass


class TenantFeatureUpdate(BaseModel):
    """Schema para atualização de tenant features"""

    is_enabled: Optional[bool] = Field(None, description="Novo status")
    usage_count: Optional[int] = Field(None, ge=0, description="Novo contador")
    limit_value: Optional[int] = Field(None, ge=0, description="Novo limite")
    config: Optional[Dict[str, Any]] = Field(None, description="Novas configurações")
    expires_at: Optional[datetime] = Field(None, description="Nova data de expiração")


class TenantFeatureResponse(TenantFeatureBase):
    """Schema de resposta para tenant features - ALINHADO COM tenant_features TABLE"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único da feature do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== SCHEMAS EXPANDIDOS ====================


class TenantWithFeatures(TenantResponse):
    """Tenant com suas features"""

    features: List[TenantFeatureResponse] = Field(
        default_factory=list, description="Features do tenant"
    )
    feature_count: int = Field(0, description="Total de features")
    active_features: int = Field(0, description="Features ativas")


class TenantUsageStats(BaseModel):
    """Estatísticas de uso do tenant"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    current_workspaces: int = Field(0, description="Workspaces atuais")
    current_users: int = Field(0, description="Usuários atuais")
    current_storage_mb: float = Field(0.0, description="Storage atual em MB")
    api_calls_today: int = Field(0, description="Chamadas API hoje")
    api_calls_this_month: int = Field(0, description="Chamadas API este mês")

    # Percentuais de uso dos limites
    workspace_usage_percent: float = Field(0.0, description="% de uso de workspaces")
    storage_usage_percent: float = Field(0.0, description="% de uso de storage")
    api_usage_percent: float = Field(0.0, description="% de uso de API")

    last_calculated: datetime = Field(..., description="Última atualização dos stats")


class TenantSettings(BaseModel):
    """Configurações avançadas do tenant"""

    # Configurações de notificação
    email_notifications: bool = Field(True, description="Notificações por email")
    slack_webhook: Optional[str] = Field(None, description="Webhook do Slack")
    webhook_events: List[str] = Field(
        default_factory=list, description="Eventos para webhook"
    )

    # Configurações de API
    api_rate_limit: int = Field(1000, description="Rate limit da API")
    webhook_secret: Optional[str] = Field(None, description="Secret para webhooks")

    # Configurações de backup
    auto_backup_enabled: bool = Field(False, description="Backup automático")
    backup_frequency: str = Field("daily", description="Frequência do backup")
    backup_retention_days: int = Field(30, description="Dias de retenção do backup")

    # Configurações de compliance
    gdpr_compliant: bool = Field(False, description="Compliance com GDPR")
    data_retention_days: int = Field(365, description="Dias de retenção de dados")
    audit_logging_enabled: bool = Field(True, description="Log de auditoria")


class TenantWithSettings(TenantResponse):
    """Tenant com configurações avançadas"""

    settings: TenantSettings = Field(..., description="Configurações do tenant")
    usage_stats: Optional[TenantUsageStats] = Field(
        None, description="Estatísticas de uso"
    )


# ==================== SCHEMAS DE BILLING E SUBSCRIPTION ====================


class TenantBillingInfo(BaseModel):
    """Informações de cobrança do tenant"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    billing_email: str = Field(..., description="Email de cobrança")
    billing_name: str = Field(..., description="Nome para cobrança")
    billing_address: Optional[Dict[str, str]] = Field(
        None, description="Endereço de cobrança"
    )
    tax_id: Optional[str] = Field(None, description="ID fiscal")
    currency: str = Field("USD", description="Moeda preferida")
    billing_cycle: BillingCycle = Field(
        BillingCycle.MONTHLY, description="Ciclo de cobrança"
    )


class TenantQuota(BaseModel):
    """Quotas e limites do tenant"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant")

    # Quotas atuais
    users_quota: int = Field(0, description="Quota de usuários")
    workspaces_quota: int = Field(0, description="Quota de workspaces")
    storage_quota_mb: int = Field(0, description="Quota de storage em MB")
    api_calls_quota: int = Field(0, description="Quota de chamadas API")

    # Uso atual
    users_used: int = Field(0, description="Usuários em uso")
    workspaces_used: int = Field(0, description="Workspaces em uso")
    storage_used_mb: float = Field(0.0, description="Storage em uso")
    api_calls_used: int = Field(0, description="API calls usadas")

    # Timestamps
    quota_reset_date: datetime = Field(..., description="Data de reset das quotas")
    last_updated: datetime = Field(..., description="Última atualização")


# ==================== SCHEMAS DE LISTAGEM E BUSCA ====================


class TenantListResponse(BaseModel):
    """Schema para listagem de tenants"""

    tenants: List[TenantResponse] = Field(..., description="Lista de tenants")
    total: int = Field(..., description="Total de tenants")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")


class TenantSearchRequest(BaseModel):
    """Schema para busca de tenants"""

    query: Optional[str] = Field(None, description="Termo de busca")
    status: Optional[TenantStatus] = Field(None, description="Filtrar por status")
    plan_id: Optional[uuid.UUID] = Field(None, description="Filtrar por plano")
    theme: Optional[TenantTheme] = Field(None, description="Filtrar por tema")
    has_domain: Optional[bool] = Field(
        None, description="Filtrar por domínio personalizado"
    )
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Tamanho da página")


class TenantFeatureListResponse(BaseModel):
    """Schema para listagem de tenant features"""

    features: List[TenantFeatureResponse] = Field(..., description="Lista de features")
    total: int = Field(..., description="Total de features")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")


# ==================== SCHEMAS DE BULK OPERATIONS ====================


class BulkTenantFeatureUpdate(BaseModel):
    """Schema para atualização em lote de features"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    feature_updates: List[Dict[str, Any]] = Field(
        ..., description="Lista de atualizações"
    )


class BulkTenantFeatureResult(BaseModel):
    """Resultado de operação em lote de features"""

    updated: int = Field(..., description="Quantidade atualizada")
    errors: List[str] = Field(default_factory=list, description="Erros encontrados")
    features: List[TenantFeatureResponse] = Field(
        default_factory=list, description="Features atualizadas"
    )


# ==================== SCHEMAS DE MIGRAÇÃO E BACKUP ====================


class TenantExportRequest(BaseModel):
    """Schema para exportação de dados do tenant"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    include_users: bool = Field(True, description="Incluir dados de usuários")
    include_workspaces: bool = Field(True, description="Incluir workspaces")
    include_workflows: bool = Field(True, description="Incluir workflows")
    include_files: bool = Field(True, description="Incluir arquivos")
    format: str = Field("json", description="Formato da exportação")


class TenantImportRequest(BaseModel):
    """Schema para importação de dados do tenant"""

    tenant_id: uuid.UUID = Field(..., description="ID do tenant de destino")
    data_source: str = Field(..., description="Fonte dos dados")
    merge_strategy: str = Field("skip", description="Estratégia de merge")
    validate_only: bool = Field(False, description="Apenas validar sem importar")
