"""
Modelos Pydantic corrigidos com validações, enums e relacionamentos adequados.
Baseado na análise real do schema synapscale_db.
"""

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    EmailStr,
    ConfigDict,
    computed_field,
)
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from enum import Enum
import re

# ============================================================================
# ENUMS BASEADOS NO SCHEMA REAL
# ============================================================================


class AgentScope(str, Enum):
    """Enum para agent_scope"""

    GLOBAL = "global"
    TENANT = "tenant"


class TriggerType(str, Enum):
    """Enum para trigger_type_en"""

    SCHEDULE = "schedule"
    EVENT = "event"


class WorkspaceType(str, Enum):
    """Enum para workspacetype"""

    INDIVIDUAL = "individual"
    COLLABORATIVE = "collaborative"


class UserStatus(str, Enum):
    """Status do usuário"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class FileStatus(str, Enum):
    """Status de arquivo"""

    ACTIVE = "active"
    PROCESSING = "processing"
    ERROR = "error"
    DELETED = "deleted"


class ScanStatus(str, Enum):
    """Status de scan de arquivo"""

    PENDING = "pending"
    SCANNING = "scanning"
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"


class WorkflowStatus(str, Enum):
    """Status de workflow"""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class AgentStatus(str, Enum):
    """Status de agent"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    ERROR = "error"


# ============================================================================
# MODELOS BASE COM VALIDAÇÕES
# ============================================================================


class UserBase(BaseModel):
    """Modelo base para usuários com validações completas"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: UUID = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email único do usuário")
    username: str = Field(
        ..., min_length=3, max_length=255, description="Nome de usuário único"
    )
    full_name: str = Field(
        ..., min_length=2, max_length=255, description="Nome completo"
    )
    is_active: Optional[bool] = Field(True, description="Se o usuário está ativo")
    is_verified: Optional[bool] = Field(False, description="Se o email foi verificado")
    is_superuser: Optional[bool] = Field(False, description="Se é administrador")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL da imagem de perfil"
    )
    bio: Optional[str] = Field(
        None, max_length=1000, description="Biografia do usuário"
    )
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")
    status: Optional[UserStatus] = Field(
        UserStatus.ACTIVE, description="Status do usuário"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")
    last_login_at: Optional[datetime] = Field(None, description="Último login")
    login_count: Optional[int] = Field(0, ge=0, description="Contador de logins")
    failed_login_attempts: Optional[int] = Field(
        0, ge=0, description="Tentativas de login falharam"
    )
    account_locked_until: Optional[datetime] = Field(None, description="Bloqueado até")
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validar formato do nome de usuário"""
        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError(
                "Username deve conter apenas letras, números, pontos, hífens e underscores"
            )
        if v.startswith(".") or v.endswith("."):
            raise ValueError("Username não pode começar ou terminar com ponto")
        if ".." in v:
            raise ValueError("Username não pode conter pontos consecutivos")
        return v.lower()

    @field_validator("profile_image_url")
    @classmethod
    def validate_profile_image_url(cls, v: Optional[str]) -> Optional[str]:
        """Validar URL da imagem de perfil"""
        if v is None:
            return v
        if not re.match(r"^https?://", v):
            raise ValueError("URL da imagem deve começar com http:// ou https://")
        return v

    @computed_field
    @property
    def display_name(self) -> str:
        """Nome para exibição"""
        return self.full_name or self.username

    @computed_field
    @property
    def is_account_locked(self) -> bool:
        """Se a conta está bloqueada"""
        if not self.account_locked_until:
            return False
        return datetime.now() < self.account_locked_until

    @computed_field
    @property
    def role(self) -> str:
        """Role baseado no is_superuser"""
        return "admin" if self.is_superuser else "user"


class AgentBase(BaseModel):
    """Modelo base para agentes com validações"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: UUID = Field(..., description="ID único do agente")
    name: str = Field(..., min_length=1, max_length=255, description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição do agente")
    is_active: bool = Field(True, description="Se o agente está ativo")
    user_id: UUID = Field(..., description="ID do usuário proprietário")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    tenant_id: UUID = Field(..., description="ID do tenant")
    status: Optional[AgentStatus] = Field(
        AgentStatus.ACTIVE, description="Status do agente"
    )
    priority: Optional[int] = Field(None, ge=1, le=10, description="Prioridade (1-10)")
    version: Optional[str] = Field(None, max_length=50, description="Versão do agente")
    environment: Optional[str] = Field(
        None, max_length=50, description="Ambiente de execução"
    )
    current_config: Optional[UUID] = Field(None, description="ID da configuração atual")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validar nome do agente"""
        if not v.strip():
            raise ValueError("Nome do agente não pode estar vazio")
        return v.strip()


