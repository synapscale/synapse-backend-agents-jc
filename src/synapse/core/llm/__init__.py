"""
Módulo de integração com Modelos de Linguagem de Grande Escala (LLMs).

Este módulo fornece uma interface unificada para interagir com diversos
provedores de LLMs como Claude, Gemini, Grok e DeepSeek.
"""

from synapse.core.llm.base import BaseLLMConnector
from synapse.core.llm.factory import LLMFactory
from synapse.core.llm.cache import CacheService
from synapse.core.llm.unified import UnifiedLLMService

# Inicialização do serviço unificado
from synapse.config import settings

# Singleton para uso em toda a aplicação
factory = LLMFactory(settings)
cache_service = CacheService(default_ttl=settings.LLM_CACHE_TTL)
unified_service = UnifiedLLMService(factory, cache_service)

__all__ = [
    "BaseLLMConnector",
    "LLMFactory",
    "CacheService",
    "UnifiedLLMService",
    "unified_service",
]
