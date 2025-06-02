"""
Implementação do método de fallback para o factory de LLM.

Este módulo estende o LLMFactory com métodos de fallback e
gerenciamento de conectores alternativos.
"""

from typing import Dict, Any, List, Optional
import random
import logging

from src.synapse.core.llm.base import BaseLLMConnector
from src.synapse.config import settings
from src.synapse.logging import get_logger

logger = get_logger(__name__)


class FallbackConnector(BaseLLMConnector):
    """
    Conector que implementa fallback entre múltiplos provedores de LLM.
    
    Este conector tenta usar um provedor primário e, em caso de falha,
    recorre automaticamente a um provedor secundário (fallback).
    """
    
    def __init__(self, primary_connector: BaseLLMConnector, fallback_connector: BaseLLMConnector):
        """
        Inicializa o conector de fallback.
        
        Args:
            primary_connector: Conector primário a ser usado
            fallback_connector: Conector de fallback a ser usado em caso de falha do primário
        """
        self.primary_connector = primary_connector
        self.fallback_connector = fallback_connector
        logger.info(f"Conector de fallback inicializado com primário: {primary_connector.__class__.__name__} e fallback: {fallback_connector.__class__.__name__}")
    
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            Nome do provedor
        """
        return "fallback"
    
    def default_model(self) -> str:
        """
        Retorna o modelo padrão para este provedor.
        
        Returns:
            Nome do modelo padrão
        """
        return self.primary_connector.default_model()
    
    def is_available(self) -> bool:
        """
        Verifica se o provedor está disponível.
        
        Returns:
            True se o provedor estiver disponível, False caso contrário
        """
        return self.primary_connector.is_available() or self.fallback_connector.is_available()
    
    def capabilities(self) -> List[str]:
        """
        Retorna as capacidades deste provedor.
        
        Returns:
            Lista de capacidades
        """
        # Combina as capacidades de ambos os conectores
        primary_capabilities = self.primary_connector.capabilities()
        fallback_capabilities = self.fallback_connector.capabilities()
        return list(set(primary_capabilities + fallback_capabilities))
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Lista os modelos disponíveis.
        
        Returns:
            Lista de modelos disponíveis
        """
        try:
            return await self.primary_connector.get_models()
        except Exception as e:
            logger.warning(f"Falha ao listar modelos com conector primário: {str(e)}. Tentando fallback.")
            return await self.fallback_connector.get_models()
    
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um modelo específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Detalhes do modelo
        """
        try:
            return await self.primary_connector.get_model_details(model_id)
        except Exception as e:
            logger.warning(f"Falha ao obter detalhes do modelo com conector primário: {str(e)}. Tentando fallback.")
            return await self.fallback_connector.get_model_details(model_id)
    
    async def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """
        Gera texto usando o conector primário, com fallback para o secundário em caso de falha.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: Modelo específico a ser usado (opcional)
            max_tokens: Número máximo de tokens a gerar
            temperature: Temperatura para amostragem (0.0-1.0)
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Texto gerado
            
        Raises:
            Exception: Se ambos os conectores falharem
        """
        try:
            logger.info(f"Tentando gerar texto com conector primário: {self.primary_connector.__class__.__name__}")
            return await self.primary_connector.generate_text(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Falha no conector primário: {str(e)}. Tentando fallback.")
            try:
                return await self.fallback_connector.generate_text(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
            except Exception as fallback_error:
                logger.error(f"Falha também no conector de fallback: {str(fallback_error)}")
                raise Exception(f"Falha em ambos os conectores. Primário: {str(e)}. Fallback: {str(fallback_error)}")
    
    async def count_tokens(self, text: str, model: Optional[str] = None, **kwargs) -> int:
        """
        Conta tokens usando o conector primário, com fallback para o secundário em caso de falha.
        
        Args:
            text: Texto para contar tokens
            model: Modelo específico a ser usado (opcional)
            **kwargs: Argumentos adicionais
            
        Returns:
            Número de tokens
            
        Raises:
            Exception: Se ambos os conectores falharem
        """
        try:
            return await self.primary_connector.count_tokens(text=text, model=model, **kwargs)
        except Exception as e:
            logger.warning(f"Falha ao contar tokens com conector primário: {str(e)}. Tentando fallback.")
            try:
                return await self.fallback_connector.count_tokens(text=text, model=model, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Falha também no conector de fallback: {str(fallback_error)}")
                raise Exception(f"Falha em ambos os conectores. Primário: {str(e)}. Fallback: {str(fallback_error)}")


def _get_fallback_connector(self) -> BaseLLMConnector:
    """
    Retorna um conector alternativo quando o solicitado não está disponível.
    
    Esta função tenta encontrar um conector alternativo disponível
    quando o conector solicitado não está configurado ou falha.
    
    Returns:
        Instância de um conector alternativo
        
    Raises:
        ValueError: Se nenhum conector alternativo estiver disponível
    """
    # Lista de provedores disponíveis
    available_providers = self.list_available_providers()
    
    if not available_providers:
        logger.error("Nenhum provedor LLM está configurado")
        raise ValueError("Nenhum provedor LLM está configurado. Configure pelo menos um provedor.")
    
    # Escolher um provedor aleatório da lista de disponíveis
    fallback_provider = random.choice(available_providers)
    logger.info(f"Usando provedor alternativo: {fallback_provider}")
    
    # Criar e retornar o conector
    if fallback_provider == "claude":
        return self._connectors.get(fallback_provider) or ClaudeConnector(
            api_key=self.config.claude_api_key
        )
    elif fallback_provider == "gemini":
        return self._connectors.get(fallback_provider) or GeminiConnector(
            api_key=self.config.gemini_api_key
        )
    elif fallback_provider == "grok":
        return self._connectors.get(fallback_provider) or GrokConnector(
            api_key=self.config.grok_api_key
        )
    elif fallback_provider == "deepseek":
        return self._connectors.get(fallback_provider) or DeepSeekConnector(
            api_key=self.config.deepseek_api_key
        )
    elif fallback_provider == "tess":
        return self._connectors.get(fallback_provider) or TessAIConnector(
            api_key=self.config.tess_api_key,
            base_url=self.config.tess_api_base_url
        )
    elif fallback_provider == "openai":
        return self._connectors.get(fallback_provider) or OpenAIConnector(
            api_key=self.config.openai_api_key
        )
    elif fallback_provider == "llama":
        return self._connectors.get(fallback_provider) or LlamaConnector(
            api_key=self.config.llama_api_key
        )
    else:
        logger.error(f"Provedor alternativo não suportado: {fallback_provider}")
        raise ValueError(f"Provedor alternativo não suportado: {fallback_provider}")

# Adicionar o método à classe LLMFactory
from src.synapse.core.llm.factory import LLMFactory
LLMFactory._get_fallback_connector = _get_fallback_connector
