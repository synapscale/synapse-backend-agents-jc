"""Middleware para limitação de taxa (rate limiting).

Este módulo implementa o middleware de rate limiting para proteger
a API contra abusos, utilizando Redis para armazenamento distribuído.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple

import redis
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from src.synapse.config import settings
from src.synapse.core.auth.jwt import get_current_user
from src.synapse.exceptions import rate_limit_exception

# Logger
logger = logging.getLogger(__name__)


class RateLimiter:
    """Implementação de limitação de taxa usando Redis."""

    def __init__(
        self,
        redis_url: str = settings.REDIS_URL,
        default_limit: int = settings.RATE_LIMIT,
        default_window: int = settings.RATE_LIMIT_WINDOW,
    ):
        """Inicializa o limitador de taxa.

        Args:
            redis_url: URL de conexão com o Redis
            default_limit: Limite padrão de requisições
            default_window: Janela de tempo padrão em segundos
        """
        self.redis_url = redis_url
        self.default_limit = default_limit
        self.default_window = default_window
        self._redis_client = None

    @property
    def redis_client(self) -> redis.Redis:
        """Obtém cliente Redis, inicializando se necessário.

        Returns:
            Cliente Redis ou implementação em memória
        """
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.redis_url)
                # Testar conexão
                self._redis_client.ping()
                logger.info("Conexão com Redis estabelecida para rate limiting")
            except (redis.ConnectionError, redis.RedisError) as e:
                # Fallback para implementação em memória se Redis não estiver disponível
                logger.warning(
                    f"Não foi possível conectar ao Redis ({str(e)}). "
                    "Usando implementação em memória para rate limiting."
                )
                self._redis_client = InMemoryRateLimiter()
        return self._redis_client

    async def is_rate_limited(
        self, key: str, limit: Optional[int] = None, window: Optional[int] = None
    ) -> Tuple[bool, Dict[str, int]]:
        """Verifica se uma chave está limitada por taxa.

        Args:
            key: Chave única para identificar o cliente
            limit: Limite de requisições (opcional)
            window: Janela de tempo em segundos (opcional)

        Returns:
            Tupla com (está_limitado, info_limite)
        """
        limit = limit or self.default_limit
        window = window or self.default_window

        # Chave Redis para este limitador específico
        redis_key = f"rate_limit:{key}:{window}"

        try:
            # Incrementar contador
            current = self.redis_client.incr(redis_key)

            # Definir TTL na primeira requisição
            if current == 1:
                self.redis_client.expire(redis_key, window)

            # Obter TTL restante
            ttl = self.redis_client.ttl(redis_key)

            # Verificar se excedeu o limite
            is_limited = current > limit

            # Registrar no log se estiver limitado
            if is_limited:
                logger.warning(
                    f"Rate limit excedido para chave {key}: {current}/{limit}"
                )

            return is_limited, {
                "total": limit,
                "remaining": max(0, limit - current),
                "reset": ttl,
                "used": current,
            }
        except Exception as e:
            # Em caso de erro, permitir a requisição
            logger.error(f"Erro ao verificar rate limit: {str(e)}")
            return False, {
                "total": limit,
                "remaining": limit,
                "reset": window,
                "used": 0,
            }


class InMemoryRateLimiter:
    """Implementação em memória para rate limiting quando Redis não está disponível."""

    def __init__(self):
        """Inicializa o limitador em memória."""
        self.limits = {}
        logger.info("Inicializando limitador de taxa em memória")

    def incr(self, key: str) -> int:
        """Incrementa o contador para uma chave.

        Args:
            key: Chave única

        Returns:
            Valor atual do contador
        """
        now = datetime.now()
        if key not in self.limits:
            self.limits[key] = {"count": 0, "reset_at": now + timedelta(seconds=3600)}

        self.limits[key]["count"] += 1
        return self.limits[key]["count"]

    def expire(self, key: str, seconds: int) -> bool:
        """Define o tempo de expiração para uma chave.

        Args:
            key: Chave única
            seconds: Tempo de expiração em segundos

        Returns:
            True se a operação foi bem-sucedida
        """
        if key in self.limits:
            self.limits[key]["reset_at"] = datetime.now() + timedelta(seconds=seconds)
        return True

    def ttl(self, key: str) -> int:
        """Retorna o tempo restante para expiração.

        Args:
            key: Chave única

        Returns:
            Tempo restante em segundos ou -2 se a chave não existir
        """
        if key not in self.limits:
            return -2

        remaining = (self.limits[key]["reset_at"] - datetime.now()).total_seconds()
        if remaining <= 0:
            del self.limits[key]
            return -2

        return int(remaining)

    def ping(self) -> bool:
        """Simula ping do Redis.

        Returns:
            Sempre True
        """
        return True


# Instância global do rate limiter
rate_limiter = RateLimiter()


def rate_limit(limit: Optional[int] = None, window: Optional[int] = None):
    """Dependência para aplicar rate limiting em endpoints.

    Args:
        limit: Limite de requisições por janela de tempo
        window: Janela de tempo em segundos

    Returns:
        Função de dependência para FastAPI
    """

    async def _rate_limit(
        request: Request, current_user: Dict = Depends(get_current_user)
    ):
        # Usar ID do usuário como chave para rate limiting
        key = f"user:{current_user['id']}"

        # Verificar limite
        is_limited, info = await rate_limiter.is_rate_limited(key, limit, window)

        # Adicionar headers de rate limit
        request.state.rate_limit_info = info

        if is_limited:
            raise rate_limit_exception(
                "Limite de requisições excedido. Tente novamente mais tarde.",
                info["reset"],
            )

        return current_user

    return _rate_limit


def setup_rate_limiting(app: FastAPI) -> None:
    """Configura o middleware de rate limiting na aplicação.

    Args:
        app: Aplicação FastAPI
    """

    @app.middleware("http")
    async def add_rate_limit_headers(request: Request, call_next: Callable) -> Response:
        """Middleware para adicionar headers de rate limit às respostas.

        Args:
            request: Requisição HTTP
            call_next: Próxima função na cadeia de middlewares

        Returns:
            Resposta HTTP
        """
        # Processar a requisição
        response = await call_next(request)

        # Adicionar headers de rate limit se disponíveis
        if hasattr(request.state, "rate_limit_info"):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(info["total"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])

        return response

    logger.info("Middleware de rate limiting configurado")
