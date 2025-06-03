"""
Sistema de Cache Avançado para SynapScale
Implementação robusta com Redis e cache em memória
"""

import asyncio
import json
import pickle
import hashlib
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import redis.asyncio as redis
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class CacheConfig(BaseModel):
    """Configuração do sistema de cache"""
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 3600  # 1 hora
    max_memory_cache_size: int = 1000
    enable_compression: bool = True
    key_prefix: str = "synapscale:"


class CacheStats(BaseModel):
    """Estatísticas do cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    memory_usage: int = 0
    redis_usage: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class CacheManager:
    """Gerenciador de cache avançado com Redis e memória"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict] = {}
        self.stats = CacheStats()
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Inicializa conexão com Redis"""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=False
            )
            await self.redis_client.ping()
            logger.info("Cache Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"Redis não disponível, usando apenas cache em memória: {e}")
            self.redis_client = None
    
    def _generate_key(self, key: str) -> str:
        """Gera chave com prefix"""
        return f"{self.config.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serializa valor para armazenamento"""
        if self.config.enable_compression:
            return pickle.dumps(value)
        return json.dumps(value, default=str).encode()
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserializa valor do armazenamento"""
        try:
            if self.config.enable_compression:
                return pickle.loads(data)
            return json.loads(data.decode())
        except Exception as e:
            logger.error(f"Erro ao deserializar cache: {e}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        cache_key = self._generate_key(key)
        
        # Tenta cache em memória primeiro
        if cache_key in self.memory_cache:
            cache_data = self.memory_cache[cache_key]
            if cache_data['expires_at'] > datetime.now():
                self.stats.hits += 1
                return cache_data['value']
            else:
                # Remove item expirado
                del self.memory_cache[cache_key]
        
        # Tenta Redis se disponível
        if self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data:
                    value = self._deserialize_value(data)
                    if value is not None:
                        self.stats.hits += 1
                        # Adiciona ao cache em memória
                        await self._add_to_memory_cache(cache_key, value)
                        return value
            except Exception as e:
                logger.error(f"Erro ao acessar Redis: {e}")
        
        self.stats.misses += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena valor no cache"""
        cache_key = self._generate_key(key)
        ttl = ttl or self.config.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # Armazena em memória
        await self._add_to_memory_cache(cache_key, value, expires_at)
        
        # Armazena no Redis se disponível
        if self.redis_client:
            try:
                serialized = self._serialize_value(value)
                await self.redis_client.setex(cache_key, ttl, serialized)
            except Exception as e:
                logger.error(f"Erro ao armazenar no Redis: {e}")
        
        self.stats.sets += 1
        return True
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        cache_key = self._generate_key(key)
        
        # Remove da memória
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        # Remove do Redis
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.error(f"Erro ao deletar do Redis: {e}")
        
        self.stats.deletes += 1
        return True
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Limpa cache com padrão opcional"""
        count = 0
        
        if pattern:
            # Limpa por padrão
            pattern_key = self._generate_key(pattern)
            
            # Limpa memória
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                count += 1
            
            # Limpa Redis
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(f"{pattern_key}*")
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
                except Exception as e:
                    logger.error(f"Erro ao limpar Redis: {e}")
        else:
            # Limpa tudo
            count = len(self.memory_cache)
            self.memory_cache.clear()
            
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(f"{self.config.key_prefix}*")
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
                except Exception as e:
                    logger.error(f"Erro ao limpar Redis: {e}")
        
        return count
    
    async def _add_to_memory_cache(self, key: str, value: Any, expires_at: Optional[datetime] = None):
        """Adiciona item ao cache em memória"""
        async with self._lock:
            # Remove itens expirados se necessário
            await self._cleanup_memory_cache()
            
            # Adiciona novo item
            self.memory_cache[key] = {
                'value': value,
                'expires_at': expires_at or datetime.now() + timedelta(seconds=self.config.default_ttl),
                'created_at': datetime.now()
            }
    
    async def _cleanup_memory_cache(self):
        """Limpa itens expirados do cache em memória"""
        now = datetime.now()
        expired_keys = [
            key for key, data in self.memory_cache.items()
            if data['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Limita tamanho do cache
        if len(self.memory_cache) > self.config.max_memory_cache_size:
            # Remove os mais antigos
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]['created_at']
            )
            
            items_to_remove = len(self.memory_cache) - self.config.max_memory_cache_size
            for key, _ in sorted_items[:items_to_remove]:
                del self.memory_cache[key]
    
    async def get_stats(self) -> CacheStats:
        """Retorna estatísticas do cache"""
        self.stats.memory_usage = len(self.memory_cache)
        
        if self.redis_client:
            try:
                info = await self.redis_client.info('memory')
                self.stats.redis_usage = info.get('used_memory', 0)
            except Exception:
                pass
        
        return self.stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de cache"""
        health = {
            'memory_cache': True,
            'redis_cache': False,
            'total_keys': len(self.memory_cache),
            'stats': await self.get_stats()
        }
        
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health['redis_cache'] = True
                
                # Conta chaves no Redis
                keys = await self.redis_client.keys(f"{self.config.key_prefix}*")
                health['redis_keys'] = len(keys)
            except Exception as e:
                health['redis_error'] = str(e)
        
        return health


