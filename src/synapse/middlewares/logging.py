"""Middleware para logging estruturado de requisições.

Este middleware captura informações detalhadas de cada requisição HTTP
para análise e monitoramento da aplicação.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware para logging estruturado de requisições HTTP."""
    
    def __init__(self, app: Callable):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        """Processa requisições com logging estruturado."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        start_time = time.time()
        
        # Gerar request ID se não existir
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Log inicial da requisição
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "user_agent": request.headers.get("user-agent"),
                "client_host": getattr(request.client, "host", None),
            }
        )
        
        # Processar requisição
        try:
            await self.app(scope, receive, send)
            
            # Log de sucesso (não podemos acessar status_code aqui)
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "process_time": process_time,
                }
            )
            
        except Exception as exc:
            # Log de erro
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {exc}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "process_time": process_time,
                    "error_type": exc.__class__.__name__,
                }
            )
            raise


async def request_logging_middleware(request: Request, call_next):
    """Middleware function para logging de requisições."""
    start_time = time.time()
    
    # Gerar ou obter request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    # Log inicial
    logger.info(
        "Processing request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent"),
            "client_host": getattr(request.client, "host", None),
        }
    )
    
    try:
        # Processar requisição
        response = await call_next(request)
        
        # Log de sucesso com informações da resposta
        process_time = time.time() - start_time
        logger.info(
            "Request completed successfully",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )
        
        # Adicionar headers de resposta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as exc:
        # Log de erro
        process_time = time.time() - start_time
        logger.error(
            f"Request failed with exception: {exc}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "process_time": process_time,
                "error_type": exc.__class__.__name__,
            }
        )
        
        # Re-raise para que o error handler processe
        raise 