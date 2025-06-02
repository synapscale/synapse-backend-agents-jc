"""
Implementação do conector Grok (xAI).

Este módulo contém a implementação do conector para a API do Grok (xAI),
permitindo a geração de texto, contagem de tokens e listagem de modelos.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import requests

from src.synapse.config import settings
from src.synapse.core.llm.base import BaseLLMConnector
from src.synapse.logging import get_logger

logger = get_logger(__name__)

# Verificar se a biblioteca xai está disponível
try:
    import xai
    GROK_AVAILABLE = True
except ImportError:
    GROK_AVAILABLE = False
    logger.warning("Biblioteca xai não instalada. O conector Grok funcionará apenas em modo de teste.")


class GrokConnector(BaseLLMConnector):
    """
    Conector para a API do Grok (xAI).
    
    Este conector implementa a interface BaseLLMConnector para
    interagir com a API do Grok (xAI).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o conector Grok.
        
        Args:
            api_key: Chave de API do Grok (opcional, usa a configuração se não fornecida)
        """
        self.api_key = api_key or settings.GROK_API_KEY
        self.client = None
        
        if not self.api_key:
            logger.warning("Chave de API Grok não configurada")
        
        # Inicializar o cliente apenas se a biblioteca estiver disponível
        if GROK_AVAILABLE and self.api_key:
            try:
                self.client = xai.GrokClient(api_key=self.api_key)
                logger.info("Conector Grok inicializado")
            except Exception as e:
                logger.error(f"Não é possível inicializar o conector Grok: {str(e)}")
        else:
            logger.error(f"Não é possível inicializar o conector Grok: biblioteca xai não instalada")
    
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            Nome do provedor
        """
        return "grok"
    
    def default_model(self) -> str:
        """
        Retorna o modelo padrão para este provedor.
        
        Returns:
            Nome do modelo padrão
        """
        return "grok-1"
    
    def is_available(self) -> bool:
        """
        Verifica se o provedor está disponível.
        
        Returns:
            True se o provedor estiver disponível, False caso contrário
        """
        return GROK_AVAILABLE and bool(self.api_key) and self.client is not None
    
    def capabilities(self) -> List[str]:
        """
        Retorna as capacidades deste provedor.
        
        Returns:
            Lista de capacidades
        """
        return ["text-generation", "function-calling"]
    
    async def _call_api(self, prompt: str, model: str, max_tokens: int, **kwargs) -> str:
        """
        Método interno para chamar a API do Grok.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: ID do modelo a ser usado
            max_tokens: Número máximo de tokens a gerar
            **kwargs: Parâmetros adicionais para a API
            
        Returns:
            Texto gerado pelo modelo
            
        Raises:
            Exception: Se ocorrer um erro na chamada da API
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar texto com Grok: {str(e)}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        **kwargs
    ) -> str:
        """
        Gera texto a partir de um prompt usando o modelo Grok especificado.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: ID do modelo a ser usado (opcional, usa o padrão se não especificado)
            max_tokens: Número máximo de tokens a gerar
            temperature: Temperatura para amostragem (0.0-1.0)
            top_p: Valor de top-p para amostragem nucleus
            top_k: Valor de top-k para amostragem
            **kwargs: Parâmetros adicionais para a API
        
        Returns:
            Texto gerado pelo modelo
        
        Raises:
            RuntimeError: Se a biblioteca xai não estiver disponível
            Exception: Se ocorrer um erro na chamada da API
        """
        # Para fins de teste, permitir bypass do check de disponibilidade
        if hasattr(self, '_test_mode') and self._test_mode:
            return await self._call_api(prompt, model or self.default_model(), max_tokens, temperature=temperature, top_p=top_p, **kwargs)
            
        if not GROK_AVAILABLE:
            raise RuntimeError("Biblioteca xai não instalada")
        
        if not self.client:
            raise RuntimeError("Cliente Grok não inicializado")
        
        model = model or self.default_model()
        logger.info(f"Gerando texto com modelo {model}: {prompt[:50]}...")
        
        return await self._call_api(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            **kwargs
        )
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Conta o número de tokens em um texto.
        
        Args:
            text: Texto para contar tokens
            model: Modelo específico a ser usado (opcional)
            
        Returns:
            Número de tokens
            
        Raises:
            RuntimeError: Se a biblioteca xai não estiver disponível
            Exception: Se ocorrer um erro na contagem
        """
        # Para fins de teste, permitir bypass do check de disponibilidade
        if hasattr(self, '_test_mode') and self._test_mode:
            # Estimativa simples para testes
            return len(text.split()) + (len(text) // 4)
            
        if not GROK_AVAILABLE:
            raise RuntimeError("Biblioteca xai não instalada")
        
        if not self.client:
            raise RuntimeError("Cliente Grok não inicializado")
        
        try:
            # Implementação simplificada - o Grok não tem uma API específica para contagem de tokens
            # Estimativa baseada em palavras e caracteres
            return len(text.split()) + (len(text) // 4)
        except Exception as e:
            logger.error(f"Erro ao contar tokens com Grok: {str(e)}")
            # Fallback para estimativa simples
            return len(text.split())
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Lista os modelos disponíveis.
        
        Returns:
            Lista de modelos disponíveis
            
        Raises:
            RuntimeError: Se a biblioteca xai não estiver disponível
            Exception: Se ocorrer um erro na listagem
        """
        # Para fins de teste, permitir bypass do check de disponibilidade
        if hasattr(self, '_test_mode') and self._test_mode:
            return [
                {
                    "id": "grok-1",
                    "name": "Grok-1",
                    "provider": "xAI",
                    "context_window": 8192,
                    "capabilities": ["text-generation", "function-calling"]
                }
            ]
            
        if not GROK_AVAILABLE:
            raise RuntimeError("Biblioteca xai não instalada")
        
        if not self.client:
            raise RuntimeError("Cliente Grok não inicializado")
        
        # O Grok tem um conjunto limitado de modelos
        return [
            {
                "id": "grok-1",
                "name": "Grok-1",
                "provider": "xAI",
                "context_window": 8192,
                "capabilities": ["text-generation", "function-calling"]
            }
        ]
    
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um modelo específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Detalhes do modelo
            
        Raises:
            RuntimeError: Se a biblioteca xai não estiver disponível
            Exception: Se ocorrer um erro na obtenção dos detalhes
        """
        # Para fins de teste, permitir bypass do check de disponibilidade
        if hasattr(self, '_test_mode') and self._test_mode:
            return {
                "id": model_id,
                "name": model_id.capitalize(),
                "provider": "xAI",
                "context_window": 8192,
                "capabilities": ["text-generation", "function-calling"]
            }
            
        if not GROK_AVAILABLE:
            raise RuntimeError("Biblioteca xai não instalada")
        
        if not self.client:
            raise RuntimeError("Cliente Grok não inicializado")
        
        models = await self.get_models()
        for model in models:
            if model["id"] == model_id:
                return model
        
        # Se não encontrar, retorna informações padrão
        return {
            "id": model_id,
            "name": model_id.capitalize(),
            "provider": "xAI",
            "context_window": 8192,
            "capabilities": ["text-generation", "function-calling"]
        }
