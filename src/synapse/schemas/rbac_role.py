"""
Schemas para RBACRole - roles do sistema RBAC
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class RBACRoleBase(BaseModel):
    """Schema base para RBACRole"""
    
    name: str = Field(..., min_length=1, max_length=100, description="Nome da role")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da role")
    
    # Configurações
    is_active: bool = Field(True, description="Role ativa")
    is_system: bool = Field(False, description="Role do sistema (não editável)")
    
    # Prioridade e hierarquia
    priority: int = Field(0, description="Prioridade da role (0=maior)")
    parent_role_id: Optional[UUID] = Field(None, description="ID da role pai")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class RBACRoleCreate(RBACRoleBase):
    """Schema para criação de RBACRole"""
    
    # Permissions podem ser adicionadas na criação
    permission_ids: Optional[List[UUID]] = Field(None, description="IDs das permissões")


class RBACRoleUpdate(BaseModel):
    """Schema para atualização de RBACRole"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome da role")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da role")
    
    is_active: Optional[bool] = Field(None, description="Role ativa")
    priority: Optional[int] = Field(None, description="Prioridade da role")
    parent_role_id: Optional[UUID] = Field(None, description="ID da role pai")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class RBACRoleResponse(RBACRoleBase):
    """Schema para resposta de RBACRole"""
    
    id: UUID = Field(..., description="ID único da role")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    parent_role_name: Optional[str] = Field(None, description="Nome da role pai")
    users_count: Optional[int] = Field(None, description="Número de usuários com esta role")
    permissions_count: Optional[int] = Field(None, description="Número de permissões")
    
    model_config = ConfigDict(from_attributes=True)


class RBACRoleWithPermissions(RBACRoleResponse):
    """Schema para RBACRole com permissões"""
    
    permissions: List[Dict[str, Any]] = Field(..., description="Permissões da role")
    
    model_config = ConfigDict(from_attributes=True)


class RBACRoleList(BaseModel):
    """Schema para lista de RBACRole"""
    
    items: List[RBACRoleResponse] = Field(..., description="Lista de roles")
    total: int = Field(..., description="Total de roles")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class RBACRoleHierarchy(BaseModel):
    """Schema para hierarquia de roles"""
    
    role: RBACRoleResponse = Field(..., description="Role principal")
    children: List["RBACRoleHierarchy"] = Field(..., description="Roles filhas")
    
    model_config = ConfigDict(from_attributes=True)


class RBACRoleAssignment(BaseModel):
    """Schema para atribuição de role"""
    
    role_id: UUID = Field(..., description="ID da role")
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Contexto da atribuição
    assigned_by: UUID = Field(..., description="ID do usuário que atribuiu")
    assigned_at: datetime = Field(..., description="Data da atribuição")
    
    # Configurações
    is_active: bool = Field(True, description="Atribuição ativa")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    model_config = ConfigDict(from_attributes=True)


class RBACRolePermissionAssignment(BaseModel):
    """Schema para atribuição de permissão a role"""
    
    role_id: UUID = Field(..., description="ID da role")
    permission_id: UUID = Field(..., description="ID da permissão")
    
    # Configurações
    is_active: bool = Field(True, description="Atribuição ativa")
    granted_by: UUID = Field(..., description="ID do usuário que concedeu")
    granted_at: datetime = Field(..., description="Data da concessão")
    
    model_config = ConfigDict(from_attributes=True)


class RBACRoleStatistics(BaseModel):
    """Schema para estatísticas de roles"""
    
    total_roles: int = Field(..., description="Total de roles")
    active_roles: int = Field(..., description="Roles ativas")
    system_roles: int = Field(..., description="Roles do sistema")
    
    # Uso
    total_assignments: int = Field(..., description="Total de atribuições")
    active_assignments: int = Field(..., description="Atribuições ativas")
    
    # Por tenant
    by_tenant: Dict[str, int] = Field(..., description="Por tenant")
    
    model_config = ConfigDict(from_attributes=True)
