"""
Schemas Comuns Reutilizáveis.

Define schemas base que podem ser herdados por outros schemas,
garantindo consistência e eliminando duplicação.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .base_fields import CommonFields, CommonConstraints, CommonValidators
from synapse.core.schemas.validators import validate_uuid, validate_tenant_id


T = TypeVar("T")


class BaseResponseSchema(BaseModel):
    """Schema base para todas as respostas da API."""

    model_config = CommonValidators.get_model_config()

    success: bool = Field(True, description="Indica se a operação foi bem-sucedida")
    message: str = Field(
        "Operação realizada com sucesso", description="Mensagem descritiva"
    )
    request_id: Optional[str] = Field(
        None, description="ID único da requisição para rastreamento"
    )


class PaginationSchema(BaseModel):
    """Schema para metadados de paginação."""

    model_config = CommonValidators.get_model_config()

    skip: int = Field(
        CommonConstraints.PAGINATION_MIN_SKIP,
        ge=CommonConstraints.PAGINATION_MIN_SKIP,
        description="Número de registros para pular",
    )
    limit: int = Field(
        CommonConstraints.PAGINATION_DEFAULT_LIMIT,
        ge=1,
        le=CommonConstraints.PAGINATION_MAX_LIMIT,
        description="Número máximo de registros por página",
    )
    total: Optional[int] = Field(None, description="Total de registros disponíveis")
    has_next: Optional[bool] = Field(None, description="Indica se há próxima página")
    has_previous: Optional[bool] = Field(
        None, description="Indica se há página anterior"
    )


class TimestampSchema(BaseModel):
    """Schema base para entidades com timestamps."""

    model_config = CommonValidators.get_model_config()

    created_at: datetime = CommonFields.created_at
    updated_at: datetime = CommonFields.updated_at


class TenantSchema(BaseModel):
    """Schema base para entidades multi-tenant."""

    model_config = CommonValidators.get_model_config()

    tenant_id: UUID = CommonFields.tenant_id

    @field_validator("tenant_id", mode="before")
    @classmethod
    def validate_tenant_id_field(cls, v):
        """Valida tenant_id"""
        return validate_tenant_id(v)


class BaseEntitySchema(BaseModel):
    """Schema base para todas as entidades principais."""

    model_config = CommonValidators.get_model_config()

    id: UUID = CommonFields.id
    tenant_id: UUID = CommonFields.tenant_id
    created_at: datetime = CommonFields.created_at
    updated_at: datetime = CommonFields.updated_at


class NamedEntitySchema(BaseEntitySchema):
    """Schema base para entidades com nome e descrição."""

    title: str = CommonFields.title
    description: Optional[str] = CommonFields.description


class ConfigurableEntitySchema(BaseEntitySchema):
    """Schema base para entidades configuráveis."""

    configuration: Dict[str, Any] = CommonFields.configuration
    metadata: Dict[str, Any] = CommonFields.metadata


class PaginatedResponseSchema(BaseResponseSchema, Generic[T]):
    """Schema para respostas paginadas."""

    data: List[T] = Field([], description="Lista de dados")
    pagination: PaginationSchema = Field(..., description="Metadados de paginação")


class CreateRequestSchema(BaseModel):
    """Schema base para requisições de criação."""

    model_config = CommonValidators.get_model_config()

    tenant_id: UUID = CommonFields.tenant_id


class UpdateRequestSchema(BaseModel):
    """Schema base para requisições de atualização."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        # Permite campos opcionais para atualização parcial
        extra="forbid",
    )


class DeleteResponseSchema(BaseResponseSchema):
    """Schema para respostas de deleção."""

    deleted_id: UUID = Field(..., description="ID do registro deletado")
    deleted_at: datetime = Field(..., description="Timestamp da deleção")


class StatusUpdateSchema(BaseModel):
    """Schema para atualização de status."""

    model_config = CommonValidators.get_model_config()

    status: str = CommonFields.status
    updated_at: datetime = CommonFields.updated_at


class ErrorResponseSchema(BaseModel):
    """Schema para respostas de erro."""

    model_config = CommonValidators.get_model_config()

    success: bool = Field(False, description="Indica que a operação falhou")
    message: str = Field(..., description="Mensagem de erro")
    error_code: Optional[str] = Field(None, description="Código específico do erro")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Detalhes adicionais do erro"
    )
    request_id: Optional[str] = Field(
        None, description="ID da requisição para rastreamento"
    )


class HealthCheckSchema(BaseResponseSchema):
    """Schema para health check."""

    status: str = Field("healthy", description="Status da aplicação")
    timestamp: datetime = Field(..., description="Timestamp do health check")
    version: str = Field(..., description="Versão da aplicação")
    components: Dict[str, str] = Field(
        default_factory=dict, description="Status dos componentes"
    )


