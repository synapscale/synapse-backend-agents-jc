"""Schemas para respostas de erro padronizadas do SynapScale.

Este módulo define os schemas Pydantic para padronizar as respostas de erro
em toda a API, garantindo consistência e facilidade de consumo pelos clientes.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """Schema para detalhes específicos de um erro.

    Usado para fornecer informações adicionais sobre o erro,
    como validações que falharam, contexto específico, etc.
    """

    field: Optional[str] = Field(
        None, description="Campo específico relacionado ao erro"
    )
    code: Optional[str] = Field(None, description="Código específico do detalhe")
    message: str = Field(..., description="Mensagem descritiva do detalhe")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional do erro"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "code": "INVALID_FORMAT",
                "message": "O formato do email é inválido",
                "context": {"provided_value": "invalid-email"},
            }
        }


class ErrorResponse(BaseModel):
    """Schema padronizado para todas as respostas de erro da API.

    Este schema garante que todas as respostas de erro sigam o mesmo formato,
    facilitando o tratamento pelos clientes e debugging pelos desenvolvedores.
    """

    error: Dict[str, Any] = Field(
        ..., description="Objeto contendo informações do erro"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "ValidationError",
                    "code": "VALIDATION_001",
                    "message": "Os dados fornecidos são inválidos",
                    "status_code": 422,
                    "details": [
                        {
                            "field": "email",
                            "code": "INVALID_FORMAT",
                            "message": "O formato do email é inválido",
                            "context": {"provided_value": "invalid-email"},
                        }
                    ],
                    "request_id": "req_123456789",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "path": "/api/v1/users",
                    "method": "POST",
                }
            }
        }


class StandardErrorResponse(BaseModel):
    """Schema simplificado para erros comuns.

    Versão mais simples do ErrorResponse para casos onde não há
    necessidade de detalhes complexos.
    """

    error: Dict[str, Any] = Field(..., description="Informações básicas do erro")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "NotFoundError",
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "O recurso solicitado não foi encontrado",
                    "status_code": 404,
                    "request_id": "req_123456789",
                }
            }
        }


class ValidationErrorResponse(BaseModel):
    """Schema específico para erros de validação.

    Especialização do ErrorResponse para erros de validação,
    com estrutura otimizada para mostrar múltiplos campos com erro.
    """

    error: Dict[str, Any] = Field(..., description="Detalhes do erro de validação")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "ValidationError",
                    "code": "VALIDATION_FAILED",
                    "message": "Falha na validação dos dados",
                    "status_code": 422,
                    "details": [
                        {
                            "field": "email",
                            "code": "REQUIRED",
                            "message": "Este campo é obrigatório",
                        },
                        {
                            "field": "password",
                            "code": "MIN_LENGTH",
                            "message": "A senha deve ter pelo menos 8 caracteres",
                        },
                    ],
                    "request_id": "req_123456789",
                }
            }
        }


class DatabaseErrorResponse(BaseModel):
    """Schema específico para erros de banco de dados.

    Especialização do ErrorResponse para erros relacionados ao banco de dados,
    evitando exposição de detalhes sensíveis em produção.
    """

    error: Dict[str, Any] = Field(
        ..., description="Informações do erro de banco de dados"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "DatabaseError",
                    "code": "DB_CONNECTION_FAILED",
                    "message": "Erro interno do banco de dados",
                    "status_code": 500,
                    "request_id": "req_123456789",
                }
            }
        }


class AuthenticationErrorResponse(BaseModel):
    """Schema específico para erros de autenticação.

    Especialização do ErrorResponse para erros de autenticação,
    com informações relevantes para problemas de login/token.
    """

    error: Dict[str, Any] = Field(..., description="Detalhes do erro de autenticação")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_CREDENTIALS",
                    "message": "Credenciais inválidas",
                    "status_code": 401,
                    "details": {
                        "reason": "Token expirado",
                        "expires_at": "2024-01-01T12:00:00Z",
                    },
                    "request_id": "req_123456789",
                }
            }
        }


class AuthorizationErrorResponse(BaseModel):
    """Schema específico para erros de autorização.

    Especialização do ErrorResponse para erros de permissão,
    com informações sobre recursos e permissões necessárias.
    """

    error: Dict[str, Any] = Field(..., description="Detalhes do erro de autorização")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "AuthorizationError",
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Permissões insuficientes para acessar este recurso",
                    "status_code": 403,
                    "details": {
                        "required_permission": "workspace:admin",
                        "user_permissions": ["workspace:read", "workspace:write"],
                        "resource": "/api/v1/workspaces/123/settings",
                    },
                    "request_id": "req_123456789",
                }
            }
        }


class RateLimitErrorResponse(BaseModel):
    """Schema específico para erros de rate limiting.

    Especialização do ErrorResponse para erros de limite de taxa,
    com informações sobre limites e tempo de reset.
    """

    error: Dict[str, Any] = Field(..., description="Detalhes do erro de rate limit")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "RateLimitError",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Limite de requisições excedido",
                    "status_code": 429,
                    "details": {
                        "limit": 100,
                        "window": "60s",
                        "reset_at": "2024-01-01T12:01:00Z",
                        "retry_after": 45,
                    },
                    "request_id": "req_123456789",
                }
            }
        }


class NotFoundErrorResponse(BaseModel):
    """Schema para resposta de erro 404 - Não encontrado"""

    message: str = Field(
        default="Recurso não encontrado", description="Mensagem de erro"
    )
    error_code: str = Field(default="NOT_FOUND", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp do erro"
    )


class ConflictErrorResponse(BaseModel):
    """Schema para resposta de erro 409 - Conflito"""

    message: str = Field(default="Conflito de recursos", description="Mensagem de erro")
    error_code: str = Field(default="CONFLICT", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp do erro"
    )


class InternalServerErrorResponse(BaseModel):
    """Schema para resposta de erro 500 - Erro interno do servidor"""

    message: str = Field(
        default="Erro interno do servidor", description="Mensagem de erro"
    )
    error_code: str = Field(
        default="INTERNAL_SERVER_ERROR", description="Código do erro"
    )
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp do erro"
    )


class BadGatewayErrorResponse(BaseModel):
    """Schema para resposta de erro 502 - Bad Gateway"""

    message: str = Field(default="Gateway inválido", description="Mensagem de erro")
    error_code: str = Field(default="BAD_GATEWAY", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp do erro"
    )
