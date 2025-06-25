from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from synapse.database import get_db
from synapse.models.message_feedback import MessageFeedback
from synapse.models.user import User
from synapse.api.deps import get_current_user

router = APIRouter()

@router.post("/messages/{message_id}/feedback", summary="Registrar feedback de mensagem", tags=["feedback"])
def create_feedback(message_id: UUID, feedback: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    feedback_obj = MessageFeedback(message_id=message_id, user_id=current_user.id, **feedback)
    db.add(feedback_obj)
    db.commit()
    db.refresh(feedback_obj)
    return feedback_obj.to_dict()

@router.get("/messages/{message_id}/feedback", summary="Listar feedbacks de uma mensagem", tags=["feedback"])
def list_feedbacks_for_message(message_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    feedbacks = db.query(MessageFeedback).filter(MessageFeedback.message_id == message_id).order_by(MessageFeedback.created_at.desc()).all()
    return [fb.to_dict() for fb in feedbacks]

@router.get("/", summary="Listar feedbacks gerais", tags=["feedback"])
def list_feedbacks(
    user_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(MessageFeedback)
    if user_id:
        query = query.filter(MessageFeedback.user_id == user_id)
    feedbacks = query.order_by(MessageFeedback.created_at.desc()).limit(100).all()
    return [fb.to_dict() for fb in feedbacks] 