"""
Schemas Pydantic para o modelo User
Sincronizados com os campos reais do banco de dados PostgreSQL
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from enum import Enum
import re


class UserStatus(str, Enum):
    """Status do usuário - deve corresponder aos valores no banco"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class UserRole(str, Enum):
    """Roles baseados no campo is_superuser"""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# ============================================================================
# SCHEMAS DE CRIAÇÃO E ATUALIZAÇÃO
# ============================================================================


class UserRegister(BaseModel):
    """Schema para registro de novos usuários"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Campos obrigatórios
    email: EmailStr = Field(
        ..., description="Email único do usuário", examples=["usuario@exemplo.com"]
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Nome de usuário único",
        examples=["usuario123"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Senha do usuário",
        examples=["senhaSegura123!"],
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nome completo do usuário",
        examples=["João Silva Santos"],
    )

    # Campos opcionais
    bio: Optional[str] = Field(
        None,
        max_length=1000,
        description="Biografia do usuário",
        examples=["Desenvolvedor Full Stack apaixonado por tecnologia"],
    )
    profile_image_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL da imagem de perfil",
        examples=["https://exemplo.com/avatar.jpg"],
    )

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

    @field_validator("profile_image_url")
    @classmethod
    def validate_profile_image_url(cls, v: Optional[str]) -> Optional[str]:
        """Validar URL da imagem de perfil"""
        if v is None:
            return v
        if not re.match(r"^https?://", v):
            raise ValueError("URL da imagem deve começar com http:// ou https://")
        return v


class UserCreate(BaseModel):
    """Schema para criação de usuários (admin)"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Campos obrigatórios
    email: EmailStr = Field(..., description="Email único do usuário")
    username: str = Field(
        ..., min_length=3, max_length=255, description="Nome de usuário único"
    )
    full_name: str = Field(
        ..., min_length=2, max_length=200, description="Nome completo"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Senha (opcional, será gerada automaticamente se não fornecida)",
    )

    # Campos opcionais do banco
    is_active: bool = Field(True, description="Se o usuário está ativo")
    is_verified: bool = Field(False, description="Se o email foi verificado")
    is_superuser: bool = Field(False, description="Se é administrador")
    status: UserStatus = Field(UserStatus.ACTIVE, description="Status do usuário")
    bio: Optional[str] = Field(None, max_length=1000, description="Biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL da imagem de perfil"
    )
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )

    # Campos de segurança (admin)
    login_count: int = Field(0, description="Contador de logins")
    failed_login_attempts: int = Field(0, description="Tentativas de login falharam")
    account_locked_until: Optional[datetime] = Field(
        None, description="Data até quando a conta está bloqueada"
    )
    last_login_at: Optional[datetime] = Field(None, description="Último login")


