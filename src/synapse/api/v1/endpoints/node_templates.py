"""
Endpoints for managing Node Templates.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.schemas.node_template import (
    NodeTemplateResponse,
    NodeTemplateCreate,
    NodeTemplateUpdate,
    NodeTemplateListResponse
)
from synapse.models import NodeTemplate

router = APIRouter()

@router.post("/", response_model=NodeTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_node_template(
    template_in: NodeTemplateCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node template."""
    if template_in.tenant_id and template_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create template for another tenant.",
        )
    if not template_in.tenant_id:
        template_in.tenant_id = current_user.tenant_id

    db_template = NodeTemplate(**template_in.model_dump())
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get("/{template_id}", response_model=NodeTemplateResponse)
async def get_node_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node template by its ID."""
    result = await db.execute(
        select(NodeTemplate).where(NodeTemplate.id == template_id, NodeTemplate.tenant_id == current_user.tenant_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node template not found"
        )
    return template

@router.get("/", response_model=NodeTemplateListResponse)
async def list_node_templates(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all node templates for the current tenant."""
    query = select(NodeTemplate).where(NodeTemplate.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                NodeTemplate.name.ilike(search_term),
                NodeTemplate.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeTemplate.created_at.desc())
    result = await db.execute(query)
    templates = result.scalars().all()

    return {
        "items": templates,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{template_id}", response_model=NodeTemplateResponse)
async def update_node_template(
    template_id: uuid.UUID,
    template_in: NodeTemplateUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node template."""
    result = await db.execute(
        select(NodeTemplate).where(NodeTemplate.id == template_id, NodeTemplate.tenant_id == current_user.tenant_id)
    )
    db_template = result.scalar_one_or_none()

    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node template not found"
        )

    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)

    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node template."""
    result = await db.execute(
        select(NodeTemplate).where(NodeTemplate.id == template_id, NodeTemplate.tenant_id == current_user.tenant_id)
    )
    db_template = result.scalar_one_or_none()

    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node template not found"
        )

    await db.delete(db_template)
    await db.commit()
    return
