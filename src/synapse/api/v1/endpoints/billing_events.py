"""
Endpoints for managing Billing Events.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.schemas.billing_event import (
    BillingEventResponse,
    BillingEventCreate,
    BillingEventUpdate,
    BillingEventListResponse
)
from synapse.models import BillingEvent

router = APIRouter()

@router.post("/", response_model=BillingEventResponse, status_code=status.HTTP_201_CREATED)
async def create_billing_event(
    event_in: BillingEventCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new billing event."""
    if event_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create billing event for another tenant.",
        )

    db_event = BillingEvent(**event_in.model_dump())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

@router.get("/{event_id}", response_model=BillingEventResponse)
async def get_billing_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific billing event by its ID."""
    result = await db.execute(
        select(BillingEvent).where(BillingEvent.id == event_id, BillingEvent.tenant_id == current_user.tenant_id)
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Billing event not found"
        )
    return event

@router.get("/", response_model=BillingEventListResponse)
async def list_billing_events(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for event type or description"),
):
    """List all billing events for the current tenant."""
    query = select(BillingEvent).where(BillingEvent.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                BillingEvent.event_type.ilike(search_term),
                BillingEvent.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(BillingEvent.created_at.desc())
    result = await db.execute(query)
    events = result.scalars().all()

    return {
        "items": events,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{event_id}", response_model=BillingEventResponse)
async def update_billing_event(
    event_id: uuid.UUID,
    event_in: BillingEventUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing billing event."""
    result = await db.execute(
        select(BillingEvent).where(BillingEvent.id == event_id, BillingEvent.tenant_id == current_user.tenant_id)
    )
    db_event = result.scalar_one_or_none()

    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Billing event not found"
        )

    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)

    await db.commit()
    await db.refresh(db_event)
    return db_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_billing_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a billing event."""
    result = await db.execute(
        select(BillingEvent).where(BillingEvent.id == event_id, BillingEvent.tenant_id == current_user.tenant_id)
    )
    db_event = result.scalar_one_or_none()

    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Billing event not found"
        )

    await db.delete(db_event)
    await db.commit()
    return