class WorkspaceBase(BaseModel):
    """Modelo base para workspaces com validações"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: UUID = Field(..., description="ID único do workspace")
    name: str = Field(
        ..., min_length=1, max_length=255, description="Nome do workspace"
    )
    slug: str = Field(..., min_length=3, max_length=255, description="Slug único")
    description: Optional[str] = Field(None, description="Descrição do workspace")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL do avatar")
    color: Optional[str] = Field(
        None, max_length=7, description="Cor do workspace (hex)"
    )
    owner_id: UUID = Field(..., description="ID do proprietário")
    is_public: bool = Field(False, description="Se é público")
    is_template: bool = Field(False, description="Se é template")
    allow_guest_access: bool = Field(False, description="Permitir acesso de convidados")
    require_approval: bool = Field(
        True, description="Requer aprovação para novos membros"
    )
    max_members: Optional[int] = Field(None, ge=1, description="Máximo de membros")
    max_projects: Optional[int] = Field(None, ge=1, description="Máximo de projetos")
    max_storage_mb: Optional[int] = Field(
        None, ge=1, description="Máximo de armazenamento (MB)"
    )
    enable_real_time_editing: bool = Field(
        True, description="Habilitar edição em tempo real"
    )
    enable_comments: bool = Field(True, description="Habilitar comentários")
    enable_chat: bool = Field(False, description="Habilitar chat")
    enable_video_calls: bool = Field(False, description="Habilitar chamadas de vídeo")
    member_count: int = Field(0, ge=0, description="Contagem de membros")
    project_count: int = Field(0, ge=0, description="Contagem de projetos")
    activity_count: int = Field(0, ge=0, description="Contagem de atividades")
    storage_used_mb: float = Field(0.0, ge=0, description="Armazenamento usado (MB)")
    status: str = Field(..., description="Status do workspace")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    last_activity_at: datetime = Field(..., description="Última atividade")
    tenant_id: UUID = Field(..., description="ID do tenant")
    email_notifications: Optional[bool] = Field(
        True, description="Notificações por email"
    )
    push_notifications: Optional[bool] = Field(True, description="Push notifications")
    api_calls_today: Optional[int] = Field(0, ge=0, description="Chamadas API hoje")
    api_calls_this_month: Optional[int] = Field(
        0, ge=0, description="Chamadas API este mês"
    )
    last_api_reset_daily: Optional[datetime] = Field(
        None, description="Último reset diário da API"
    )
    last_api_reset_monthly: Optional[datetime] = Field(
        None, description="Último reset mensal da API"
    )
    feature_usage_count: Optional[Dict[str, Any]] = Field(
        None, description="Contagem de uso de features"
    )
    type: WorkspaceType = Field(..., description="Tipo do workspace")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validar slug do workspace"""
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug deve conter apenas letras minúsculas, números e hífens"
            )
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug não pode começar ou terminar com hífen")
        if "--" in v:
            raise ValueError("Slug não pode conter hífens consecutivos")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validar cor hex"""
        if v is None:
            return v
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Cor deve ser um código hex válido (#RRGGBB)")
        return v.upper()


class WorkflowBase(BaseModel):
    """Modelo base para workflows com validações"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: UUID = Field(..., description="ID único do workflow")
    name: str = Field(..., min_length=1, max_length=255, description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição do workflow")
    definition: Dict[str, Any] = Field(..., description="Definição JSON do workflow")
    is_active: bool = Field(True, description="Se o workflow está ativo")
    user_id: UUID = Field(..., description="ID do usuário proprietário")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    is_public: Optional[bool] = Field(False, description="Se é público")
    category: Optional[str] = Field(
        None, max_length=100, description="Categoria do workflow"
    )
    tags: Optional[List[str]] = Field(None, description="Tags do workflow")
    version: Optional[str] = Field(
        None, max_length=50, description="Versão do workflow"
    )
    thumbnail_url: Optional[str] = Field(
        None, max_length=500, description="URL da thumbnail"
    )
    downloads_count: Optional[int] = Field(0, ge=0, description="Contagem de downloads")
    rating_average: Optional[int] = Field(
        None, ge=1, le=5, description="Avaliação média (1-5)"
    )
    rating_count: Optional[int] = Field(0, ge=0, description="Contagem de avaliações")
    execution_count: Optional[int] = Field(0, ge=0, description="Contagem de execuções")
    last_executed_at: Optional[datetime] = Field(None, description="Última execução")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    tenant_id: UUID = Field(..., description="ID do tenant")
    status: Optional[WorkflowStatus] = Field(
        WorkflowStatus.DRAFT, description="Status do workflow"
    )
    priority: Optional[int] = Field(None, ge=1, le=10, description="Prioridade (1-10)")
    timeout_seconds: Optional[int] = Field(
        None, ge=1, description="Timeout em segundos"
    )
    retry_count: Optional[int] = Field(
        0, ge=0, le=10, description="Contagem de tentativas"
    )

    @field_validator("definition")
    @classmethod
    def validate_definition(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validar definição do workflow"""
        required_keys = ["nodes", "connections"]
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Definição deve conter a chave: {key}")
        return v


class FileBase(BaseModel):
    """Modelo base para arquivos com validações"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: UUID = Field(..., description="ID único do arquivo")
    filename: str = Field(
        ..., min_length=1, max_length=255, description="Nome do arquivo"
    )
    original_name: str = Field(
        ..., min_length=1, max_length=255, description="Nome original"
    )
    file_path: str = Field(
        ..., min_length=1, max_length=500, description="Caminho do arquivo"
    )
    file_size: int = Field(..., ge=0, description="Tamanho do arquivo em bytes")
    mime_type: str = Field(..., min_length=1, max_length=100, description="Tipo MIME")
    category: str = Field(
        ..., min_length=1, max_length=50, description="Categoria do arquivo"
    )
    is_public: bool = Field(False, description="Se o arquivo é público")
    user_id: UUID = Field(..., description="ID do usuário proprietário")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    tags: Optional[List[str]] = Field(None, description="Tags do arquivo")
    description: Optional[str] = Field(
        None, max_length=1000, description="Descrição do arquivo"
    )
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")
    status: Optional[FileStatus] = Field(
        FileStatus.ACTIVE, description="Status do arquivo"
    )
    scan_status: Optional[ScanStatus] = Field(
        ScanStatus.PENDING, description="Status do scan"
    )
    access_count: Optional[int] = Field(0, ge=0, description="Contagem de acessos")
    last_accessed_at: Optional[datetime] = Field(None, description="Último acesso")

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validar tamanho do arquivo (max 100MB)"""
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError(f"Arquivo muito grande. Máximo: {max_size} bytes")
        return v

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v: str) -> str:
        """Validar tipo MIME"""
        allowed_types = [
            "text/plain",
            "text/csv",
            "text/html",
            "text/markdown",
            "application/json",
            "application/pdf",
            "application/zip",
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "video/mp4",
            "video/webm",
            "audio/mp3",
            "audio/wav",
        ]
        if v not in allowed_types:
            raise ValueError(f"Tipo MIME não permitido: {v}")
        return v


# ============================================================================
# MODELOS DE RESPOSTA SEGUROS
# ============================================================================


class UserResponse(UserBase):
    """Resposta segura para usuários (sem hashed_password)"""

    pass


class AgentResponse(AgentBase):
    """Resposta para agentes"""

    pass


class WorkspaceResponse(WorkspaceBase):
    """Resposta para workspaces"""

    pass


class WorkflowResponse(WorkflowBase):
    """Resposta para workflows"""

    pass


class FileResponse(FileBase):
    """Resposta para arquivos"""

    pass


# ============================================================================
# MODELOS DE CRIAÇÃO E ATUALIZAÇÃO
# ============================================================================


class UserCreate(BaseModel):
    """Criação de usuário"""

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    email: EmailStr = Field(..., description="Email único")
    username: str = Field(
        ..., min_length=3, max_length=255, description="Username único"
    )
    password: str = Field(..., min_length=8, max_length=100, description="Senha")
    full_name: str = Field(
        ..., min_length=2, max_length=255, description="Nome completo"
    )
    bio: Optional[str] = Field(None, max_length=1000, description="Biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL da imagem"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validar força da senha"""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("Senha deve conter pelo menos um número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Senha deve conter pelo menos um caractere especial")
        return v


class UserUpdate(BaseModel):
    """Atualização de usuário"""

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    email: Optional[EmailStr] = Field(None, description="Novo email")
    username: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Novo username"
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=255, description="Novo nome"
    )
    bio: Optional[str] = Field(None, max_length=1000, description="Nova biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="Nova URL da imagem"
    )
    is_active: Optional[bool] = Field(None, description="Novo status ativo")
    status: Optional[UserStatus] = Field(None, description="Novo status")


class AgentCreate(BaseModel):
    """Criação de agente"""

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    priority: Optional[int] = Field(5, ge=1, le=10, description="Prioridade")
    environment: Optional[str] = Field(
        "production", max_length=50, description="Ambiente"
    )


class WorkspaceCreate(BaseModel):
    """Criação de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome")
    slug: str = Field(..., min_length=3, max_length=255, description="Slug único")
    description: Optional[str] = Field(None, description="Descrição")
    type: WorkspaceType = Field(WorkspaceType.INDIVIDUAL, description="Tipo")
    is_public: bool = Field(False, description="Público")
    max_members: Optional[int] = Field(10, ge=1, description="Máx membros")


# ============================================================================
# MODELOS DE AUTENTICAÇÃO
# ============================================================================


class Token(BaseModel):
    """Token de autenticação"""

    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Expira em segundos")


class RefreshTokenRequest(BaseModel):
    """Solicitação de refresh token"""

    refresh_token: str = Field(..., description="Token de refresh")


class PasswordResetRequest(BaseModel):
    """Solicitação de reset de senha"""

    email: EmailStr = Field(..., description="Email para reset")


class PasswordResetConfirm(BaseModel):
    """Confirmação de reset de senha"""

    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=8, description="Nova senha")


class EmailVerificationRequest(BaseModel):
    """Solicitação de verificação de email"""

    email: EmailStr = Field(..., description="Email para verificação")


class UserRegister(BaseModel):
    """Registro de usuário"""

    email: EmailStr = Field(..., description="Email único")
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    password: str = Field(..., min_length=8, description="Senha")
    full_name: str = Field(..., min_length=2, description="Nome completo")
    bio: Optional[str] = Field(None, description="Biografia")


# ============================================================================
# MODELOS DE LISTA COM PAGINAÇÃO
# ============================================================================


class PaginatedResponse(BaseModel):
    """Resposta paginada base"""

    total: int = Field(..., ge=0, description="Total de itens")
    page: int = Field(..., ge=1, description="Página atual")
    pages: int = Field(..., ge=1, description="Total de páginas")
    size: int = Field(..., ge=1, le=100, description="Itens por página")


class UserListResponse(PaginatedResponse):
    """Lista paginada de usuários"""

    items: List[UserResponse] = Field(..., description="Lista de usuários")


class AgentListResponse(PaginatedResponse):
    """Lista paginada de agentes"""

    items: List[AgentResponse] = Field(..., description="Lista de agentes")


class WorkspaceListResponse(PaginatedResponse):
    """Lista paginada de workspaces"""

    items: List[WorkspaceResponse] = Field(..., description="Lista de workspaces")


class WorkflowListResponse(PaginatedResponse):
    """Lista paginada de workflows"""

    items: List[WorkflowResponse] = Field(..., description="Lista de workflows")


class FileListResponse(PaginatedResponse):
    """Lista paginada de arquivos"""

    items: List[FileResponse] = Field(..., description="Lista de arquivos")


# ============================================================================
# CLASSES CRUD FALTANTES
# ============================================================================


class TenantCreate(BaseModel):
    """Criação de tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome do tenant")
    description: Optional[str] = Field(None, description="Descrição")
    is_active: bool = Field(True, description="Se está ativo")


class TenantUpdate(BaseModel):
    """Atualização de tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    description: Optional[str] = Field(None, description="Nova descrição")
    is_active: Optional[bool] = Field(None, description="Novo status")


class AgentUpdate(BaseModel):
    """Atualização de agente"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    description: Optional[str] = Field(None, description="Nova descrição")
    is_active: Optional[bool] = Field(None, description="Novo status ativo")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Nova prioridade")


class WorkflowCreate(BaseModel):
    """Criação de workflow"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição")
    definition: Dict[str, Any] = Field(..., description="Definição JSON")
    category: Optional[str] = Field(None, max_length=100, description="Categoria")
    tags: Optional[List[str]] = Field(None, description="Tags")


class WorkflowUpdate(BaseModel):
    """Atualização de workflow"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    description: Optional[str] = Field(None, description="Nova descrição")
    definition: Optional[Dict[str, Any]] = Field(None, description="Nova definição")
    is_active: Optional[bool] = Field(None, description="Novo status")


class NodeCreate(BaseModel):
    """Criação de node"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome do node")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    code_template: Optional[str] = Field(None, description="Template de código")


class NodeUpdate(BaseModel):
    """Atualização de node"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    description: Optional[str] = Field(None, description="Nova descrição")
    category: Optional[str] = Field(None, description="Nova categoria")


class ConversationCreate(BaseModel):
    """Criação de conversação"""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=255, description="Título")
    agent_id: Optional[UUID] = Field(None, description="ID do agente")


