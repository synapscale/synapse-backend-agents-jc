"""
Implementação do conector para a API Claude da Anthropic.

Este módulo fornece integração com os modelos Claude da Anthropic,
permitindo geração de texto e processamento de imagens.
"""

import os
import json
import base64
from typing import List, Dict, Any, Optional, Union

from synapse.core.llm.base import BaseLLMConnector
from synapse.logging import get_logger

logger = get_logger(__name__)

# Importação condicional para evitar erros se a biblioteca não estiver instalada
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Biblioteca Anthropic não encontrada. O conector Claude não estará disponível.")


class ClaudeConnector(BaseLLMConnector):
    """
    Conector para a API Claude da Anthropic.
    
    Este conector permite interagir com os modelos Claude para geração de texto
    e processamento de imagens.
    """
    
    def __init__(self, api_key: str, base_url: str = None, **kwargs):
        """
        Inicializa o conector Claude com a chave de API e configurações.
        
        Args:
            api_key: Chave de API da Anthropic
            base_url: URL base da API (opcional)
            **kwargs: Configurações adicionais
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.anthropic.com/v1"
        
        if not ANTHROPIC_AVAILABLE:
            logger.error("Não é possível inicializar o conector Claude: biblioteca anthropic não instalada")
            return
            
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Conector Claude inicializado com sucesso")
        
    async def generate_text(self, prompt: str, model: str = None, 
                           max_tokens: int = 1000, **kwargs) -> str:
        """
        Gera texto a partir de um prompt usando o modelo Claude especificado.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: ID do modelo a ser usado (opcional, usa o padrão se não especificado)
            max_tokens: Número máximo de tokens a gerar
            **kwargs: Parâmetros adicionais para a API
            
        Returns:
            Texto gerado pelo modelo
            
        Raises:
            RuntimeError: Se a biblioteca anthropic não estiver disponível
            Exception: Se ocorrer um erro na chamada da API
        """
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("Biblioteca anthropic não instalada")
            
        model = model or self.default_model()
        logger.debug(f"Gerando texto com Claude (modelo: {model}, max_tokens: {max_tokens})")
        
        try:
            # Processar imagens se fornecidas
            messages = [{"role": "user", "content": prompt}]
            if "image" in kwargs:
                image_data = kwargs.pop("image")
                if isinstance(image_data, bytes):
                    image_b64 = base64.b64encode(image_data).decode()
                    messages = [{"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                        {"type": "text", "text": prompt}
                    ]}]
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                **kwargs
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Erro ao gerar texto com Claude: {str(e)}")
            raise
        
    async def count_tokens(self, text: str, model: str = None) -> int:
        """
        Conta o número de tokens em um texto para o modelo especificado.
        
        Args:
            text: Texto para contar tokens
            model: ID do modelo a ser usado (opcional, usa o padrão se não especificado)
            
        Returns:
            Número de tokens no texto
            
        Raises:
            RuntimeError: Se a biblioteca anthropic não estiver disponível
            Exception: Se ocorrer um erro na chamada da API
        """
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("Biblioteca anthropic não instalada")
            
        model = model or self.default_model()
        
        try:
            response = await self.client.messages.count_tokens(
                model=model,
                messages=[{"role": "user", "content": text}]
            )
            return response.token_count
        except Exception as e:
            logger.error(f"Erro ao contar tokens com Claude: {str(e)}")
            raise
        
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de modelos Claude disponíveis.
        
        Returns:
            Lista de dicionários com informações sobre cada modelo
            
        Raises:
            RuntimeError: Se a biblioteca anthropic não estiver disponível
        """
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("Biblioteca anthropic não instalada")
            
        # A API da Anthropic não fornece um endpoint para listar modelos,
        # então retornamos uma lista estática dos modelos conhecidos
        return [
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "context_window": 200000,
                "capabilities": ["text-generation", "image-understanding", "reasoning"]
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "context_window": 200000,
                "capabilities": ["text-generation", "image-understanding"]
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "context_window": 200000,
                "capabilities": ["text-generation", "image-understanding"]
            }
        ]
        
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Retorna detalhes sobre um modelo Claude específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Dicionário com detalhes do modelo
            
        Raises:
            RuntimeError: Se a biblioteca anthropic não estiver disponível
            ValueError: Se o modelo não for encontrado
        """
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("Biblioteca anthropic não instalada")
            
        models = await self.get_models()
        for model in models:
            if model["id"] == model_id:
                return model
                
        raise ValueError(f"Modelo não encontrado: {model_id}")
        
    def is_available(self) -> bool:
        """
        Verifica se o conector Claude está disponível e configurado corretamente.
        
        Returns:
            True se o conector estiver disponível, False caso contrário
        """
        return ANTHROPIC_AVAILABLE and bool(self.api_key)
        
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            "claude"
        """
        return "claude"
        
    def default_model(self) -> str:
        """
        Retorna o ID do modelo Claude padrão.
        
        Returns:
            ID do modelo padrão ("claude-3-sonnet-20240229")
        """
        return "claude-3-sonnet-20240229"
        
    def capabilities(self) -> List[str]:
        """
        Retorna a lista de capacidades suportadas pelo conector Claude.
        
        Returns:
            Lista de capacidades
        """
        return ["text-generation", "image-understanding"]
