"""
Endpoints for managing Campaigns (CRM).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.campaign import (
    CampaignResponse,
    CampaignCreate,
    CampaignUpdate,
    CampaignList
)
from synapse.models import Campaign

router = APIRouter()

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_in: CampaignCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new campaign."""
    if campaign_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create campaign for another tenant.",
        )

    db_campaign = Campaign(**campaign_in.model_dump())
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific campaign by its ID."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == current_user.tenant_id)
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )
    return campaign

@router.get("/", response_model=CampaignList)
async def list_campaigns(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all campaigns for the current tenant."""
    query = select(Campaign).where(Campaign.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Campaign.name.ilike(search_term),
                Campaign.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Campaign.created_at.desc())
    result = await db.execute(query)
    campaigns = result.scalars().all()

    return {
        "items": campaigns,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    campaign_in: CampaignUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == current_user.tenant_id)
    )
    db_campaign = result.scalar_one_or_none()

    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    update_data = campaign_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)

    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == current_user.tenant_id)
    )
    db_campaign = result.scalar_one_or_none()

    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    await db.delete(db_campaign)
    await db.commit()
    return
