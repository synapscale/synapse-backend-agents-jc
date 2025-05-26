"""Exemplo de segurança com docstrings."""

import os
from typing import Dict


def validate_input(data: str) -> bool:
    """Valida entrada do usuário."""
    if len(data) > 100:
        return False
    return True


def sanitize_path(path: str) -> str:
    """Sanitiza caminho de arquivo."""
    return os.path.normpath(path)


def check_permissions(user_id: str, resource: str) -> bool:
    """Verifica permissões do usuário."""
    # Implementação simplificada
    return True


def get_security_headers() -> Dict[str, str]:
    """Retorna cabeçalhos de segurança."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
    }


def validate_file_upload(filename: str, content_type: str, size: int) -> bool:
    """Valida upload de arquivo."""
    # Verificar extensão
    allowed_extensions = [".jpg", ".png", ".pdf", ".txt"]
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return False

    # Verificar tamanho
    max_size = 10 * 1024 * 1024  # 10MB
    if size > max_size:
        return False

    return True


def hash_password(password: str) -> str:
    """Gera hash da senha."""
    # Implementação simplificada
    return f"hashed_{password}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha."""
    return f"hashed_{password}" == hashed


def generate_token(user_data: Dict[str, str]) -> str:
    """Gera token de autenticação."""
    # Implementação simplificada
    return f"token_{user_data.get('id', 'unknown')}"


def validate_token(token: str) -> bool:
    """Valida token de autenticação."""
    return token.startswith("token_")


def get_user_permissions(user_id: str) -> list:
    """Obtém permissões do usuário."""
    # Implementação simplificada
    return ["read", "write"]
