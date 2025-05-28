"""Roteador principal da API v1.
Este módulo configura o roteador principal da API v1, incluindo
todos os endpoints disponíveis nesta versão.
"""
from fastapi import APIRouter
from .endpoints.files import router as files_router
from .endpoints.llm import router as llm_router

# Criar roteador principal
router = APIRouter()

# Incluir sub-roteadores
# LLM router deve vir antes do files router para evitar conflitos com {file_id}
router.include_router(llm_router, prefix="/llm")
router.include_router(files_router)
