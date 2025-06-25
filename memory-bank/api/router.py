from fastapi import APIRouter
from memory_bank.api.memory import router as memory_router
from memory_bank.api.collection import router as collection_router

# Criar router principal
router = APIRouter(prefix="/api/v1/memory-bank")

# Incluir sub-routers
router.include_router(memory_router)
router.include_router(collection_router)
