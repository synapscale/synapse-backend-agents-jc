"""
Implementação do conector OpenAI (ChatGPT).

Este módulo contém a implementação do conector para a API do ChatGPT (OpenAI),
permitindo a geração de texto, contagem de tokens e listagem de modelos.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import requests
import tiktoken

from src.synapse.config import settings
from src.synapse.core.llm.base import BaseLLMConnector
from src.synapse.logging import get_logger

logger = get_logger(__name__)


class OpenAIConnector(BaseLLMConnector):
    """
    Conector para a API do ChatGPT (OpenAI).
    
    Este conector implementa a interface BaseLLMConnector para
    interagir com a API do ChatGPT (OpenAI).
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa o conector OpenAI.
        
        Args:
            api_key: Chave de API do OpenAI (opcional, usa a configuração se não fornecida)
            base_url: URL base da API (opcional, usa o padrão se não fornecida)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url or "https://api.openai.com/v1"
        
        if not self.api_key:
            logger.warning("Chave de API OpenAI não configurada")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Cache para modelos disponíveis
        self._models_cache = None
        
        logger.info("Conector OpenAI inicializado")
    
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            Nome do provedor
        """
        return "openai"
    
    def default_model(self) -> str:
        """
        Retorna o modelo padrão para este provedor.
        
        Returns:
            Nome do modelo padrão
        """
        return "gpt-4o"
    
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
        return ["text-generation", "embeddings", "function-calling", "vision"]
    
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
            "provider": "OpenAI",
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
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "n": 1,
                "stream": False
            }
            
            # Adicionar parâmetros adicionais
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Erro na API OpenAI: {response.status_code} - {response.text}")
                raise Exception(f"Erro na API OpenAI: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Erro ao gerar texto com OpenAI: {str(e)}")
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
            # Usar tiktoken para contagem de tokens
            encoding_name = "cl100k_base"  # Codificação para modelos mais recentes
            
            # Mapeamento de modelos para codificações
            model_to_encoding = {
                "gpt-4": "cl100k_base",
                "gpt-4o": "cl100k_base",
                "gpt-3.5-turbo": "cl100k_base"
            }
            
            if model in model_to_encoding:
                encoding_name = model_to_encoding[model]
            
            try:
                encoding = tiktoken.get_encoding(encoding_name)
            except:
                encoding = tiktoken.encoding_for_model(model)
            
            tokens = encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"Erro ao contar tokens com OpenAI: {str(e)}")
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
                
                # Filtrar apenas modelos GPT
                gpt_models = [
                    {
                        "id": model["id"],
                        "name": model["id"],
                        "provider": "OpenAI",
                        "context_window": self._get_context_window(model["id"]),
                        "capabilities": self._get_model_capabilities(model["id"])
                    }
                    for model in result["data"]
                    if model["id"].startswith(("gpt-", "text-"))
                ]
                
                self._models_cache = gpt_models
                return gpt_models
            else:
                logger.error(f"Erro na API OpenAI: {response.status_code} - {response.text}")
                
                # Fallback para lista estática de modelos
                fallback_models = [
                    {
                        "id": "gpt-4o",
                        "name": "GPT-4o",
                        "provider": "OpenAI",
                        "context_window": 128000,
                        "capabilities": ["text-generation", "vision", "function-calling"]
                    },
                    {
                        "id": "gpt-4-turbo",
                        "name": "GPT-4 Turbo",
                        "provider": "OpenAI",
                        "context_window": 128000,
                        "capabilities": ["text-generation", "function-calling"]
                    },
                    {
                        "id": "gpt-3.5-turbo",
                        "name": "GPT-3.5 Turbo",
                        "provider": "OpenAI",
                        "context_window": 16385,
                        "capabilities": ["text-generation", "function-calling"]
                    }
                ]
                
                self._models_cache = fallback_models
                return fallback_models
        except Exception as e:
            logger.error(f"Erro ao listar modelos com OpenAI: {str(e)}")
            raise
    
    def _get_context_window(self, model_id: str) -> int:
        """
        Retorna o tamanho da janela de contexto para um modelo.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Tamanho da janela de contexto
        """
        context_windows = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385
        }
        
        # Verificar correspondências parciais
        for key, value in context_windows.items():
            if model_id.startswith(key):
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
        
        if "gpt-4" in model_id:
            capabilities.append("function-calling")
        
        if "vision" in model_id or model_id == "gpt-4o":
            capabilities.append("vision")
        
        return capabilities
