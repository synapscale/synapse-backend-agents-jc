"""
Middleware de Rate Limiting para APIs
"""
import functools
from typing import Callable
from fastapi import HTTPException, status


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
            # Por enquanto apenas passa através sem fazer rate limiting
            # Em produção, implementar logica real de rate limiting
            return await func(*args, **kwargs)
        return wrapper
    return decorator
