from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from uuid import UUID
from synapse.database import get_db
from synapse.models.llm import LLM
from synapse.models.user import User
from synapse.api.deps import get_current_user

router = APIRouter()

@router.get("/", summary="Listar catálogo de LLMs", tags=["llm"])
def list_llms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    llms = db.query(LLM).filter(LLM.is_active == True).all()
    return [llm.to_dict() for llm in llms]

@router.get("/{llm_id}", summary="Detalhe de LLM", tags=["llm"])
def get_llm(llm_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    llm = db.query(LLM).filter(LLM.id == llm_id, LLM.is_active == True).first()
    if not llm:
        raise HTTPException(status_code=404, detail="LLM não encontrado")
    return llm.to_dict() 