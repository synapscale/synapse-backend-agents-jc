"""Sistema global de tratamento de erros para SynapScale.

Este módulo implementa handlers globais para capturar e tratar exceções
de forma consistente em toda a aplicação FastAPI.
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    SynapseBaseException,
    DatabaseError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    WorkspaceError,
    ProjectError,
    AnalyticsError,
    ConversationError,
    AgentError,
    WorkflowError,
    LLMServiceError,
    ConfigurationError,
    ServiceUnavailableError,
    RateLimitError,
    StorageError,
    FileValidationError,
    ServiceError,
)
from .schemas.error import ErrorResponse, ErrorDetail

# Configuração do logger
logger = logging.getLogger(__name__)


def get_request_info(request: Request) -> Dict[str, Any]:
    """Extrai informações relevantes da requisição para logging.

    Args:
        request: Requisição FastAPI

    Returns:
        Dict com informações da requisição
    """
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_host": getattr(request.client, "host", None),
        "user_agent": request.headers.get("user-agent"),
    }


def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    error_code: Optional[str] = None,
    details: Any = None,
    request: Optional[Request] = None,
) -> JSONResponse:
    """Cria uma resposta de erro padronizada.

    Args:
        status_code: Código de status HTTP
        error_type: Tipo do erro (ex: "ValidationError")
        message: Mensagem de erro amigável
        error_code: Código de erro opcional (ex: "AUTH_001")
        details: Detalhes adicionais opcionais
        request: Requisição FastAPI opcional

    Returns:
        JSONResponse formatada
    """
    request_id = str(uuid.uuid4())

    # Criar o objeto de erro estruturado
    error_data = {
        "type": error_type,
        "message": message,
        "status_code": status_code,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Adicionar campos opcionais
    if error_code:
        error_data["code"] = error_code
    if details is not None:
        error_data["details"] = details
    if request:
        error_data["path"] = request.url.path
        error_data["method"] = request.method

    headers = {"X-Request-ID": request_id}

    return JSONResponse(
        status_code=status_code,
        content=error_data,
        headers=headers,
    )


async def synapse_exception_handler(
    request: Request, exc: SynapseBaseException
) -> JSONResponse:
    """Handler para exceções customizadas do SynapScale.

    Args:
        request: Requisição FastAPI
        exc: Exceção SynapseBaseException capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    # Mapeamento de exceções para códigos HTTP
    status_map = {
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ValidationError: status.HTTP_400_BAD_REQUEST,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
        StorageError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    }

    status_code = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Log estruturado
    log_level = logging.WARNING if status_code < 500 else logging.ERROR
    logger.log(
        log_level,
        f"SynapScale Exception: {exc.__class__.__name__}: {exc.message}",
        extra={
            **request_info,
            "error_type": exc.__class__.__name__,
            "error_code": exc.error_code,
            "status_code": status_code,
            "details": exc.details,
        },
    )

    return create_error_response(
        status_code=status_code,
        error_type=exc.__class__.__name__,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        request=request,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler para HTTPException do FastAPI.

    Args:
        request: Requisição FastAPI
        exc: Exceção HTTPException capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            **request_info,
            "error_type": "HTTPException",
            "status_code": exc.status_code,
        },
    )

    return create_error_response(
        status_code=exc.status_code,
        error_type="HTTPException",
        message=str(exc.detail),
        request=request,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler para erros de validação do FastAPI.

    Args:
        request: Requisição FastAPI
        exc: Exceção RequestValidationError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    # Extrair detalhes dos erros de validação
    validation_details = []
    for error in exc.errors():
        detail = ErrorDetail(
            field=".".join(str(x) for x in error.get("loc", [])),
            code=error.get("type"),
            message=error.get("msg", "Erro de validação"),
        )
        validation_details.append(detail.dict())

    logger.warning(
        f"Validation Error: {len(exc.errors())} validation errors",
        extra={
            **request_info,
            "error_type": "ValidationError",
            "validation_errors": validation_details,
        },
    )

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_type="ValidationError",
        message="Dados de entrada inválidos",
        error_code="VALIDATION_ERROR",
        details=validation_details,
        request=request,
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handler para erros de validação do Pydantic.

    Args:
        request: Requisição FastAPI
        exc: Exceção PydanticValidationError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    # Extrair detalhes dos erros do Pydantic
    validation_details = []
    for error in exc.errors():
        detail = ErrorDetail(
            field=".".join(str(x) for x in error.get("loc", [])),
            code=error.get("type"),
            message=error.get("msg", "Erro de validação"),
        )
        validation_details.append(detail.dict())

    logger.warning(
        f"Pydantic Validation Error: {len(exc.errors())} validation errors",
        extra={
            **request_info,
            "error_type": "PydanticValidationError",
            "validation_errors": validation_details,
        },
    )

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_type="PydanticValidationError",
        message="Erro de validação de dados",
        error_code="PYDANTIC_VALIDATION_ERROR",
        details=validation_details,
        request=request,
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handler para erros do SQLAlchemy.

    Args:
        request: Requisição FastAPI
        exc: Exceção SQLAlchemyError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.error(
        f"Database Error: {str(exc)}",
        extra={
            **request_info,
            "error_type": "SQLAlchemyError",
            "exception_class": exc.__class__.__name__,
        },
    )

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="DatabaseError",
        message="Erro interno do banco de dados",
        error_code="DB_ERROR",
        request=request,
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handler específico para ValueError.

    Args:
        request: Requisição FastAPI
        exc: Exceção ValueError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.warning(
        f"Value Error: {str(exc)}",
        extra={
            **request_info,
            "error_type": "ValueError",
        },
    )

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_type="ValueError",
        message="Valor inválido fornecido",
        error_code="INVALID_VALUE",
        details=str(exc),
        request=request,
    )


