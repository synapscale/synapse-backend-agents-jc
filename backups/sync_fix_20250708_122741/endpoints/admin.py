"""
Admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from synapse.api.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_admin_stats(
    current_user=Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Obter estatísticas administrativas"""
    return {"message": "Estatísticas administrativas"}
