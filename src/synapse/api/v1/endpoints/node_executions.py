"""
Endpoints for managing Node Executions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.models.user import User
from synapse.schemas.node_execution import (
    NodeExecutionResponse,
    NodeExecutionCreate,
    NodeExecutionUpdate,
    NodeExecutionList
)
from synapse.models import NodeExecution

router = APIRouter()

@router.post("/", response_model=NodeExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_node_execution(
    execution_in: NodeExecutionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node execution record."""
    # NodeExecution is typically created by the system, but for API, we allow it
    # Ensure tenant_id is set if not provided
    if not execution_in.tenant_id:
        execution_in.tenant_id = current_user.tenant_id

    db_execution = NodeExecution(**execution_in.model_dump())
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)
    return db_execution

@router.get("/{execution_id}", response_model=NodeExecutionResponse)
async def get_node_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node execution record by its ID."""
    result = await db.execute(
        select(NodeExecution).where(NodeExecution.id == execution_id, NodeExecution.tenant_id == current_user.tenant_id)
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node execution not found"
        )
    return execution

@router.get("/", response_model=NodeExecutionList)
async def list_node_executions(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    node_id: Optional[uuid.UUID] = Query(None, description="Filter by node ID"),
    workflow_execution_id: Optional[uuid.UUID] = Query(None, description="Filter by workflow execution ID"),
    status_name: Optional[str] = Query(None, description="Filter by execution status name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List all node execution records for the current tenant."""
    query = select(NodeExecution).where(NodeExecution.tenant_id == current_user.tenant_id)

    if node_id:
        query = query.where(NodeExecution.node_id == node_id)
    if workflow_execution_id:
        query = query.where(NodeExecution.workflow_execution_id == workflow_execution_id)
    if status_name:
        query = query.where(NodeExecution.status == status_name)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeExecution.created_at.desc())
    result = await db.execute(query)
    executions = result.scalars().all()

    return {
        "items": executions,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{execution_id}", response_model=NodeExecutionResponse)
async def update_node_execution(
    execution_id: uuid.UUID,
    execution_in: NodeExecutionUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node execution record."""
    result = await db.execute(
        select(NodeExecution).where(NodeExecution.id == execution_id, NodeExecution.tenant_id == current_user.tenant_id)
    )
    db_execution = result.scalar_one_or_none()

    if not db_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node execution not found"
        )

    update_data = execution_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_execution, field, value)

    await db.commit()
    await db.refresh(db_execution)
    return db_execution

@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node execution record."""
    result = await db.execute(
        select(NodeExecution).where(NodeExecution.id == execution_id, NodeExecution.tenant_id == current_user.tenant_id)
    )
    db_execution = result.scalar_one_or_none()

    if not db_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node execution not found"
        )

    await db.delete(db_execution)
    await db.commit()
    return
