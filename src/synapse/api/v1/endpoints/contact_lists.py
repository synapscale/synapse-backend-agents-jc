"""
Endpoints for managing Contact Lists (CRM).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.contact_list import (
    ContactListResponse,
    ContactListCreate,
    ContactListUpdate,
    ContactListListResponse
)
from synapse.models import ContactList

router = APIRouter()

@router.post("/", response_model=ContactListResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_list(
    contact_list_in: ContactListCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact list."""
    if contact_list_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contact list for another tenant.",
        )

    db_contact_list = ContactList(**contact_list_in.model_dump())
    db.add(db_contact_list)
    await db.commit()
    await db.refresh(db_contact_list)
    return db_contact_list

@router.get("/{contact_list_id}", response_model=ContactListResponse)
async def get_contact_list(
    contact_list_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact list by its ID."""
    result = await db.execute(
        select(ContactList).where(ContactList.id == contact_list_id, ContactList.tenant_id == current_user.tenant_id)
    )
    contact_list = result.scalar_one_or_none()

    if not contact_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found"
        )
    return contact_list

@router.get("/", response_model=ContactListListResponse)
async def list_contact_lists(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all contact lists for the current tenant."""
    query = select(ContactList).where(ContactList.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                ContactList.name.ilike(search_term),
                ContactList.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(ContactList.created_at.desc())
    result = await db.execute(query)
    contact_lists = result.scalars().all()

    return {
        "items": contact_lists,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{contact_list_id}", response_model=ContactListResponse)
async def update_contact_list(
    contact_list_id: uuid.UUID,
    contact_list_in: ContactListUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact list."""
    result = await db.execute(
        select(ContactList).where(ContactList.id == contact_list_id, ContactList.tenant_id == current_user.tenant_id)
    )
    db_contact_list = result.scalar_one_or_none()

    if not db_contact_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found"
        )

    update_data = contact_list_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact_list, field, value)

    await db.commit()
    await db.refresh(db_contact_list)
    return db_contact_list

@router.delete("/{contact_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_list(
    contact_list_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact list."""
    result = await db.execute(
        select(ContactList).where(ContactList.id == contact_list_id, ContactList.tenant_id == current_user.tenant_id)
    )
    db_contact_list = result.scalar_one_or_none()

    if not db_contact_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found"
        )

    await db.delete(db_contact_list)
    await db.commit()
    return
