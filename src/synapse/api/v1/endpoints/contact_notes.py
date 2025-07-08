"""
Endpoints for managing Contact Notes (CRM).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.contact_note import (
    ContactNoteResponse,
    ContactNoteCreate,
    ContactNoteUpdate,
    ContactNoteListResponse
)
from synapse.models import ContactNote

router = APIRouter()

@router.post("/", response_model=ContactNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_note(
    contact_note_in: ContactNoteCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact note."""
    if contact_note_in.tenant_id and contact_note_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contact note for another tenant.",
        )
    if not contact_note_in.tenant_id:
        contact_note_in.tenant_id = current_user.tenant_id

    db_contact_note = ContactNote(**contact_note_in.model_dump())
    db.add(db_contact_note)
    await db.commit()
    await db.refresh(db_contact_note)
    return db_contact_note

@router.get("/{contact_note_id}", response_model=ContactNoteResponse)
async def get_contact_note(
    contact_note_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact note by its ID."""
    result = await db.execute(
        select(ContactNote).where(ContactNote.id == contact_note_id, ContactNote.tenant_id == current_user.tenant_id)
    )
    contact_note = result.scalar_one_or_none()

    if not contact_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact note not found"
        )
    return contact_note

@router.get("/", response_model=ContactNoteListResponse)
async def list_contact_notes(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    contact_id: Optional[uuid.UUID] = Query(None, description="Filter by contact ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List all contact notes for the current tenant."""
    query = select(ContactNote).where(ContactNote.tenant_id == current_user.tenant_id)

    if contact_id:
        query = query.where(ContactNote.contact_id == contact_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(ContactNote.created_at.desc())
    result = await db.execute(query)
    contact_notes = result.scalars().all()

    return {
        "items": contact_notes,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{contact_note_id}", response_model=ContactNoteResponse)
async def update_contact_note(
    contact_note_id: uuid.UUID,
    contact_note_in: ContactNoteUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact note."""
    result = await db.execute(
        select(ContactNote).where(ContactNote.id == contact_note_id, ContactNote.tenant_id == current_user.tenant_id)
    )
    db_contact_note = result.scalar_one_or_none()

    if not db_contact_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact note not found"
        )

    update_data = contact_note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact_note, field, value)

    await db.commit()
    await db.refresh(db_contact_note)
    return db_contact_note

@router.delete("/{contact_note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_note(
    contact_note_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact note."""
    result = await db.execute(
        select(ContactNote).where(ContactNote.id == contact_note_id, ContactNote.tenant_id == current_user.tenant_id)
    )
    db_contact_note = result.scalar_one_or_none()

    if not db_contact_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact note not found"
        )

    await db.delete(db_contact_note)
    await db.commit()
    return
