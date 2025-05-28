"""Inicialização do pacote de armazenamento.

Este módulo exporta as funcionalidades de gerenciamento de armazenamento.
"""

from .storage_manager import StorageManager, get_storage_usage

__all__ = ["StorageManager", "get_storage_usage"]
