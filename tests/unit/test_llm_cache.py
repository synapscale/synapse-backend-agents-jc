"""
Testes unitários para o serviço de cache de LLM.

Este módulo contém testes unitários para o serviço de cache,
verificando armazenamento, recuperação e expiração de itens.
"""

import pytest
import time
from unittest.mock import patch

from synapse.core.llm.cache import CacheService


def test_cache_set_get():
    """Testa o armazenamento e recuperação básica do cache."""
    cache = CacheService(default_ttl=60)
    
    # Armazenar um valor
    cache.set("test_key", "test_value")
    
    # Recuperar o valor
    result = cache.get("test_key")
    
    # Verificar o resultado
    assert result == "test_value"


def test_cache_expiration():
    """Testa a expiração de itens do cache."""
    cache = CacheService(default_ttl=1)  # TTL de 1 segundo
    
    # Armazenar um valor
    cache.set("test_key", "test_value")
    
    # Verificar que o valor existe
    assert cache.get("test_key") == "test_value"
    
    # Esperar pela expiração
    time.sleep(1.1)
    
    # Verificar que o valor expirou
    assert cache.get("test_key") is None


def test_cache_custom_ttl():
    """Testa TTL personalizado para itens do cache."""
    cache = CacheService(default_ttl=60)
    
    # Armazenar um valor com TTL personalizado de 1 segundo
    cache.set("test_key", "test_value", ttl=1)
    
    # Verificar que o valor existe
    assert cache.get("test_key") == "test_value"
    
    # Esperar pela expiração
    time.sleep(1.1)
    
    # Verificar que o valor expirou
    assert cache.get("test_key") is None


def test_cache_delete():
    """Testa a remoção de itens do cache."""
    cache = CacheService()
    
    # Armazenar um valor
    cache.set("test_key", "test_value")
    
    # Verificar que o valor existe
    assert cache.get("test_key") == "test_value"
    
    # Remover o valor
    result = cache.delete("test_key")
    
    # Verificar que a remoção foi bem-sucedida
    assert result is True
    
    # Verificar que o valor não existe mais
    assert cache.get("test_key") is None
    
    # Tentar remover um valor inexistente
    result = cache.delete("nonexistent_key")
    
    # Verificar que a remoção falhou
    assert result is False


def test_cache_clear():
    """Testa a limpeza completa do cache."""
    cache = CacheService()
    
    # Armazenar alguns valores
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    # Verificar que os valores existem
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    
    # Limpar o cache
    cache.clear()
    
    # Verificar que os valores não existem mais
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.get("key3") is None


def test_cache_cleanup_expired():
    """Testa a limpeza de itens expirados do cache."""
    cache = CacheService(default_ttl=1)  # TTL de 1 segundo
    
    # Armazenar alguns valores
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    # Esperar pela expiração
    time.sleep(1.1)
    
    # Limpar itens expirados
    removed = cache.cleanup_expired()
    
    # Verificar que 3 itens foram removidos
    assert removed == 3
    
    # Verificar que os valores não existem mais
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.get("key3") is None


def test_cache_complex_keys():
    """Testa o uso de chaves complexas (dicionários, listas) no cache."""
    cache = CacheService()
    
    # Chaves complexas
    dict_key = {"name": "test", "id": 123}
    list_key = ["test", 123, True]
    
    # Armazenar valores com chaves complexas
    cache.set(dict_key, "dict_value")
    cache.set(list_key, "list_value")
    
    # Recuperar os valores
    assert cache.get(dict_key) == "dict_value"
    assert cache.get(list_key) == "list_value"
    
    # Verificar que a ordem das chaves em dicionários não importa
    reordered_dict = {"id": 123, "name": "test"}
    assert cache.get(reordered_dict) == "dict_value"


def test_cache_stats():
    """Testa a obtenção de estatísticas do cache."""
    cache = CacheService(default_ttl=60)
    
    # Cache vazio
    stats = cache.get_stats()
    assert stats["total_items"] == 0
    assert stats["valid_items"] == 0
    assert stats["expired_items"] == 0
    
    # Adicionar alguns itens
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3", ttl=1)  # Item com TTL curto
    
    # Verificar estatísticas
    stats = cache.get_stats()
    assert stats["total_items"] == 3
    assert stats["valid_items"] == 3
    assert stats["expired_items"] == 0
    
    # Esperar pela expiração do item com TTL curto
    time.sleep(1.1)
    
    # Verificar estatísticas novamente
    stats = cache.get_stats()
    assert stats["total_items"] == 3
    assert stats["valid_items"] == 2
    assert stats["expired_items"] == 1
