"""
Schemas Pydantic para RBAC (Role-Based Access Control)
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
Tabelas: rbac_roles, rbac_permissions, rbac_role_permissions
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ==================== ENUMS ALINHADOS COM O BANCO ====================


class PermissionCategory(str, Enum):
    """Categorias de permissões"""

    USER = "user"
    WORKSPACE = "workspace"
    WORKFLOW = "workflow"
    AGENT = "agent"
    BILLING = "billing"
    ADMIN = "admin"
    SYSTEM = "system"


class PermissionAction(str, Enum):
    """Ações de permissões"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SHARE = "share"
    MANAGE = "manage"
    ADMIN = "admin"


class PermissionResource(str, Enum):
    """Recursos de permissões"""

    USER = "user"
    WORKSPACE = "workspace"
    WORKFLOW = "workflow"
    NODE = "node"
    AGENT = "agent"
    FILE = "file"
    BILLING = "billing"
    ANALYTICS = "analytics"
    SYSTEM = "system"


# ==================== RBAC ROLES SCHEMAS ====================


class RoleBase(BaseModel):
    """Schema base para roles - ALINHADO COM rbac_roles TABLE"""

    name: str = Field(..., min_length=1, max_length=100, description="Nome do role")
    description: Optional[str] = Field(None, description="Descrição do role")
    is_system: bool = Field(False, description="Se é um role do sistema")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados do role"
    )


class RoleCreate(RoleBase):
    """Schema para criação de roles"""

    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class RoleUpdate(BaseModel):
    """Schema para atualização de roles"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Novo nome"
    )
    description: Optional[str] = Field(None, description="Nova descrição")
    is_system: Optional[bool] = Field(None, description="Novo status de sistema")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Novos metadados")


class RoleResponse(RoleBase):
    """Schema de resposta para roles - ALINHADO COM rbac_roles TABLE"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do role")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== RBAC PERMISSIONS SCHEMAS ====================


class PermissionBase(BaseModel):
    """Schema base para permissões - ALINHADO COM rbac_permissions TABLE"""

    key: str = Field(
        ..., min_length=1, max_length=100, description="Chave única da permissão"
    )
    description: Optional[str] = Field(None, description="Descrição da permissão")
    category: Optional[PermissionCategory] = Field(
        None, description="Categoria da permissão"
    )
    resource: Optional[PermissionResource] = Field(
        None, description="Recurso da permissão"
    )
    action: Optional[PermissionAction] = Field(None, description="Ação da permissão")

    @validator("key")
    def validate_permission_key(cls, v):
        """Valida formato da chave de permissão"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Chave da permissão é obrigatória")
        # Formato esperado: resource:action ou categoria.resource:action
        if ":" not in v:
            raise ValueError(
                "Chave deve seguir formato 'resource:action' ou 'categoria.resource:action'"
            )
        return v.strip().lower()


class PermissionCreate(PermissionBase):
    """Schema para criação de permissões"""

    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class PermissionUpdate(BaseModel):
    """Schema para atualização de permissões"""

    key: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nova chave"
    )
    description: Optional[str] = Field(None, description="Nova descrição")
    category: Optional[PermissionCategory] = Field(None, description="Nova categoria")
    resource: Optional[PermissionResource] = Field(None, description="Novo recurso")
    action: Optional[PermissionAction] = Field(None, description="Nova ação")


class PermissionResponse(PermissionBase):
    """Schema de resposta para permissões - ALINHADO COM rbac_permissions TABLE"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único da permissão")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== RBAC ROLE PERMISSIONS SCHEMAS ====================


class RolePermissionBase(BaseModel):
    """Schema base para role-permissions - ALINHADO COM rbac_role_permissions TABLE"""

    role_id: uuid.UUID = Field(..., description="ID do role")
    permission_id: uuid.UUID = Field(..., description="ID da permissão")
    granted: bool = Field(True, description="Se a permissão está concedida")
    conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Condições para a permissão"
    )


class RolePermissionCreate(RolePermissionBase):
    """Schema para criação de role-permissions"""

    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class RolePermissionUpdate(BaseModel):
    """Schema para atualização de role-permissions"""

    granted: Optional[bool] = Field(None, description="Novo status de concessão")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Novas condições")