class ConversationUpdate(BaseModel):
    """Atualização de conversação"""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo título"
    )


class MessageCreate(BaseModel):
    """Criação de mensagem"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., min_length=1, description="Conteúdo da mensagem")
    role: str = Field(..., description="Role da mensagem")


class MessageUpdate(BaseModel):
    """Atualização de mensagem"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: Optional[str] = Field(None, min_length=1, description="Novo conteúdo")


class WorkspaceMemberCreate(BaseModel):
    """Criação de membro de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: UUID = Field(..., description="ID do usuário")
    role: str = Field(..., description="Role do membro")


class WorkspaceMemberUpdate(BaseModel):
    """Atualização de membro de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    role: Optional[str] = Field(None, description="Novo role")


# Response models baseados nas tabelas reais
class TenantResponse(BaseModel):
    """Resposta para tenant"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID do tenant")
    name: str = Field(..., description="Nome")
    description: Optional[str] = Field(None, description="Descrição")
    is_active: bool = Field(..., description="Se está ativo")
    created_at: datetime = Field(..., description="Data de criação")


class NodeResponse(BaseModel):
    """Resposta para node"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID do node")
    name: str = Field(..., description="Nome")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    created_at: datetime = Field(..., description="Data de criação")


class ConversationResponse(BaseModel):
    """Resposta para conversação"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID da conversação")
    title: str = Field(..., description="Título")
    created_at: datetime = Field(..., description="Data de criação")


class MessageResponse(BaseModel):
    """Resposta para mensagem"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID da mensagem")
    content: str = Field(..., description="Conteúdo")
    role: str = Field(..., description="Role")
    created_at: datetime = Field(..., description="Data de criação")