class UserUpdate(BaseModel):
    """Schema para atualização de usuários"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Todos os campos são opcionais para atualização
    email: Optional[EmailStr] = Field(None, description="Novo email")
    username: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Novo username"
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=200, description="Novo nome completo"
    )
    bio: Optional[str] = Field(None, max_length=1000, description="Nova biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="Nova URL da imagem"
    )
    is_active: Optional[bool] = Field(None, description="Novo status ativo")
    is_verified: Optional[bool] = Field(None, description="Novo status verificado")
    status: Optional[UserStatus] = Field(None, description="Novo status")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Novos metadados")


class UserPasswordUpdate(BaseModel):
    """Schema para atualização de senha"""

    model_config = ConfigDict(str_strip_whitespace=True)

    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="Nova senha"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validar força da nova senha"""
        if len(v) < 8:
            raise ValueError("Nova senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("Nova senha deve conter pelo menos um número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Nova senha deve conter pelo menos um caractere especial")
        return v


class UserStatusUpdate(BaseModel):
    """Schema para atualização de status administrativo"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    status: UserStatus = Field(..., description="Novo status do usuário")
    is_active: Optional[bool] = Field(None, description="Se deve ativar/desativar")
    is_verified: Optional[bool] = Field(
        None, description="Se deve verificar/des-verificar"
    )
    is_superuser: Optional[bool] = Field(
        None, description="Se deve promover/rebaixar admin"
    )
    reason: Optional[str] = Field(None, max_length=500, description="Motivo da mudança")


# ============================================================================
# SCHEMAS DE RESPOSTA
# ============================================================================


class UserResponse(BaseModel):
    """Schema completo de resposta do usuário"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    # Campos principais
    id: UUID = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., description="Nome de usuário")
    full_name: str = Field(..., description="Nome completo")

    # Status e permissões
    is_active: bool = Field(..., description="Se o usuário está ativo")
    is_verified: bool = Field(..., description="Se o email foi verificado")
    is_superuser: bool = Field(..., description="Se é administrador")
    status: UserStatus = Field(..., description="Status atual")

    # Informações de perfil
    bio: Optional[str] = Field(None, description="Biografia do usuário")
    profile_image_url: Optional[str] = Field(
        None, description="URL da imagem de perfil"
    )
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )

    # Informações de login
    last_login_at: Optional[datetime] = Field(None, description="Último login")
    login_count: int = Field(0, description="Total de logins")
    failed_login_attempts: int = Field(0, description="Tentativas falharam")
    account_locked_until: Optional[datetime] = Field(None, description="Bloqueado até")

    # Timestamps
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Propriedades computadas
    @property
    def first_name(self) -> str:
        """Primeiro nome extraído do full_name"""
        return self.full_name.split(" ")[0] if self.full_name else ""

    @property
    def last_name(self) -> str:
        """Sobrenome extraído do full_name"""
        if self.full_name and " " in self.full_name:
            return " ".join(self.full_name.split(" ")[1:])
        return ""

    @property
    def role(self) -> UserRole:
        """Role baseado no is_superuser"""
        return UserRole.ADMIN if self.is_superuser else UserRole.USER

    @property
    def avatar_url(self) -> str:
        """URL do avatar (compatibilidade)"""
        return self.profile_image_url or ""

    @property
    def is_account_locked(self) -> bool:
        """Se a conta está bloqueada"""
        if not self.account_locked_until:
            return False
        return datetime.now() < self.account_locked_until

    @property
    def display_name(self) -> str:
        """Nome para exibição"""
        return self.full_name or self.username


class UserPublic(BaseModel):
    """Schema com informações públicas do usuário"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID = Field(..., description="ID único do usuário")
    username: str = Field(..., description="Nome de usuário")
    full_name: str = Field(..., description="Nome completo")
    bio: Optional[str] = Field(None, description="Biografia pública")
    profile_image_url: Optional[str] = Field(
        None, description="URL da imagem de perfil"
    )
    is_verified: bool = Field(..., description="Se está verificado")
    created_at: datetime = Field(..., description="Membro desde")

    @property
    def display_name(self) -> str:
        """Nome para exibição pública"""
        return self.full_name or self.username

    @property
    def avatar_url(self) -> str:
        """URL do avatar público"""
        return self.profile_image_url or ""


class UserProfile(BaseModel):
    """Schema detalhado de perfil do usuário"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    # Informações básicas
    id: UUID = Field(..., description="ID único")
    email: EmailStr = Field(..., description="Email")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Nome completo")
    bio: Optional[str] = Field(None, description="Biografia")
    profile_image_url: Optional[str] = Field(None, description="Imagem de perfil")

    # Status
    is_active: bool = Field(..., description="Status ativo")
    is_verified: bool = Field(..., description="Email verificado")
    status: UserStatus = Field(..., description="Status da conta")

    # Estatísticas
    login_count: int = Field(0, description="Total de logins")
    last_login_at: Optional[datetime] = Field(None, description="Último login")
    created_at: datetime = Field(..., description="Membro desde")

    # Metadados (sem dados sensíveis)
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Configurações do usuário"
    )


