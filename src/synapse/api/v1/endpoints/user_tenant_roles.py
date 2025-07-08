"""
Endpoints for managing User Tenant Roles.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db, require_admin
from synapse.models.user import User
from synapse.schemas.user_tenant_role import (
    UserTenantRoleResponse,
    UserTenantRoleCreate,
    UserTenantRoleUpdate,
    UserTenantRoleListResponse
)
from synapse.models import UserTenantRole, User, RBACRole, Tenant

router = APIRouter()

@router.post("/", response_model=UserTenantRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_user_role_to_tenant(
    role_assignment_in: UserTenantRoleCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """Assign a role to a user within a specific tenant (Admin only)."""
    # Ensure the assignment is for the current user's tenant or a tenant the admin manages
    if role_assignment_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign role for another tenant.",
        )

    # Check if user exists
    user_exists = await db.execute(select(User).where(User.id == role_assignment_in.user_id))
    if not user_exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Check if tenant exists
    tenant_exists = await db.execute(select(Tenant).where(Tenant.id == role_assignment_in.tenant_id))
    if not tenant_exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    # Check if role exists
    role_exists = await db.execute(select(RBACRole).where(RBACRole.id == role_assignment_in.role_id))
    if not role_exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    # Check for existing assignment to prevent duplicates
    existing_assignment = await db.execute(
        select(UserTenantRole).where(
            UserTenantRole.user_id == role_assignment_in.user_id,
            UserTenantRole.tenant_id == role_assignment_in.tenant_id,
            UserTenantRole.role_id == role_assignment_in.role_id
        )
    )
    if existing_assignment.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already has this role in this tenant.")

    db_assignment = UserTenantRole(
        **role_assignment_in.model_dump(exclude_unset=True),
        granted_by=current_user.id
    )
    db.add(db_assignment)
    await db.commit()
    await db.refresh(db_assignment)
    return db_assignment


@router.get("/{assignment_id}", response_model=UserTenantRoleResponse)
async def get_user_tenant_role_assignment(
    assignment_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific user-tenant role assignment by its ID."""
    result = await db.execute(
        select(UserTenantRole).where(
            UserTenantRole.id == assignment_id,
            UserTenantRole.tenant_id == current_user.tenant_id # Ensure tenant ownership
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role assignment not found"
        )
    return assignment


@router.get("/", response_model=UserTenantRoleListResponse)
async def list_user_tenant_role_assignments(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    role_id: Optional[uuid.UUID] = Query(None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List all user-tenant role assignments for the current tenant."""
    query = select(UserTenantRole).where(UserTenantRole.tenant_id == current_user.tenant_id)

    if user_id:
        query = query.where(UserTenantRole.user_id == user_id)
    if role_id:
        query = query.where(UserTenantRole.role_id == role_id)
    if is_active is not None:
        query = query.where(UserTenantRole.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(UserTenantRole.granted_at.desc())
    result = await db.execute(query)
    assignments = result.scalars().all()

    return {
        "items": assignments,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.put("/{assignment_id}", response_model=UserTenantRoleResponse)
async def update_user_tenant_role_assignment(
    assignment_id: uuid.UUID,
    assignment_in: UserTenantRoleUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """Update an existing user-tenant role assignment (Admin only)."""
    result = await db.execute(
        select(UserTenantRole).where(
            UserTenantRole.id == assignment_id,
            UserTenantRole.tenant_id == current_user.tenant_id
        )
    )
    db_assignment = result.scalar_one_or_none()

    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role assignment not found"
        )

    update_data = assignment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assignment, field, value)

    await db.commit()
    await db.refresh(db_assignment)
    return db_assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_tenant_role_assignment(
    assignment_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """Delete a user-tenant role assignment (Admin only)."""
    result = await db.execute(
        select(UserTenantRole).where(
            UserTenantRole.id == assignment_id,
            UserTenantRole.tenant_id == current_user.tenant_id
        )
    )
    db_assignment = result.scalar_one_or_none()

    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role assignment not found"
        )

    await db.delete(db_assignment)
    await db.commit()
    return
