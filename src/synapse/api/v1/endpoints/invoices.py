"""
Endpoints for managing Invoices.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_async_db
from synapse.schemas.invoice import (
    InvoiceResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceListResponse
)
from synapse.models import Invoice

router = APIRouter()

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new invoice."""
    if invoice_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create invoice for another tenant.",
        )

    db_invoice = Invoice(**invoice_in.model_dump())
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific invoice by its ID."""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    return invoice

@router.get("/", response_model=InvoiceListResponse)
async def list_invoices(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for invoice number or status"),
):
    """List all invoices for the current tenant."""
    query = select(Invoice).where(Invoice.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Invoice.invoice_number.ilike(search_term),
                Invoice.status.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Invoice.created_at.desc())
    result = await db.execute(query)
    invoices = result.scalars().all()

    return {
        "items": invoices,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: uuid.UUID,
    invoice_in: InvoiceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing invoice."""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
    )
    db_invoice = result.scalar_one_or_none()

    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    update_data = invoice_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)

    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an invoice."""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
    )
    db_invoice = result.scalar_one_or_none()

    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    await db.delete(db_invoice)
    await db.commit()
    return
