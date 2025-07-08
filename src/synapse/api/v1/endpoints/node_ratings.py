"""
Endpoints for managing Node Ratings.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.schemas.node_rating import (
    NodeRatingResponse,
    NodeRatingCreate,
    NodeRatingUpdate,
    NodeRatingListResponse,
    NodeRatingSummary,
    NodeRatingTrend
)
from synapse.models import NodeRating

router = APIRouter()

@router.post("/", response_model=NodeRatingResponse, status_code=status.HTTP_201_CREATED)
async def create_node_rating(
    rating_in: NodeRatingCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new node rating."""
    # Ensure the rating belongs to the current user's tenant if tenant_id is provided
    if rating_in.tenant_id and rating_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create rating for another tenant.",
        )
    # If tenant_id is not provided, assign current user's tenant_id
    if not rating_in.tenant_id:
        rating_in.tenant_id = current_user.tenant_id

    # Check if user already rated this node
    existing_rating = await db.execute(
        select(NodeRating).where(
            NodeRating.node_id == rating_in.node_id,
            NodeRating.user_id == rating_in.user_id,
            NodeRating.tenant_id == rating_in.tenant_id
        )
    )
    existing_rating = existing_rating.scalar_one_or_none()

    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User has already rated this node. Use PUT to update."
        )

    db_rating = NodeRating(**rating_in.model_dump())
    db.add(db_rating)
    await db.commit()
    await db.refresh(db_rating)
    return db_rating

@router.get("/{rating_id}", response_model=NodeRatingResponse)
async def get_node_rating(
    rating_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific node rating by its ID."""
    result = await db.execute(
        select(NodeRating).where(NodeRating.id == rating_id, NodeRating.tenant_id == current_user.tenant_id)
    )
    rating = result.scalar_one_or_none()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node rating not found"
        )
    return rating

@router.get("/", response_model=NodeRatingListResponse)
async def list_node_ratings(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    node_id: Optional[uuid.UUID] = Query(None, description="Filter by node ID"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List all node ratings for the current tenant."""
    query = select(NodeRating).where(NodeRating.tenant_id == current_user.tenant_id)

    if node_id:
        query = query.where(NodeRating.node_id == node_id)
    if user_id:
        query = query.where(NodeRating.user_id == user_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(NodeRating.created_at.desc())
    result = await db.execute(query)
    ratings = result.scalars().all()

    return {
        "items": ratings,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{rating_id}", response_model=NodeRatingResponse)
async def update_node_rating(
    rating_id: uuid.UUID,
    rating_in: NodeRatingUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing node rating."""
    result = await db.execute(
        select(NodeRating).where(NodeRating.id == rating_id, NodeRating.tenant_id == current_user.tenant_id)
    )
    db_rating = result.scalar_one_or_none()

    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node rating not found"
        )

    update_data = rating_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rating, field, value)

    await db.commit()
    await db.refresh(db_rating)
    return db_rating

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_rating(
    rating_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a node rating."""
    result = await db.execute(
        select(NodeRating).where(NodeRating.id == rating_id, NodeRating.tenant_id == current_user.tenant_id)
    )
    db_rating = result.scalar_one_or_none()

    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node rating not found"
        )

    await db.delete(db_rating)
    await db.commit()
    return

@router.get("/{node_id}/summary", response_model=NodeRatingSummary)
async def get_node_rating_summary(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get rating summary for a specific node."""
    # This would typically involve a service layer call to aggregate ratings
    # For now, a placeholder or direct query
    # Assuming NodeRating model has a method to get summary
    summary = await NodeRating.get_node_rating_summary(db, node_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ratings found for this node")
    return summary

@router.get("/{node_id}/trends", response_model=List[NodeRatingTrend])
async def get_node_rating_trends(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    days: int = Query(30, ge=1, description="Number of days to get trends for"),
):
    """Get rating trends for a specific node over time."""
    trends = await NodeRating.get_rating_trends(db, node_id, days)
    return trends
