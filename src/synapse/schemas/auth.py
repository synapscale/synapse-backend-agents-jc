"""
Schemas Pydantic para autenticação e validação de dados
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import re


class UserLogin(BaseModel):
    """Schema para login de usuário"""
    username: str = Field(..., description="Email ou username do usuário")
    password: str = Field(..., min_length=1, description="Senha do usuário")

    @validator("username")
    def validate_username(cls, v):
        """Valida username ou email"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username/email é obrigatório")
        return v.strip()


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=200)

    @validator("username")
    def validate_username(cls, v):
        """Valida username"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username deve conter apenas letras, números, _ ou -")
        return v.lower()

    @validator("full_name")
    def validate_full_name(cls, v):
        """Valida nome completo"""
        if len(v.strip()) < 2:
            raise ValueError("Nome completo deve ter pelo menos 2 caracteres")
        return v.strip()


class UserCreate(UserBase):
    """
    Schema para criação de novos usuários.
    Inclui validações específicas para registro.
    """
    password: str = Field(..., min_length=8, description="Senha do usuário (mínimo 8 caracteres)")
    confirm_password: Optional[str] = Field(None, description="Confirmação da senha")
    terms_accepted: Optional[bool] = Field(False, description="Aceite dos termos de uso")
    marketing_consent: Optional[bool] = Field(False, description="Consentimento para marketing")

    @validator("password")
    def validate_password(cls, v):
        """Valida a força da senha"""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Valida se as senhas coincidem"""
        if 'password' in values and v != values['password']:
            raise ValueError("Senhas não coincidem")
        return v


