"""Inicialização do pacote de segurança.

Este módulo exporta as funcionalidades de segurança e validação.
"""

from .file_validation import (
    SecurityValidator,
    extract_safe_metadata,
    sanitize_filename,
)

__all__ = [
    "SecurityValidator",
    "extract_safe_metadata",
    "sanitize_filename",
]
