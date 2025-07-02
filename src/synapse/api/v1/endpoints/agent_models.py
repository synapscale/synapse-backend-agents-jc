"""
Agent Models endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from synapse.api.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/test", operation_id="test_endpoint_agent_models")
async def test_endpoint():
    """Endpoint de teste para Agent Models"""
    return {"message": "Agent Models endpoint working"}
