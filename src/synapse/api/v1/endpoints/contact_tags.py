"""
Endpoints for managing Contact Tags (CRM).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.contact_tag import (
    ContactTagResponse,
    ContactTagCreate,
    ContactTagUpdate,
    ContactTagListResponse
)
from synapse.models import ContactTag

router = APIRouter()

@router.post("/", response_model=ContactTagResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_tag(
    contact_tag_in: ContactTagCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact tag."""
    if contact_tag_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contact tag for another tenant.",
        )

    db_contact_tag = ContactTag(**contact_tag_in.model_dump())
    db.add(db_contact_tag)
    await db.commit()
    await db.refresh(db_contact_tag)
    return db_contact_tag

@router.get("/{contact_tag_id}", response_model=ContactTagResponse)
async def get_contact_tag(
    contact_tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact tag by its ID."""
    result = await db.execute(
        select(ContactTag).where(ContactTag.id == contact_tag_id, ContactTag.tenant_id == current_user.tenant_id)
    )
    contact_tag = result.scalar_one_or_none()

    if not contact_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact tag not found"
        )
    return contact_tag

@router.get("/", response_model=ContactTagListResponse)
async def list_contact_tags(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all contact tags for the current tenant."""
    query = select(ContactTag).where(ContactTag.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                ContactTag.name.ilike(search_term),
                ContactTag.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(ContactTag.created_at.desc())
    result = await db.execute(query)
    contact_tags = result.scalars().all()

    return {
        "items": contact_tags,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{contact_tag_id}", response_model=ContactTagResponse)
async def update_contact_tag(
    contact_tag_id: uuid.UUID,
    contact_tag_in: ContactTagUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact tag."""
    result = await db.execute(
        select(ContactTag).where(ContactTag.id == contact_tag_id, ContactTag.tenant_id == current_user.tenant_id)
    )
    db_contact_tag = result.scalar_one_or_none()

    if not db_contact_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact tag not found"
        )

    update_data = contact_tag_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact_tag, field, value)

    await db.commit()
    await db.refresh(db_contact_tag)
    return db_contact_tag

@router.delete("/{contact_tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_tag(
    contact_tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact tag."""
    result = await db.execute(
        select(ContactTag).where(ContactTag.id == contact_tag_id, ContactTag.tenant_id == current_user.tenant_id)
    )
    db_contact_tag = result.scalar_one_or_none()

    if not db_contact_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact tag not found"
        )

    await db.delete(db_contact_tag)
    await db.commit()
    return