class WorkspaceMemberResponse(BaseModel):
    """Resposta para membro de workspace"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID do membro")
    user_id: UUID = Field(..., description="ID do usuário")
    workspace_id: UUID = Field(..., description="ID do workspace")
    role: str = Field(..., description="Role")
    created_at: datetime = Field(..., description="Data de criação")


# File Models
class FileCreate(BaseModel):
    """Schema para criação de arquivo"""

    filename: str = Field(..., description="Nome do arquivo")
    original_name: str = Field(..., description="Nome original")
    file_size: int = Field(..., description="Tamanho do arquivo")
    mime_type: str = Field(..., description="Tipo MIME")
    category: str = Field(..., description="Categoria")
    is_public: bool = Field(False, description="Arquivo público")


class FileUpdate(BaseModel):
    """Schema para atualização de arquivo"""

    filename: Optional[str] = Field(None, description="Nome do arquivo")
    category: Optional[str] = Field(None, description="Categoria")
    is_public: Optional[bool] = Field(None, description="Arquivo público")
    description: Optional[str] = Field(None, description="Descrição")


# Node Models
class NodeCreate(BaseModel):
    """Schema para criação de nó"""

    name: str = Field(..., description="Nome do nó")
    description: Optional[str] = Field(None, description="Descrição")
    node_type: str = Field(..., description="Tipo do nó")
    config: dict = Field(default_factory=dict, description="Configuração")


# Workflow Update
class WorkflowUpdate(BaseModel):
    """Schema para atualização de workflow"""

    name: Optional[str] = Field(None, description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição")
