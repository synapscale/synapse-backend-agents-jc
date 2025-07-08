"""
Endpoints for managing Node Statuses.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.models.user import User
from synapse.schemas.node_status import (
    NodeStatusResponse,
    NodeStatusCreate,
    NodeStatusUpdate,
    NodeStatusListResponse
)
from synapse.models import NodeStatus

router = APIRouter()

@router.post("/", response_model=NodeStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_node_status(
    status_in: NodeStatusCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node status."""
    # NodeStatus are typically global, no tenant_id check needed
    db_status = NodeStatus(**status_in.model_dump())
    db.add(db_status)
    await db.commit()
    await db.refresh(db_status)
    return db_status

@router.get("/{status_id}", response_model=NodeStatusResponse)
async def get_node_status(
    status_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node status by its ID."""
    result = await db.execute(
        select(NodeStatus).where(NodeStatus.id == status_id)
    )
    status_obj = result.scalar_one_or_none()

    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node status not found"
        )
    return status_obj

@router.get("/", response_model=NodeStatusListResponse)
async def list_node_statuses(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all node statuses."""
    query = select(NodeStatus)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                NodeStatus.name.ilike(search_term),
                NodeStatus.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeStatus.created_at.desc())
    result = await db.execute(query)
    statuses = result.scalars().all()

    return {
        "items": statuses,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{status_id}", response_model=NodeStatusResponse)
async def update_node_status(
    status_id: uuid.UUID,
    status_in: NodeStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node status."""
    result = await db.execute(
        select(NodeStatus).where(NodeStatus.id == status_id)
    )
    db_status = result.scalar_one_or_none()

    if not db_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node status not found"
        )

    update_data = status_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_status, field, value)

    await db.commit()
    await db.refresh(db_status)
    return db_status

@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_status(
    status_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node status."""
    result = await db.execute(
        select(NodeStatus).where(NodeStatus.id == status_id)
    )
    db_status = result.scalar_one_or_none()

    if not db_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node status not found"
        )

    await db.delete(db_status)
    await db.commit()
    return
