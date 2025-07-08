"""
Endpoints for managing Analytics Alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.analytics_alert import (
    AnalyticsAlertResponse,
    AnalyticsAlertCreate,
    AnalyticsAlertUpdate,
    AnalyticsAlertListResponse
)
from synapse.models import AnalyticsAlert

router = APIRouter()

@router.post("/", response_model=AnalyticsAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_analytics_alert(
    alert_in: AnalyticsAlertCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new analytics alert."""
    if alert_in.tenant_id and alert_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create alert for another tenant.",
        )
    if not alert_in.tenant_id:
        alert_in.tenant_id = current_user.tenant_id

    db_alert = AnalyticsAlert(**alert_in.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert

@router.get("/{alert_id}", response_model=AnalyticsAlertResponse)
async def get_analytics_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific analytics alert by its ID."""
    result = await db.execute(
        select(AnalyticsAlert).where(AnalyticsAlert.id == alert_id, AnalyticsAlert.tenant_id == current_user.tenant_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )
    return alert

@router.get("/", response_model=AnalyticsAlertListResponse)
async def list_analytics_alerts(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all analytics alerts for the current tenant."""
    query = select(AnalyticsAlert).where(AnalyticsAlert.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                AnalyticsAlert.name.ilike(search_term),
                AnalyticsAlert.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(AnalyticsAlert.created_at.desc())
    result = await db.execute(query)
    alerts = result.scalars().all()

    return {
        "items": alerts,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{alert_id}", response_model=AnalyticsAlertResponse)
async def update_analytics_alert(
    alert_id: uuid.UUID,
    alert_in: AnalyticsAlertUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing analytics alert."""
    result = await db.execute(
        select(AnalyticsAlert).where(AnalyticsAlert.id == alert_id, AnalyticsAlert.tenant_id == current_user.tenant_id)
    )
    db_alert = result.scalar_one_or_none()

    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )

    update_data = alert_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)

    await db.commit()
    await db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analytics_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an analytics alert."""
    result = await db.execute(
        select(AnalyticsAlert).where(AnalyticsAlert.id == alert_id, AnalyticsAlert.tenant_id == current_user.tenant_id)
    )
    db_alert = result.scalar_one_or_none()

    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )

    await db.delete(db_alert)
    await db.commit()
    return