class UserSummary(BaseModel):
    """Schema resumido do usuário para listagens"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID = Field(..., description="ID único")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Nome completo")
    email: EmailStr = Field(..., description="Email")
    is_active: bool = Field(..., description="Status ativo")
    is_verified: bool = Field(..., description="Email verificado")
    role: str = Field(..., description="Role do usuário")
    created_at: datetime = Field(..., description="Data de criação")


class UserStats(BaseModel):
    """Schema com estatísticas do usuário"""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID = Field(..., description="ID do usuário")
    login_count: int = Field(0, description="Total de logins")
    failed_login_attempts: int = Field(0, description="Tentativas falharam")
    last_login_at: Optional[datetime] = Field(None, description="Último login")
    account_locked: bool = Field(False, description="Conta bloqueada")
    days_since_creation: int = Field(0, description="Dias desde criação")
    is_verified: bool = Field(False, description="Email verificado")


# ============================================================================
# SCHEMAS DE AUTENTICAÇÃO
# ============================================================================


class UserLogin(BaseModel):
    """Schema para login de usuário"""

    model_config = ConfigDict(str_strip_whitespace=True)

    username_or_email: str = Field(
        ...,
        min_length=3,
        description="Username ou email para login",
        examples=["usuario123", "usuario@exemplo.com"],
    )
    password: str = Field(..., min_length=1, description="Senha do usuário")
    remember_me: bool = Field(False, description="Lembrar login")


class UserLoginResponse(BaseModel):
    """Schema de resposta do login"""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Expira em (segundos)")
    user: UserProfile = Field(..., description="Dados do usuário logado")


# ============================================================================
# SCHEMAS DE TOKENS E RECOVERY
# ============================================================================


class PasswordResetRequest(BaseModel):
    """Schema para solicitação de reset de senha"""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(..., description="Email para reset de senha")


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha"""

    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(..., description="Token de reset")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="Nova senha"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validar força da nova senha"""
        if len(v) < 8:
            raise ValueError("Nova senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("Nova senha deve conter pelo menos um número")
        return v


class EmailVerificationRequest(BaseModel):
    """Schema para solicitação de verificação de email"""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(..., description="Email para verificação")


class EmailVerificationConfirm(BaseModel):
    """Schema para confirmação de verificação de email"""

    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(..., description="Token de verificação")


# ============================================================================
# SCHEMAS DE LISTAS E FILTROS
# ============================================================================


class UserListResponse(BaseModel):
    """Schema de resposta para listagem de usuários"""

    model_config = ConfigDict(from_attributes=True)

    users: List[UserSummary] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de usuários")
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Tamanho da página")
    total_pages: int = Field(..., description="Total de páginas")


class UserFilter(BaseModel):
    """Schema para filtros de busca de usuários"""

    model_config = ConfigDict(str_strip_whitespace=True)

    search: Optional[str] = Field(None, description="Busca por nome, username ou email")
    status: Optional[UserStatus] = Field(None, description="Filtrar por status")
    is_active: Optional[bool] = Field(None, description="Filtrar por ativo/inativo")
    is_verified: Optional[bool] = Field(None, description="Filtrar por verificado")
    is_superuser: Optional[bool] = Field(None, description="Filtrar por admin")
    created_after: Optional[datetime] = Field(None, description="Criado após esta data")
    created_before: Optional[datetime] = Field(
        None, description="Criado antes desta data"
    )
    last_login_after: Optional[datetime] = Field(None, description="Último login após")
    last_login_before: Optional[datetime] = Field(
        None, description="Último login antes"
    )


# ============================================================================
# SCHEMAS DE PREFERÊNCIAS E CONFIGURAÇÕES
# ============================================================================


class UserPreferences(BaseModel):
    """Schema para preferências do usuário"""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    # Aparência
    theme: Optional[str] = Field("light", description="Tema da interface")
    language: Optional[str] = Field("pt-BR", description="Idioma preferido")
    timezone: Optional[str] = Field("America/Sao_Paulo", description="Fuso horário")

    # Notificações
    email_notifications: bool = Field(
        True, description="Receber notificações por email"
    )
    push_notifications: bool = Field(True, description="Receber push notifications")
    marketing_emails: bool = Field(False, description="Receber emails de marketing")

    # Interface
    sidebar_collapsed: bool = Field(False, description="Sidebar recolhida")
    show_tutorials: bool = Field(True, description="Mostrar tutoriais")
    animations_enabled: bool = Field(True, description="Animações habilitadas")

    # Privacidade
    profile_public: bool = Field(True, description="Perfil público")
    show_email: bool = Field(False, description="Mostrar email no perfil")
    show_last_login: bool = Field(False, description="Mostrar último login")


class UserPreferencesUpdate(BaseModel):
    """Schema para atualização de preferências"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Todos os campos opcionais
    theme: Optional[str] = Field(None, description="Novo tema")
    language: Optional[str] = Field(None, description="Novo idioma")
    timezone: Optional[str] = Field(None, description="Novo fuso horário")
    email_notifications: Optional[bool] = Field(None, description="Notificações email")
    push_notifications: Optional[bool] = Field(None, description="Push notifications")
    marketing_emails: Optional[bool] = Field(None, description="Emails marketing")
    sidebar_collapsed: Optional[bool] = Field(None, description="Sidebar recolhida")
    show_tutorials: Optional[bool] = Field(None, description="Mostrar tutoriais")
    animations_enabled: Optional[bool] = Field(None, description="Animações")
    profile_public: Optional[bool] = Field(None, description="Perfil público")
    show_email: Optional[bool] = Field(None, description="Mostrar email")
    show_last_login: Optional[bool] = Field(None, description="Mostrar último login")


