"""
Endpoints for managing Agent Quotas.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from synapse.database import get_async_db
from synapse.schemas.agent_quota import (
    AgentQuotaBase,
    AgentQuotaUpdate,
    AgentQuotaUsageCheck,
    AgentQuotaListResponse,
    AgentQuotaCreateDaily,
    AgentQuotaCreateHourly,
    AgentQuotaCreateMonthly,
)
from synapse.models import AgentQuota, User

router = APIRouter()


@router.post("/daily", response_model=AgentQuotaBase, status_code=status.HTTP_201_CREATED)
async def create_daily_quota(
    quota_in: AgentQuotaCreateDaily,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a daily quota for an agent."""
    db_quota = AgentQuota(**quota_in.model_dump(), tenant_id=current_user.tenant_id)
    db.add(db_quota)
    await db.commit()
    await db.refresh(db_quota)
    return db_quota


@router.post("/hourly", response_model=AgentQuotaBase, status_code=status.HTTP_201_CREATED)
async def create_hourly_quota(
    quota_in: AgentQuotaCreateHourly,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an hourly quota for an agent."""
    db_quota = AgentQuota(**quota_in.model_dump(), tenant_id=current_user.tenant_id)
    db.add(db_quota)
    await db.commit()
    await db.refresh(db_quota)
    return db_quota


@router.post("/monthly", response_model=AgentQuotaBase, status_code=status.HTTP_201_CREATED)
async def create_monthly_quota(
    quota_in: AgentQuotaCreateMonthly,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a monthly quota for an agent."""
    db_quota = AgentQuota(**quota_in.model_dump(), tenant_id=current_user.tenant_id)
    db.add(db_quota)
    await db.commit()
    await db.refresh(db_quota)
    return db_quota


@router.get("/{quota_id}", response_model=AgentQuotaBase)
async def get_quota(
    quota_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific quota by its ID."""
    result = await db.execute(
        select(AgentQuota).where(
            AgentQuota.id == quota_id,
            AgentQuota.tenant_id == current_user.tenant_id
        )
    )
    quota = result.scalar_one_or_none()

    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quota not found"
        )
    return quota


@router.get("/", response_model=AgentQuotaListResponse)
async def list_quotas(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    agent_id: Optional[uuid.UUID] = Query(None, description="Filter by agent ID"),
):
    """List all quotas for the current tenant."""
    query = select(AgentQuota).where(AgentQuota.tenant_id == current_user.tenant_id)
    
    if agent_id:
        query = query.where(AgentQuota.agent_id == agent_id)

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    quotas = result.scalars().all()

    return AgentQuotaListResponse(
        items=quotas,
        total=total,
        page=page,
        size=size,
    )


@router.put("/{quota_id}", response_model=AgentQuotaBase)
async def update_quota(
    quota_id: uuid.UUID,
    quota_in: AgentQuotaUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing quota."""
    result = await db.execute(
        select(AgentQuota).where(
            AgentQuota.id == quota_id,
            AgentQuota.tenant_id == current_user.tenant_id
        )
    )
    db_quota = result.scalar_one_or_none()

    if not db_quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quota not found"
        )

    update_data = quota_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_quota, field, value)

    await db.commit()
    await db.refresh(db_quota)
    return db_quota


@router.delete("/{quota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quota(
    quota_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a quota."""
    result = await db.execute(
        select(AgentQuota).where(
            AgentQuota.id == quota_id,
            AgentQuota.tenant_id == current_user.tenant_id
        )
    )
    db_quota = result.scalar_one_or_none()

    if not db_quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quota not found"
        )

    await db.delete(db_quota)
    await db.commit()


@router.post("/{quota_id}/check", response_model=AgentQuotaUsageCheck)
async def check_quota_usage(
    quota_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check current usage against quota limits."""
    result = await db.execute(
        select(AgentQuota).where(
            AgentQuota.id == quota_id,
            AgentQuota.tenant_id == current_user.tenant_id
        )
    )
    quota = result.scalar_one_or_none()

    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quota not found"
        )

    # Aqui você implementaria a lógica para calcular o uso atual
    # Por agora, retornamos dados de exemplo
    return AgentQuotaUsageCheck(
        quota_id=quota.id,
        current_usage=0,
        quota_limit=quota.quota_limit,
        usage_percentage=0.0,
        is_exceeded=False,
        remaining_quota=quota.quota_limit
    )
