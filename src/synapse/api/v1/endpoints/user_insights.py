"""
Endpoints for managing User Insights.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.models.user import User
from synapse.schemas.user_insight import (
    UserInsightResponse,
    UserInsightCreate,
    UserInsightUpdate,
    UserInsightListResponse
)
from synapse.models import UserInsight

router = APIRouter()

@router.post("/", response_model=UserInsightResponse, status_code=status.HTTP_201_CREATED)
async def create_user_insight(
    insight_in: UserInsightCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new user insight."""
    if insight_in.tenant_id and insight_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create insight for another tenant.",
        )
    if not insight_in.tenant_id:
        insight_in.tenant_id = current_user.tenant_id

    db_insight = UserInsight(**insight_in.model_dump())
    db.add(db_insight)
    await db.commit()
    await db.refresh(db_insight)
    return db_insight

@router.get("/{insight_id}", response_model=UserInsightResponse)
async def get_user_insight(
    insight_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific user insight by its ID."""
    result = await db.execute(
        select(UserInsight).where(UserInsight.id == insight_id, UserInsight.tenant_id == current_user.tenant_id)
    )
    insight = result.scalar_one_or_none()

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User insight not found"
        )
    return insight

@router.get("/", response_model=UserInsightListResponse)
async def list_user_insights(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List all user insights for the current tenant."""
    query = select(UserInsight).where(UserInsight.tenant_id == current_user.tenant_id)

    if user_id:
        query = query.where(UserInsight.user_id == user_id)
    if insight_type:
        query = query.where(UserInsight.insight_type == insight_type)
    if category:
        query = query.where(UserInsight.category == category)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(UserInsight.created_at.desc())
    result = await db.execute(query)
    insights = result.scalars().all()

    return {
        "items": insights,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{insight_id}", response_model=UserInsightResponse)
async def update_user_insight(
    insight_id: uuid.UUID,
    insight_in: UserInsightUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing user insight."""
    result = await db.execute(
        select(UserInsight).where(UserInsight.id == insight_id, UserInsight.tenant_id == current_user.tenant_id)
    )
    db_insight = result.scalar_one_or_none()

    if not db_insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User insight not found"
        )

    update_data = insight_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_insight, field, value)

    await db.commit()
    await db.refresh(db_insight)
    return db_insight

@router.delete("/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_insight(
    insight_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a user insight."""
    result = await db.execute(
        select(UserInsight).where(UserInsight.id == insight_id, UserInsight.tenant_id == current_user.tenant_id)
    )
    db_insight = result.scalar_one_or_none()

    if not db_insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User insight not found"
        )

    await db.delete(db_insight)
    await db.commit()
    return
