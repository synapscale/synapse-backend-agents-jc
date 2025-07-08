"""
Endpoints for managing Node Types.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.models.user import User
from synapse.schemas.node_type import (
    NodeTypeResponse,
    NodeTypeCreate,
    NodeTypeUpdate,
    NodeTypeListResponse
)
from synapse.models import NodeType

router = APIRouter()

@router.post("/", response_model=NodeTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_node_type(
    type_in: NodeTypeCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node type."""
    # NodeTypes are typically global, no tenant_id check needed
    db_type = NodeType(**type_in.model_dump())
    db.add(db_type)
    await db.commit()
    await db.refresh(db_type)
    return db_type

@router.get("/{type_id}", response_model=NodeTypeResponse)
async def get_node_type(
    type_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node type by its ID."""
    result = await db.execute(
        select(NodeType).where(NodeType.id == type_id)
    )
    type_obj = result.scalar_one_or_none()

    if not type_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node type not found"
        )
    return type_obj

@router.get("/", response_model=NodeTypeListResponse)
async def list_node_types(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all node types."""
    query = select(NodeType)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                NodeType.name.ilike(search_term),
                NodeType.display_name.ilike(search_term),
                NodeType.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeType.created_at.desc())
    result = await db.execute(query)
    types = result.scalars().all()

    return {
        "items": types,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{type_id}", response_model=NodeTypeResponse)
async def update_node_type(
    type_id: uuid.UUID,
    type_in: NodeTypeUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node type."""
    result = await db.execute(
        select(NodeType).where(NodeType.id == type_id)
    )
    db_type = result.scalar_one_or_one()

    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node type not found"
        )

    update_data = type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_type, field, value)

    await db.commit()
    await db.refresh(db_type)
    return db_type

@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_type(
    type_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node type."""
    result = await db.execute(
        select(NodeType).where(NodeType.id == type_id)
    )
    db_type = result.scalar_one_or_none()

    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node type not found"
        )

    await db.delete(db_type)
    await db.commit()
    return
