"""
Workspace Members endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from synapse.api.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_workspace_members(
    current_user=Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Listar membros do workspace"""
    return {"message": "Lista de membros"}
