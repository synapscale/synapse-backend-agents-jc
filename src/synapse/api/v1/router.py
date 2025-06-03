"""
Router principal da API v1
"""
from fastapi import APIRouter

# Importar apenas os routers que existem
from .endpoints.auth import router as auth_router
from .endpoints.files import router as files_router
from .endpoints.llm import router as llm_router
from .endpoints.conversations import router as conversations_router

# Router principal da API v1
api_router = APIRouter()

# Incluir todos os routers de endpoints existentes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
