"""Schemas padronizados para respostas da API SynapScale.

Este módulo define os schemas base Pydantic para padronizar todas as respostas
da API, garantindo consistência, facilidade de uso e manutenibilidade.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union, Callable
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4


# Type variable para respostas genéricas
T = TypeVar("T")


class BaseResponse(BaseModel):
    """Schema base para todas as respostas da API.

    Fornece campos padrão que todas as respostas devem incluir para
    garantir consistência e facilitar debugging e rastreamento.
    """

    status: str = Field(
        default="success",
        description="Status da resposta: 'success', 'error', 'warning'",
        example="success",
    )
    message: Optional[str] = Field(
        default=None,
        description="Mensagem opcional para contexto adicional",
        example="Operação realizada com sucesso",
    )
    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        description="ID único da requisição para rastreamento",
        example="req_123e4567-e89b-12d3-a456-426614174000",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp UTC da resposta",
        example="2024-01-01T12:00:00Z",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operação realizada com sucesso",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class DataResponse(BaseResponse, Generic[T]):
    """Schema para respostas que retornam um único objeto de dados.

    Usado quando a API retorna um único recurso ou resultado.
    """

    data: T = Field(..., description="Os dados da resposta")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Usuário encontrado",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
                "data": {
                    "id": "user_123",
                    "name": "João Silva",
                    "email": "joao@example.com",
                },
            }
        }


class ListResponse(BaseResponse, Generic[T]):
    """Schema para respostas que retornam listas de dados.

    Versão flexível que pode incluir total e paginação opcionalmente.
    """

    data: List[T] = Field(..., description="Lista de itens da resposta")
    total: Optional[int] = Field(
        default=None, ge=0, description="Número total de itens (opcional)"
    )
    pagination: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadados de paginação (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Lista de usuários recuperada",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
                "data": [
                    {"id": "user_1", "name": "João Silva"},
                    {"id": "user_2", "name": "Maria Santos"},
                ],
                "pagination": {
                    "total": 150,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 8,
                    "has_next": True,
                    "has_previous": False,
                    "next_page": 2,
                    "previous_page": None,
                },
            }
        }


class PaginationMeta(BaseModel):
    """Schema para metadados de paginação.

    Fornece informações completas sobre paginação para facilitar
    navegação e implementação de interfaces de usuário.
    """

    current_page: int = Field(
        ..., ge=1, description="Página atual (começando em 1)", example=1
    )
    page_size: int = Field(
        ..., ge=1, le=1000, description="Número de itens por página", example=20
    )
    total_pages: int = Field(
        ..., ge=0, description="Número total de páginas", example=8
    )
    total_items: int = Field(
        ..., ge=0, description="Número total de itens disponíveis", example=150
    )
    has_next: bool = Field(..., description="Se existe próxima página", example=True)
    has_previous: bool = Field(
        ..., description="Se existe página anterior", example=False
    )
    next_page: Optional[int] = Field(
        default=None,
        ge=1,
        description="Número da próxima página (se existir)",
        example=2,
    )
    previous_page: Optional[int] = Field(
        default=None,
        ge=1,
        description="Número da página anterior (se existir)",
        example=None,
    )
    first_page_url: Optional[str] = Field(
        default=None,
        description="URL da primeira página",
        example="/api/v1/users?page=1&size=20",
    )
    last_page_url: Optional[str] = Field(
        default=None,
        description="URL da última página",
        example="/api/v1/users?page=8&size=20",
    )
    next_page_url: Optional[str] = Field(
        default=None,
        description="URL da próxima página",
        example="/api/v1/users?page=2&size=20",
    )
    previous_page_url: Optional[str] = Field(
        default=None, description="URL da página anterior", example=None
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_page": 1,
                "page_size": 20,
                "total_pages": 8,
                "total_items": 150,
                "has_next": True,
                "has_previous": False,
                "next_page": 2,
                "previous_page": None,
                "first_page_url": "/api/v1/users?page=1&size=20",
                "last_page_url": "/api/v1/users?page=8&size=20",
                "next_page_url": "/api/v1/users?page=2&size=20",
                "previous_page_url": None,
            }
        }


class PaginatedListResponse(BaseResponse, Generic[T]):
    """Schema para respostas paginadas usando PaginationMeta estruturado.

    Versão mais estruturada do ListResponse com metadados de paginação bem definidos.
    """

    data: List[T] = Field(..., description="Lista de itens da resposta")
    pagination: PaginationMeta = Field(
        ..., description="Metadados estruturados de paginação"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Lista paginada recuperada",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
                "data": [
                    {"id": "item_1", "name": "Item 1"},
                    {"id": "item_2", "name": "Item 2"},
                ],
                "pagination": {
                    "total": 150,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 8,
                    "has_next": True,
                    "has_previous": False,
                    "next_page": 2,
                    "previous_page": None,
                },
            }
        }


class EmptyResponse(BaseResponse):
    """Schema para respostas que não retornam dados.

    Usado para operações como DELETE, ou quando apenas o status da operação é relevante.
    """

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Recurso deletado com sucesso",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class GenericBulkOperationResponse(BaseResponse):
    """Schema genérico para respostas de operações em lote.

    Fornece informações detalhadas sobre sucessos e falhas em operações bulk.
    Use este schema quando precisar de uma resposta bulk genérica.
    Para operações específicas, use os schemas específicos de cada domínio.
    """

    results: Dict[str, Any] = Field(..., description="Resultados da operação em lote")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operação em lote concluída",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
                "results": {
                    "total_processed": 100,
                    "successful": 95,
                    "failed": 5,
                    "errors": [
                        {
                            "item_id": "item_10",
                            "error": "Validation failed",
                            "details": "Email format is invalid",
                        }
                    ],
                    "warnings": [
                        {
                            "item_id": "item_25",
                            "warning": "Duplicate entry",
                            "details": "Item already exists, skipped",
                        }
                    ],
                },
            }
        }


class MetadataResponse(BaseResponse):
    """Schema para respostas que incluem metadados adicionais.

    Usado quando é necessário retornar informações contextuais junto com a resposta.
    """

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais da resposta"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operação com metadados",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {
                    "execution_time_ms": 150,
                    "cache_hit": True,
                    "api_version": "v1.2.0",
                    "rate_limit_remaining": 45,
                },
            }
        }


class HealthCheckResponse(BaseResponse):
    """Schema específico para health checks da API.

    Inclui informações sobre o status dos serviços e dependências.
    """

    services: Dict[str, str] = Field(..., description="Status dos serviços dependentes")
    version: str = Field(..., description="Versão da API", example="1.2.0")
    uptime: str = Field(
        ..., description="Tempo de atividade do serviço", example="2d 14h 30m"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Sistema operacional",
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T12:00:00Z",
                "services": {
                    "database": "healthy",
                    "redis": "healthy",
                    "storage": "healthy",
                    "external_api": "degraded",
                },
                "version": "1.2.0",
                "uptime": "2d 14h 30m",
            }
        }


# ==================== UTILITY FUNCTIONS ====================


def create_data_response(
    data: T,
    message: str = "Success",
    status: str = "success",
    request_id: Optional[str] = None,
) -> DataResponse[T]:
    """
    Create a standardized data response.

    Args:
        data: The data to include in the response
        message: Success message
        status: Response status (default: "success")
        request_id: Optional request ID for tracking

    Returns:
        DataResponse[T]: Standardized data response
    """
    return DataResponse(
        status=status,
        message=message,
        data=data,
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )


def create_list_response(
    items: List[T],
    total: Optional[int] = None,
    pagination: Optional[Dict[str, Any]] = None,
    message: str = "Success",
    status: str = "success",
    request_id: Optional[str] = None,
) -> ListResponse[T]:
    """
    Create a standardized list response.

    Args:
        items: List of items to include
        total: Total count of items (optional)
        pagination: Pagination metadata (optional)
        message: Success message
        status: Response status (default: "success")
        request_id: Optional request ID for tracking

    Returns:
        ListResponse[T]: Standardized list response
    """
    return ListResponse(
        status=status,
        message=message,
        data=items,
        total=total,
        pagination=pagination,
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )


def create_empty_response(
    message: str = "Operation completed successfully",
    status: str = "success",
    request_id: Optional[str] = None,
) -> EmptyResponse:
    """
    Create a standardized empty response for operations that don't return data.

    Args:
        message: Success message
        status: Response status (default: "success")
        request_id: Optional request ID for tracking

    Returns:
        EmptyResponse: Standardized empty response
    """
    return EmptyResponse(
        status=status,
        message=message,
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )


def create_pagination_meta(
    current_page: int, page_size: int, total_items: int, base_url: Optional[str] = None
) -> PaginationMeta:
    """
    Create pagination metadata from common pagination parameters.

    Args:
        current_page: Current page number (1-based)
        page_size: Number of items per page
        total_items: Total number of items
        base_url: Base URL for generating navigation links (optional)

    Returns:
        PaginationMeta: Pagination metadata
    """
    total_pages = (total_items + page_size - 1) // page_size

    return PaginationMeta(
        current_page=current_page,
        page_size=page_size,
        total_pages=total_pages,
        total_items=total_items,
        has_next=current_page < total_pages,
        has_previous=current_page > 1,
        next_page=current_page + 1 if current_page < total_pages else None,
        previous_page=current_page - 1 if current_page > 1 else None,
        first_page_url=f"{base_url}?page=1&size={page_size}" if base_url else None,
        last_page_url=(
            f"{base_url}?page={total_pages}&size={page_size}" if base_url else None
        ),
        next_page_url=(
            f"{base_url}?page={current_page + 1}&size={page_size}"
            if base_url and current_page < total_pages
            else None
        ),
        previous_page_url=(
            f"{base_url}?page={current_page - 1}&size={page_size}"
            if base_url and current_page > 1
            else None
        ),
    )


# ==================== ENDPOINT INTEGRATION HELPERS ====================


def wrap_data_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Wrap existing endpoint data in a standardized response format.

    This helper allows gradual migration of existing endpoints to use
    standardized responses without breaking existing clients.

    Args:
        data: The original response data
        message: Success message

    Returns:
        Dict[str, Any]: Standardized response dictionary
    """
    return {
        "status": "success",
        "message": message,
        "data": data,
        "request_id": None,  # Will be populated by middleware
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def wrap_list_response(
    items: List[Any],
    total: Optional[int] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    message: str = "Success",
) -> Dict[str, Any]:
    """
    Wrap existing endpoint list data in a standardized response format.

    Args:
        items: List of items
        total: Total count (optional)
        page: Current page (optional)
        size: Page size (optional)
        message: Success message

    Returns:
        Dict[str, Any]: Standardized list response dictionary
    """
    response = {
        "status": "success",
        "message": message,
        "data": items,
        "request_id": None,  # Will be populated by middleware
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if total is not None:
        response["total"] = total

    if page is not None and size is not None and total is not None:
        response["pagination"] = create_pagination_meta(page, size, total).__dict__

    return response


def wrap_empty_response(
    message: str = "Operation completed successfully",
) -> Dict[str, Any]:
    """
    Wrap empty responses in a standardized format.

    Args:
        message: Success message

    Returns:
        Dict[str, Any]: Standardized empty response dictionary
    """
    return {
        "status": "success",
        "message": message,
        "request_id": None,  # Will be populated by middleware
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ==================== LEGACY COMPATIBILITY ====================


def convert_legacy_response(
    legacy_data: Any, response_type: str = "data"
) -> Dict[str, Any]:
    """
    Convert legacy response formats to standardized format.

    This function helps maintain backward compatibility while migrating
    to standardized responses.

    Args:
        legacy_data: The legacy response data
        response_type: Type of response ("data", "list", "empty")

    Returns:
        Dict[str, Any]: Standardized response
    """
    if response_type == "list":
        # Handle legacy list responses
        if isinstance(legacy_data, list):
            return wrap_list_response(legacy_data)
        elif isinstance(legacy_data, dict) and "items" in legacy_data:
            return wrap_list_response(
                legacy_data["items"],
                total=legacy_data.get("total"),
                page=legacy_data.get("page"),
                size=legacy_data.get("size"),
            )
    elif response_type == "empty":
        # Handle legacy empty responses
        if isinstance(legacy_data, dict) and "message" in legacy_data:
            return wrap_empty_response(legacy_data["message"])
        return wrap_empty_response()
    else:
        # Handle legacy data responses
        return wrap_data_response(legacy_data)

    return wrap_data_response(legacy_data)


# ==================== FASTAPI INTEGRATION ====================

from fastapi import Request


def add_request_context(
    response_data: Dict[str, Any], request: Request
) -> Dict[str, Any]:
    """
    Add request context (request_id, etc.) to response data.

    This function should be called by middleware or in endpoints to add
    request-specific information to responses.

    Args:
        response_data: The response data dictionary
        request: FastAPI Request object

    Returns:
        Dict[str, Any]: Response data with request context
    """
    # Get request ID from headers (set by middleware)
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        response_data["request_id"] = request_id

    return response_data


def standardize_endpoint_response(endpoint_func: Callable) -> Callable:
    """
    Decorator to automatically standardize endpoint responses.

    This decorator can be applied to endpoint functions to automatically
    wrap their responses in standardized format.

    Args:
        endpoint_func: The endpoint function to wrap

    Returns:
        Callable: Wrapped endpoint function
    """

    async def wrapper(*args, **kwargs):
        # Get the request object from kwargs
        request = None
        for arg in args:
            if hasattr(arg, "url"):  # FastAPI Request object
                request = arg
                break

        # Call the original endpoint
        result = await endpoint_func(*args, **kwargs)

        # If result is already standardized, return as-is
        if isinstance(result, dict) and "status" in result and "timestamp" in result:
            if request:
                return add_request_context(result, request)
            return result

        # Otherwise, wrap in standardized format
        standardized = wrap_data_response(result)
        if request:
            standardized = add_request_context(standardized, request)

        return standardized

    return wrapper