# ============================================================================
# SCHEMAS DE VALIDAÇÃO E DISPONIBILIDADE
# ============================================================================


class UsernameAvailability(BaseModel):
    """Schema para verificar disponibilidade de username"""

    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(
        ..., min_length=3, max_length=255, description="Username a verificar"
    )


class EmailAvailability(BaseModel):
    """Schema para verificar disponibilidade de email"""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(..., description="Email a verificar")


class AvailabilityResponse(BaseModel):
    """Schema de resposta de disponibilidade"""

    model_config = ConfigDict(from_attributes=True)

    available: bool = Field(..., description="Se está disponível")
    suggestions: List[str] = Field(
        default_factory=list, description="Sugestões alternativas"
    )


# ============================================================================
# SCHEMAS AUXILIARES E UTILITÁRIOS
# ============================================================================


class UserBulkAction(BaseModel):
    """Schema para ações em lote"""

    model_config = ConfigDict(from_attributes=True)

    user_ids: List[UUID] = Field(..., description="IDs dos usuários")
    action: str = Field(..., description="Ação a executar")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parâmetros da ação"
    )


class UserExportFormat(str, Enum):
    """Formatos de exportação"""

    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"


class UserExportRequest(BaseModel):
    """Schema para solicitação de exportação"""

    model_config = ConfigDict(from_attributes=True)

    format: UserExportFormat = Field(..., description="Formato de exportação")
    filters: Optional[UserFilter] = Field(None, description="Filtros a aplicar")
    fields: List[str] = Field(default_factory=list, description="Campos a incluir")


# ============================================================================
# SCHEMAS ESPECÍFICOS PARA BACKWARDS COMPATIBILITY
# ============================================================================


class UserProfileResponse(BaseModel):
    """Schema legacy - mantido para compatibilidade"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID do usuário")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email")
    full_name: str = Field(..., description="Nome completo")
    is_active: bool = Field(..., description="Status ativo")
    is_verified: bool = Field(..., description="Email verificado")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")


class UserProfileUpdate(BaseModel):
    """Schema legacy - mantido para compatibilidade"""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: Optional[str] = Field(None, description="Novo nome completo")
    username: Optional[str] = Field(None, description="Novo username")
    bio: Optional[str] = Field(None, description="Nova biografia")
