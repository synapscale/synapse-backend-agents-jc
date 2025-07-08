"""
Endpoints for managing ConversionJourneys.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from synapse.database import get_async_db
from synapse.schemas.conversion_journey import (
    ConversionJourneyCreate,
    ConversionJourneyUpdate,
    ConversionJourneyResponse,
    ConversionJourneyListResponse,
)
from synapse.models import ConversionJourney, User

router = APIRouter()


@router.post("/", response_model=ConversionJourneyResponse, status_code=status.HTTP_201_CREATED)
async def create_conversion_journey(
    item_in: ConversionJourneyCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new conversion journey."""
    create_data = item_in.model_dump()
    if 'tenant_id' not in create_data:
        create_data['tenant_id'] = current_user.tenant_id
    db_item = ConversionJourney(**create_data)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ConversionJourneyResponse)
async def get_conversion_journey(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific conversion journey by its ID."""
    result = await db.execute(
        select(ConversionJourney).where(ConversionJourney.id == item_id, ConversionJourney.tenant_id == current_user.tenant_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="ConversionJourney not found"
        )
    return item


@router.get("/", response_model=ConversionJourneyListResponse)
async def list_conversion_journeys(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
):
    """List all conversion journeys for the current user."""
    query = select(ConversionJourney).where(ConversionJourney.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        # Add search logic here based on model fields
        pass

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return ConversionJourneyListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.put("/{item_id}", response_model=ConversionJourneyResponse)
async def update_conversion_journey(
    item_id: uuid.UUID,
    item_in: ConversionJourneyUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing conversion journey."""
    result = await db.execute(
        select(ConversionJourney).where(ConversionJourney.id == item_id, ConversionJourney.tenant_id == current_user.tenant_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="ConversionJourney not found"
        )

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversion_journey(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a conversion journey."""
    result = await db.execute(
        select(ConversionJourney).where(ConversionJourney.id == item_id, ConversionJourney.tenant_id == current_user.tenant_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="ConversionJourney not found"
        )

    await db.delete(db_item)
    await db.commit()
