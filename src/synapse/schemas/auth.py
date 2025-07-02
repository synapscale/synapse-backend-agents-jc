"""
Schemas Pydantic para autenticação e validação de dados
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
"""

from pydantic import BaseModel, EmailStr, validator, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re
import uuid


# ==================== ENUMS ALINHADOS COM O BANCO ====================


class UserStatus(str, Enum):
    """Status do usuário - ALINHADO COM O BANCO"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# ==================== SCHEMAS DE AUTENTICAÇÃO - LOGIN ====================


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


# ==================== SCHEMAS BASE PARA USUÁRIOS ====================


class UserBase(BaseModel):
    """Schema base para usuários - ALINHADO COM users TABLE"""

    email: EmailStr = Field(..., max_length=255, description="Email do usuário")
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    full_name: str = Field(
        ..., min_length=2, max_length=200, description="Nome completo"
    )

    @validator("username")
    def validate_username(cls, v):
        """Valida username - ALINHADO COM CONSTRAINT DO BANCO"""
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
    Schema para criação de novos usuários
    ALINHADO COM users TABLE + validações de negócio
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="Senha do usuário (mínimo 8 caracteres)",
    )
    confirm_password: Optional[str] = Field(None, description="Confirmação da senha")

    # Campos opcionais alinhados com a tabela users
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL da imagem de perfil"
    )
    bio: Optional[str] = Field(
        None, max_length=1000, description="Biografia do usuário"
    )
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")

    # Campos de negócio não persistidos diretamente
    terms_accepted: Optional[bool] = Field(
        False, description="Aceite dos termos de uso"
    )
    marketing_consent: Optional[bool] = Field(
        False, description="Consentimento para marketing"
    )

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
        if "password" in values and v != values["password"]:
            raise ValueError("Senhas não coincidem")
        return v


# Alias para compatibilidade
UserRegister = UserCreate


class UserUpdate(BaseModel):
    """Schema para atualização de usuários - ALINHADO COM users TABLE"""

    email: Optional[EmailStr] = Field(None, max_length=255, description="Novo email")
    username: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Novo username"
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=200, description="Novo nome completo"
    )
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="Nova URL da imagem"
    )
    bio: Optional[str] = Field(None, max_length=1000, description="Nova biografia")
    is_active: Optional[bool] = Field(None, description="Novo status ativo")
    is_verified: Optional[bool] = Field(None, description="Novo status verificado")
    status: Optional[UserStatus] = Field(None, description="Novo status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Novos metadados")

    @validator("username")
    def validate_username(cls, v):
        """Valida username"""
        if v and not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username deve conter apenas letras, números, _ ou -")
        return v.lower() if v else v

    @validator("full_name")
    def validate_full_name(cls, v):
        """Valida nome completo"""
        if v and len(v.strip()) < 2:
            raise ValueError("Nome completo deve ter pelo menos 2 caracteres")
        return v.strip() if v else v


class UserResponse(BaseModel):
    """Schema completo de resposta do usuário - PERFEITAMENTE ALINHADO COM users TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    # Campos principais - EXATAMENTE como na tabela
    id: uuid.UUID = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., description="Nome de usuário")
    full_name: str = Field(..., description="Nome completo")

    # Status e permissões - EXATAMENTE como na tabela
    is_active: bool = Field(..., description="Se o usuário está ativo")
    is_verified: bool = Field(..., description="Se o email foi verificado")
    is_superuser: bool = Field(..., description="Se é administrador")
    status: UserStatus = Field(..., description="Status atual")

    # Informações de perfil - EXATAMENTE como na tabela
    profile_image_url: Optional[str] = Field(
        None, description="URL da imagem de perfil"
    )
    bio: Optional[str] = Field(None, description="Biografia do usuário")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )

    # Informações de segurança - EXATAMENTE como na tabela
    last_login_at: Optional[datetime] = Field(None, description="Último login")
    login_count: int = Field(0, description="Número de logins")
    failed_login_attempts: int = Field(0, description="Tentativas de login falhadas")
    account_locked_until: Optional[datetime] = Field(
        None, description="Conta bloqueada até"
    )

    # Relacionamentos - EXATAMENTE como na tabela
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")

    # Timestamps - EXATAMENTE como na tabela
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== SCHEMAS DE TOKENS ====================


class Token(BaseModel):
    """Schema básico para tokens de autenticação"""

    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: Optional[int] = Field(
        None, description="Tempo de expiração em segundos"
    )


class TokenResponse(BaseModel):
    """Schema completo para resposta de autenticação"""

    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: Optional[int] = Field(
        None, description="Tempo de expiração em segundos"
    )
    refresh_token: Optional[str] = Field(None, description="Token de refresh")
    user: Optional[UserResponse] = Field(
        None, description="Dados do usuário autenticado"
    )


class RefreshTokenRequest(BaseModel):
    """Schema para solicitação de refresh token - ALINHADO COM refresh_tokens TABLE"""

    refresh_token: str = Field(..., max_length=500, description="Token de refresh")


class RefreshTokenResponse(BaseModel):
    """Schema de resposta do refresh token - ALINHADO COM refresh_tokens TABLE"""

    id: uuid.UUID = Field(..., description="ID do token")
    token: str = Field(..., description="Token de refresh")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    expires_at: datetime = Field(..., description="Data de expiração")
    is_revoked: Optional[bool] = Field(False, description="Se foi revogado")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS DE RESET DE SENHA ====================