# Schemas específicos por funcionalidade
class WorkspaceBaseSchema(BaseEntitySchema):
    """Schema base para workspaces."""

    name: str = Field(
        ...,
        min_length=CommonConstraints.NAME_MIN_LENGTH,
        max_length=CommonConstraints.NAME_MAX_LENGTH,
        description="Nome do workspace",
    )
    description: Optional[str] = CommonFields.description
    is_active: bool = CommonFields.is_active


class UserBaseSchema(BaseEntitySchema):
    """Schema base para usuários."""

    email: str = Field(..., description="Email do usuário")
    username: Optional[str] = Field(None, description="Nome de usuário")
    is_active: bool = CommonFields.is_active


class AgentBaseSchema(BaseEntitySchema):
    """Schema base para agentes."""

    name: str = CommonFields.name
    description: Optional[str] = CommonFields.description
    agent_type: str = Field(..., description="Tipo do agente")
    configuration: Dict[str, Any] = CommonFields.configuration


class WorkflowBaseSchema(BaseEntitySchema):
    """Schema base para workflows."""

    name: str = CommonFields.name
    description: Optional[str] = CommonFields.description
    definition: Dict[str, Any] = Field(..., description="Definição do workflow")
    is_active: bool = CommonFields.is_active


class FileBaseSchema(BaseEntitySchema):
    """Schema base para arquivos."""

    filename: str = Field(..., description="Nome do arquivo")
    file_path: str = Field(..., description="Caminho do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")
    mime_type: str = Field(..., description="Tipo MIME do arquivo")
    description: Optional[str] = CommonFields.description


class AnalyticsBaseSchema(BaseEntitySchema):
    """Schema base para analytics."""

    event_type: str = Field(..., description="Tipo do evento")
    event_data: Dict[str, Any] = Field(..., description="Dados do evento")
    timestamp: datetime = Field(..., description="Timestamp do evento")


# Mixins para funcionalidades específicas
class SoftDeleteMixin(BaseModel):
    """Mixin para soft delete."""

    deleted_at: Optional[datetime] = Field(
        None, description="Timestamp da deleção (soft delete)"
    )
    is_deleted: bool = Field(False, description="Indica se o registro foi deletado")


class AuditMixin(BaseModel):
    """Mixin para auditoria."""

    created_by: Optional[UUID] = Field(None, description="ID do usuário que criou")
    updated_by: Optional[UUID] = Field(None, description="ID do usuário que atualizou")
    version: int = Field(
        1, description="Versão do registro para controle de concorrência"
    )


class TagMixin(BaseModel):
    """Mixin para tags."""

    tags: List[str] = Field(
        default_factory=list, description="Tags associadas ao registro"
    )


class SearchableMixin(BaseModel):
    """Mixin para entidades pesquisáveis."""

    search_vector: Optional[str] = Field(
        None, description="Vetor de busca para pesquisa full-text"
    )
    searchable_content: Optional[str] = Field(
        None, description="Conteúdo indexável para busca"
    )


# Factory functions para criar schemas rapidamente
def create_response_schema(
    data_schema: type, description: str = "Dados da resposta"
) -> type:
    """Factory para criar schemas de resposta."""

    class ResponseSchema(BaseResponseSchema):
        data: data_schema = Field(..., description=description)

    return ResponseSchema


def create_paginated_schema(
    data_schema: type, description: str = "Lista de dados"
) -> type:
    """Factory para criar schemas paginados."""

    class PaginatedSchema(BaseResponseSchema):
        data: List[data_schema] = Field([], description=description)
        pagination: PaginationSchema = Field(..., description="Metadados de paginação")

    return PaginatedSchema


def create_create_schema(base_schema: type, exclude_fields: List[str] = None) -> type:
    """Factory para criar schemas de criação."""
    exclude_fields = exclude_fields or ["id", "created_at", "updated_at"]

    fields = {
        name: field
        for name, field in base_schema.model_fields.items()
        if name not in exclude_fields
    }

    class CreateSchema(BaseModel):
        model_config = CommonValidators.get_model_config()

        for field_name, field_info in fields.items():
            locals()[field_name] = field_info

    return CreateSchema


def create_update_schema(base_schema: type, exclude_fields: List[str] = None) -> type:
    """Factory para criar schemas de atualização."""
    exclude_fields = exclude_fields or ["id", "tenant_id", "created_at", "updated_at"]

    fields = {
        name: field
        for name, field in base_schema.model_fields.items()
        if name not in exclude_fields
    }

    class UpdateSchema(BaseModel):
        model_config = ConfigDict(
            from_attributes=True,
            validate_assignment=True,
            str_strip_whitespace=True,
            extra="forbid",
        )

        for field_name, field_info in fields.items():
            # Torna todos os campos opcionais para atualização parcial
            optional_field = Field(None, **field_info.json_schema_extra or {})
            locals()[field_name] = optional_field

    return UpdateSchema