# Instância global do cache
cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Retorna instância do gerenciador de cache"""
    global cache_manager
    if cache_manager is None:
        config = CacheConfig()
        cache_manager = CacheManager(config)
        await cache_manager.initialize()
    return cache_manager


def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """Decorator para cache de resultados de funções"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gera chave única baseada na função e argumentos
            func_name = f"{func.__module__}.{func.__name__}"
            args_str = str(args) + str(sorted(kwargs.items()))
            key_hash = hashlib.md5(args_str.encode()).hexdigest()
            cache_key = f"{key_prefix}func:{func_name}:{key_hash}"
            
            cache = await get_cache_manager()
            
            # Tenta recuperar do cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # Executa função e armazena resultado
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_model_query(model_name: str, ttl: int = 1800):
    """Decorator específico para cache de queries de modelo"""
    return cache_result(ttl=ttl, key_prefix=f"model:{model_name}:")


def cache_api_response(ttl: int = 300):
    """Decorator específico para cache de respostas de API"""
    return cache_result(ttl=ttl, key_prefix="api:")


def cache_user_data(ttl: int = 900):
    """Decorator específico para cache de dados de usuário"""
    return cache_result(ttl=ttl, key_prefix="user:")


# Funções utilitárias para invalidação de cache

async def invalidate_user_cache(user_id: int):
    """Invalida cache específico de um usuário"""
    cache = await get_cache_manager()
    await cache.clear(f"user:*user_id:{user_id}*")


async def invalidate_model_cache(model_name: str):
    """Invalida cache específico de um modelo"""
    cache = await get_cache_manager()
    await cache.clear(f"model:{model_name}:")


async def invalidate_api_cache(endpoint: str = ""):
    """Invalida cache de API"""
    cache = await get_cache_manager()
    pattern = f"api:{endpoint}" if endpoint else "api:"
    await cache.clear(pattern)


# Middleware para cache de respostas HTTP

class CacheMiddleware:
    """Middleware para cache automático de respostas HTTP"""
    
    def __init__(self, app, cache_ttl: int = 300):
        self.app = app
        self.cache_ttl = cache_ttl
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = scope
        method = request.get("method", "GET")
        path = request.get("path", "")
        
        # Só faz cache de GET requests
        if method != "GET":
            await self.app(scope, receive, send)
            return
        
        # Gera chave de cache
        cache_key = f"http:{method}:{path}"
        if request.get("query_string"):
            cache_key += f":{request['query_string'].decode()}"
        
        cache = await get_cache_manager()
        
        # Tenta recuperar resposta do cache
        cached_response = await cache.get(cache_key)
        if cached_response:
            await send({
                "type": "http.response.start",
                "status": cached_response["status"],
                "headers": cached_response["headers"],
            })
            await send({
                "type": "http.response.body",
                "body": cached_response["body"],
            })
            return
        
        # Captura resposta para cache
        response_data = {"status": 200, "headers": [], "body": b""}
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
                response_data["headers"] = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_data["body"] += message.get("body", b"")
                
                # Se é o último chunk, armazena no cache
                if not message.get("more_body", False):
                    # Só faz cache de respostas 200
                    if response_data["status"] == 200:
                        await cache.set(cache_key, response_data, self.cache_ttl)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