async def type_error_handler(request: Request, exc: TypeError) -> JSONResponse:
    """Handler específico para TypeError.

    Args:
        request: Requisição FastAPI
        exc: Exceção TypeError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.warning(
        f"Type Error: {str(exc)}",
        extra={
            **request_info,
            "error_type": "TypeError",
        },
    )

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_type="TypeError",
        message="Tipo de dado inválido",
        error_code="INVALID_TYPE",
        details=str(exc),
        request=request,
    )


async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
    """Handler específico para KeyError.

    Args:
        request: Requisição FastAPI
        exc: Exceção KeyError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.warning(
        f"Key Error: {str(exc)}",
        extra={
            **request_info,
            "error_type": "KeyError",
        },
    )

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_type="KeyError",
        message="Chave obrigatória não encontrada",
        error_code="MISSING_KEY",
        details=str(exc),
        request=request,
    )


async def attribute_error_handler(
    request: Request, exc: AttributeError
) -> JSONResponse:
    """Handler específico para AttributeError.

    Args:
        request: Requisição FastAPI
        exc: Exceção AttributeError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.warning(
        f"Attribute Error: {str(exc)}",
        extra={
            **request_info,
            "error_type": "AttributeError",
        },
    )

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="AttributeError",
        message="Erro interno de atributo",
        error_code="ATTRIBUTE_ERROR",
        details=str(exc),
        request=request,
    )


async def not_implemented_error_handler(
    request: Request, exc: NotImplementedError
) -> JSONResponse:
    """Handler específico para NotImplementedError.

    Args:
        request: Requisição FastAPI
        exc: Exceção NotImplementedError capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    logger.error(
        f"Not Implemented Error: {str(exc)}",
        extra={
            **request_info,
            "error_type": "NotImplementedError",
        },
    )

    return create_error_response(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        error_type="NotImplementedError",
        message="Funcionalidade não implementada",
        error_code="NOT_IMPLEMENTED",
        details=str(exc),
        request=request,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler genérico para qualquer exceção não capturada.

    Args:
        request: Requisição FastAPI
        exc: Exceção genérica capturada

    Returns:
        JSONResponse com erro formatado
    """
    request_info = get_request_info(request)

    # Log completo do erro incluindo traceback
    logger.error(
        f"Unhandled Exception: {exc.__class__.__name__}: {str(exc)}",
        extra={
            **request_info,
            "error_type": exc.__class__.__name__,
            "traceback": traceback.format_exc(),
        },
    )

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="InternalServerError",
        message="Erro interno do servidor",
        error_code="INTERNAL_ERROR",
        request=request,
    )


def setup_error_handlers(app: FastAPI):
    """Configura os handlers de erro globais para a aplicação FastAPI.

    Args:
        app: Instância da aplicação FastAPI
    """
    # Handlers para exceções customizadas do SynapScale
    app.add_exception_handler(SynapseBaseException, synapse_exception_handler)

    # Handlers para exceções do FastAPI
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Handlers para exceções do Pydantic
    app.add_exception_handler(
        PydanticValidationError, pydantic_validation_exception_handler
    )

    # Handlers para exceções do SQLAlchemy
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

    # Handlers para exceções Python nativas
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(TypeError, type_error_handler)
    app.add_exception_handler(KeyError, key_error_handler)
    app.add_exception_handler(AttributeError, attribute_error_handler)
    app.add_exception_handler(NotImplementedError, not_implemented_error_handler)

    # Handler genérico (deve ser o último)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Global error handlers configured successfully")


async def add_request_id_middleware(request: Request, call_next):
    """Middleware para adicionar request ID único a cada requisição.

    Args:
        request: Requisição FastAPI
        call_next: Próximo middleware/handler na cadeia

    Returns:
        Response com header X-Request-ID
    """
    # Gerar ou usar request ID existente
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    # Processar requisição
    response = await call_next(request)

    # Adicionar request ID ao header de resposta
    response.headers["X-Request-ID"] = request_id

    return response
