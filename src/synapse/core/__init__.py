"""Inicialização do pacote core.

Este módulo exporta as funcionalidades centrais do sistema.
"""

from .auth import (
    create_access_token,
    get_current_user,
    verify_admin_access,
    verify_scope,
)
from .security import SecurityValidator, extract_safe_metadata, sanitize_filename
from .storage import StorageManager, get_storage_usage

__all__ = [
    "create_access_token",
    "get_current_user",
    "verify_admin_access",
    "verify_scope",
    "SecurityValidator",
    "extract_safe_metadata",
    "sanitize_filename",
    "StorageManager",
    "get_storage_usage",
]