class RolePermissionResponse(RolePermissionBase):
    """Schema de resposta para role-permissions - ALINHADO COM rbac_role_permissions TABLE"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único da associação")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== SCHEMAS EXPANDIDOS COM RELACIONAMENTOS ====================


class RoleWithPermissions(RoleResponse):
    """Role com suas permissões"""

    permissions: List[PermissionResponse] = Field(
        default_factory=list, description="Permissões do role"
    )
    permission_count: int = Field(0, description="Total de permissões")


class PermissionWithRoles(PermissionResponse):
    """Permissão com seus roles"""

    roles: List[RoleResponse] = Field(
        default_factory=list, description="Roles com esta permissão"
    )
    role_count: int = Field(0, description="Total de roles")


class UserPermissionCheck(BaseModel):
    """Schema para verificação de permissões de usuário"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    permission_key: str = Field(..., description="Chave da permissão a verificar")
    resource_id: Optional[uuid.UUID] = Field(
        None, description="ID do recurso específico"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Contexto adicional"
    )


class UserPermissionResult(BaseModel):
    """Resultado da verificação de permissão"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    permission_key: str = Field(..., description="Chave da permissão")
    granted: bool = Field(..., description="Se a permissão foi concedida")
    source_role: Optional[str] = Field(
        None, description="Role que concedeu a permissão"
    )
    conditions_met: bool = Field(True, description="Se as condições foram atendidas")
    reason: Optional[str] = Field(None, description="Razão da decisão")


# ==================== SCHEMAS DE BULK OPERATIONS ====================


class BulkRolePermissionCreate(BaseModel):
    """Schema para criação em lote de role-permissions"""

    role_id: uuid.UUID = Field(..., description="ID do role")
    permission_ids: List[uuid.UUID] = Field(
        ..., min_items=1, description="IDs das permissões"
    )
    granted: bool = Field(True, description="Status de concessão")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Condições")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class BulkRolePermissionResult(BaseModel):
    """Resultado de operação em lote"""

    created: int = Field(..., description="Quantidade criada")
    updated: int = Field(..., description="Quantidade atualizada")
    errors: List[str] = Field(default_factory=list, description="Erros encontrados")
    role_permissions: List[RolePermissionResponse] = Field(
        default_factory=list, description="Associações criadas/atualizadas"
    )


# ==================== SCHEMAS DE LISTAGEM E BUSCA ====================


class RoleListResponse(BaseModel):
    """Schema para listagem de roles"""

    roles: List[RoleResponse] = Field(..., description="Lista de roles")
    total: int = Field(..., description="Total de roles")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")


class PermissionListResponse(BaseModel):
    """Schema para listagem de permissões"""

    permissions: List[PermissionResponse] = Field(
        ..., description="Lista de permissões"
    )
    total: int = Field(..., description="Total de permissões")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")


class RoleSearchRequest(BaseModel):
    """Schema para busca de roles"""

    query: Optional[str] = Field(None, description="Termo de busca")
    tenant_id: Optional[uuid.UUID] = Field(None, description="Filtrar por tenant")
    is_system: Optional[bool] = Field(None, description="Filtrar por roles do sistema")
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Tamanho da página")


class PermissionSearchRequest(BaseModel):
    """Schema para busca de permissões"""

    query: Optional[str] = Field(None, description="Termo de busca")
    category: Optional[PermissionCategory] = Field(
        None, description="Filtrar por categoria"
    )
    resource: Optional[PermissionResource] = Field(
        None, description="Filtrar por recurso"
    )
    action: Optional[PermissionAction] = Field(None, description="Filtrar por ação")
    tenant_id: Optional[uuid.UUID] = Field(None, description="Filtrar por tenant")
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Tamanho da página")


# ==================== SCHEMAS DE TEMPLATES E PRESETS ====================


class RoleTemplate(BaseModel):
    """Schema para templates de roles predefinidos"""

    template_name: str = Field(..., description="Nome do template")
    role_data: RoleCreate = Field(..., description="Dados do role")
    permission_keys: List[str] = Field(..., description="Chaves das permissões")
    description: Optional[str] = Field(None, description="Descrição do template")


class PermissionPreset(BaseModel):
    """Schema para conjuntos predefinidos de permissões"""

    preset_name: str = Field(..., description="Nome do preset")
    category: PermissionCategory = Field(..., description="Categoria do preset")
    permissions: List[PermissionCreate] = Field(..., description="Permissões do preset")
    description: Optional[str] = Field(None, description="Descrição do preset")
