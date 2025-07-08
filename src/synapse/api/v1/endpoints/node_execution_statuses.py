"""
Endpoints for managing Node Execution Statuses.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.models.user import User
from synapse.schemas.node_execution_status import (
    NodeExecutionStatusResponse,
    NodeExecutionStatusCreate,
    NodeExecutionStatusUpdate,
    NodeExecutionStatusList
)
from synapse.models import NodeExecutionStatus

router = APIRouter()

@router.post("/", response_model=NodeExecutionStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_node_execution_status(
    status_in: NodeExecutionStatusCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node execution status."""
    # NodeExecutionStatus are global, no tenant_id check needed
    db_status = NodeExecutionStatus(**status_in.model_dump())
    db.add(db_status)
    await db.commit()
    await db.refresh(db_status)
    return db_status

@router.get("/{status_id}", response_model=NodeExecutionStatusResponse)
async def get_node_execution_status(
    status_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node execution status by its ID."""
    result = await db.execute(
        select(NodeExecutionStatus).where(NodeExecutionStatus.id == status_id)
    )
    status_obj = result.scalar_one_or_none()

    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node execution status not found"
        )
    return status_obj

@router.get("/", response_model=NodeExecutionStatusList)
async def list_node_execution_statuses(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all node execution statuses."""
    query = select(NodeExecutionStatus)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                NodeExecutionStatus.name.ilike(search_term),
                NodeExecutionStatus.display_name.ilike(search_term),
                NodeExecutionStatus.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeExecutionStatus.created_at.desc())
    result = await db.execute(query)
    statuses = result.scalars().all()

    return NodeExecutionStatusList(
        items=statuses,
        total=total,
        page=page,
        size=size
    )

@router.put("/{status_id}", response_model=NodeExecutionStatusResponse)
async def update_node_execution_status(
    status_id: uuid.UUID,
    status_in: NodeExecutionStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node execution status."""
    result = await db.execute(
        select(NodeExecutionStatus).where(NodeExecutionStatus.id == status_id)
    )
    db_status = result.scalar_one_or_none()

    if not db_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node execution status not found"
        )

    update_data = status_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_status, field, value)

    await db.commit()
    await db.refresh(db_status)
    return db_status

@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_execution_status(
    status_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node execution status."""
    result = await db.execute(
        select(NodeExecutionStatus).where(NodeExecutionStatus.id == status_id)
    )
    db_status = result.scalar_one_or_none()

    if not db_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node execution status not found"
        )

    await db.delete(db_status)
    await db.commit()
    return
