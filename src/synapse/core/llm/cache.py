"""
Serviço de cache para respostas de LLMs.

Este módulo implementa um sistema de cache para armazenar temporariamente
respostas de LLMs, reduzindo chamadas repetidas às APIs externas.
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, List

from src.synapse.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """
    Serviço de cache para respostas de LLMs.
    
    Este serviço armazena temporariamente respostas de LLMs para reduzir
    chamadas repetidas às APIs externas, economizando tempo e recursos.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Inicializa o serviço de cache com TTL padrão.
        
        Args:
            default_ttl: Tempo de vida padrão em segundos para itens do cache (padrão: 1 hora)
        """
        self.default_ttl = default_ttl
        self._cache = {}
        self._expiry = {}
        logger.info(f"Serviço de cache inicializado com TTL padrão de {default_ttl} segundos")
        
    def _generate_key(self, data: Any) -> str:
        """
        Gera uma chave única para os dados de entrada.
        
        Args:
            data: Dados para gerar a chave (será serializado para JSON)
            
        Returns:
            Chave hash MD5 para os dados
        """
        if isinstance(data, dict):
            # Ordenar as chaves para garantir consistência
            serialized = json.dumps(data, sort_keys=True)
        else:
            serialized = json.dumps(data)
            
        return hashlib.md5(serialized.encode()).hexdigest()
        
    def get(self, key: Any) -> Optional[Any]:
        """
        Recupera um valor do cache se existir e não estiver expirado.
        
        Args:
            key: Chave para buscar no cache (pode ser qualquer objeto serializável)
            
        Returns:
            Valor armazenado ou None se não encontrado ou expirado
        """
        cache_key = self._generate_key(key)
        
        if cache_key not in self._cache:
            logger.debug(f"Cache miss: chave {cache_key[:8]}... não encontrada")
            return None
            
        if time.time() > self._expiry.get(cache_key, 0):
            logger.debug(f"Cache miss: chave {cache_key[:8]}... expirada")
            self.delete(key)
            return None
            
        logger.debug(f"Cache hit: chave {cache_key[:8]}...")
        return self._cache[cache_key]
        
    def set(self, key: Any, value: Any, ttl: Optional[int] = None) -> None:
        """
        Armazena um valor no cache com tempo de vida especificado.
        
        Args:
            key: Chave para armazenar o valor (pode ser qualquer objeto serializável)
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (usa o padrão se não especificado)
        """
        cache_key = self._generate_key(key)
        self._cache[cache_key] = value
        self._expiry[cache_key] = time.time() + (ttl or self.default_ttl)
        logger.debug(f"Cache set: chave {cache_key[:8]}... armazenada com TTL de {ttl or self.default_ttl} segundos")
        
    def delete(self, key: Any) -> bool:
        """
        Remove um valor do cache.
        
        Args:
            key: Chave a ser removida
            
        Returns:
            True se a chave foi removida, False se não existia
        """
        cache_key = self._generate_key(key)
        
        if cache_key in self._cache:
            del self._cache[cache_key]
            if cache_key in self._expiry:
                del self._expiry[cache_key]
            logger.debug(f"Cache delete: chave {cache_key[:8]}... removida")
            return True
            
        return False
        
    def clear(self) -> None:
        """
        Limpa todo o cache.
        """
        count = len(self._cache)
        self._cache.clear()
        self._expiry.clear()
        logger.info(f"Cache limpo: {count} itens removidos")
        
    def cleanup_expired(self) -> int:
        """
        Remove todos os itens expirados do cache.
        
        Returns:
            Número de itens removidos
        """
        now = time.time()
        expired_keys = [k for k, exp in self._expiry.items() if exp <= now]
        
        for key in expired_keys:
            if key in self._cache:
                del self._cache[key]
            del self._expiry[key]
            
        logger.info(f"Cache cleanup: {len(expired_keys)} itens expirados removidos")
        return len(expired_keys)
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o cache.
        
        Returns:
            Dicionário com estatísticas do cache
        """
        now = time.time()
        total_items = len(self._cache)
        expired_items = sum(1 for exp in self._expiry.values() if exp <= now)
        valid_items = total_items - expired_items
        
        # Calcular TTL médio restante para itens válidos
        avg_ttl_remaining = 0
        if valid_items > 0:
            valid_ttls = [exp - now for exp in self._expiry.values() if exp > now]
            avg_ttl_remaining = sum(valid_ttls) / len(valid_ttls)
            
        return {
            "total_items": total_items,
            "valid_items": valid_items,
            "expired_items": expired_items,
            "avg_ttl_remaining": avg_ttl_remaining
        }
