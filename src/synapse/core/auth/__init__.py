"""Inicialização do pacote de autenticação.

Este módulo exporta as funcionalidades de autenticação e autorização.
"""

from .jwt import (
    create_access_token,
    get_current_user,
    verify_admin_access,
    verify_scope,
)

__all__ = [
    "create_access_token",
    "get_current_user",
    "verify_admin_access",
    "verify_scope",
]
