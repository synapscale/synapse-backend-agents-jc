"""
Endpoints for managing Contact Sources (CRM).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.contact_source import (
    ContactSourceResponse,
    ContactSourceCreate,
    ContactSourceUpdate,
    ContactSourceListResponse
)
from synapse.models import ContactSource

router = APIRouter()

@router.post("/", response_model=ContactSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_source(
    contact_source_in: ContactSourceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact source."""
    if contact_source_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contact source for another tenant.",
        )

    db_contact_source = ContactSource(**contact_source_in.model_dump())
    db.add(db_contact_source)
    await db.commit()
    await db.refresh(db_contact_source)
    return db_contact_source

@router.get("/{contact_source_id}", response_model=ContactSourceResponse)
async def get_contact_source(
    contact_source_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact source by its ID."""
    result = await db.execute(
        select(ContactSource).where(ContactSource.id == contact_source_id, ContactSource.tenant_id == current_user.tenant_id)
    )
    contact_source = result.scalar_one_or_none()

    if not contact_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact source not found"
        )
    return contact_source

@router.get("/", response_model=ContactSourceListResponse)
async def list_contact_sources(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all contact sources for the current tenant."""
    query = select(ContactSource).where(ContactSource.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                ContactSource.name.ilike(search_term),
                ContactSource.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(ContactSource.created_at.desc())
    result = await db.execute(query)
    contact_sources = result.scalars().all()

    return {
        "items": contact_sources,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{contact_source_id}", response_model=ContactSourceResponse)
async def update_contact_source(
    contact_source_id: uuid.UUID,
    contact_source_in: ContactSourceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact source."""
    result = await db.execute(
        select(ContactSource).where(ContactSource.id == contact_source_id, ContactSource.tenant_id == current_user.tenant_id)
    )
    db_contact_source = result.scalar_one_or_none()

    if not db_contact_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact source not found"
        )

    update_data = contact_source_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact_source, field, value)

    await db.commit()
    await db.refresh(db_contact_source)
    return db_contact_source

@router.delete("/{contact_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_source(
    contact_source_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact source."""
    result = await db.execute(
        select(ContactSource).where(ContactSource.id == contact_source_id, ContactSource.tenant_id == current_user.tenant_id)
    )
    db_contact_source = result.scalar_one_or_none()

    if not db_contact_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact source not found"
        )

    await db.delete(db_contact_source)
    await db.commit()
    return
