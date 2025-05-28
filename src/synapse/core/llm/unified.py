"""
Serviço unificado para interação com múltiplos LLMs.

Este módulo fornece uma interface unificada para interagir com
diferentes provedores de LLM através de uma API consistente.
"""

import time
from typing import Dict, Any, List, Optional, Union

from synapse.core.llm.base import BaseLLMConnector
from synapse.core.llm.factory import LLMFactory
from synapse.core.llm.cache import CacheService
from synapse.logging import get_logger

logger = get_logger(__name__)


class UnifiedLLMService:
    """
    Serviço unificado para interação com múltiplos LLMs.
    
    Esta classe fornece uma interface comum para todos os conectores
    de LLM, com suporte a cache e fallback automático entre provedores.
    """
    
    def __init__(self, factory: LLMFactory, cache_service: Optional[CacheService] = None):
        """
        Inicializa o serviço unificado.
        
        Args:
            factory: Fábrica de conectores de LLM
            cache_service: Serviço de cache (opcional)
        """
        self.factory = factory
        self.cache_service = cache_service
        logger.info("Serviço unificado de LLM inicializado")
        
    async def generate_text(self, prompt: str, provider: str = None, 
                           use_cache: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Gera texto a partir de um prompt usando o provedor especificado.
        
        Args:
            prompt: Texto de entrada para o modelo
            provider: Nome do provedor (usa o padrão se não especificado)
            use_cache: Se deve usar o cache (se disponível)
            **kwargs: Parâmetros adicionais para o conector
            
        Returns:
            Dicionário com o texto gerado e metadados
            
        Raises:
            Exception: Se ocorrer um erro na geração e não houver fallback disponível
        """
        # Verificar cache se habilitado
        if use_cache and self.cache_service:
            cache_key = {"prompt": prompt, "provider": provider, **kwargs}
            cached_result = self.cache_service.get(cache_key)
            if cached_result:
                logger.info(f"Usando resposta em cache para provedor {provider or 'padrão'}")
                return {**cached_result, "cached": True}
                
        # Obter conector e gerar texto
        try:
            start_time = time.time()
            connector = self.factory.get_connector(provider)
            logger.info(f"Gerando texto com provedor {connector.provider_name()}")
            
            text = await connector.generate_text(prompt, **kwargs)
            
            # Calcular tempo de execução
            execution_time = time.time() - start_time
            
            result = {
                "text": text,
                "provider": connector.provider_name(),
                "model": kwargs.get("model") or connector.default_model(),
                "execution_time": execution_time,
                "cached": False
            }
            
            # Armazenar em cache se habilitado
            if use_cache and self.cache_service:
                self.cache_service.set(cache_key, result)
                
            return result
        except Exception as e:
            logger.error(f"Erro ao gerar texto com provedor {provider or 'padrão'}: {str(e)}")
            
            # Tentar fallback se o provedor especificado falhar
            if provider:
                available_providers = self.factory.list_available_providers()
                for fallback_provider in available_providers:
                    if fallback_provider != provider:
                        try:
                            logger.info(f"Tentando fallback para provedor {fallback_provider}")
                            connector = self.factory.get_connector(fallback_provider)
                            
                            start_time = time.time()
                            text = await connector.generate_text(prompt, **kwargs)
                            execution_time = time.time() - start_time
                            
                            result = {
                                "text": text,
                                "provider": connector.provider_name(),
                                "model": kwargs.get("model") or connector.default_model(),
                                "execution_time": execution_time,
                                "fallback": True,
                                "original_error": str(e),
                                "cached": False
                            }
                            
                            # Não armazenar respostas de fallback em cache
                            return result
                        except Exception as fallback_error:
                            logger.error(f"Erro no fallback para {fallback_provider}: {str(fallback_error)}")
                            continue
                            
            # Se não houver fallback disponível, propagar o erro original
            raise
            
    async def count_tokens(self, text: str, provider: str = None, model: str = None) -> Dict[str, Any]:
        """
        Conta o número de tokens em um texto.
        
        Args:
            text: Texto para contar tokens
            provider: Nome do provedor (usa o padrão se não especificado)
            model: ID do modelo (usa o padrão do provedor se não especificado)
            
        Returns:
            Dicionário com a contagem de tokens e metadados
            
        Raises:
            Exception: Se ocorrer um erro na contagem e não houver fallback disponível
        """
        try:
            connector = self.factory.get_connector(provider)
            logger.info(f"Contando tokens com provedor {connector.provider_name()}")
            
            token_count = await connector.count_tokens(text, model)
            
            return {
                "token_count": token_count,
                "provider": connector.provider_name(),
                "model": model or connector.default_model()
            }
        except Exception as e:
            logger.error(f"Erro ao contar tokens com provedor {provider or 'padrão'}: {str(e)}")
            
            # Tentar fallback se o provedor especificado falhar
            if provider:
                available_providers = self.factory.list_available_providers()
                for fallback_provider in available_providers:
                    if fallback_provider != provider:
                        try:
                            logger.info(f"Tentando fallback para provedor {fallback_provider}")
                            connector = self.factory.get_connector(fallback_provider)
                            token_count = await connector.count_tokens(text, model)
                            
                            return {
                                "token_count": token_count,
                                "provider": connector.provider_name(),
                                "model": model or connector.default_model(),
                                "fallback": True,
                                "original_error": str(e)
                            }
                        except:
                            continue
                            
            # Se não houver fallback disponível, propagar o erro original
            raise
            
    async def list_models(self, provider: str = None) -> Dict[str, Any]:
        """
        Lista os modelos disponíveis.
        
        Args:
            provider: Nome do provedor (lista todos se não especificado)
            
        Returns:
            Dicionário com a lista de modelos agrupados por provedor
        """
        result = {"providers": {}}
        
        if provider:
            # Listar modelos de um provedor específico
            try:
                connector = self.factory.get_connector(provider)
                models = await connector.get_models()
                result["providers"][connector.provider_name()] = {
                    "available": True,
                    "models": models
                }
            except Exception as e:
                logger.error(f"Erro ao listar modelos do provedor {provider}: {str(e)}")
                result["providers"][provider] = {
                    "available": False,
                    "error": str(e)
                }
        else:
            # Listar modelos de todos os provedores disponíveis
            available_providers = self.factory.list_available_providers()
            
            for provider_name in available_providers:
                try:
                    connector = self.factory.get_connector(provider_name)
                    models = await connector.get_models()
                    result["providers"][connector.provider_name()] = {
                        "available": True,
                        "models": models
                    }
                except Exception as e:
                    logger.error(f"Erro ao listar modelos do provedor {provider_name}: {str(e)}")
                    result["providers"][provider_name] = {
                        "available": False,
                        "error": str(e)
                    }
                    
        return result
        
    def list_providers(self) -> Dict[str, Any]:
        """
        Lista os provedores disponíveis.
        
        Returns:
            Dicionário com a lista de provedores disponíveis
        """
        available_providers = self.factory.list_available_providers()
        
        result = {
            "providers": [],
            "default_provider": self.factory.config.LLM_DEFAULT_PROVIDER
        }
        
        for provider_name in available_providers:
            try:
                connector = self.factory.get_connector(provider_name)
                result["providers"].append({
                    "name": provider_name,
                    "available": connector.is_available(),
                    "capabilities": connector.capabilities(),
                    "default_model": connector.default_model()
                })
            except Exception as e:
                logger.error(f"Erro ao verificar provedor {provider_name}: {str(e)}")
                result["providers"].append({
                    "name": provider_name,
                    "available": False,
                    "error": str(e)
                })
                
        return result
