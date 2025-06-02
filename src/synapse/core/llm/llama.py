"""
Implementação do conector LLaMA (Meta).

Este módulo contém a implementação do conector para a API do LLaMA (Meta),
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


class LlamaConnector(BaseLLMConnector):
    """
    Conector para a API do LLaMA (Meta).
    
    Este conector implementa a interface BaseLLMConnector para
    interagir com a API do LLaMA (Meta).
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa o conector LLaMA.
        
        Args:
            api_key: Chave de API do LLaMA (opcional, usa a configuração se não fornecida)
            base_url: URL base da API (opcional, usa o padrão se não fornecida)
        """
        self.api_key = api_key or settings.LLAMA_API_KEY
        self.base_url = base_url or "https://llama.developer.meta.com/api/v1"
        
        if not self.api_key:
            logger.warning("Chave de API LLaMA não configurada")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Cache para modelos disponíveis
        self._models_cache = None
        
        logger.info("Conector LLaMA inicializado")
    
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            Nome do provedor
        """
        return "llama"
    
    def default_model(self) -> str:
        """
        Retorna o modelo padrão para este provedor.
        
        Returns:
            Nome do modelo padrão
        """
        return "llama-3-70b-instruct"
    
    def is_available(self) -> bool:
        """
        Verifica se o provedor está disponível.
        
        Returns:
            True se o provedor estiver disponível, False caso contrário
        """
        return bool(self.api_key)
    
    def capabilities(self) -> List[str]:
        """
        Retorna as capacidades deste provedor.
        
        Returns:
            Lista de capacidades
        """
        return ["text-generation", "embeddings"]
    
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um modelo específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Detalhes do modelo
        """
        models = await self.get_models()
        for model in models:
            if model["id"] == model_id:
                return model
        
        # Se não encontrar, retorna informações padrão
        return {
            "id": model_id,
            "name": model_id,
            "provider": "Meta",
            "context_window": self._get_context_window(model_id),
            "capabilities": self._get_model_capabilities(model_id)
        }
    
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
        Gera texto a partir de um prompt.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: Modelo específico a ser usado (opcional)
            max_tokens: Número máximo de tokens a gerar
            temperature: Temperatura para amostragem (0.0-1.0)
            top_p: Valor de top-p para amostragem nucleus
            top_k: Valor de top-k para amostragem
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Texto gerado
            
        Raises:
            Exception: Se ocorrer um erro na geração
        """
        model = model or self.default_model()
        logger.info(f"Gerando texto com modelo {model}: {prompt[:50]}...")
        
        try:
            # Formatar o prompt para o formato esperado pelo LLaMA
            formatted_prompt = self._format_prompt(prompt)
            
            payload = {
                "model": model,
                "prompt": formatted_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
            
            # Adicionar parâmetros adicionais
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            response = requests.post(
                f"{self.base_url}/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["output"]["content"]
            else:
                logger.error(f"Erro na API LLaMA: {response.status_code} - {response.text}")
                raise Exception(f"Erro na API LLaMA: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Erro ao gerar texto com LLaMA: {str(e)}")
            raise
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Conta o número de tokens em um texto.
        
        Args:
            text: Texto para contar tokens
            model: Modelo específico a ser usado (opcional)
            
        Returns:
            Número de tokens
            
        Raises:
            Exception: Se ocorrer um erro na contagem
        """
        model = model or self.default_model()
        
        try:
            # Tentar usar a API para contagem de tokens
            payload = {
                "model": model,
                "text": text
            }
            
            response = requests.post(
                f"{self.base_url}/tokenize",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["token_count"]
            else:
                logger.warning(f"Erro na API LLaMA para contagem de tokens: {response.status_code} - {response.text}")
                # Fallback para estimativa simples
                return len(text.split()) + (len(text) // 4)
        except Exception as e:
            logger.error(f"Erro ao contar tokens com LLaMA: {str(e)}")
            # Fallback para estimativa simples
            return len(text.split()) + (len(text) // 4)
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Lista os modelos disponíveis.
        
        Returns:
            Lista de modelos disponíveis
            
        Raises:
            Exception: Se ocorrer um erro na listagem
        """
        # Usar cache se disponível
        if self._models_cache is not None:
            return self._models_cache
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                models = [
                    {
                        "id": model["id"],
                        "name": model["name"],
                        "provider": "Meta",
                        "context_window": self._get_context_window(model["id"]),
                        "capabilities": self._get_model_capabilities(model["id"])
                    }
                    for model in result["models"]
                ]
                
                self._models_cache = models
                return models
            else:
                logger.error(f"Erro na API LLaMA: {response.status_code} - {response.text}")
                
                # Fallback para lista estática de modelos
                fallback_models = [
                    {
                        "id": "llama-3-70b-instruct",
                        "name": "Llama 3 70B Instruct",
                        "provider": "Meta",
                        "context_window": 128000,
                        "capabilities": ["text-generation"]
                    },
                    {
                        "id": "llama-3-8b-instruct",
                        "name": "Llama 3 8B Instruct",
                        "provider": "Meta",
                        "context_window": 128000,
                        "capabilities": ["text-generation"]
                    },
                    {
                        "id": "llama-2-70b-chat",
                        "name": "Llama 2 70B Chat",
                        "provider": "Meta",
                        "context_window": 4096,
                        "capabilities": ["text-generation"]
                    }
                ]
                
                self._models_cache = fallback_models
                return fallback_models
        except Exception as e:
            logger.error(f"Erro ao listar modelos com LLaMA: {str(e)}")
            raise
    
    def _format_prompt(self, prompt: str) -> str:
        """
        Formata o prompt para o formato esperado pelo LLaMA.
        
        Args:
            prompt: Prompt original
            
        Returns:
            Prompt formatado
        """
        # Para modelos instruct, adicionar formatação específica
        if "instruct" in self.default_model():
            return f"<|begin_of_text|><|user|>\n{prompt}<|end_of_turn|>\n<|assistant|>"
        
        # Para modelos chat, usar formato de chat
        if "chat" in self.default_model():
            return f"<|user|>\n{prompt}\n<|assistant|>"
        
        # Formato padrão
        return prompt
    
    def _get_context_window(self, model_id: str) -> int:
        """
        Retorna o tamanho da janela de contexto para um modelo.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Tamanho da janela de contexto
        """
        context_windows = {
            "llama-3-70b": 128000,
            "llama-3-8b": 128000,
            "llama-2-70b": 4096,
            "llama-2-13b": 4096,
            "llama-2-7b": 4096
        }
        
        # Verificar correspondências parciais
        for key, value in context_windows.items():
            if key in model_id:
                return value
        
        # Valor padrão
        return 4096
    
    def _get_model_capabilities(self, model_id: str) -> List[str]:
        """
        Retorna as capacidades de um modelo.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Lista de capacidades
        """
        capabilities = ["text-generation"]
        
        if "code" in model_id:
            capabilities.append("code-generation")
        
        return capabilities
