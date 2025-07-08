"""
Endpoints para gerenciamento do sistema RBAC
Inclui roles, permissions e user tenant roles
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from synapse.api.deps import get_db, get_current_user, require_admin
from synapse.models.user import User
from synapse.models.rbac import (
    RBACRole,
    RBACPermission,
    RBACRolePermission,
    UserTenantRole,
)
from synapse.schemas.rbac import (
    RBACRoleCreate,
    RBACRoleUpdate,
    RBACRoleResponse,
    RBACRoleListResponse,
    RBACPermissionCreate,
    RBACPermissionResponse,
    RBACPermissionListResponse,
    UserTenantRoleCreate,
    UserTenantRoleResponse,
    PaginatedResponse,
)

router = APIRouter()


# ===== ROLES ENDPOINTS =====


@router.get("/roles", response_model=RBACRoleListResponse)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Buscar por nome"),
    is_system: Optional[bool] = Query(None, description="Filtrar por roles do sistema"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista roles RBAC do tenant atual
    """
    query = db.query(RBACRole).filter(RBACRole.tenant_id == current_user.tenant_id)

    if search:
        query = query.filter(RBACRole.name.ilike(f"%{search}%"))

    if is_system is not None:
        query = query.filter(RBACRole.is_system == is_system)

    total = query.count()
    roles = query.offset(skip).limit(limit).all()

    return RBACRoleListResponse(
        items=[RBACRoleResponse.model_validate(role) for role in roles],
        total=total,
        page=(skip // limit) + 1,
        pages=((total - 1) // limit) + 1 if total > 0 else 0,
        size=limit,
    )


@router.post(
    "/roles", response_model=RBACRoleResponse, status_code=status.HTTP_201_CREATED
)
async def create_role(
    role_data: RBACRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Cria um novo role RBAC (apenas admins)
    """
    # Verificar se já existe role com o mesmo nome no tenant
    existing_role = (
        db.query(RBACRole)
        .filter(
            RBACRole.name == role_data.name,
            RBACRole.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role com este nome já existe",
        )

    # Criar role
    role = RBACRole(**role_data.model_dump(), tenant_id=current_user.tenant_id)

    db.add(role)
    db.commit()
    db.refresh(role)

    return RBACRoleResponse.model_validate(role)


@router.get("/roles/{role_id}", response_model=RBACRoleResponse)
async def get_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém detalhes de um role específico
    """
    role = (
        db.query(RBACRole)
        .filter(RBACRole.id == role_id, RBACRole.tenant_id == current_user.tenant_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role não encontrado"
        )

    return RBACRoleResponse.model_validate(role)


@router.put("/roles/{role_id}", response_model=RBACRoleResponse)
async def update_role(
    role_id: uuid.UUID,
    role_data: RBACRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Atualiza um role existente (apenas admins)
    """
    role = (
        db.query(RBACRole)
        .filter(RBACRole.id == role_id, RBACRole.tenant_id == current_user.tenant_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role não encontrado"
        )

    # Não permitir edição de roles do sistema
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível editar roles do sistema",
        )

    # Verificar conflito de nome
    if role_data.name and role_data.name != role.name:
        existing_role = (
            db.query(RBACRole)
            .filter(
                RBACRole.name == role_data.name,
                RBACRole.tenant_id == current_user.tenant_id,
                RBACRole.id != role_id,
            )
            .first()
        )

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role com este nome já existe",
            )

    # Atualizar campos
    for field, value in role_data.model_dump(exclude_unset=True).items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)

    return RBACRoleResponse.model_validate(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Remove um role (apenas admins)
    """
    role = (
        db.query(RBACRole)
        .filter(RBACRole.id == role_id, RBACRole.tenant_id == current_user.tenant_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role não encontrado"
        )

    # Não permitir remoção de roles do sistema
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível remover roles do sistema",
        )

    # Verificar se há usuários usando este role
    user_roles = (
        db.query(UserTenantRole).filter(UserTenantRole.role_id == role_id).count()
    )
    if user_roles > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover role que está sendo usado por usuários",
        )

    db.delete(role)
    db.commit()


# ===== PERMISSIONS ENDPOINTS =====


@router.get("/permissions", response_model=RBACPermissionListResponse)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Buscar por nome"),
    resource: Optional[str] = Query(None, description="Filtrar por recurso"),
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Lista todas as permissions (apenas admins)
    """
    query = db.query(RBACPermission)

    if search:
        query = query.filter(RBACPermission.name.ilike(f"%{search}%"))

    if resource:
        query = query.filter(RBACPermission.resource == resource)

    if action:
        query = query.filter(RBACPermission.action == action)

    total = query.count()
    permissions = query.offset(skip).limit(limit).all()

    return RBACPermissionListResponse(
        items=[RBACPermissionResponse.model_validate(perm) for perm in permissions],
        total=total,
        page=(skip // limit) + 1,
        pages=((total - 1) // limit) + 1 if total > 0 else 0,
        size=limit,
    )


@router.post(
    "/permissions",
    response_model=RBACPermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    permission_data: RBACPermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Cria uma nova permission (apenas admins)
    """
    # Verificar se já existe permission com o mesmo nome
    existing_perm = (
        db.query(RBACPermission)
        .filter(RBACPermission.name == permission_data.name)
        .first()
    )

    if existing_perm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission com este nome já existe",
        )

    # Criar permission
    permission = RBACPermission(**permission_data.model_dump())

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return RBACPermissionResponse.model_validate(permission)


# ===== USER TENANT ROLES ENDPOINTS =====


@router.post(
    "/user-roles",
    response_model=UserTenantRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_user_role(
    user_role_data: UserTenantRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Atribui um role a um usuário em um tenant (apenas admins)
    """
    # Verificar se o role existe no mesmo tenant
    role = (
        db.query(RBACRole)
        .filter(
            RBACRole.id == user_role_data.role_id,
            RBACRole.tenant_id == user_role_data.tenant_id,
        )
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado no tenant especificado",
        )

    # Verificar se já existe esta atribuição
    existing_assignment = (
        db.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == user_role_data.user_id,
            UserTenantRole.tenant_id == user_role_data.tenant_id,
            UserTenantRole.role_id == user_role_data.role_id,
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já possui este role no tenant",
        )

    # Criar atribuição
    user_role = UserTenantRole(**user_role_data.model_dump())

    db.add(user_role)
    db.commit()
    db.refresh(user_role)

    return UserTenantRoleResponse.model_validate(user_role)


@router.delete("/user-roles/{user_role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_role(
    user_role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Remove um role de um usuário (apenas admins)
    """
    user_role = (
        db.query(UserTenantRole).filter(UserTenantRole.id == user_role_id).first()
    )

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atribuição de role não encontrada",
        )

    db.delete(user_role)
    db.commit()


@router.get("/roles/{role_id}/permissions", response_model=RBACPermissionListResponse)
async def get_role_permissions(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista permissions de um role específico
    """
    role = (
        db.query(RBACRole)
        .filter(RBACRole.id == role_id, RBACRole.tenant_id == current_user.tenant_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role não encontrado"
        )

    # Buscar permissions através da tabela de relacionamento
    permissions = (
        db.query(RBACPermission)
        .join(RBACRolePermission, RBACPermission.id == RBACRolePermission.permission_id)
        .filter(RBACRolePermission.role_id == role_id)
        .all()
    )

    return RBACPermissionListResponse(
        items=[RBACPermissionResponse.model_validate(perm) for perm in permissions],
        total=len(permissions),
        page=1,
        pages=1,
        size=len(permissions),
    )


@router.post(
    "/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_201_CREATED
)
async def assign_permission_to_role(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Atribui uma permission a um role (apenas admins)
    """
    # Verificar se o role existe no tenant atual
    role = (
        db.query(RBACRole)
        .filter(RBACRole.id == role_id, RBACRole.tenant_id == current_user.tenant_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role não encontrado"
        )

    # Verificar se a permission existe
    permission = (
        db.query(RBACPermission).filter(RBACPermission.id == permission_id).first()
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission não encontrada"
        )

    # Verificar se já existe esta atribuição
    existing_assignment = (
        db.query(RBACRolePermission)
        .filter(
            RBACRolePermission.role_id == role_id,
            RBACRolePermission.permission_id == permission_id,
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission já está atribuída ao role",
        )

    # Criar atribuição
    role_permission = RBACRolePermission(role_id=role_id, permission_id=permission_id)

    db.add(role_permission)
    db.commit()

    return {"message": "Permission atribuída ao role com sucesso"}


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_permission_from_role(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Remove uma permission de um role (apenas admins)
    """
    # Verificar se o role existe no tenant atual
    role = (
        db.query(RBACRole)
        .filter(RBACRole.id == role_id, RBACRole.tenant_id == current_user.tenant_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role não encontrado"
        )

    # Buscar a atribuição
    role_permission = (
        db.query(RBACRolePermission)
        .filter(
            RBACRolePermission.role_id == role_id,
            RBACRolePermission.permission_id == permission_id,
        )
        .first()
    )

    if not role_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission não está atribuída ao role",
        )

    db.delete(role_permission)
    db.commit()
