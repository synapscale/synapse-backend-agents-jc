"""
Endpoints for managing EmailVerificationTokens.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from synapse.database import get_async_db
from synapse.schemas.email_verification_token import (
    EmailVerificationTokenCreate,
    EmailVerificationTokenUpdate,
    EmailVerificationTokenResponse,
    EmailVerificationTokenListResponse,
)
from synapse.models import EmailVerificationToken, User

router = APIRouter()


@router.post("/", response_model=EmailVerificationTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_email_verification_token(
    item_in: EmailVerificationTokenCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new email verification token."""
    create_data = item_in.model_dump()
    
    db_item = EmailVerificationToken(**create_data)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=EmailVerificationTokenResponse)
async def get_email_verification_token(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific email verification token by its ID."""
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="EmailVerificationToken not found"
        )
    return item


@router.get("/", response_model=EmailVerificationTokenListResponse)
async def list_email_verification_tokens(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
):
    """List all email verification tokens for the current user."""
    query = select(EmailVerificationToken)
    
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

    return EmailVerificationTokenListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.put("/{item_id}", response_model=EmailVerificationTokenResponse)
async def update_email_verification_token(
    item_id: uuid.UUID,
    item_in: EmailVerificationTokenUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing email verification token."""
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="EmailVerificationToken not found"
        )

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_verification_token(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a email verification token."""
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="EmailVerificationToken not found"
        )

    await db.delete(db_item)
    await db.commit()
