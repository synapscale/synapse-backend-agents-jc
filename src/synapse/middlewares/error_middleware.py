"""Middleware específico para interceptação e processamento de erros.

Este middleware complementa o sistema de error handlers, fornecendo
interceptação de erros em diferentes camadas da aplicação.
"""

import logging
import time
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from synapse.exceptions import (
    SynapseBaseException,
    DatabaseError,
    WorkspaceError,
    ProjectError,
    AnalyticsError,
    ConversationError,
    AgentError,
    WorkflowError,
    LLMServiceError,
    ConfigurationError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)


class ErrorInterceptionMiddleware:
    """Middleware para interceptação e processamento de erros."""
    
    def __init__(self, app: Callable):
        self.app = app
        self.error_count = 0
        self.start_time = time.time()
    
    async def __call__(self, scope, receive, send):
        """Intercepta requisições e processa erros."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        request_id = getattr(request.state, "request_id", "unknown")
        
        try:
            # Processar requisição normalmente
            await self.app(scope, receive, send)
            
        except SynapseBaseException as exc:
            # Erro customizado do SynapScale - deixar para o handler específico
            logger.info(f"SynapScale exception intercepted: {exc.__class__.__name__}")
            raise
            
        except Exception as exc:
            # Erro não tratado - interceptar e processar
            self.error_count += 1
            
            logger.error(
                f"Unhandled error intercepted by middleware: {exc}",
                extra={
                    "request_id": request_id,
                    "url": str(request.url),
                    "method": request.method,
                    "error_type": exc.__class__.__name__,
                    "error_count": self.error_count,
                    "uptime": time.time() - self.start_time,
                    "traceback": traceback.format_exc(),
                }
            )
            
            # Criar resposta de erro
            error_response = {
                "error": {
                    "type": "UnhandledError",
                    "message": "Erro interno interceptado pelo middleware",
                    "status_code": 500,
                    "request_id": request_id,
                    "timestamp": time.time(),
                    "error_count": self.error_count,
                }
            }
            
            response = JSONResponse(
                status_code=500,
                content=error_response
            )
            
            await response(scope, receive, send)


async def error_tracking_middleware(request: Request, call_next):
    """Middleware para rastreamento de erros por endpoint."""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Log de requisições bem-sucedidas
        process_time = time.time() - start_time
        
        if hasattr(request.state, "request_id"):
            logger.info(
                f"Request completed successfully",
                extra={
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
        
        return response
        
    except SynapseBaseException as exc:
        # Erro customizado - adicionar contexto e repassar
        process_time = time.time() - start_time
        
        logger.warning(
            f"SynapScale exception in endpoint: {exc.__class__.__name__}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "method": request.method,
                "url": str(request.url),
                "error_type": exc.__class__.__name__,
                "process_time": process_time,
            }
        )
        raise
        
    except Exception as exc:
        # Erro não tratado - adicionar contexto e repassar
        process_time = time.time() - start_time
        
        logger.error(
            f"Unhandled exception in endpoint: {exc}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "method": request.method,
                "url": str(request.url),
                "error_type": exc.__class__.__name__,
                "process_time": process_time,
                "traceback": traceback.format_exc(),
            }
        )
        raise


async def endpoint_error_categorizer_middleware(request: Request, call_next):
    """Middleware para categorizar erros por tipo de endpoint."""
    
    # Identificar categoria do endpoint
    path = request.url.path
    endpoint_category = "unknown"
    
    if "/workspaces" in path:
        endpoint_category = "workspaces"
    elif "/projects" in path:
        endpoint_category = "projects"
    elif "/analytics" in path:
        endpoint_category = "analytics"
    elif "/conversations" in path or "/agents" in path:
        endpoint_category = "ai_conversations"
    elif "/workflows" in path:
        endpoint_category = "workflows"
    elif "/llm" in path:
        endpoint_category = "llm_services"
    elif "/auth" in path:
        endpoint_category = "authentication"
    elif "/marketplace" in path:
        endpoint_category = "marketplace"
    
    # Adicionar categoria ao request state
    request.state.endpoint_category = endpoint_category
    
    try:
        response = await call_next(request)
        return response
        
    except Exception as exc:
        # Log específico por categoria
        logger.error(
            f"Error in {endpoint_category} endpoint",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "endpoint_category": endpoint_category,
                "method": request.method,
                "url": str(request.url),
                "error_type": exc.__class__.__name__,
            }
        )
        
        # Transformar erro genérico em erro específico da categoria
        if not isinstance(exc, SynapseBaseException):
            if endpoint_category == "workspaces":
                raise WorkspaceError(f"Erro no workspace: {str(exc)}")
            elif endpoint_category == "projects":
                raise ProjectError(f"Erro no projeto: {str(exc)}")
            elif endpoint_category == "analytics":
                raise AnalyticsError(f"Erro no analytics: {str(exc)}")
            elif endpoint_category == "ai_conversations":
                if "/agents" in path:
                    raise AgentError(f"Erro no agente: {str(exc)}")
                else:
                    raise ConversationError(f"Erro na conversação: {str(exc)}")
            elif endpoint_category == "workflows":
                raise WorkflowError(f"Erro no workflow: {str(exc)}")
            elif endpoint_category == "llm_services":
                raise LLMServiceError(f"Erro no serviço LLM: {str(exc)}")
        
        # Se não conseguiu categorizar, repassar o erro original
        raise


def setup_error_middleware(app):
    """Configura todos os middlewares de erro na aplicação."""
    
    # Middleware de rastreamento de erros
    app.middleware("http")(error_tracking_middleware)
    
    # Middleware de categorização de erros por endpoint
    app.middleware("http")(endpoint_error_categorizer_middleware)
    
    logger.info("Error middleware configurado com sucesso")


# Função para obter estatísticas de erro
def get_error_stats():
    """Retorna estatísticas de erro do middleware."""
    # Esta função poderia ser expandida para incluir métricas reais
    return {
        "error_count": 0,
        "uptime": time.time(),
        "categories": {
            "workspaces": 0,
            "projects": 0,
            "analytics": 0,
            "ai_conversations": 0,
            "workflows": 0,
            "llm_services": 0,
            "authentication": 0,
            "marketplace": 0,
        }
    } 