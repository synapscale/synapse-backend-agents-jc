"""
Endpoints for managing Payment Customers.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from synapse.database import get_async_db
from synapse.schemas.payment_customer import (
    PaymentCustomerBase,
    PaymentCustomerUpdate,
    PaymentCustomerListResponse,
    PaymentCustomerCreateSimple,
    PaymentCustomerSearch,
    PaymentCustomerSummary,
    PaymentCustomerActivateDeactivate,
    PaymentCustomerUpdateData,
)
from synapse.models import PaymentCustomer, User

router = APIRouter()


@router.post("/", response_model=PaymentCustomerBase, status_code=status.HTTP_201_CREATED)
async def create_payment_customer(
    customer_in: PaymentCustomerCreateSimple,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new payment customer."""
    db_customer = PaymentCustomer(
        **customer_in.model_dump(),
        tenant_id=current_user.tenant_id
    )
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


@router.get("/{customer_id}", response_model=PaymentCustomerBase)
async def get_payment_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific payment customer by its ID."""
    result = await db.execute(
        select(PaymentCustomer).where(
            PaymentCustomer.id == customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id
        )
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment customer not found"
        )
    return customer


@router.get("/", response_model=PaymentCustomerListResponse)
async def list_payment_customers(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in customer name or email"),
    provider: Optional[str] = Query(None, description="Filter by payment provider"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """List all payment customers for the current tenant."""
    query = select(PaymentCustomer).where(PaymentCustomer.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                PaymentCustomer.customer_name.ilike(search_term),
                PaymentCustomer.email.ilike(search_term),
            )
        )
    
    if provider:
        query = query.where(PaymentCustomer.provider == provider)
    
    if is_active is not None:
        query = query.where(PaymentCustomer.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    customers = result.scalars().all()

    return PaymentCustomerListResponse(
        items=customers,
        total=total,
        page=page,
        size=size,
    )


@router.put("/{customer_id}", response_model=PaymentCustomerBase)
async def update_payment_customer(
    customer_id: uuid.UUID,
    customer_in: PaymentCustomerUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing payment customer."""
    result = await db.execute(
        select(PaymentCustomer).where(
            PaymentCustomer.id == customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id
        )
    )
    db_customer = result.scalar_one_or_none()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment customer not found"
        )

    update_data = customer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    await db.commit()
    await db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a payment customer."""
    result = await db.execute(
        select(PaymentCustomer).where(
            PaymentCustomer.id == customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id
        )
    )
    db_customer = result.scalar_one_or_none()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment customer not found"
        )

    await db.delete(db_customer)
    await db.commit()


@router.post("/search", response_model=List[PaymentCustomerBase])
async def search_payment_customers(
    search_params: PaymentCustomerSearch,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Advanced search for payment customers."""
    query = select(PaymentCustomer).where(PaymentCustomer.tenant_id == current_user.tenant_id)
    
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.where(
            or_(
                PaymentCustomer.customer_name.ilike(search_term),
                PaymentCustomer.email.ilike(search_term),
                PaymentCustomer.external_customer_id.ilike(search_term),
            )
        )
    
    if search_params.provider:
        query = query.where(PaymentCustomer.provider == search_params.provider)
    
    if search_params.is_active is not None:
        query = query.where(PaymentCustomer.is_active == search_params.is_active)
    
    if search_params.limit:
        query = query.limit(search_params.limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{customer_id}/summary", response_model=PaymentCustomerSummary)
async def get_customer_summary(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get summary information for a payment customer."""
    result = await db.execute(
        select(PaymentCustomer).where(
            PaymentCustomer.id == customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id
        )
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment customer not found"
        )

    # Aqui você implementaria a lógica para calcular estatísticas
    # Por agora, retornamos dados básicos
    return PaymentCustomerSummary(
        customer_id=customer.id,
        customer_name=customer.customer_name,
        email=customer.email,
        provider=customer.provider,
        is_active=customer.is_active,
        total_payments=0,  # Implementar cálculo real
        total_amount=0.0,  # Implementar cálculo real
        last_payment_date=None,  # Implementar busca real
        created_at=customer.created_at
    )


@router.patch("/{customer_id}/activate", response_model=PaymentCustomerBase)
async def activate_customer(
    customer_id: uuid.UUID,
    activation_data: PaymentCustomerActivateDeactivate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Activate or deactivate a payment customer."""
    result = await db.execute(
        select(PaymentCustomer).where(
            PaymentCustomer.id == customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id
        )
    )
    db_customer = result.scalar_one_or_none()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment customer not found"
        )

    db_customer.is_active = activation_data.is_active
    if activation_data.reason:
        # Você pode armazenar o motivo em um campo de metadata se disponível
        pass

    await db.commit()
    await db.refresh(db_customer)
    return db_customer


@router.patch("/{customer_id}/update-data", response_model=PaymentCustomerBase)
async def update_customer_data(
    customer_id: uuid.UUID,
    update_data: PaymentCustomerUpdateData,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update specific customer data fields."""
    result = await db.execute(
        select(PaymentCustomer).where(
            PaymentCustomer.id == customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id
        )
    )
    db_customer = result.scalar_one_or_none()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment customer not found"
        )

    # Atualizar apenas os campos fornecidos
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(db_customer, field):
            setattr(db_customer, field, value)

    await db.commit()
    await db.refresh(db_customer)
    return db_customer
