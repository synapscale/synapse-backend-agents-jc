"""
Endpoints for managing Contacts (CRM).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.contact import (
    ContactResponse, 
    ContactCreate, 
    ContactUpdate, 
    ContactListResponse
)
from synapse.models import Contact

router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact."""
    # Ensure the contact belongs to the current user's tenant
    if contact_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contact for another tenant.",
        )

    db_contact = Contact(**contact_in.model_dump())
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact by its ID."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.tenant_id == current_user.tenant_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.get("/", response_model=ContactListResponse)
async def list_contacts(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name, email, or company"),
):
    """List all contacts for the current tenant."""
    query = select(Contact).where(Contact.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Contact.first_name.ilike(search_term),
                Contact.last_name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.company.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Contact.created_at.desc())
    result = await db.execute(query)
    contacts = result.scalars().all()

    return {
        "items": contacts,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: uuid.UUID,
    contact_in: ContactUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.tenant_id == current_user.tenant_id)
    )
    db_contact = result.scalar_one_or_none()

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    update_data = contact_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact, field, value)

    await db.commit()
    await db.refresh(db_contact)
    return db_contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.tenant_id == current_user.tenant_id)
    )
    db_contact = result.scalar_one_or_none()

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    await db.delete(db_contact)
    await db.commit()
    return
