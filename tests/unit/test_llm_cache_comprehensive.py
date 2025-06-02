"""
Testes unitários para o módulo de cache de LLM.

Este módulo contém testes unitários para o serviço de cache de LLM,
garantindo que o armazenamento e recuperação de respostas funcionem corretamente.
"""

import pytest
import json
import hashlib
from unittest.mock import patch, MagicMock, AsyncMock
import time

from src.synapse.core.llm.cache import CacheService


@pytest.fixture
def cache_service():
    """Fixture para o serviço de cache."""
    return CacheService(default_ttl=60)


def test_cache_service_init():
    """Testa a inicialização do serviço de cache."""
    # Testar com TTL padrão
    cache = CacheService()
    assert cache.default_ttl == 3600  # 1 hora
    
    # Testar com TTL personalizado
    cache = CacheService(default_ttl=120)
    assert cache.default_ttl == 120


def test_generate_cache_key():
    """Testa a geração de chaves de cache."""
    cache = CacheService()
    
    # Testar com prompt simples
    key1 = cache._generate_cache_key(
        prompt="Teste",
        provider="claude",
        model="claude-3-sonnet"
    )
    
    # Verificar formato da chave (hash SHA-256)
    assert len(key1) == 64  # SHA-256 produz 64 caracteres hexadecimais
    
    # Testar com prompt diferente
    key2 = cache._generate_cache_key(
        prompt="Outro teste",
        provider="claude",
        model="claude-3-sonnet"
    )
    
    # Verificar que chaves diferentes são geradas para prompts diferentes
    assert key1 != key2
    
    # Testar com mesmo prompt mas provedor diferente
    key3 = cache._generate_cache_key(
        prompt="Teste",
        provider="gemini",
        model="claude-3-sonnet"
    )
    
    # Verificar que chaves diferentes são geradas para provedores diferentes
    assert key1 != key3
    
    # Testar com mesmo prompt e provedor mas modelo diferente
    key4 = cache._generate_cache_key(
        prompt="Teste",
        provider="claude",
        model="claude-3-opus"
    )
    
    # Verificar que chaves diferentes são geradas para modelos diferentes
    assert key1 != key4


@pytest.mark.asyncio
async def test_get_cached_response_miss(cache_service):
    """Testa a recuperação de resposta não existente no cache."""
    # Tentar recuperar uma resposta que não existe no cache
    result = await cache_service.get_cached_response(
        prompt="Teste não existente",
        provider="claude",
        model="claude-3-sonnet"
    )
    
    # Verificar que o resultado é None
    assert result is None


@pytest.mark.asyncio
async def test_cache_and_retrieve_response(cache_service):
    """Testa o armazenamento e recuperação de resposta no cache."""
    # Dados para teste
    prompt = "Teste de cache"
    provider = "claude"
    model = "claude-3-sonnet"
    response = "Esta é uma resposta de teste para o cache"
    
    # Armazenar resposta no cache
    await cache_service.cache_response(
        prompt=prompt,
        provider=provider,
        model=model,
        response=response
    )
    
    # Recuperar resposta do cache
    cached = await cache_service.get_cached_response(
        prompt=prompt,
        provider=provider,
        model=model
    )
    
    # Verificar que a resposta foi recuperada corretamente
    assert cached == response


@pytest.mark.asyncio
async def test_cache_ttl_expiration(cache_service):
    """Testa a expiração do cache baseada no TTL."""
    # Configurar cache com TTL muito curto para teste
    cache_service = CacheService(default_ttl=1)  # 1 segundo
    
    # Dados para teste
    prompt = "Teste de expiração"
    provider = "claude"
    model = "claude-3-sonnet"
    response = "Esta resposta deve expirar rapidamente"
    
    # Armazenar resposta no cache
    await cache_service.cache_response(
        prompt=prompt,
        provider=provider,
        model=model,
        response=response
    )
    
    # Verificar que a resposta está no cache imediatamente
    cached = await cache_service.get_cached_response(
        prompt=prompt,
        provider=provider,
        model=model
    )
    assert cached == response
    
    # Esperar pelo TTL expirar
    time.sleep(1.5)  # Esperar mais que o TTL
    
    # Verificar que a resposta não está mais no cache
    cached = await cache_service.get_cached_response(
        prompt=prompt,
        provider=provider,
        model=model
    )
    assert cached is None


@pytest.mark.asyncio
async def test_cache_with_custom_ttl(cache_service):
    """Testa o armazenamento com TTL personalizado."""
    # Dados para teste
    prompt = "Teste de TTL personalizado"
    provider = "claude"
    model = "claude-3-sonnet"
    response = "Esta resposta tem TTL personalizado"
    
    # Armazenar resposta no cache com TTL personalizado
    await cache_service.cache_response(
        prompt=prompt,
        provider=provider,
        model=model,
        response=response,
        ttl=2  # 2 segundos
    )
    
    # Verificar que a resposta está no cache imediatamente
    cached = await cache_service.get_cached_response(
        prompt=prompt,
        provider=provider,
        model=model
    )
    assert cached == response
    
    # Esperar menos que o TTL personalizado
    time.sleep(1)
    
    # Verificar que a resposta ainda está no cache
    cached = await cache_service.get_cached_response(
        prompt=prompt,
        provider=provider,
        model=model
    )
    assert cached == response
    
    # Esperar pelo TTL personalizado expirar
    time.sleep(1.5)  # Total: 2.5 segundos
    
    # Verificar que a resposta não está mais no cache
    cached = await cache_service.get_cached_response(
        prompt=prompt,
        provider=provider,
        model=model
    )
    assert cached is None


@pytest.mark.asyncio
async def test_clear_cache(cache_service):
    """Testa a limpeza do cache."""
    # Armazenar múltiplas respostas no cache
    await cache_service.cache_response(
        prompt="Teste 1",
        provider="claude",
        model="claude-3-sonnet",
        response="Resposta 1"
    )
    
    await cache_service.cache_response(
        prompt="Teste 2",
        provider="gemini",
        model="gemini-1.5-pro",
        response="Resposta 2"
    )
    
    # Verificar que as respostas estão no cache
    cached1 = await cache_service.get_cached_response(
        prompt="Teste 1",
        provider="claude",
        model="claude-3-sonnet"
    )
    assert cached1 == "Resposta 1"
    
    cached2 = await cache_service.get_cached_response(
        prompt="Teste 2",
        provider="gemini",
        model="gemini-1.5-pro"
    )
    assert cached2 == "Resposta 2"
    
    # Limpar o cache
    cache_service.clear_cache()
    
    # Verificar que as respostas não estão mais no cache
    cached1 = await cache_service.get_cached_response(
        prompt="Teste 1",
        provider="claude",
        model="claude-3-sonnet"
    )
    assert cached1 is None
    
    cached2 = await cache_service.get_cached_response(
        prompt="Teste 2",
        provider="gemini",
        model="gemini-1.5-pro"
    )
    assert cached2 is None
