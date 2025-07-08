"""
Endpoints for managing User Variables.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.models.user import User
from synapse.models import UserVariable, User
from synapse.schemas.user_variable import (
    UserVariableCreate,
    UserVariableUpdate,
    UserVariableResponse,
    UserVariableListResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Temporary encryption functions (as per existing code comment)
# These should ideally be moved to a dedicated service layer.
def encrypt_value(value: str) -> str:
    """Temporary encryption - implement proper encryption later"""
    return value

def decrypt_value(value: str) -> str:
    """Temporary decryption - implement proper decryption later"""
    return value


@router.post("/", response_model=UserVariableResponse, status_code=status.HTTP_201_CREATED)
async def create_user_variable(
    variable_in: UserVariableCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new user variable."""
    # Ensure the variable belongs to the current user's tenant
    if variable_in.tenant_id and variable_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create variable for another tenant.",
        )
    if not variable_in.tenant_id:
        variable_in.tenant_id = current_user.tenant_id
    
    # Ensure the variable belongs to the current user
    if variable_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create variable for another user.",
        )

    # Check if key already exists for this user
    existing_variable = await db.execute(
        select(UserVariable).where(
            UserVariable.user_id == current_user.id,
            UserVariable.key == variable_in.key,
            UserVariable.is_active == True
        )
    )
    if existing_variable.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Variable with key '{variable_in.key}' already exists for this user."
        )
    
    # Handle encryption if needed
    stored_value = variable_in.value
    if variable_in.is_encrypted:
        stored_value = encrypt_value(variable_in.value)

    db_variable = UserVariable(
        user_id=current_user.id,
        tenant_id=variable_in.tenant_id,
        key=variable_in.key,
        value=stored_value,
        description=variable_in.description,
        category=variable_in.category or "general",
        is_secret=variable_in.is_secret,
        is_encrypted=variable_in.is_encrypted,
        is_active=variable_in.is_active,
    )
    
    db.add(db_variable)
    await db.commit()
    await db.refresh(db_variable)
    
    # Return response with decrypted value for display if not secret
    if db_variable.is_secret:
        db_variable.value = "***HIDDEN***"
    elif db_variable.is_encrypted:
        db_variable.value = decrypt_value(db_variable.value)

    return db_variable


@router.get("/{variable_id}", response_model=UserVariableResponse)
async def get_user_variable(
    variable_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific user variable by its ID."""
    result = await db.execute(
        select(UserVariable).where(
            UserVariable.id == variable_id,
            UserVariable.user_id == current_user.id,
            UserVariable.tenant_id == current_user.tenant_id
        )
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User variable not found"
        )
    
    # Return with decrypted value for display if not secret
    if variable.is_secret:
        variable.value = "***HIDDEN***"
    elif variable.is_encrypted:
        variable.value = decrypt_value(variable.value)

    return variable


@router.get("/", response_model=UserVariableListResponse)
async def list_user_variables(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in key or description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List all user variables for the current user and tenant."""
    query = select(UserVariable).where(
        UserVariable.user_id == current_user.id,
        UserVariable.tenant_id == current_user.tenant_id
    )

    if category:
        query = query.where(UserVariable.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                UserVariable.key.ilike(search_term),
                UserVariable.description.ilike(search_term)
            )
        )
    
    if is_active is not None:
        query = query.where(UserVariable.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(UserVariable.created_at.desc())
    result = await db.execute(query)
    variables = result.scalars().all()

    # Apply decryption/masking for response
    for var in variables:
        if var.is_secret:
            var.value = "***HIDDEN***"
        elif var.is_encrypted:
            var.value = decrypt_value(var.value)

    return {
        "items": variables,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.put("/{variable_id}", response_model=UserVariableResponse)
async def update_user_variable(
    variable_id: uuid.UUID,
    variable_in: UserVariableUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing user variable."""
    result = await db.execute(
        select(UserVariable).where(
            UserVariable.id == variable_id,
            UserVariable.user_id == current_user.id,
            UserVariable.tenant_id == current_user.tenant_id
        )
    )
    db_variable = result.scalar_one_or_none()

    if not db_variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User variable not found"
        )

    update_data = variable_in.model_dump(exclude_unset=True)
    
    # Handle value and encryption separately
    if "value" in update_data:
        new_value = update_data.pop("value")
        if db_variable.is_encrypted or variable_in.is_encrypted:
            db_variable.value = encrypt_value(new_value)
            db_variable.is_encrypted = True
        else:
            db_variable.value = new_value
            db_variable.is_encrypted = False
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_variable, field, value)

    await db.commit()
    await db.refresh(db_variable)
    
    # Return response with decrypted value for display if not secret
    if db_variable.is_secret:
        db_variable.value = "***HIDDEN***"
    elif db_variable.is_encrypted:
        db_variable.value = decrypt_value(db_variable.value)

    return db_variable


@router.delete("/{variable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_variable(
    variable_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a user variable (soft delete)."""
    result = await db.execute(
        select(UserVariable).where(
            UserVariable.id == variable_id,
            UserVariable.user_id == current_user.id,
            UserVariable.tenant_id == current_user.tenant_id
        )
    )
    db_variable = result.scalar_one_or_none()

    if not db_variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User variable not found"
        )

    # Soft delete
    db_variable.is_active = False
    await db.commit()
    return


@router.get("/key/{key}", response_model=UserVariableResponse)
async def get_user_variable_by_key(
    key: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific user variable by its key."""
    result = await db.execute(
        select(UserVariable).where(
            UserVariable.key == key,
            UserVariable.user_id == current_user.id,
            UserVariable.tenant_id == current_user.tenant_id
        )
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User variable not found"
        )
    
    # Return with decrypted value for display if not secret
    if variable.is_secret:
        variable.value = "***HIDDEN***"
    elif variable.is_encrypted:
        variable.value = decrypt_value(variable.value)

    return variable
