"""
Agent Tools endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from synapse.api.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/test", operation_id="test_endpoint_agent_tools")
async def test_endpoint():
    """Endpoint de teste para Agent Tools"""
    return {"message": "Agent Tools endpoint working"}
