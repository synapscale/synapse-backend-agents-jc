"""
LLM endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from synapse.api.deps import get_current_active_user, get_db

router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_text(current_user=Depends(get_current_active_user)):
    """Gerar texto com LLM"""
    return {"message": "Text generated"}


@router.post("/chat", response_model=Dict[str, Any])
async def chat_completion(current_user=Depends(get_current_active_user)):
    """Chat completion"""
    return {"message": "Chat response"}


@router.get("/models", response_model=List[Dict[str, Any]])
async def list_models():
    """Listar modelos disponíveis"""
    return []


@router.get("/providers", response_model=List[Dict[str, Any]])
async def list_providers():
    """Listar provedores disponíveis"""
    return []
