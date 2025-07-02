"""
Schemas Pydantic para Workspaces - Sistema Centralizado
Criado por José - um desenvolvedor Full Stack
Validação e serialização para workspaces colaborativos usando configurações centralizadas
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict

# Import do sistema centralizado
from synapse.core.schemas import (
    CommonFields,
    BaseResponseSchema,
    PaginationSchema,
    TimestampSchema,
    TenantSchema,
    CommonValidatorsMixin,
)
from synapse.core.schemas.validators import (
    validate_uuid,
    validate_email,
    validate_title,
    validate_description,
    validate_slug,
    validate_configuration,
    validate_metadata,
    validate_status,
    validate_color_hex,
    validate_pagination_limit,
    validate_pagination_skip,
)

from synapse.models.workspace import WorkspaceType

# from synapse.models.subscription import PlanType  # REMOVIDO - campo type não existe

# ==================== ENUMS ====================


class WorkspaceRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


# ==================== PLAN SCHEMAS (CENTRALIZADOS) ====================


class PlanResponse(BaseResponseSchema, TenantSchema, TimestampSchema):
    """Schema centralizado para resposta de plano - usando sistema unificado"""

    # Campos específicos do plano
    id: str = CommonFields.id
    name: str = CommonFields.name
    slug: str = CommonFields.slug
    description: str | None = CommonFields.short_description

    # Configurações de preço
    price_monthly: float = Field(0.0, ge=0, description="Preço mensal em USD")
    price_yearly: float = Field(0.0, ge=0, description="Preço anual em USD")

    # Limites do plano - usando campos centralizados
    max_workspaces: int = Field(1, ge=1, le=1000, description="Máximo de workspaces")
    max_members_per_workspace: int = Field(
        1, ge=1, le=10000, description="Máximo de membros por workspace"
    )
    max_projects_per_workspace: int = Field(
        10, ge=1, le=100000, description="Máximo de projetos por workspace"
    )
    max_storage_mb: int = Field(
        100, ge=10, le=100000, description="Máximo de armazenamento em MB"
    )
    max_executions_per_month: int = Field(
        100, ge=1, le=1000000, description="Máximo de execuções por mês"
    )

    # Recursos do plano
    allow_collaborative_workspaces: bool = Field(
        False, description="Permite workspaces colaborativos"
    )
    allow_custom_domains: bool = Field(
        False, description="Permite domínios customizados"
    )
    allow_api_access: bool = Field(False, description="Permite acesso à API")
    allow_advanced_analytics: bool = Field(
        False, description="Permite analytics avançados"
    )
    allow_priority_support: bool = Field(
        False, description="Permite suporte prioritário"
    )

    # Status do plano
    is_active: bool = Field(True, description="Plano ativo")
    is_public: bool = Field(True, description="Plano público")

    # Herda automaticamente: tenant_id, created_at, updated_at, success, message


# ==================== WORKSPACE SCHEMAS (CENTRALIZADOS) ====================


class WorkspaceBase(CommonValidatorsMixin, BaseModel):
    """Schema base centralizado para workspace"""

    # Campos obrigatórios usando definições centralizadas
    name: str = CommonFields.name
    description: str | None = CommonFields.short_description

    # Configurações visuais
    avatar_url: str | None = CommonFields.avatar_url
    color: str | None = Field(
        "#3B82F6",
        description="Cor do workspace em hexadecimal",
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    # Configurações de acesso
    is_public: bool = Field(False, description="Workspace público")
    allow_guest_access: bool = Field(False, description="Permite acesso de convidados")
    require_approval: bool = Field(True, description="Requer aprovação para membros")

    # Limites usando constantes centralizadas
    max_members: int = Field(10, ge=1, le=1000, description="Máximo de membros")
    max_projects: int = Field(50, ge=1, le=10000, description="Máximo de projetos")
    max_storage_mb: int = Field(
        1000, ge=100, le=100000, description="Máximo de armazenamento em MB"
    )

    # Recursos
    enable_real_time_editing: bool = Field(
        True, description="Habilita edição em tempo real"
    )
    enable_comments: bool = Field(True, description="Habilita comentários")
    enable_chat: bool = Field(True, description="Habilita chat")
    enable_video_calls: bool = Field(False, description="Habilita chamadas de vídeo")

    # Configurações usando validador centralizado
    notification_settings: Dict[str, Any] | None = CommonFields.configuration


class WorkspaceCreate(WorkspaceBase):
    """Schema para criação de workspace usando sistema centralizado"""

    type: WorkspaceType = Field(
        WorkspaceType.COLLABORATIVE, description="Tipo do workspace"
    )

    # Valores padrão explícitos para criação
    is_public: bool = Field(False, description="Workspace público")
    allow_guest_access: bool = Field(False, description="Permite acesso de convidados")
    require_approval: bool = Field(True, description="Requer aprovação")
    enable_real_time_editing: bool = Field(True, description="Edição em tempo real")
    enable_comments: bool = Field(True, description="Comentários habilitados")
    enable_chat: bool = Field(True, description="Chat habilitado")
    enable_video_calls: bool = Field(False, description="Chamadas de vídeo")
    notification_settings: Dict[str, Any] | None = None


class WorkspaceUpdate(CommonValidatorsMixin, BaseModel):
    """Schema para atualização de workspace usando validadores centralizados"""

    # Todos os campos opcionais para update
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    avatar_url: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_public: bool | None = None
    allow_guest_access: bool | None = None
    require_approval: bool | None = None
    max_members: int | None = Field(None, ge=1, le=1000)
    max_projects: int | None = Field(None, ge=1, le=10000)
    max_storage_mb: int | None = Field(None, ge=100, le=100000)
    enable_real_time_editing: bool | None = None
    enable_comments: bool | None = None
    enable_chat: bool | None = None
    enable_video_calls: bool | None = None
    notification_settings: Dict[str, Any] | None = None


class WorkspaceResponse(WorkspaceBase, TenantSchema, TimestampSchema):
    """Schema de resposta de workspace usando sistema centralizado completo"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    slug: str = CommonFields.slug
    type: WorkspaceType = Field(..., description="Tipo do workspace")
    owner_id: UUID = Field(..., description="ID do proprietário")
    owner_name: str | None = Field(None, description="Nome do proprietário")

    # Relacionamento com plano via sistema centralizado
    plan: Optional[PlanResponse] = Field(
        None, description="Plano do workspace via tenant"
    )

    # Configurações usando valores padrão centralizados
    is_template: bool = Field(False, description="É um template")

    # Estatísticas de uso
    member_count: int = Field(0, ge=0, description="Número de membros")
    project_count: int = Field(0, ge=0, description="Número de projetos")
    activity_count: int = Field(0, ge=0, description="Número de atividades")
    storage_used_mb: float = Field(0.0, ge=0, description="Armazenamento usado em MB")

    # Status usando validador centralizado
    status: str = Field("active", description="Status do workspace")
    last_activity_at: datetime | None = Field(None, description="Última atividade")

    # Herda automaticamente: tenant_id, created_at, updated_at

    # Validadores usando sistema centralizado - apenas campos que existem nesta classe
    @validator("id", "owner_id", pre=True)
    def validate_uuids(cls, v):
        """Valida UUIDs usando validador centralizado"""
        return str(validate_uuid(v)) if v else v


