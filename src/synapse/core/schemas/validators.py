"""
Validadores Centralizados.

Define funções de validação reutilizáveis para garantir
consistência em toda a aplicação.
"""

import re
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime
from pydantic import validator, field_validator
from .base_fields import CommonConstraints


def validate_uuid(value: Union[str, UUID]) -> UUID:
    """Valida e converte UUID."""
    if isinstance(value, str):
        if not re.match(CommonConstraints.UUID_PATTERN, value):
            raise ValueError("Formato de UUID inválido")
        return UUID(value)
    return value


def validate_tenant_id(value: Union[str, UUID]) -> UUID:
    """Valida tenant_id específicamente."""
    return validate_uuid(value)


def validate_email(value: str) -> str:
    """Valida formato de email."""
    if not re.match(CommonConstraints.EMAIL_PATTERN, value):
        raise ValueError("Formato de email inválido")
    return value.lower().strip()


def validate_title(value: str) -> str:
    """Valida título."""
    if not value or not value.strip():
        raise ValueError("Título não pode estar vazio")

    cleaned = value.strip()

    if len(cleaned) < CommonConstraints.TITLE_MIN_LENGTH:
        raise ValueError(
            f"Título deve ter pelo menos {CommonConstraints.TITLE_MIN_LENGTH} caractere(s)"
        )

    if len(cleaned) > CommonConstraints.TITLE_MAX_LENGTH:
        raise ValueError(
            f"Título deve ter no máximo {CommonConstraints.TITLE_MAX_LENGTH} caracteres"
        )

    return cleaned


def validate_name(value: str) -> str:
    """Valida nome."""
    if not value or not value.strip():
        raise ValueError("Nome não pode estar vazio")

    cleaned = value.strip()

    if len(cleaned) < CommonConstraints.NAME_MIN_LENGTH:
        raise ValueError(
            f"Nome deve ter pelo menos {CommonConstraints.NAME_MIN_LENGTH} caractere(s)"
        )

    if len(cleaned) > CommonConstraints.NAME_MAX_LENGTH:
        raise ValueError(
            f"Nome deve ter no máximo {CommonConstraints.NAME_MAX_LENGTH} caracteres"
        )

    return cleaned


def validate_description(value: Optional[str]) -> Optional[str]:
    """Valida descrição."""
    if value is None:
        return None

    cleaned = value.strip()

    if len(cleaned) > CommonConstraints.DESCRIPTION_MAX_LENGTH:
        raise ValueError(
            f"Descrição deve ter no máximo {CommonConstraints.DESCRIPTION_MAX_LENGTH} caracteres"
        )

    return cleaned if cleaned else None


def validate_short_description(value: Optional[str]) -> Optional[str]:
    """Valida descrição curta."""
    if value is None:
        return None

    cleaned = value.strip()

    if len(cleaned) > CommonConstraints.SHORT_DESCRIPTION_MAX_LENGTH:
        raise ValueError(
            f"Descrição curta deve ter no máximo {CommonConstraints.SHORT_DESCRIPTION_MAX_LENGTH} caracteres"
        )

    return cleaned if cleaned else None


def validate_long_description(value: Optional[str]) -> Optional[str]:
    """Valida descrição longa."""
    if value is None:
        return None

    cleaned = value.strip()

    if len(cleaned) > CommonConstraints.LONG_DESCRIPTION_MAX_LENGTH:
        raise ValueError(
            f"Descrição longa deve ter no máximo {CommonConstraints.LONG_DESCRIPTION_MAX_LENGTH} caracteres"
        )

    return cleaned if cleaned else None


def validate_slug(value: str) -> str:
    """Valida slug."""
    if not value or not value.strip():
        raise ValueError("Slug não pode estar vazio")

    cleaned = value.strip().lower()

    if not re.match(CommonConstraints.SLUG_PATTERN, cleaned):
        raise ValueError("Slug deve conter apenas letras minúsculas, números e hífens")

    if len(cleaned) < CommonConstraints.SLUG_MIN_LENGTH:
        raise ValueError(
            f"Slug deve ter pelo menos {CommonConstraints.SLUG_MIN_LENGTH} caractere(s)"
        )

    if len(cleaned) > CommonConstraints.SLUG_MAX_LENGTH:
        raise ValueError(
            f"Slug deve ter no máximo {CommonConstraints.SLUG_MAX_LENGTH} caracteres"
        )

    return cleaned


def validate_status(value: str, allowed_statuses: List[str] = None) -> str:
    """Valida status com lista de valores permitidos."""
    if allowed_statuses is None:
        allowed_statuses = ["active", "inactive", "pending", "archived", "deleted"]

    cleaned = value.strip().lower()

    if cleaned not in allowed_statuses:
        raise ValueError(
            f"Status deve ser um dos seguintes: {', '.join(allowed_statuses)}"
        )

    return cleaned


def validate_pagination_skip(value: int) -> int:
    """Valida parâmetro skip de paginação."""
    if value < CommonConstraints.PAGINATION_MIN_SKIP:
        raise ValueError(
            f"Skip deve ser maior ou igual a {CommonConstraints.PAGINATION_MIN_SKIP}"
        )

    return value


def validate_pagination_limit(value: int) -> int:
    """Valida parâmetro limit de paginação."""
    if value < 1:
        raise ValueError("Limit deve ser maior que 0")

    if value > CommonConstraints.PAGINATION_MAX_LIMIT:
        raise ValueError(
            f"Limit deve ser menor ou igual a {CommonConstraints.PAGINATION_MAX_LIMIT}"
        )

    return value


