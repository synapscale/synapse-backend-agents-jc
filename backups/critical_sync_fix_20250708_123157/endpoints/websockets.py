"""
WebSocket endpoints
"""

from fastapi import APIRouter, WebSocket
from typing import Dict, Any

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()
    await websocket.send_text("Hello WebSocket!")
    await websocket.close()
