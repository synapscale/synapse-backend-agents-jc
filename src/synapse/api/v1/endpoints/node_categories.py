"""
Endpoints for managing Node Categories.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.schemas.node_category import (
    NodeCategoryResponse,
    NodeCategoryCreate,
    NodeCategoryUpdate,
    NodeCategoryListResponse
)
from synapse.models import NodeCategory

router = APIRouter()

@router.post("/", response_model=NodeCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_node_category(
    category_in: NodeCategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node category."""
    if category_in.tenant_id and category_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create category for another tenant.",
        )
    if not category_in.tenant_id:
        category_in.tenant_id = current_user.tenant_id

    db_category = NodeCategory(**category_in.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.get("/{category_id}", response_model=NodeCategoryResponse)
async def get_node_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node category by its ID."""
    result = await db.execute(
        select(NodeCategory).where(NodeCategory.id == category_id, NodeCategory.tenant_id == current_user.tenant_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node category not found"
        )
    return category

@router.get("/", response_model=NodeCategoryListResponse)
async def list_node_categories(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all node categories for the current tenant."""
    query = select(NodeCategory).where(NodeCategory.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                NodeCategory.name.ilike(search_term),
                NodeCategory.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeCategory.created_at.desc())
    result = await db.execute(query)
    categories = result.scalars().all()

    return {
        "items": categories,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{category_id}", response_model=NodeCategoryResponse)
async def update_node_category(
    category_id: uuid.UUID,
    category_in: NodeCategoryUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node category."""
    result = await db.execute(
        select(NodeCategory).where(NodeCategory.id == category_id, NodeCategory.tenant_id == current_user.tenant_id)
    )
    db_category = result.scalar_one_or_none()

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node category not found"
        )

    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node category."""
    result = await db.execute(
        select(NodeCategory).where(NodeCategory.id == category_id, NodeCategory.tenant_id == current_user.tenant_id)
    )
    db_category = result.scalar_one_or_none()

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node category not found"
        )

    await db.delete(db_category)
    await db.commit()
    return