def validate_configuration(value: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dicionário de configuração."""
    if not isinstance(value, dict):
        raise ValueError("Configuração deve ser um dicionário")

    # Remove valores nulos e vazios
    cleaned = {k: v for k, v in value.items() if v is not None and v != ""}

    return cleaned


def validate_metadata(value: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dicionário de metadata."""
    if not isinstance(value, dict):
        raise ValueError("Metadata deve ser um dicionário")

    # Remove valores nulos
    cleaned = {k: v for k, v in value.items() if v is not None}

    return cleaned


def validate_tags(value: List[str]) -> List[str]:
    """Valida lista de tags."""
    if not isinstance(value, list):
        raise ValueError("Tags devem ser uma lista")

    # Remove duplicatas e valores vazios
    cleaned_tags = []
    seen = set()

    for tag in value:
        if not isinstance(tag, str):
            raise ValueError("Todas as tags devem ser strings")

        cleaned_tag = tag.strip().lower()

        if cleaned_tag and cleaned_tag not in seen:
            cleaned_tags.append(cleaned_tag)
            seen.add(cleaned_tag)

    return cleaned_tags


def validate_json_field(value: Any) -> Any:
    """Valida campos JSON genéricos."""
    if value is None:
        return {}

    if isinstance(value, str):
        try:
            import json

            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError("JSON inválido")

    return value


def validate_datetime_string(value: Union[str, datetime]) -> datetime:
    """Valida e converte string para datetime."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Formato de data/hora inválido. Use ISO 8601")

    raise ValueError("Data/hora deve ser string ISO 8601 ou objeto datetime")


def validate_file_size(value: int, max_size: int = 50 * 1024 * 1024) -> int:
    """Valida tamanho de arquivo."""
    if value < 0:
        raise ValueError("Tamanho do arquivo não pode ser negativo")

    if value > max_size:
        raise ValueError(f"Arquivo muito grande. Máximo permitido: {max_size} bytes")

    return value


def validate_mime_type(value: str, allowed_types: List[str] = None) -> str:
    """Valida tipo MIME."""
    if allowed_types is None:
        allowed_types = [
            "text/plain",
            "text/csv",
            "application/json",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/jpeg",
            "image/png",
            "image/gif",
        ]

    cleaned = value.strip().lower()

    if cleaned not in allowed_types:
        raise ValueError(
            f"Tipo de arquivo não permitido. Tipos aceitos: {', '.join(allowed_types)}"
        )

    return cleaned


def validate_url(value: str) -> str:
    """Valida URL."""
    url_pattern = r"^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*)?(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?$"

    if not re.match(url_pattern, value):
        raise ValueError("URL inválida")

    return value.strip()


def validate_color_hex(value: str) -> str:
    """Valida cor em formato hexadecimal."""
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

    if not re.match(pattern, value):
        raise ValueError("Cor deve estar no formato hexadecimal (#RRGGBB ou #RGB)")

    return value.upper()


def validate_phone_number(value: str) -> str:
    """Valida número de telefone."""
    # Remove caracteres não numéricos
    digits_only = re.sub(r"[^\d+]", "", value)

    # Padrão básico para números internacionais
    pattern = r"^\+?[1-9]\d{7,14}$"

    if not re.match(pattern, digits_only):
        raise ValueError("Número de telefone inválido")

    return digits_only


def validate_version(value: str) -> str:
    """Valida número de versão semântica."""
    pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

    if not re.match(pattern, value):
        raise ValueError("Versão deve seguir o padrão semântico (x.y.z)")

    return value


class CommonValidatorsMixin:
    """Mixin com validadores comuns para usar em schemas Pydantic."""

    @field_validator("title", mode="before", check_fields=False)
    @classmethod
    def validate_title_field(cls, v):
        return validate_title(v) if v is not None else v

    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def validate_name_field(cls, v):
        return validate_name(v) if v is not None else v

    @field_validator("description", mode="before", check_fields=False)
    @classmethod
    def validate_description_field(cls, v):
        return validate_description(v)

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def validate_email_field(cls, v):
        return validate_email(v) if v is not None else v

    @field_validator("slug", mode="before", check_fields=False)
    @classmethod
    def validate_slug_field(cls, v):
        return validate_slug(v) if v is not None else v

    @field_validator("configuration", mode="before", check_fields=False)
    @classmethod
    def validate_configuration_field(cls, v):
        return validate_configuration(v) if v is not None else {}

    @field_validator("metadata", mode="before", check_fields=False)
    @classmethod
    def validate_metadata_field(cls, v):
        return validate_metadata(v) if v is not None else {}

    @field_validator("tags", mode="before", check_fields=False)
    @classmethod
    def validate_tags_field(cls, v):
        return validate_tags(v) if v is not None else []


# Dicionário de validadores para uso dinâmico
VALIDATORS = {
    "uuid": validate_uuid,
    "tenant_id": validate_tenant_id,
    "email": validate_email,
    "title": validate_title,
    "name": validate_name,
    "description": validate_description,
    "short_description": validate_short_description,
    "long_description": validate_long_description,
    "slug": validate_slug,
    "status": validate_status,
    "configuration": validate_configuration,
    "metadata": validate_metadata,
    "tags": validate_tags,
    "json": validate_json_field,
    "datetime": validate_datetime_string,
    "file_size": validate_file_size,
    "mime_type": validate_mime_type,
    "url": validate_url,
    "color": validate_color_hex,
    "phone": validate_phone_number,
    "version": validate_version,
}


def get_validator(field_type: str):
    """Retorna validador por tipo de campo."""
    return VALIDATORS.get(field_type)
