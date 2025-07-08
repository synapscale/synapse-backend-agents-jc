"""
Schemas para UserTenantRole - roles de usuários por tenant
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, validator
from uuid import UUID


class UserTenantRoleBase(BaseModel):
    """Schema base para UserTenantRole"""
    
    # Relacionamentos
    user_id: UUID = Field(..., description="ID do usuário")
    tenant_id: UUID = Field(..., description="ID do tenant")
    role_id: UUID = Field(..., description="ID do role")
    granted_by: Optional[UUID] = Field(None, description="ID do usuário que concedeu")
    
    # Configuração
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    is_active: bool = Field(True, description="Role ativo")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Condições específicas")

    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('Expiration date must be in the future')
        return v


class UserTenantRoleCreate(UserTenantRoleBase):
    """Schema para criação de UserTenantRole"""
    pass


class UserTenantRoleUpdate(BaseModel):
    """Schema para atualização de UserTenantRole"""
    
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    is_active: Optional[bool] = Field(None, description="Role ativo")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Condições específicas")

    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('Expiration date must be in the future')
        return v


class UserTenantRoleResponse(UserTenantRoleBase):
    """Schema para resposta de UserTenantRole"""
    
    id: UUID = Field(..., description="ID único do role assignment")
    granted_at: datetime = Field(..., description="Data de concessão")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    tenant_name: Optional[str] = Field(None, description="Nome do tenant")
    role_name: Optional[str] = Field(None, description="Nome do role")
    role_description: Optional[str] = Field(None, description="Descrição do role")
    granter_name: Optional[str] = Field(None, description="Nome do usuário que concedeu")
    
    # Campos computados
    is_valid: Optional[bool] = Field(None, description="Role válido")
    is_expired: Optional[bool] = Field(None, description="Role expirado")
    is_permanent: Optional[bool] = Field(None, description="Role permanente")
    days_until_expiry: Optional[int] = Field(None, description="Dias até expirar")
    is_expiring_soon: Optional[bool] = Field(None, description="Expira em breve")
    
    # Permissões
    permissions: Optional[List[str]] = Field(None, description="Lista de permissões")
    permission_count: Optional[int] = Field(None, description="Número de permissões")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleList(BaseModel):
    """Schema para lista de UserTenantRole"""
    
    items: List[UserTenantRoleResponse] = Field(..., description="Lista de role assignments")
    total: int = Field(..., description="Total de role assignments")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleFilter(BaseModel):
    """Schema para filtro de UserTenantRole"""
    
    user_id: Optional[UUID] = Field(None, description="Filtrar por usuário")
    tenant_id: Optional[UUID] = Field(None, description="Filtrar por tenant")
    role_id: Optional[UUID] = Field(None, description="Filtrar por role")
    granted_by: Optional[UUID] = Field(None, description="Filtrar por quem concedeu")
    
    is_active: Optional[bool] = Field(None, description="Filtrar por status ativo")
    is_expired: Optional[bool] = Field(None, description="Filtrar por expirados")
    is_permanent: Optional[bool] = Field(None, description="Filtrar por permanentes")
    is_expiring_soon: Optional[bool] = Field(None, description="Filtrar por expirando em breve")
    
    granted_after: Optional[datetime] = Field(None, description="Concedido após")
    granted_before: Optional[datetime] = Field(None, description="Concedido antes")
    expires_after: Optional[datetime] = Field(None, description="Expira após")
    expires_before: Optional[datetime] = Field(None, description="Expira antes")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleAssign(BaseModel):
    """Schema para atribuição de UserTenantRole"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    tenant_id: UUID = Field(..., description="ID do tenant")
    role_id: UUID = Field(..., description="ID do role")
    
    # Configuração
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Condições específicas")
    
    # Contexto
    reason: Optional[str] = Field(None, description="Motivo da atribuição")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleRevoke(BaseModel):
    """Schema para revogação de UserTenantRole"""
    
    role_assignment_id: Optional[UUID] = Field(None, description="ID do assignment específico")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")
    role_id: Optional[UUID] = Field(None, description="ID do role")
    
    # Contexto
    reason: Optional[str] = Field(None, description="Motivo da revogação")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleExtend(BaseModel):
    """Schema para extensão de UserTenantRole"""
    
    role_assignment_id: UUID = Field(..., description="ID do assignment")
    
    # Extensão
    extend_days: Optional[int] = Field(None, description="Dias para estender")
    new_expires_at: Optional[datetime] = Field(None, description="Nova data de expiração")
    make_permanent: Optional[bool] = Field(None, description="Tornar permanente")
    
    # Contexto
    reason: Optional[str] = Field(None, description="Motivo da extensão")
    
    model_config = ConfigDict(from_attributes=True)

    @validator('new_expires_at')
    def validate_new_expires_at(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('New expiration date must be in the future')
        return v

    @validator('extend_days')
    def validate_extend_days(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Extend days must be positive')
        return v


class UserTenantRolePermissionCheck(BaseModel):
    """Schema para verificação de permissão"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    tenant_id: UUID = Field(..., description="ID do tenant")
    permission_key: str = Field(..., description="Chave da permissão")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRolePermissionResult(BaseModel):
    """Schema para resultado da verificação de permissão"""
    
    has_permission: bool = Field(..., description="Tem permissão")
    
    # Detalhes
    matching_roles: List[str] = Field([], description="Roles que concedem a permissão")
    active_assignments: int = Field(0, description="Assignments ativos")
    
    # Contexto
    checked_at: datetime = Field(..., description="Data da verificação")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleStatistics(BaseModel):
    """Schema para estatísticas de UserTenantRole"""
    
    # Totais
    total_assignments: int = Field(..., description="Total de assignments")
    active_assignments: int = Field(..., description="Assignments ativos")
    expired_assignments: int = Field(..., description="Assignments expirados")
    permanent_assignments: int = Field(..., description="Assignments permanentes")
    
    # Por usuário
    unique_users: int = Field(..., description="Usuários únicos")
    assignments_per_user: Dict[str, int] = Field(..., description="Assignments por usuário")
    
    # Por tenant
    unique_tenants: int = Field(..., description="Tenants únicos")
    assignments_per_tenant: Dict[str, int] = Field(..., description="Assignments por tenant")
    
    # Por role
    unique_roles: int = Field(..., description="Roles únicos")
    assignments_per_role: Dict[str, int] = Field(..., description="Assignments por role")
    
    # Expiração
    expiring_soon: int = Field(..., description="Expirando em breve")
    expiring_today: int = Field(..., description="Expirando hoje")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleCleanup(BaseModel):
    """Schema para limpeza de UserTenantRole"""
    
    # Critérios
    cleanup_expired: bool = Field(True, description="Limpar expirados")
    cleanup_inactive: bool = Field(True, description="Limpar inativos")
    cleanup_older_than_days: Optional[int] = Field(None, description="Limpar mais antigos que X dias")
    
    # Contexto
    tenant_id: Optional[UUID] = Field(None, description="Tenant específico")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleCleanupResult(BaseModel):
    """Schema para resultado da limpeza"""
    
    cleaned_assignments: int = Field(..., description="Assignments limpos")
    
    # Detalhes
    expired_cleaned: int = Field(..., description="Expirados limpos")
    inactive_cleaned: int = Field(..., description="Inativos limpos")
    old_cleaned: int = Field(..., description="Antigos limpos")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleAudit(BaseModel):
    """Schema para auditoria de UserTenantRole"""
    
    # Identificação
    assignment_id: UUID = Field(..., description="ID do assignment")
    
    # Evento
    event_type: str = Field(..., description="Tipo de evento")
    event_data: Dict[str, Any] = Field(..., description="Dados do evento")
    
    # Contexto
    performed_by: UUID = Field(..., description="Quem realizou")
    performed_at: datetime = Field(..., description="Quando foi realizado")
    
    model_config = ConfigDict(from_attributes=True)


class UserTenantRoleExpirationAlert(BaseModel):
    """Schema para alertas de expiração"""
    
    # Configuração
    days_before_expiry: int = Field(7, description="Dias antes da expiração")
    
    # Resultados
    expiring_assignments: List[UserTenantRoleResponse] = Field([], description="Assignments expirando")
    alert_count: int = Field(0, description="Número de alertas")
    
    model_config = ConfigDict(from_attributes=True)
