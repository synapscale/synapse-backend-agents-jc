"""
Testes unitários para o middleware de rate limiting.

Este módulo contém testes unitários para o middleware de rate limiting,
garantindo que a limitação de requisições funcione corretamente.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.synapse.middlewares.rate_limiting import RateLimitingMiddleware, setup_rate_limiting
from src.synapse.config import settings


@pytest.fixture
def mock_app():
    """Mock para aplicação FastAPI."""
    return MagicMock(spec=FastAPI)


@pytest.fixture
def mock_request():
    """Mock para requisição HTTP."""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.url = MagicMock()
    request.url.path = "/api/v1/llm/generate"
    request.method = "POST"
    request.headers = {}
    return request


@pytest.fixture
def mock_response():
    """Mock para resposta HTTP."""
    return MagicMock(spec=Response)


@pytest.fixture
def rate_limiting_middleware():
    """Fixture para o middleware de rate limiting."""
    return RateLimitingMiddleware(
        app=MagicMock(),
        redis_url="redis://localhost:6379/0",
        rate_limit=100,
        rate_limit_window=3600
    )


def test_setup_rate_limiting():
    """Testa a configuração do middleware de rate limiting."""
    # Configurar mock para settings
    with patch("synapse.middlewares.rate_limiting.settings") as mock_settings:
        mock_settings.RATE_LIMIT_ENABLED = True
        mock_settings.REDIS_URL = "redis://localhost:6379/0"
        mock_settings.RATE_LIMIT = 100
        mock_settings.RATE_LIMIT_WINDOW = 3600
        
        # Configurar mock para aplicação
        app = MagicMock(spec=FastAPI)
        
        # Chamar a função
        setup_rate_limiting(app)
        
        # Verificar que o middleware foi adicionado
        app.add_middleware.assert_called_once()
        args, kwargs = app.add_middleware.call_args
        assert args[0] == RateLimitingMiddleware


def test_setup_rate_limiting_disabled():
    """Testa a configuração do middleware de rate limiting quando desabilitado."""
    # Configurar mock para settings
    with patch("synapse.middlewares.rate_limiting.settings") as mock_settings:
        mock_settings.RATE_LIMIT_ENABLED = False
        
        # Configurar mock para aplicação
        app = MagicMock(spec=FastAPI)
        
        # Chamar a função
        setup_rate_limiting(app)
        
        # Verificar que o middleware não foi adicionado
        app.add_middleware.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limiting_middleware_init():
    """Testa a inicialização do middleware de rate limiting."""
    # Criar middleware
    middleware = RateLimitingMiddleware(
        app=MagicMock(),
        redis_url="redis://localhost:6379/0",
        rate_limit=100,
        rate_limit_window=3600
    )
    
    # Verificar atributos
    assert middleware.rate_limit == 100
    assert middleware.rate_limit_window == 3600
    assert middleware.redis_url == "redis://localhost:6379/0"


@pytest.mark.asyncio
async def test_rate_limiting_middleware_dispatch_under_limit(rate_limiting_middleware, mock_request, mock_response):
    """Testa o middleware quando a requisição está abaixo do limite."""
    # Configurar mock para redis
    with patch("synapse.middlewares.rate_limiting.aioredis.from_url") as mock_redis_from_url:
        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=10)  # Abaixo do limite
        mock_redis.expire = AsyncMock()
        mock_redis_from_url.return_value = mock_redis
        
        # Configurar mock para call_next
        call_next = AsyncMock(return_value=mock_response)
        
        # Chamar o método
        result = await rate_limiting_middleware.dispatch(mock_request, call_next)
        
        # Verificar resultado
        assert result == mock_response
        call_next.assert_called_once_with(mock_request)
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limiting_middleware_dispatch_over_limit(rate_limiting_middleware, mock_request):
    """Testa o middleware quando a requisição está acima do limite."""
    # Configurar middleware com limite baixo
    rate_limiting_middleware.rate_limit = 10
    
    # Configurar mock para redis
    with patch("synapse.middlewares.rate_limiting.aioredis.from_url") as mock_redis_from_url:
        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=11)  # Acima do limite
        mock_redis.expire = AsyncMock()
        mock_redis_from_url.return_value = mock_redis
        
        # Configurar mock para call_next
        call_next = AsyncMock()
        
        # Chamar o método e verificar exceção
        with pytest.raises(HTTPException) as excinfo:
            await rate_limiting_middleware.dispatch(mock_request, call_next)
        
        # Verificar código de status da exceção
        assert excinfo.value.status_code == 429
        
        # Verificar que call_next não foi chamado
        call_next.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limiting_middleware_dispatch_with_api_key(rate_limiting_middleware, mock_request, mock_response):
    """Testa o middleware com API key no header."""
    # Configurar request com API key
    mock_request.headers = {"X-API-Key": "test-api-key"}
    
    # Configurar mock para redis
    with patch("synapse.middlewares.rate_limiting.aioredis.from_url") as mock_redis_from_url:
        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=10)
        mock_redis.expire = AsyncMock()
        mock_redis_from_url.return_value = mock_redis
        
        # Configurar mock para call_next
        call_next = AsyncMock(return_value=mock_response)
        
        # Chamar o método
        result = await rate_limiting_middleware.dispatch(mock_request, call_next)
        
        # Verificar resultado
        assert result == mock_response
        call_next.assert_called_once_with(mock_request)
        
        # Verificar que a chave do redis inclui a API key
        args, kwargs = mock_redis.incr.call_args
        assert "test-api-key" in args[0]


@pytest.mark.asyncio
async def test_rate_limiting_middleware_dispatch_with_custom_limits(mock_request, mock_response):
    """Testa o middleware com limites personalizados para diferentes endpoints."""
    # Criar middleware com configurações personalizadas
    middleware = RateLimitingMiddleware(
        app=MagicMock(),
        redis_url="redis://localhost:6379/0",
        rate_limit=100,
        rate_limit_window=3600,
        endpoint_limits={
            "/api/v1/llm/generate": 20,
            "/api/v1/files/upload": 10
        }
    )
    
    # Configurar mock para redis
    with patch("synapse.middlewares.rate_limiting.aioredis.from_url") as mock_redis_from_url:
        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=15)  # Abaixo do limite para generate, acima para upload
        mock_redis.expire = AsyncMock()
        mock_redis_from_url.return_value = mock_redis
        
        # Configurar mock para call_next
        call_next = AsyncMock(return_value=mock_response)
        
        # Testar endpoint de geração (abaixo do limite)
        mock_request.url.path = "/api/v1/llm/generate"
        result = await middleware.dispatch(mock_request, call_next)
        assert result == mock_response
        
        # Testar endpoint de upload (acima do limite)
        mock_request.url.path = "/api/v1/files/upload"
        with pytest.raises(HTTPException) as excinfo:
            await middleware.dispatch(mock_request, call_next)
        assert excinfo.value.status_code == 429
