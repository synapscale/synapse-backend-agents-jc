"""
Campos Base Centralizados.

Define campos comuns reutilizáveis em toda a aplicação,
eliminando duplicação de definições de schema.
"""

from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import Field, ConfigDict
from datetime import datetime


class CommonFields:
    """Definições centralizadas de campos comuns."""

    # Campos de identificação - usando tipos UUID consistentes
    id: UUID = Field(
        ...,
        description="ID único do registro",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )

    tenant_id: UUID = Field(
        ...,
        description="ID do tenant - multi-tenancy",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440001"},
    )

    # Campos de relacionamento - usando tipos UUID consistentes
    workspace_id: UUID = Field(
        ...,
        description="ID do workspace",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440002"},
    )

    user_id: UUID = Field(
        ...,
        description="ID do usuário",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440003"},
    )

    project_id: UUID = Field(
        ...,
        description="ID do projeto",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440004"},
    )

    # Campos de texto
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Título do registro",
        json_schema_extra={"example": "Título do Item"},
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome do registro",
        json_schema_extra={"example": "Nome do Item"},
    )

    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição do registro",
        json_schema_extra={"example": "Descrição detalhada do item"},
    )

    short_description: Optional[str] = Field(
        None,
        max_length=200,
        description="Descrição curta do registro",
        json_schema_extra={"example": "Descrição resumida"},
    )

    long_description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Descrição longa e detalhada",
        json_schema_extra={
            "example": "Descrição muito detalhada com múltiplos parágrafos..."
        },
    )

    # Campos de usuário
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email do usuário",
        json_schema_extra={"example": "usuario@exemplo.com"},
    )

    avatar_url: Optional[str] = Field(
        None,
        description="URL do avatar/imagem",
        json_schema_extra={"example": "https://exemplo.com/avatar.jpg"},
    )

    # Campos de metadata
    slug: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Slug único do registro",
        json_schema_extra={"example": "slug-unico"},
    )

    status: str = Field(
        "active",
        description="Status do registro",
        json_schema_extra={"example": "active"},
    )

    is_active: bool = Field(
        True,
        description="Indica se o registro está ativo",
        json_schema_extra={"example": True},
    )

    # Campos de timestamp
    created_at: datetime = Field(
        ...,
        description="Data de criação do registro",
        json_schema_extra={"example": "2024-01-01T00:00:00Z"},
    )

    updated_at: datetime = Field(
        ...,
        description="Data da última atualização",
        json_schema_extra={"example": "2024-01-01T12:00:00Z"},
    )

    # Campos de configuração
    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configurações específicas do registro",
        json_schema_extra={"example": {"key": "value"}},
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados adicionais",
        json_schema_extra={"example": {"extra_info": "value"}},
    )


class CommonConstraints:
    """Restrições comuns para validação."""

    # Tamanhos de string
    TITLE_MIN_LENGTH = 1
    TITLE_MAX_LENGTH = 255

    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 255

    DESCRIPTION_MAX_LENGTH = 500
    SHORT_DESCRIPTION_MAX_LENGTH = 200
    LONG_DESCRIPTION_MAX_LENGTH = 2000

    SLUG_MIN_LENGTH = 1
    SLUG_MAX_LENGTH = 100
    SLUG_PATTERN = r"^[a-z0-9-]+$"

    # Limites numéricos
    PAGINATION_MIN_SKIP = 0
    PAGINATION_MAX_LIMIT = 500
    PAGINATION_DEFAULT_LIMIT = 100

    # Padrões de validação
    UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class CommonValidators:
    """Configurações de validação comuns."""

    @staticmethod
    def get_model_config() -> ConfigDict:
        """Configuração padrão para modelos Pydantic."""
        return ConfigDict(
            from_attributes=True,
            validate_assignment=True,
            str_strip_whitespace=True,
            json_schema_extra={
                "examples": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Exemplo",
                        "description": "Descrição do exemplo",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                    }
                ]
            },
        )


# Campos específicos por domínio
class WorkspaceFields:
    """Campos específicos para workspaces."""

    workspace_name = Field(
        ...,
        min_length=CommonConstraints.NAME_MIN_LENGTH,
        max_length=CommonConstraints.NAME_MAX_LENGTH,
        description="Nome do workspace",
        json_schema_extra={"example": "Meu Workspace"},
    )


class UserFields:
    """Campos específicos para usuários."""

    username = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Nome de usuário",
        json_schema_extra={"example": "usuario123"},
    )


class AgentFields:
    """Campos específicos para agentes."""

    agent_id = Field(
        ...,
        description="ID do agente",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440004"},
    )

    agent_type = Field(
        ..., description="Tipo do agente", json_schema_extra={"example": "chatbot"}
    )


class WorkflowFields:
    """Campos específicos para workflows."""

    workflow_id = Field(
        ...,
        description="ID do workflow",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440005"},
    )

    workflow_definition = Field(
        ...,
        description="Definição estruturada do workflow",
        json_schema_extra={"example": {"nodes": [], "edges": []}},
    )


# Aliases para compatibilidade
TitleField = CommonFields.title
DescriptionField = CommonFields.description
TenantIdField = CommonFields.tenant_id
IdField = CommonFields.id
CreatedAtField = CommonFields.created_at
UpdatedAtField = CommonFields.updated_at
