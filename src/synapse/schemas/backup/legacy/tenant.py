"""
Schemas Pydantic para o modelo Tenant
Sincronizados com os campos reais do banco de dados PostgreSQL
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class TenantStatus(str, Enum):
    """Status do tenant - deve corresponder aos valores no banco"""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class TenantTheme(str, Enum):
    """Temas disponíveis para interface"""

    LIGHT = "light"
    DARK = "dark"


class TenantType(str, Enum):
    """Tipo do tenant (campo legacy, mantido para compatibilidade)"""

    INDIVIDUAL = "individual"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


# ===== SCHEMAS DE CRIAÇÃO =====


class TenantCreate(BaseModel):
    """Schema para criação de novo tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Campos obrigatórios
    name: str = Field(..., min_length=1, max_length=255, description="Nome do tenant")
    slug: str = Field(
        ..., min_length=1, max_length=120, description="Slug único do tenant"
    )
    plan_id: UUID = Field(..., description="ID do plano selecionado")

    # Campos opcionais do banco
    domain: Optional[str] = Field(
        None, max_length=255, description="Domínio personalizado"
    )
    status: TenantStatus = Field(
        TenantStatus.ACTIVE, description="Status inicial do tenant"
    )
    theme: Optional[TenantTheme] = Field(
        TenantTheme.LIGHT, description="Tema da interface"
    )
    default_language: Optional[str] = Field(
        "en", min_length=2, max_length=10, description="Idioma padrão"
    )
    timezone: Optional[str] = Field("UTC", max_length=50, description="Timezone padrão")

    # Configurações de segurança
    mfa_required: Optional[bool] = Field(False, description="MFA obrigatório")
    session_timeout: Optional[int] = Field(
        3600, ge=300, le=86400, description="Timeout da sessão em segundos"
    )
    ip_whitelist: Optional[List[str]] = Field(
        default_factory=list, description="Lista de IPs permitidos"
    )

    # Limites (opcional, se não definido usa os do plano)
    max_storage_mb: Optional[int] = Field(
        None, ge=0, description="Limite de storage em MB"
    )
    max_workspaces: Optional[int] = Field(
        None, ge=1, description="Máximo de workspaces"
    )
    max_api_calls_per_day: Optional[int] = Field(
        None, ge=0, description="Limite de chamadas API por dia"
    )
    max_members_per_workspace: Optional[int] = Field(
        None, ge=1, description="Máximo de membros por workspace"
    )

    # Features habilitadas
    enabled_features: Optional[List[str]] = Field(
        default_factory=list, description="Features habilitadas"
    )

    # Campos legacy para compatibilidade (não salvos no banco)
    description: Optional[str] = Field(None, description="Descrição (campo legacy)")
    logo_url: Optional[str] = Field(
        None, max_length=500, description="URL do logo (campo legacy)"
    )
    website: Optional[str] = Field(
        None, max_length=255, description="Website (campo legacy)"
    )
    type: Optional[TenantType] = Field(
        TenantType.INDIVIDUAL, description="Tipo do tenant (campo legacy)"
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validar formato do slug"""
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug deve conter apenas letras minúsculas, números e hífens"
            )
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug não pode começar ou terminar com hífen")
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato do domínio"""
        if v is None:
            return v
        import re

        domain_pattern = (
            r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError("Formato de domínio inválido")
        return v.lower()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validar timezone"""
        if v is None:
            return v
        try:
            import pytz

            pytz.timezone(v)
        except Exception:
            raise ValueError(f"Timezone inválida: {v}")
        return v

    @field_validator("ip_whitelist")
    @classmethod
    def validate_ip_whitelist(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validar lista de IPs"""
        if not v:
            return v
        import ipaddress

        for ip in v:
            try:
                ipaddress.ip_network(ip, strict=False)
            except ValueError:
                raise ValueError(f"IP ou CIDR inválido: {ip}")
        return v

    @field_validator("enabled_features")
    @classmethod
    def validate_enabled_features(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validar features habilitadas"""
        if not v:
            return v

        valid_features = [
            "analytics",
            "api_access",
            "advanced_workflows",
            "priority_support",
            "custom_integrations",
            "sso",
            "audit_logs",
            "data_export",
            "white_labeling",
            "custom_domains",
            "unlimited_storage",
        ]

        for feature in v:
            if feature not in valid_features:
                raise ValueError(
                    f"Feature inválida: {feature}. Features válidas: {valid_features}"
                )

        return list(set(v))  # Remove duplicatas


# ===== SCHEMAS DE ATUALIZAÇÃO =====


class TenantUpdate(BaseModel):
    """Schema para atualização de tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Campos básicos
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    status: Optional[TenantStatus] = None
    theme: Optional[TenantTheme] = None
    default_language: Optional[str] = Field(None, min_length=2, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)

    # Configurações de segurança
    mfa_required: Optional[bool] = None
    session_timeout: Optional[int] = Field(None, ge=300, le=86400)
    ip_whitelist: Optional[List[str]] = None

    # Plano e limites
    plan_id: Optional[UUID] = None
    max_storage_mb: Optional[int] = Field(None, ge=0)
    max_workspaces: Optional[int] = Field(None, ge=1)
    max_api_calls_per_day: Optional[int] = Field(None, ge=0)
    max_members_per_workspace: Optional[int] = Field(None, ge=1)

    # Features
    enabled_features: Optional[List[str]] = None

    # Campos legacy
    description: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=255)
    type: Optional[TenantType] = None

    # Aplicar as mesmas validações do TenantCreate
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import re

        domain_pattern = (
            r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError("Formato de domínio inválido")
        return v.lower()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            import pytz

            pytz.timezone(v)
        except Exception:
            raise ValueError(f"Timezone inválida: {v}")
        return v

    @field_validator("ip_whitelist")
    @classmethod
    def validate_ip_whitelist(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if not v:
            return v
        import ipaddress

        for ip in v:
            try:
                ipaddress.ip_network(ip, strict=False)
            except ValueError:
                raise ValueError(f"IP ou CIDR inválido: {ip}")
        return v

    @field_validator("enabled_features")
    @classmethod
    def validate_enabled_features(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if not v:
            return v

        valid_features = [
            "analytics",
            "api_access",
            "advanced_workflows",
            "priority_support",
            "custom_integrations",
            "sso",
            "audit_logs",
            "data_export",
            "white_labeling",
            "custom_domains",
            "unlimited_storage",
        ]

        for feature in v:
            if feature not in valid_features:
                raise ValueError(
                    f"Feature inválida: {feature}. Features válidas: {valid_features}"
                )

        return list(set(v))


# ===== SCHEMAS DE RESPOSTA =====


class TenantResponse(BaseModel):
    """Schema completo de resposta do tenant com todos os campos"""

    model_config = ConfigDict(from_attributes=True)

    # Campos do banco de dados
    id: UUID
    name: str
    slug: str
    domain: Optional[str] = None
    status: str
    theme: Optional[str] = None
    default_language: Optional[str] = None
    timezone: Optional[str] = None
    mfa_required: Optional[bool] = None
    session_timeout: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None
    plan_id: Optional[UUID] = None
    max_storage_mb: Optional[int] = None
    max_workspaces: Optional[int] = None
    max_api_calls_per_day: Optional[int] = None
    max_members_per_workspace: Optional[int] = None
    enabled_features: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Campos legacy (do modelo, não do banco)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    max_users: Optional[int] = None
    max_storage_gb: Optional[int] = None
    user_count: Optional[int] = None
    workspace_count: Optional[int] = None
    storage_used_gb: Optional[int] = None
    last_activity_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    subscription_status: Optional[str] = None

    # Propriedades computadas
    is_active: Optional[bool] = None
    is_trial: Optional[bool] = None
    is_trial_expired: Optional[bool] = None

    # Relacionamentos expandidos
    plan: Optional[Dict[str, Any]] = None


class TenantPublic(BaseModel):
    """Schema público do tenant (informações não sensíveis)"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    domain: Optional[str] = None
    theme: Optional[str] = None
    default_language: Optional[str] = None
    timezone: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: datetime


class TenantSummary(BaseModel):
    """Schema resumido do tenant para listagens"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    status: str
    plan_id: Optional[UUID] = None
    workspace_count: Optional[int] = None
    user_count: Optional[int] = None
    created_at: datetime


# ===== SCHEMAS PARA ESTATÍSTICAS =====


class TenantStats(BaseModel):
    """Schema para estatísticas do tenant"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID
    tenant_name: str
    workspace_count: int = 0
    user_count: int = 0
    conversation_count: int = 0
    message_count: int = 0
    status: str
    storage_used_gb: int = 0
    max_storage_gb: int = 10
    storage_usage_percent: float = 0.0
    last_activity_at: Optional[datetime] = None
    subscription_status: str = "trial"
    trial_ends_at: Optional[datetime] = None
    created_at: datetime

    # Limites atuais baseados no plano
    api_calls_today: int = 0
    api_calls_this_month: int = 0
    max_api_calls_per_day: Optional[int] = None

    # Usage insights
    features_usage: Dict[str, int] = Field(default_factory=dict)
    most_active_workspace: Optional[Dict[str, Any]] = None


# ===== SCHEMAS PARA CONFIGURAÇÕES =====


class TenantSecuritySettings(BaseModel):
    """Schema para configurações de segurança"""

    model_config = ConfigDict(str_strip_whitespace=True)

    mfa_required: bool = False
    session_timeout: int = Field(3600, ge=300, le=86400)
    ip_whitelist: List[str] = Field(default_factory=list)
    password_policy: Dict[str, Any] = Field(default_factory=dict)
    login_attempts_limit: int = Field(5, ge=3, le=10)

    @field_validator("ip_whitelist")
    @classmethod
    def validate_ip_whitelist(cls, v: List[str]) -> List[str]:
        import ipaddress

        for ip in v:
            try:
                ipaddress.ip_network(ip, strict=False)
            except ValueError:
                raise ValueError(f"IP ou CIDR inválido: {ip}")
        return v


class TenantNotificationSettings(BaseModel):
    """Schema para configurações de notificação"""

    model_config = ConfigDict(from_attributes=True)

    email_notifications: bool = True
    push_notifications: bool = True
    webhook_url: Optional[str] = None
    notification_types: List[str] = Field(default_factory=list)
    quiet_hours_start: Optional[str] = None  # formato HH:MM
    quiet_hours_end: Optional[str] = None  # formato HH:MM


# ===== SCHEMAS PARA RELACIONAMENTOS =====


class TenantWithPlan(TenantResponse):
    """Tenant com informações detalhadas do plano"""

    plan: Dict[str, Any]  # Detalhes completos do plano


class TenantWithWorkspaces(TenantResponse):
    """Tenant com lista de workspaces"""

    workspaces: List[Dict[str, Any]] = Field(default_factory=list)


class TenantWithUsers(TenantResponse):
    """Tenant com lista de usuários"""

    users: List[Dict[str, Any]] = Field(default_factory=list)


# ===== UTILITÁRIOS =====


def get_tenant_fields_for_database() -> List[str]:
    """Retorna lista de campos que existem realmente no banco de dados"""
    return [
        "id",
        "name",
        "slug",
        "domain",
        "status",
        "theme",
        "default_language",
        "timezone",
        "mfa_required",
        "session_timeout",
        "ip_whitelist",
        "plan_id",
        "max_storage_mb",
        "max_workspaces",
        "max_api_calls_per_day",
        "max_members_per_workspace",
        "enabled_features",
        "created_at",
        "updated_at",
    ]


def get_tenant_legacy_fields() -> List[str]:
    """Retorna lista de campos legacy que não existem no banco"""
    return [
        "description",
        "logo_url",
        "website",
        "type",
        "settings",
        "extra_metadata",
        "max_users",
        "max_storage_gb",
        "user_count",
        "workspace_count",
        "storage_used_gb",
        "last_activity_at",
        "trial_ends_at",
        "subscription_status",
    ]
