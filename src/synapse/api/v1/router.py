"""Roteador principal da API v1.

Este módulo configura o roteador principal da API v1, incluindo
todos os endpoints disponíveis nesta versão.
"""

from fastapi import APIRouter

from .endpoints.files import router as files_router

# Criar roteador principal
router = APIRouter()

# Incluir sub-roteadores
router.include_router(files_router)