# ==================== MEMBER SCHEMAS (CENTRALIZADOS) ====================


class MemberInvite(CommonValidatorsMixin, BaseModel):
    """Schema para convite de membro usando validadores centralizados"""

    email: str = CommonFields.email
    role: WorkspaceRole = Field(WorkspaceRole.MEMBER, description="Papel no workspace")
    message: str | None = Field(None, max_length=500, description="Mensagem do convite")


class MemberResponse(TimestampSchema, BaseModel):
    """Schema de resposta de membro usando timestamps centralizados"""

    # Identificadores
    id: int = Field(..., description="ID do membro")
    workspace_id: UUID = CommonFields.workspace_id
    user_id: UUID = CommonFields.user_id

    # Informações do usuário
    user_name: str = CommonFields.name
    user_email: str = CommonFields.email
    user_avatar: str | None = CommonFields.avatar_url

    # Papel e status
    role: WorkspaceRole = Field(..., description="Papel no workspace")
    status: str = Field("active", description="Status do membro")

    # Timestamps específicos
    joined_at: datetime = Field(..., description="Data de entrada")
    last_active_at: datetime | None = Field(None, description="Última atividade")

    # Herda automaticamente: created_at, updated_at

    @validator("workspace_id", "user_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


class MemberUpdate(BaseModel):
    """Schema para atualização de membro"""

    role: WorkspaceRole = Field(..., description="Novo papel no workspace")


# ==================== INVITATION SCHEMAS (CENTRALIZADOS) ====================


class InvitationResponse(TenantSchema, TimestampSchema, BaseModel):
    """Schema de resposta de convite usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    workspace_id: UUID = CommonFields.workspace_id
    workspace_name: str = CommonFields.name
    inviter_id: UUID = CommonFields.user_id
    inviter_name: str = CommonFields.name

    # Dados do convite
    email: str = CommonFields.email
    role: WorkspaceRole = Field(..., description="Papel oferecido")
    message: str | None = CommonFields.short_description
    token: str = Field(..., description="Token de verificação")
    status: InvitationStatus = Field(..., description="Status do convite")

    # Timestamps específicos
    expires_at: datetime = Field(..., description="Data de expiração")
    responded_at: datetime | None = Field(None, description="Data da resposta")

    # Herda automaticamente: tenant_id, created_at, updated_at

    @validator("id", "workspace_id", "inviter_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


# ==================== PROJECT SCHEMAS (CENTRALIZADOS) ====================


class ProjectBase(CommonValidatorsMixin, BaseModel):
    """Schema base centralizado para projeto"""

    # Campos obrigatórios usando definições centralizadas
    name: str = CommonFields.name
    description: str | None = CommonFields.short_description

    # Configurações visuais
    color: str | None = Field(
        "#10B981",
        description="Cor do projeto em hexadecimal",
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    # Configurações de colaboração
    allow_concurrent_editing: bool = Field(
        True, description="Permite edição concorrente"
    )
    auto_save_interval: int = Field(
        30, ge=5, le=300, description="Intervalo de auto-save em segundos"
    )
    version_control_enabled: bool = Field(
        True, description="Controle de versão habilitado"
    )


class ProjectCreate(ProjectBase):
    """Schema para criação de projeto usando sistema centralizado"""

    workflow_id: UUID | None = Field(None, description="ID do workflow associado")


class ProjectUpdate(CommonValidatorsMixin, BaseModel):
    """Schema para atualização de projeto usando validadores centralizados"""

    # Todos os campos opcionais para update
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    allow_concurrent_editing: bool | None = None
    auto_save_interval: int | None = Field(None, ge=5, le=300)
    version_control_enabled: bool | None = None


class ProjectResponse(ProjectBase, TimestampSchema, BaseModel):
    """Schema de resposta de projeto usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    workspace_id: UUID = CommonFields.workspace_id
    workflow_id: UUID = Field(..., description="ID do workflow")

    # Estatísticas de uso
    collaborator_count: int = Field(0, ge=0, description="Número de colaboradores")
    comment_count: int = Field(0, ge=0, description="Número de comentários")
    version_count: int = Field(0, ge=0, description="Número de versões")

    # Status e atividade
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Status do projeto")
    last_edited_at: datetime | None = Field(None, description="Última edição")

    # Herda automaticamente: created_at, updated_at

    @validator("id", "workspace_id", "workflow_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


# ==================== COLLABORATOR SCHEMAS (CENTRALIZADOS) ====================


class CollaboratorPermissions(BaseModel):
    """Schema centralizado para permissões de colaborador"""

    can_edit: bool = Field(True, description="Pode editar")
    can_comment: bool = Field(True, description="Pode comentar")
    can_share: bool = Field(False, description="Pode compartilhar")
    can_delete: bool = Field(False, description="Pode deletar")


class CollaboratorAdd(BaseModel):
    """Schema para adicionar colaborador usando campos centralizados"""

    user_id: UUID = CommonFields.user_id
    permissions: CollaboratorPermissions = Field(
        ..., description="Permissões do colaborador"
    )


class CollaboratorResponse(TimestampSchema, BaseModel):
    """Schema de resposta de colaborador usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    project_id: UUID = CommonFields.project_id
    user_id: UUID = CommonFields.user_id

    # Informações do usuário
    user_name: str = CommonFields.name
    user_email: str = CommonFields.email
    user_avatar: str | None = CommonFields.avatar_url

    # Permissões
    can_edit: bool = Field(True, description="Pode editar")
    can_comment: bool = Field(True, description="Pode comentar")
    can_share: bool = Field(False, description="Pode compartilhar")
    can_delete: bool = Field(False, description="Pode deletar")

    # Timestamp específico
    added_at: datetime = Field(..., description="Data de adição")

    # Herda automaticamente: created_at, updated_at

    @validator("id", "project_id", "user_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


# ==================== COMMENT SCHEMAS (CENTRALIZADOS) ====================


class CommentBase(CommonValidatorsMixin, BaseModel):
    """Schema base centralizado para comentário"""

    # Conteúdo usando validador centralizado
    content: str = Field(
        ..., min_length=1, max_length=2000, description="Conteúdo do comentário"
    )
    content_type: str = Field(
        "text", pattern=r"^(text|markdown)$", description="Tipo do conteúdo"
    )

    # Posicionamento no projeto
    node_id: str | None = Field(None, max_length=50, description="ID do nó relacionado")
    position_x: float | None = Field(None, description="Posição X")
    position_y: float | None = Field(None, description="Posição Y")


class CommentCreate(CommentBase):
    """Schema para criação de comentário usando sistema centralizado"""

    parent_id: UUID | None = Field(
        None, description="ID do comentário pai (para respostas)"
    )


class CommentUpdate(CommonValidatorsMixin, BaseModel):
    """Schema para atualização de comentário usando validadores centralizados"""

    content: str | None = Field(None, min_length=1, max_length=2000)
    content_type: str | None = Field(None, pattern=r"^(text|markdown)$")


class CommentResponse(CommentBase, TimestampSchema, BaseModel):
    """Schema de resposta de comentário usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    project_id: UUID = CommonFields.project_id
    user_id: UUID = CommonFields.user_id

    # Informações do usuário
    user_name: str = CommonFields.name
    user_avatar: str | None = CommonFields.avatar_url

    # Hierarquia de comentários
    parent_id: UUID | None = Field(None, description="ID do comentário pai")
    reply_count: int = Field(0, ge=0, description="Número de respostas")
    is_resolved: bool = Field(False, description="Comentário resolvido")

    # Herda automaticamente: created_at, updated_at

    @validator("id", "project_id", "user_id", "parent_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


# ==================== ACTIVITY SCHEMAS (CENTRALIZADOS) ====================


class ActivityResponse(TimestampSchema, BaseModel):
    """Schema de resposta de atividade usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    workspace_id: UUID = CommonFields.workspace_id
    user_id: UUID = CommonFields.user_id

    # Informações do usuário
    user_name: str = CommonFields.name
    user_avatar: str | None = CommonFields.avatar_url

    # Dados da atividade
    action: str = Field(..., description="Ação realizada")
    resource_type: str = Field(..., description="Tipo do recurso")
    resource_id: int | None = Field(None, description="ID do recurso")
    description: str = CommonFields.description
    metadata: Dict[str, Any] | None = CommonFields.metadata

    # Herda automaticamente: created_at, updated_at

    @validator("id", "workspace_id", "user_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


# ==================== VERSION SCHEMAS (CENTRALIZADOS) ====================


class ProjectVersionResponse(TimestampSchema, BaseModel):
    """Schema de resposta de versão de projeto usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    project_id: UUID = CommonFields.project_id
    created_by: UUID = CommonFields.user_id

    # Dados da versão
    version_number: int = Field(..., ge=1, description="Número da versão")
    name: str | None = CommonFields.title
    description: str | None = CommonFields.description
    workflow_data: Dict[str, Any] = Field(..., description="Dados do workflow")
    creator_name: str = CommonFields.name
    is_current: bool = Field(False, description="É a versão atual")

    # Herda automaticamente: created_at, updated_at

    @validator("id", "project_id", "created_by", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


class VersionCreate(CommonValidatorsMixin, BaseModel):
    """Schema para criação de versão usando validadores centralizados"""

    name: str | None = Field(None, max_length=100, description="Nome da versão")
    description: str | None = Field(
        None, max_length=500, description="Descrição da versão"
    )


# ==================== STATS & SEARCH SCHEMAS (CENTRALIZADOS) ====================


class WorkspaceStats(BaseModel):
    """Schema centralizado para estatísticas de workspace"""

    # Contadores de uso
    member_count: int = Field(0, ge=0, description="Número de membros")
    project_count: int = Field(0, ge=0, description="Número de projetos")
    activity_count: int = Field(0, ge=0, description="Número de atividades")

    # Estatísticas de armazenamento
    storage_used_mb: float = Field(0.0, ge=0, description="Armazenamento usado em MB")
    storage_limit_mb: int = Field(
        1000, ge=100, description="Limite de armazenamento em MB"
    )
    storage_usage_percent: float = Field(
        0.0, ge=0, le=100, description="Percentual de uso do armazenamento"
    )

    # Atividades recentes
    recent_activity_count: int = Field(0, ge=0, description="Atividades recentes")
    active_projects: int = Field(0, ge=0, description="Projetos ativos")


class WorkspaceSearch(PaginationSchema, BaseModel):
    """Schema para busca de workspace usando paginação centralizada"""

    # Critérios de busca
    query: str | None = Field(None, description="Termo de busca")
    is_public: bool | None = Field(None, description="Filtrar por público")
    has_projects: bool | None = Field(None, description="Tem projetos")
    min_members: int | None = Field(None, ge=1, description="Mínimo de membros")
    max_members: int | None = Field(None, ge=1, description="Máximo de membros")

    # Ordenação
    sort_by: str | None = Field(
        "activity",
        pattern=r"^(activity|members|projects|created|name)$",
        description="Campo de ordenação",
    )

    # Herda automaticamente: limit, offset


class ProjectSearch(PaginationSchema, BaseModel):
    """Schema para busca de projeto usando paginação centralizada"""

    # Critérios de busca
    query: str | None = Field(None, description="Termo de busca")
    workspace_id: UUID | None = CommonFields.workspace_id
    status: ProjectStatus | None = Field(None, description="Status do projeto")
    has_collaborators: bool | None = Field(None, description="Tem colaboradores")

    # Ordenação
    sort_by: str | None = Field(
        "updated_at",
        pattern=r"^(name|created_at|updated_at|status)$",
        description="Campo para ordenação",
    )
    sort_order: str | None = Field(
        "desc", pattern=r"^(asc|desc)$", description="Ordem da ordenação"
    )

    # Herda automaticamente: limit, offset


# ==================== BULK OPERATION SCHEMAS (CENTRALIZADOS) ====================


class BulkMemberOperation(BaseModel):
    """Schema para operação em lote de membros"""

    action: str = Field(
        ..., pattern=r"^(remove|change_role|send_reminder)$", description="Ação em lote"
    )
    member_ids: List[int] = Field(
        ..., min_items=1, max_items=50, description="IDs dos membros"
    )
    new_role: WorkspaceRole | None = Field(
        None, description="Novo papel (para change_role)"
    )
    reason: str | None = Field(None, max_length=500, description="Motivo da operação")


class BulkProjectOperation(BaseModel):
    """Schema para operação em lote de projetos"""

    action: str = Field(
        ..., pattern=r"^(archive|delete|move_workspace)$", description="Ação em lote"
    )
    project_ids: List[UUID] = Field(
        ..., min_items=1, max_items=50, description="IDs dos projetos"
    )
    target_workspace_id: UUID | None = CommonFields.workspace_id
    reason: str | None = Field(None, max_length=500, description="Motivo da operação")


class BulkOperationResponse(BaseResponseSchema):
    """Schema de resposta para operações em lote usando sistema centralizado"""

    success_count: int = Field(0, ge=0, description="Operações bem-sucedidas")
    error_count: int = Field(0, ge=0, description="Operações com erro")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de erros"
    )

    # Herda automaticamente: success, message, request_id


# ==================== REAL-TIME SCHEMAS (CENTRALIZADOS) ====================


class RealTimeEvent(BaseModel):
    """Schema centralizado para eventos em tempo real"""

    event_type: str = Field(..., description="Tipo do evento")
    workspace_id: UUID = CommonFields.workspace_id
    project_id: UUID | None = CommonFields.project_id
    user_id: UUID = CommonFields.user_id
    user_name: str = CommonFields.name
    data: Dict[str, Any] = Field(..., description="Dados do evento")
    timestamp: datetime = Field(..., description="Timestamp do evento")


class CursorPosition(BaseModel):
    """Schema para posição do cursor em tempo real"""

    user_id: UUID = CommonFields.user_id
    user_name: str = CommonFields.name
    user_color: str = Field(..., description="Cor do cursor do usuário")
    x: float = Field(..., description="Posição X")
    y: float = Field(..., description="Posição Y")
    node_id: str | None = Field(None, description="ID do nó")
    timestamp: datetime = Field(..., description="Timestamp da posição")


class EditOperation(BaseModel):
    """Schema para operações de edição em tempo real"""

    operation_type: str = Field(
        ..., pattern=r"^(insert|delete|update|move)$", description="Tipo da operação"
    )
    node_id: str | None = Field(None, description="ID do nó")
    data: Dict[str, Any] = Field(..., description="Dados da operação")
    user_id: UUID = CommonFields.user_id
    timestamp: datetime = Field(..., description="Timestamp da operação")


# ==================== NOTIFICATION SCHEMAS (CENTRALIZADOS) ====================


class NotificationSettings(BaseModel):
    """Schema centralizado para configurações de notificação"""

    # Tipos de notificação
    email_notifications: bool = Field(True, description="Notificações por email")
    push_notifications: bool = Field(True, description="Notificações push")
    desktop_notifications: bool = Field(True, description="Notificações desktop")

    # Frequência
    digest_frequency: str = Field(
        "daily",
        pattern=r"^(immediate|hourly|daily|weekly|never)$",
        description="Frequência do resumo",
    )

    # Eventos específicos
    notify_on_mention: bool = Field(True, description="Notificar em menções")
    notify_on_comment: bool = Field(True, description="Notificar em comentários")
    notify_on_project_update: bool = Field(
        True, description="Notificar em atualizações de projeto"
    )
    notify_on_member_join: bool = Field(
        True, description="Notificar quando membro entra"
    )
    notify_on_invitation: bool = Field(True, description="Notificar em convites")


class NotificationPreferences(BaseModel):
    """Schema para preferências de notificação"""

    workspace_id: UUID = CommonFields.workspace_id
    settings: NotificationSettings = Field(
        ..., description="Configurações de notificação"
    )


# ==================== INTEGRATION SCHEMAS (CENTRALIZADOS) ====================


class WorkspaceIntegration(BaseModel):
    """Schema para integração de workspace"""

    integration_type: str = Field(..., max_length=50, description="Tipo da integração")
    config: Dict[str, Any] = CommonFields.configuration
    is_enabled: bool = Field(True, description="Integração habilitada")


class IntegrationResponse(TimestampSchema, BaseModel):
    """Schema de resposta de integração usando sistema centralizado"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    workspace_id: UUID = CommonFields.workspace_id

    # Dados da integração
    integration_type: str = Field(..., description="Tipo da integração")
    config: Dict[str, Any] = CommonFields.configuration
    is_enabled: bool = Field(True, description="Integração habilitada")

    # Herda automaticamente: created_at, updated_at

    @validator("id", "workspace_id", pre=True)
    def validate_uuids(cls, v):
        return str(validate_uuid(v)) if v else v


# ============================================================================
# NOVOS SCHEMAS ADICIONADOS PARA TASK 7
# ============================================================================


class WorkspaceAPIStats(BaseModel):
    """Schema para estatísticas de uso de API do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Contadores atuais
    api_calls_today: int = Field(0, ge=0, description="Chamadas API hoje")
    api_calls_this_month: int = Field(0, ge=0, description="Chamadas API este mês")

    # Controle de reset
    last_api_reset_daily: Optional[datetime] = Field(
        None, description="Último reset diário"
    )
    last_api_reset_monthly: Optional[datetime] = Field(
        None, description="Último reset mensal"
    )

    # Limites do plano
    daily_limit: Optional[int] = Field(None, ge=0, description="Limite diário do plano")
    monthly_limit: Optional[int] = Field(
        None, ge=0, description="Limite mensal do plano"
    )

    # Estatísticas calculadas
    usage_percentage_daily: float = Field(
        0.0, ge=0, le=100, description="Percentual de uso diário"
    )
    usage_percentage_monthly: float = Field(
        0.0, ge=0, le=100, description="Percentual de uso mensal"
    )
    can_make_calls: bool = Field(True, description="Pode fazer mais chamadas")
    calls_remaining_today: Optional[int] = Field(
        None, description="Chamadas restantes hoje"
    )
    calls_remaining_month: Optional[int] = Field(
        None, description="Chamadas restantes este mês"
    )


class WorkspaceUsageStats(BaseModel):
    """Schema para contadores de uso de features do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Contadores de features
    feature_usage_count: Dict[str, int] = Field(
        default_factory=dict, description="Contadores de uso por feature"
    )

    # Features específicas (exemplos comuns)
    workflows_created: int = Field(0, ge=0, description="Workflows criados")
    workflows_executed: int = Field(0, ge=0, description="Workflows executados")
    projects_created: int = Field(0, ge=0, description="Projetos criados")
    comments_made: int = Field(0, ge=0, description="Comentários feitos")
    collaborations_started: int = Field(0, ge=0, description="Colaborações iniciadas")
    files_uploaded: int = Field(0, ge=0, description="Arquivos enviados")
    ai_interactions: int = Field(0, ge=0, description="Interações com IA")

    # Estatísticas de tempo
    total_editing_time_minutes: int = Field(
        0, ge=0, description="Tempo total de edição em minutos"
    )
    total_collaboration_time_minutes: int = Field(
        0, ge=0, description="Tempo total de colaboração em minutos"
    )

    # Features premium usadas
    premium_features_used: List[str] = Field(
        default_factory=list, description="Features premium utilizadas"
    )

    # Período de tracking
    tracking_period_start: Optional[datetime] = Field(
        None, description="Início do período de tracking"
    )
    tracking_period_end: Optional[datetime] = Field(
        None, description="Fim do período de tracking"
    )


class WorkspaceSettings(BaseModel):
    """Schema específico para configurações do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Configurações de notificação individuais (campos reais do banco)
    email_notifications: bool = Field(
        True, description="Notificações por email habilitadas"
    )
    push_notifications: bool = Field(
        False, description="Push notifications habilitadas"
    )

    # Configurações de notificação avançadas (JSONB)
    notification_settings: Dict[str, Any] = Field(
        default_factory=dict, description="Configurações avançadas de notificação"
    )

    # Configurações de colaboração
    enable_real_time_editing: bool = Field(True, description="Edição em tempo real")
    enable_comments: bool = Field(True, description="Comentários habilitados")
    enable_chat: bool = Field(True, description="Chat habilitado")
    enable_video_calls: bool = Field(False, description="Chamadas de vídeo habilitadas")

    # Configurações de acesso
    is_public: bool = Field(False, description="Workspace público")
    allow_guest_access: bool = Field(False, description="Permite acesso de convidados")
    require_approval: bool = Field(
        True, description="Requer aprovação para novos membros"
    )

    # Configurações de aparência
    color: Optional[str] = Field(
        "#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor do workspace"
    )
    avatar_url: Optional[str] = Field(None, description="URL do avatar")

    # Limites
    max_members: int = Field(10, ge=1, le=1000, description="Máximo de membros")
    max_projects: int = Field(50, ge=1, le=10000, description="Máximo de projetos")
    max_storage_mb: int = Field(
        1000, ge=100, le=100000, description="Máximo de armazenamento"
    )


class WorkspaceSettingsUpdate(BaseModel):
    """Schema para atualização de configurações do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Todos os campos opcionais para atualização
    email_notifications: Optional[bool] = Field(
        None, description="Atualizar notificações email"
    )
    push_notifications: Optional[bool] = Field(
        None, description="Atualizar push notifications"
    )
    notification_settings: Optional[Dict[str, Any]] = Field(
        None, description="Atualizar configurações de notificação"
    )
    enable_real_time_editing: Optional[bool] = Field(
        None, description="Atualizar edição em tempo real"
    )
    enable_comments: Optional[bool] = Field(None, description="Atualizar comentários")
    enable_chat: Optional[bool] = Field(None, description="Atualizar chat")
    enable_video_calls: Optional[bool] = Field(
        None, description="Atualizar chamadas de vídeo"
    )
    is_public: Optional[bool] = Field(
        None, description="Atualizar visibilidade pública"
    )
    allow_guest_access: Optional[bool] = Field(
        None, description="Atualizar acesso de convidados"
    )
    require_approval: Optional[bool] = Field(
        None, description="Atualizar requerimento de aprovação"
    )
    color: Optional[str] = Field(
        None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Atualizar cor"
    )
    avatar_url: Optional[str] = Field(None, description="Atualizar avatar")
    max_members: Optional[int] = Field(
        None, ge=1, le=1000, description="Atualizar limite de membros"
    )
    max_projects: Optional[int] = Field(
        None, ge=1, le=10000, description="Atualizar limite de projetos"
    )
    max_storage_mb: Optional[int] = Field(
        None, ge=100, le=100000, description="Atualizar limite de armazenamento"
    )


class WorkspaceFullStats(BaseModel):
    """Schema completo com todas as estatísticas do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Estatísticas básicas
    basic_stats: WorkspaceStats = Field(..., description="Estatísticas básicas")

    # Estatísticas de API
    api_stats: WorkspaceAPIStats = Field(..., description="Estatísticas de uso de API")

    # Estatísticas de usage
    usage_stats: WorkspaceUsageStats = Field(
        ..., description="Estatísticas de uso de features"
    )

    # Informações do plano
    plan_limits: Dict[str, Any] = Field(
        default_factory=dict, description="Limites do plano atual"
    )

    # Projeções e insights
    projected_monthly_usage: Optional[int] = Field(
        None, description="Projeção de uso mensal"
    )
    cost_savings_opportunities: List[str] = Field(
        default_factory=list, description="Oportunidades de economia"
    )
    upgrade_recommendations: List[str] = Field(
        default_factory=list, description="Recomendações de upgrade"
    )


# ============================================================================
# ATUALIZAÇÕES DOS SCHEMAS EXISTENTES PARA INCLUIR NOVOS CAMPOS
# ============================================================================


class WorkspaceResponseEnhanced(WorkspaceBase, TenantSchema, TimestampSchema):
    """Schema de resposta ATUALIZADO com todos os campos do banco de dados"""

    # Identificadores usando campos centralizados
    id: UUID = CommonFields.id
    slug: str = CommonFields.slug
    type: WorkspaceType = Field(..., description="Tipo do workspace")
    owner_id: UUID = Field(..., description="ID do proprietário")
    owner_name: str | None = Field(None, description="Nome do proprietário")

    # Campo de multi-tenancy
    tenant_id: UUID = Field(..., description="ID do tenant para multi-tenancy")

    # Relacionamento com plano via sistema centralizado
    plan: Optional[PlanResponse] = Field(
        None, description="Plano do workspace via tenant"
    )

    # Configurações usando valores padrão centralizados
    is_template: bool = Field(False, description="É um template")

    # Estatísticas de uso
    member_count: int = Field(0, ge=0, description="Número de membros")
    project_count: int = Field(0, ge=0, description="Número de projetos")
    activity_count: int = Field(0, ge=0, description="Número de atividades")
    storage_used_mb: float = Field(0.0, ge=0, description="Armazenamento usado em MB")

    # NOVOS CAMPOS ADICIONADOS PARA TASK 7
    # Configurações de notificação individuais (campos reais do banco)
    email_notifications: bool = Field(True, description="Notificações por email")
    push_notifications: bool = Field(False, description="Push notifications")

    # Tracking de API calls (campos reais do banco)
    api_calls_today: int = Field(0, ge=0, description="Chamadas API hoje")
    api_calls_this_month: int = Field(0, ge=0, description="Chamadas API este mês")
    last_api_reset_daily: Optional[datetime] = Field(
        None, description="Último reset diário da API"
    )
    last_api_reset_monthly: Optional[datetime] = Field(
        None, description="Último reset mensal da API"
    )

    # Contadores de uso de features (campo real do banco)
    feature_usage_count: Dict[str, int] = Field(
        default_factory=dict, description="Contadores de uso de features"
    )

    # Status usando validador centralizado
    status: str = Field("active", description="Status do workspace")
    last_activity_at: datetime | None = Field(None, description="Última atividade")

    @validator("id", "owner_id", "tenant_id", pre=True)
    def validate_uuids(cls, v):
        """Validar UUIDs usando validador centralizado"""
        return validate_uuid(v)


class WorkspaceCreateEnhanced(WorkspaceBase):
    """Schema de criação ATUALIZADO com novos campos opcionais"""

    type: WorkspaceType = Field(
        WorkspaceType.COLLABORATIVE, description="Tipo do workspace"
    )

    # Campo obrigatório de multi-tenancy
    tenant_id: UUID = Field(..., description="ID do tenant para multi-tenancy")

    # Valores padrão explícitos para criação
    is_public: bool = Field(False, description="Workspace público")
    allow_guest_access: bool = Field(False, description="Permite acesso de convidados")
    require_approval: bool = Field(True, description="Requer aprovação")
    enable_real_time_editing: bool = Field(True, description="Edição em tempo real")
    enable_comments: bool = Field(True, description="Comentários habilitados")
    enable_chat: bool = Field(True, description="Chat habilitado")
    enable_video_calls: bool = Field(False, description="Chamadas de vídeo")

    # NOVOS CAMPOS OPCIONAIS PARA TASK 7
    # Configurações de notificação individuais
    email_notifications: bool = Field(True, description="Notificações por email")
    push_notifications: bool = Field(False, description="Push notifications")
    notification_settings: Dict[str, Any] | None = None

    # Contadores iniciais (normalmente 0)
    api_calls_today: int = Field(0, description="Inicializar contador API diário")
    api_calls_this_month: int = Field(0, description="Inicializar contador API mensal")
    feature_usage_count: Dict[str, int] = Field(
        default_factory=dict, description="Inicializar contadores de features"
    )


class WorkspaceUpdateEnhanced(CommonValidatorsMixin, BaseModel):
    """Schema de atualização ATUALIZADO incluindo novos campos opcionais"""

    # Todos os campos originais opcionais para update
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    avatar_url: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_public: bool | None = None
    allow_guest_access: bool | None = None
    require_approval: bool | None = None
    max_members: int | None = Field(None, ge=1, le=1000)
    max_projects: int | None = Field(None, ge=1, le=10000)
    max_storage_mb: int | None = Field(None, ge=100, le=100000)
    enable_real_time_editing: bool | None = None
    enable_comments: bool | None = None
    enable_chat: bool | None = None
    enable_video_calls: bool | None = None

    # NOVOS CAMPOS ADICIONADOS PARA TASK 7
    # Configurações de notificação individuais
    email_notifications: Optional[bool] = Field(
        None, description="Atualizar notificações email"
    )
    push_notifications: Optional[bool] = Field(
        None, description="Atualizar push notifications"
    )
    notification_settings: Dict[str, Any] | None = None

    # Contadores de API (normalmente gerenciados pelo sistema, mas pode ser útil para reset/admin)
    api_calls_today: Optional[int] = Field(
        None, ge=0, description="Resetar contador API diário"
    )
    api_calls_this_month: Optional[int] = Field(
        None, ge=0, description="Resetar contador API mensal"
    )

    # Contadores de features (para reset ou ajuste administrativo)
    feature_usage_count: Optional[Dict[str, int]] = Field(
        None, description="Atualizar contadores de features"
    )

    # Campo de status
    status: Optional[str] = Field(
        None, pattern=r"^(active|suspended|deleted)$", description="Atualizar status"
    )


# ============================================================================
# SCHEMAS DE GESTÃO E CONFIGURAÇÃO AVANÇADA
# ============================================================================


class WorkspaceConfigurationRequest(BaseModel):
    """Schema para solicitação de configuração avançada do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Configurações básicas
    settings: WorkspaceSettingsUpdate = Field(
        ..., description="Configurações a atualizar"
    )

    # Configurações de API (admin only)
    reset_api_counters: bool = Field(False, description="Resetar contadores de API")
    reset_feature_counters: bool = Field(
        False, description="Resetar contadores de features"
    )

    # Configurações específicas de features
    enable_premium_features: List[str] = Field(
        default_factory=list, description="Habilitar features premium"
    )
    disable_features: List[str] = Field(
        default_factory=list, description="Desabilitar features"
    )

    # Motivo da alteração (para auditoria)
    change_reason: Optional[str] = Field(
        None, max_length=500, description="Motivo da alteração"
    )


class WorkspaceConfigurationResponse(BaseModel):
    """Schema de resposta para configuração do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Status da operação
    success: bool = Field(..., description="Se a configuração foi bem-sucedida")
    message: str = Field(..., description="Mensagem de resultado")

    # Configurações aplicadas
    applied_settings: WorkspaceSettings = Field(
        ..., description="Configurações aplicadas"
    )

    # Estatísticas atualizadas
    updated_stats: WorkspaceFullStats = Field(
        ..., description="Estatísticas atualizadas"
    )

    # Alterações feitas
    changes_made: List[str] = Field(
        default_factory=list, description="Lista de alterações realizadas"
    )

    # Warnings ou alertas
    warnings: List[str] = Field(
        default_factory=list, description="Avisos sobre a configuração"
    )


class WorkspaceAnalytics(BaseModel):
    """Schema para analytics avançado do workspace"""

    model_config = ConfigDict(from_attributes=True)

    # Período de análise
    period_start: datetime = Field(..., description="Início do período analisado")
    period_end: datetime = Field(..., description="Fim do período analisado")

    # Métricas de uso
    total_api_calls: int = Field(0, description="Total de chamadas API no período")
    average_daily_api_calls: float = Field(
        0.0, description="Média diária de chamadas API"
    )
    peak_api_usage_day: Optional[datetime] = Field(
        None, description="Dia de maior uso da API"
    )

    # Métricas de colaboração
    active_members: int = Field(0, description="Membros ativos no período")
    collaboration_sessions: int = Field(0, description="Sessões de colaboração")
    total_editing_time_hours: float = Field(
        0.0, description="Tempo total de edição em horas"
    )

    # Métricas de storage
    storage_growth_mb: float = Field(
        0.0, description="Crescimento de storage no período"
    )
    files_uploaded: int = Field(0, description="Arquivos enviados")
    files_deleted: int = Field(0, description="Arquivos deletados")

    # Features mais usadas
    top_features: List[Dict[str, Any]] = Field(
        default_factory=list, description="Features mais utilizadas"
    )
    feature_adoption_rate: Dict[str, float] = Field(
        default_factory=dict, description="Taxa de adoção por feature"
    )

    # Insights e recomendações
    usage_trends: Dict[str, str] = Field(
        default_factory=dict, description="Tendências de uso"
    )
    optimization_suggestions: List[str] = Field(
        default_factory=list, description="Sugestões de otimização"
    )
    plan_recommendations: List[str] = Field(
        default_factory=list, description="Recomendações de plano"
    )


# ============================================================================
# COMPATIBILIDADE COM SCHEMAS LEGADOS
# ============================================================================


# Manter WorkspaceResponse original para compatibilidade, mas marcar como deprecado
class WorkspaceResponse(WorkspaceResponseEnhanced):
    """Schema de resposta legacy - use WorkspaceResponseEnhanced para novos desenvolvimentos"""

    pass


# Manter WorkspaceCreate original para compatibilidade, mas marcar como deprecado
class WorkspaceCreate(WorkspaceCreateEnhanced):
    """Schema de criação legacy - use WorkspaceCreateEnhanced para novos desenvolvimentos"""

    pass


# Manter WorkspaceUpdate original para compatibilidade, mas marcar como deprecado
class WorkspaceUpdate(WorkspaceUpdateEnhanced):
    """Schema de atualização legacy - use WorkspaceUpdateEnhanced para novos desenvolvimentos"""

    pass
