"""
Schemas para RBACPermission - permissões do sistema RBAC
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class RBACPermissionBase(BaseModel):
    """Schema base para RBACPermission"""
    
    name: str = Field(..., min_length=1, max_length=100, description="Nome da permissão")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da permissão")
    
    # Identificação única
    permission_key: str = Field(..., description="Chave única da permissão")
    
    # Categoria e tipo
    category: str = Field(..., description="Categoria da permissão")
    action: str = Field(..., description="Ação da permissão (read, write, delete, etc)")
    resource: str = Field(..., description="Recurso da permissão")
    
    # Configurações
    is_active: bool = Field(True, description="Permissão ativa")
    is_system: bool = Field(False, description="Permissão do sistema (não editável)")
    
    # Contexto
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant (null para permissões globais)")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class RBACPermissionCreate(RBACPermissionBase):
    """Schema para criação de RBACPermission"""
    pass


class RBACPermissionUpdate(BaseModel):
    """Schema para atualização de RBACPermission"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome da permissão")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da permissão")
    
    category: Optional[str] = Field(None, description="Categoria da permissão")
    action: Optional[str] = Field(None, description="Ação da permissão")
    resource: Optional[str] = Field(None, description="Recurso da permissão")
    
    is_active: Optional[bool] = Field(None, description="Permissão ativa")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class RBACPermissionResponse(RBACPermissionBase):
    """Schema para resposta de RBACPermission"""
    
    id: UUID = Field(..., description="ID único da permissão")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    roles_count: Optional[int] = Field(None, description="Número de roles com esta permissão")
    users_count: Optional[int] = Field(None, description="Número de usuários com esta permissão")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionList(BaseModel):
    """Schema para lista de RBACPermission"""
    
    items: List[RBACPermissionResponse] = Field(..., description="Lista de permissões")
    total: int = Field(..., description="Total de permissões")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionCheck(BaseModel):
    """Schema para verificação de permissão"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    permission_key: str = Field(..., description="Chave da permissão")
    resource_id: Optional[UUID] = Field(None, description="ID do recurso específico")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionCheckResult(BaseModel):
    """Schema para resultado da verificação de permissão"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    permission_key: str = Field(..., description="Chave da permissão")
    resource_id: Optional[UUID] = Field(None, description="ID do recurso")
    
    # Resultado
    has_permission: bool = Field(..., description="Usuário tem a permissão")
    granted_by: Optional[str] = Field(None, description="Como foi concedida (role, direct, etc)")
    role_name: Optional[str] = Field(None, description="Nome da role que concedeu")
    
    # Contexto
    checked_at: datetime = Field(..., description="Data da verificação")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionGrant(BaseModel):
    """Schema para concessão de permissão"""
    
    permission_id: UUID = Field(..., description="ID da permissão")
    user_id: Optional[UUID] = Field(None, description="ID do usuário (se concessão direta)")
    role_id: Optional[UUID] = Field(None, description="ID da role (se concessão via role)")
    
    # Configurações
    is_active: bool = Field(True, description="Concessão ativa")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    # Contexto
    granted_by: UUID = Field(..., description="ID do usuário que concedeu")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionsByCategory(BaseModel):
    """Schema para permissões agrupadas por categoria"""
    
    category: str = Field(..., description="Nome da categoria")
    permissions: List[RBACPermissionResponse] = Field(..., description="Permissões da categoria")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionMatrix(BaseModel):
    """Schema para matrix de permissões"""
    
    user_id: UUID = Field(..., description="ID do usuário")
    permissions: Dict[str, bool] = Field(..., description="Mapa de permissões")
    roles: List[str] = Field(..., description="Roles do usuário")
    
    # Contexto
    generated_at: datetime = Field(..., description="Data de geração")
    
    model_config = ConfigDict(from_attributes=True)


class RBACPermissionStatistics(BaseModel):
    """Schema para estatísticas de permissões"""
    
    total_permissions: int = Field(..., description="Total de permissões")
    active_permissions: int = Field(..., description="Permissões ativas")
    system_permissions: int = Field(..., description="Permissões do sistema")
    
    # Por categoria
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    by_action: Dict[str, int] = Field(..., description="Por ação")
    by_resource: Dict[str, int] = Field(..., description="Por recurso")
    
    model_config = ConfigDict(from_attributes=True)