class PasswordResetRequest(BaseModel):
    """Schema para solicitação de reset de senha - ALINHADO COM password_reset_tokens TABLE"""

    email: EmailStr = Field(..., description="Email para reset")


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha - ALINHADO COM password_reset_tokens TABLE"""

    token: str = Field(..., max_length=500, description="Token de reset")
    new_password: str = Field(
        ..., min_length=8, max_length=255, description="Nova senha"
    )

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


class PasswordResetTokenResponse(BaseModel):
    """Schema de resposta do token de reset - ALINHADO COM password_reset_tokens TABLE"""

    id: uuid.UUID = Field(..., description="ID do token")
    token: str = Field(..., description="Token de reset")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    expires_at: datetime = Field(..., description="Data de expiração")
    is_used: Optional[bool] = Field(False, description="Se foi usado")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS DE VERIFICAÇÃO DE EMAIL ====================


class EmailVerificationRequest(BaseModel):
    """Schema para verificação de email - ALINHADO COM email_verification_tokens TABLE"""

    token: str = Field(..., max_length=500, description="Token de verificação")


class EmailVerificationTokenResponse(BaseModel):
    """Schema de resposta do token de verificação - ALINHADO COM email_verification_tokens TABLE"""

    id: uuid.UUID = Field(..., description="ID do token")
    token: str = Field(..., description="Token de verificação")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    expires_at: datetime = Field(..., description="Data de expiração")
    is_used: Optional[bool] = Field(False, description="Se foi usado")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS DE MUDANÇA DE SENHA ====================


class PasswordChangeRequest(BaseModel):
    """Schema para mudança de senha autenticada"""

    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(
        ..., min_length=8, max_length=255, description="Nova senha"
    )
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
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Senhas não coincidem")
        return v


# ==================== SCHEMAS DE ROLES E TENANT ====================


class UserTenantRoleResponse(BaseModel):
    """Schema para roles do usuário por tenant - ALINHADO COM user_tenant_roles TABLE"""

    id: uuid.UUID = Field(..., description="ID do role")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    role_id: uuid.UUID = Field(..., description="ID do role")
    granted_by: Optional[uuid.UUID] = Field(None, description="Concedido por")
    granted_at: datetime = Field(..., description="Data de concessão")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    is_active: bool = Field(True, description="Se está ativo")
    conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Condições do role"
    )
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS DE 2FA (FUTURO) ====================


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


# ==================== SCHEMAS DE PREFERÊNCIAS E PERFIL ====================


class UserPreferences(BaseModel):
    """Schema para preferências do usuário (armazenadas em metadata)"""

    language: Optional[str] = Field("en", description="Idioma preferido")
    timezone: Optional[str] = Field("UTC", description="Fuso horário")
    email_notifications: Optional[bool] = Field(
        True, description="Notificações por email"
    )
    push_notifications: Optional[bool] = Field(True, description="Notificações push")
    newsletter: Optional[bool] = Field(False, description="Receber newsletter")


class UserProfile(BaseModel):
    """Schema para perfil estendido do usuário"""

    bio: Optional[str] = Field(
        None, max_length=1000, description="Biografia do usuário"
    )
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL do avatar"
    )
    website: Optional[str] = Field(None, description="Website pessoal")
    location: Optional[str] = Field(None, description="Localização")
    company: Optional[str] = Field(None, description="Empresa")
    job_title: Optional[str] = Field(None, description="Cargo")


class UserStats(BaseModel):
    """Schema para estatísticas do usuário"""

    login_count: int = Field(0, description="Número total de logins")
    last_login_at: Optional[datetime] = Field(None, description="Último login")
    failed_login_attempts: int = Field(0, description="Tentativas de login falhadas")
    account_created: datetime = Field(..., description="Data de criação da conta")
    workspaces_count: Optional[int] = Field(0, description="Número de workspaces")
    workflows_count: Optional[int] = Field(0, description="Número de workflows")


# ==================== SCHEMAS DE SESSÃO E SEGURANÇA ====================


class SessionInfo(BaseModel):
    """Schema para informações da sessão"""

    session_id: str = Field(..., description="ID da sessão")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Data de criação da sessão")
    expires_at: datetime = Field(..., description="Data de expiração da sessão")
    is_active: bool = Field(True, description="Sessão ativa")


class AuthProvider(BaseModel):
    """Schema para provedores de autenticação externos"""

    provider_id: str = Field(..., description="ID do provedor")
    provider_name: str = Field(..., description="Nome do provedor")
    client_id: Optional[str] = Field(None, description="Client ID")
    is_enabled: bool = Field(True, description="Provedor habilitado")
    scopes: Optional[List[str]] = Field(None, description="Escopos de permissão")


# ==================== SCHEMAS DE LISTAGEM E BUSCA ====================


class UserListResponse(BaseModel):
    """Schema para listagem de usuários"""

    users: List[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de usuários")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")


class UserSearchRequest(BaseModel):
    """Schema para busca de usuários"""

    query: Optional[str] = Field(None, description="Termo de busca")
    status: Optional[UserStatus] = Field(None, description="Filtrar por status")
    tenant_id: Optional[uuid.UUID] = Field(None, description="Filtrar por tenant")
    is_verified: Optional[bool] = Field(None, description="Filtrar por verificação")
    is_active: Optional[bool] = Field(None, description="Filtrar por ativo")
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Tamanho da página")
