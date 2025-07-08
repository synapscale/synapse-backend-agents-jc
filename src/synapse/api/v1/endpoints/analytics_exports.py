"""
Endpoints for managing Analytics Exports.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.schemas.analytics_export import (
    AnalyticsExportResponse,
    AnalyticsExportCreate,
    AnalyticsExportUpdate,
    AnalyticsExportListResponse
)
from synapse.models import AnalyticsExport

router = APIRouter()

@router.post("/", response_model=AnalyticsExportResponse, status_code=status.HTTP_201_CREATED)
async def create_analytics_export(
    export_in: AnalyticsExportCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new analytics export."""
    if export_in.tenant_id and export_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create export for another tenant.",
        )
    if not export_in.tenant_id:
        export_in.tenant_id = current_user.tenant_id

    db_export = AnalyticsExport(**export_in.model_dump())
    db.add(db_export)
    await db.commit()
    await db.refresh(db_export)
    return db_export

@router.get("/{export_id}", response_model=AnalyticsExportResponse)
async def get_analytics_export(
    export_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific analytics export by its ID."""
    result = await db.execute(
        select(AnalyticsExport).where(AnalyticsExport.id == export_id, AnalyticsExport.tenant_id == current_user.tenant_id)
    )
    export = result.scalar_one_or_none()

    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export not found"
        )
    return export

@router.get("/", response_model=AnalyticsExportListResponse)
async def list_analytics_exports(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
):
    """List all analytics exports for the current tenant."""
    query = select(AnalyticsExport).where(AnalyticsExport.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                AnalyticsExport.name.ilike(search_term),
                AnalyticsExport.export_type.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(AnalyticsExport.created_at.desc())
    result = await db.execute(query)
    exports = result.scalars().all()

    return {
        "items": exports,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{export_id}", response_model=AnalyticsExportResponse)
async def update_analytics_export(
    export_id: uuid.UUID,
    export_in: AnalyticsExportUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing analytics export."""
    result = await db.execute(
        select(AnalyticsExport).where(AnalyticsExport.id == export_id, AnalyticsExport.tenant_id == current_user.tenant_id)
    )
    db_export = result.scalar_one_or_none()

    if not db_export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export not found"
        )

    update_data = export_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_export, field, value)

    await db.commit()
    await db.refresh(db_export)
    return db_export

@router.delete("/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analytics_export(
    export_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an analytics export."""
    result = await db.execute(
        select(AnalyticsExport).where(AnalyticsExport.id == export_id, AnalyticsExport.tenant_id == current_user.tenant_id)
    )
    db_export = result.scalar_one_or_none()

    if not db_export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export not found"
        )

    await db.delete(db_export)
    await db.commit()
    return
