"""
Endpoints for managing Analytics Dashboards.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.analytics_dashboard import (
    AnalyticsDashboardResponse,
    AnalyticsDashboardCreate,
    AnalyticsDashboardUpdate,
    AnalyticsDashboardListResponse
)
from synapse.models import AnalyticsDashboard

router = APIRouter()

@router.post("/", response_model=AnalyticsDashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_analytics_dashboard(
    dashboard_in: AnalyticsDashboardCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new analytics dashboard."""
    if dashboard_in.tenant_id and dashboard_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create dashboard for another tenant.",
        )
    if not dashboard_in.tenant_id:
        dashboard_in.tenant_id = current_user.tenant_id

    db_dashboard = AnalyticsDashboard(**dashboard_in.model_dump())
    db.add(db_dashboard)
    await db.commit()
    await db.refresh(db_dashboard)
    return db_dashboard

@router.get("/{dashboard_id}", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    dashboard_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific analytics dashboard by its ID."""
    result = await db.execute(
        select(AnalyticsDashboard).where(AnalyticsDashboard.id == dashboard_id, AnalyticsDashboard.tenant_id == current_user.tenant_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found"
        )
    return dashboard

@router.get("/", response_model=AnalyticsDashboardListResponse)
async def list_analytics_dashboards(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all analytics dashboards for the current tenant."""
    query = select(AnalyticsDashboard).where(AnalyticsDashboard.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                AnalyticsDashboard.name.ilike(search_term),
                AnalyticsDashboard.description.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(AnalyticsDashboard.created_at.desc())
    result = await db.execute(query)
    dashboards = result.scalars().all()

    return {
        "items": dashboards,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{dashboard_id}", response_model=AnalyticsDashboardResponse)
async def update_analytics_dashboard(
    dashboard_id: uuid.UUID,
    dashboard_in: AnalyticsDashboardUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing analytics dashboard."""
    result = await db.execute(
        select(AnalyticsDashboard).where(AnalyticsDashboard.id == dashboard_id, AnalyticsDashboard.tenant_id == current_user.tenant_id)
    )
    db_dashboard = result.scalar_one_or_none()

    if not db_dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found"
        )

    update_data = dashboard_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dashboard, field, value)

    await db.commit()
    await db.refresh(db_dashboard)
    return db_dashboard

@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analytics_dashboard(
    dashboard_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an analytics dashboard."""
    result = await db.execute(
        select(AnalyticsDashboard).where(AnalyticsDashboard.id == dashboard_id, AnalyticsDashboard.tenant_id == current_user.tenant_id)
    )
    db_dashboard = result.scalar_one_or_none()

    if not db_dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found"
        )

    await db.delete(db_dashboard)
    await db.commit()
    return
