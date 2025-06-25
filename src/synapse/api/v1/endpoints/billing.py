from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from synapse.database import get_db
from synapse.models.billing_event import BillingEvent
from synapse.models.user import User
from synapse.api.deps import get_current_user

router = APIRouter()

@router.post("/", summary="Registrar evento de cobrança", tags=["billing"])
def create_billing_event(event: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    billing_event = BillingEvent(**event)
    db.add(billing_event)
    db.commit()
    db.refresh(billing_event)
    return billing_event.to_dict()

@router.get("/", summary="Listar eventos de cobrança", tags=["billing"])
def list_billing_events(
    user_id: Optional[UUID] = Query(None),
    workspace_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(BillingEvent)
    if user_id:
        query = query.filter(BillingEvent.user_id == user_id)
    if workspace_id:
        query = query.filter(BillingEvent.workspace_id == workspace_id)
    if status:
        query = query.filter(BillingEvent.status == status)
    events = query.order_by(BillingEvent.created_at.desc()).limit(100).all()
    return [event.to_dict() for event in events] 