# Alias para compatibilidade
UserRegister = UserCreate


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        """Valida nomes"""
        if v and len(v.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        return v.strip() if v else v


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    full_name: str
    avatar_url: str | None
    profile_image_url: str | None
    bio: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    role: str
    created_at: datetime | None
    updated_at: datetime | None

    @validator("id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, '__str__'):
            return str(v)
        return v

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema para tokens de autenticação"""
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: Optional[int] = Field(None, description="Tempo de expiração em segundos")


class TokenResponse(BaseModel):
    """Schema completo para resposta de autenticação"""
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: Optional[int] = Field(None, description="Tempo de expiração em segundos")
    refresh_token: Optional[str] = Field(None, description="Token de refresh (opcional)")
    user: Optional[UserResponse] = Field(None, description="Dados do usuário autenticado")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password(cls, v):
        """Valida força da senha"""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Senha deve conter pelo menos um caractere especial")

        return v


class EmailVerificationRequest(BaseModel):
    token: str


class PasswordChangeRequest(BaseModel):
    """Schema para solicitação de mudança de senha"""
    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=8, description="Nova senha")
    confirm_password: str = Field(..., description="Confirmação da nova senha")

    @validator("new_password")
    def validate_new_password(cls, v):
        """Valida a nova senha"""
        if len(v) < 8:
            raise ValueError("Nova senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra")
        if not re.search(r"\d", v):
            raise ValueError("Nova senha deve conter pelo menos um número")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Valida se as senhas coincidem"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Senhas não coincidem")
        return v


class TwoFactorSetup(BaseModel):
    """Schema para configuração de autenticação de dois fatores"""
    secret: Optional[str] = Field(None, description="Chave secreta do 2FA")
    qr_code: Optional[str] = Field(None, description="QR code para configuração")
    backup_codes: Optional[List[str]] = Field(None, description="Códigos de backup")


class TwoFactorVerify(BaseModel):
    """Schema para verificação de código 2FA"""
    code: str = Field(..., description="Código de verificação 2FA")
    remember_device: Optional[bool] = Field(False, description="Lembrar dispositivo")


class TwoFactorDisable(BaseModel):
    """Schema para desabilitação de 2FA"""
    password: str = Field(..., description="Senha atual para confirmação")
    code: Optional[str] = Field(None, description="Código 2FA (se habilitado)")


class UserPreferences(BaseModel):
    """Schema para preferências do usuário"""
    language: Optional[str] = Field("pt-BR", description="Idioma preferido")
    timezone: Optional[str] = Field("America/Sao_Paulo", description="Fuso horário")
    email_notifications: Optional[bool] = Field(True, description="Receber notificações por email")
    push_notifications: Optional[bool] = Field(True, description="Receber notificações push")
    newsletter: Optional[bool] = Field(False, description="Receber newsletter")


class UserProfile(BaseModel):
    """Schema para perfil completo do usuário"""
    bio: Optional[str] = Field(None, description="Biografia do usuário")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    website: Optional[str] = Field(None, description="Website pessoal")
    location: Optional[str] = Field(None, description="Localização")
    company: Optional[str] = Field(None, description="Empresa")
    job_title: Optional[str] = Field(None, description="Cargo")


class UserStats(BaseModel):
    """Schema para estatísticas do usuário"""
    workflows_created: Optional[int] = Field(0, description="Workflows criados")
    workflows_executed: Optional[int] = Field(0, description="Workflows executados")
    last_login: Optional[datetime] = Field(None, description="Último login")
    account_created: Optional[datetime] = Field(None, description="Data de criação da conta")
    total_executions: Optional[int] = Field(0, description="Total de execuções")


class SessionInfo(BaseModel):
    """Schema para informações da sessão"""
    session_id: str = Field(..., description="ID da sessão")
    user_id: str = Field(..., description="ID do usuário")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Data de criação da sessão")
    expires_at: datetime = Field(..., description="Data de expiração da sessão")
    is_active: bool = Field(True, description="Sessão ativa")


class AuthProvider(BaseModel):
    """Schema para provedores de autenticação"""
    provider_id: str = Field(..., description="ID do provedor")
    provider_name: str = Field(..., description="Nome do provedor")
    client_id: Optional[str] = Field(None, description="Client ID")
    is_enabled: bool = Field(True, description="Provedor habilitado")
    scopes: Optional[List[str]] = Field(None, description="Escopos de permissão")


# ==================== WORKFLOW SCHEMAS ====================
# Note: Estas classes provavelmente deveriam estar em workflow.py
# mas estão aqui para manter compatibilidade


# Schemas para Workflow
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = []
    is_public: bool = False


class WorkflowCreate(WorkflowBase):
    definition: dict = Field(..., description="Estrutura completa do workflow")

    @validator("definition")
    def validate_definition(cls, v):
        """Valida estrutura da definição"""
        if not isinstance(v, dict):
            raise ValueError("Definição deve ser um objeto JSON válido")

        required_keys = ["nodes", "connections"]
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Definição deve conter a chave "{key}"')

        if not isinstance(v["nodes"], list):
            raise ValueError("Nodes deve ser uma lista")

        if not isinstance(v["connections"], list):
            raise ValueError("Connections deve ser uma lista")

        return v


class WorkflowUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    is_public: bool | None = None
    definition: dict | None = None
    status: str | None = None


class WorkflowResponse(WorkflowBase):
    id: str
    user_id: str
    workspace_id: str | None
    version: str
    status: str
    thumbnail_url: str | None
    downloads_count: int
    rating_average: float
    rating_count: int
    execution_count: int
    last_executed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    definition: dict | None = None

    @validator("id", "user_id", "workspace_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, '__str__'):
            return str(v)
        return v

    model_config = {"from_attributes": True}


# Schemas para Node
class NodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    type: str
    category: str | None = None
    is_public: bool = False


class NodeCreate(NodeBase):
    code_template: str = Field(..., min_length=1)
    input_schema: dict
    output_schema: dict
    parameters_schema: dict | None = {}
    icon: str | None = "🔧"
    color: str | None = "#6366f1"
    documentation: str | None = None
    examples: list[dict] | None = []

    @validator("input_schema", "output_schema")
    def validate_schemas(cls, v):
        """Valida schemas JSON"""
        if not isinstance(v, dict):
            raise ValueError("Schema deve ser um objeto JSON válido")

        required_keys = ["type", "properties"]
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Schema deve conter a chave "{key}"')

        return v


class NodeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    is_public: bool | None = None
    code_template: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    parameters_schema: dict | None = None
    icon: str | None = None
    color: str | None = None
    documentation: str | None = None
    examples: list[dict] | None = None


class NodeResponse(NodeBase):
    id: str
    user_id: str
    workspace_id: str | None
    status: str
    version: str
    icon: str
    color: str
    documentation: str | None
    examples: list[dict]
    downloads_count: int
    usage_count: int
    rating_average: float
    rating_count: int
    created_at: datetime | None
    updated_at: datetime | None
    code_template: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    parameters_schema: dict | None = None

    @validator("id", "user_id", "workspace_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, '__str__'):
            return str(v)
        return v

    model_config = {"from_attributes": True}


# Schemas para Agent
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    agent_type: str = "general"


class AgentCreate(AgentBase):
    personality: str | None = None
    instructions: str | None = None
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=4000)
    tools: list[str] | None = []
    knowledge_base: dict | None = {}
    avatar_url: str | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    personality: str | None = None
    instructions: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=4000)
    tools: list[str] | None = None
    knowledge_base: dict | None = None
    avatar_url: str | None = None
    status: str | None = None


class AgentResponse(AgentBase):
    id: str
    user_id: str
    workspace_id: str | None
    model_provider: str
    model_name: str
    temperature: float
    max_tokens: int
    status: str
    avatar_url: str | None
    conversation_count: int
    message_count: int
    rating_average: float
    rating_count: int
    last_active_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    @validator("id", "user_id", "workspace_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, '__str__'):
            return str(v)
        return v

    model_config = {"from_attributes": True}


# Schemas para Conversation
class ConversationCreate(BaseModel):
    agent_id: str | None = None
    title: str | None = None
    context: dict | None = {}


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    agent_id: str | None
    workspace_id: str | None
    title: str | None
    status: str
    message_count: int
    total_tokens_used: int
    last_message_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    @validator("id", "user_id", "agent_id", "workspace_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, '__str__'):
            return str(v)
        return v

    model_config = {"from_attributes": True}


# Schemas para Message
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    attachments: list[dict] | None = []


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    attachments: list[dict]
    model_used: str | None
    tokens_used: int
    processing_time_ms: int
    created_at: datetime | None

    @validator("id", "conversation_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, '__str__'):
            return str(v)
        return v

    model_config = {"from_attributes": True}


# Schemas para paginação
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list[dict]
    total: int
    page: int
    size: int
    pages: int
