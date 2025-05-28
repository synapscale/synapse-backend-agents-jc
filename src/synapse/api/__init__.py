"""Inicialização do pacote API.

Este módulo exporta os roteadores da API.
"""

from .v1 import router as v1_router

__all__ = ["v1_router"]
