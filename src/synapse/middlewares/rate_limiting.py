"""
Middleware de Rate Limiting para APIs
"""

import functools
from collections.abc import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List
import time


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware de Rate Limiting para FastAPI
    """
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_log: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Por enquanto apenas um passthrough
        # TODO: Implementar lógica de rate limiting real
        response = await call_next(request)
        return response


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Decorator básico para rate limiting.
    Por enquanto apenas um placeholder que não faz nada.

    Args:
        max_requests: Número máximo de requisições por janela
        window_seconds: Tamanho da janela em segundos
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
