"""
Implementação do conector para a API Gemini do Google.

Este módulo fornece integração com os modelos Gemini do Google,
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
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Biblioteca Google Generative AI não encontrada. O conector Gemini não estará disponível.")


class GeminiConnector(BaseLLMConnector):
    """
    Conector para a API Gemini do Google.
    
    Este conector permite interagir com os modelos Gemini para geração de texto
    e processamento de imagens.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa o conector Gemini com a chave de API e configurações.
        
        Args:
            api_key: Chave de API do Google
            **kwargs: Configurações adicionais
        """
        self.api_key = api_key
        
        if not GEMINI_AVAILABLE:
            logger.error("Não é possível inicializar o conector Gemini: biblioteca google.generativeai não instalada")
            return
            
        genai.configure(api_key=api_key)
        logger.info("Conector Gemini inicializado com sucesso")
        
    async def generate_text(self, prompt: str, model: str = None, 
                           max_tokens: int = 1000, **kwargs) -> str:
        """
        Gera texto a partir de um prompt usando o modelo Gemini especificado.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: ID do modelo a ser usado (opcional, usa o padrão se não especificado)
            max_tokens: Número máximo de tokens a gerar
            **kwargs: Parâmetros adicionais para a API
            
        Returns:
            Texto gerado pelo modelo
            
        Raises:
            RuntimeError: Se a biblioteca google.generativeai não estiver disponível
            Exception: Se ocorrer um erro na chamada da API
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Biblioteca google.generativeai não instalada")
            
        model = model or self.default_model()
        logger.debug(f"Gerando texto com Gemini (modelo: {model}, max_tokens: {max_tokens})")
        
        try:
            # Configurar geração
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40)
            }
            
            # Processar imagens se fornecidas
            content = prompt
            if "image" in kwargs:
                image_data = kwargs.pop("image")
                if isinstance(image_data, bytes):
                    content = [prompt, image_data]
            
            # Criar modelo e gerar conteúdo
            gemini_model = genai.GenerativeModel(model)
            response = await gemini_model.generate_content_async(
                content,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar texto com Gemini: {str(e)}")
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
            RuntimeError: Se a biblioteca google.generativeai não estiver disponível
            Exception: Se ocorrer um erro na chamada da API
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Biblioteca google.generativeai não instalada")
            
        model = model or self.default_model()
        
        try:
            gemini_model = genai.GenerativeModel(model)
            token_count = await gemini_model.count_tokens_async(text)
            return token_count.total_tokens
        except Exception as e:
            logger.error(f"Erro ao contar tokens com Gemini: {str(e)}")
            raise
        
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de modelos Gemini disponíveis.
        
        Returns:
            Lista de dicionários com informações sobre cada modelo
            
        Raises:
            RuntimeError: Se a biblioteca google.generativeai não estiver disponível
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Biblioteca google.generativeai não instalada")
            
        try:
            models = await genai.list_models_async()
            result = []
            
            for model in models:
                if "gemini" in model.name:
                    result.append({
                        "id": model.name,
                        "name": model.display_name,
                        "context_window": model.input_token_limit,
                        "capabilities": self._extract_capabilities(model)
                    })
                    
            return result
        except Exception as e:
            logger.error(f"Erro ao listar modelos Gemini: {str(e)}")
            # Fallback para lista estática em caso de erro
            return [
                {
                    "id": "gemini-1.5-pro-latest",
                    "name": "Gemini 1.5 Pro",
                    "context_window": 1000000,
                    "capabilities": ["text-generation", "image-understanding", "code-generation"]
                },
                {
                    "id": "gemini-1.5-flash-latest",
                    "name": "Gemini 1.5 Flash",
                    "context_window": 1000000,
                    "capabilities": ["text-generation", "image-understanding"]
                }
            ]
        
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Retorna detalhes sobre um modelo Gemini específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Dicionário com detalhes do modelo
            
        Raises:
            RuntimeError: Se a biblioteca google.generativeai não estiver disponível
            ValueError: Se o modelo não for encontrado
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Biblioteca google.generativeai não instalada")
            
        models = await self.get_models()
        for model in models:
            if model["id"] == model_id:
                return model
                
        raise ValueError(f"Modelo não encontrado: {model_id}")
        
    def is_available(self) -> bool:
        """
        Verifica se o conector Gemini está disponível e configurado corretamente.
        
        Returns:
            True se o conector estiver disponível, False caso contrário
        """
        return GEMINI_AVAILABLE and bool(self.api_key)
        
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            "gemini"
        """
        return "gemini"
        
    def default_model(self) -> str:
        """
        Retorna o ID do modelo Gemini padrão.
        
        Returns:
            ID do modelo padrão ("gemini-1.5-pro-latest")
        """
        return "gemini-1.5-pro-latest"
        
    def capabilities(self) -> List[str]:
        """
        Retorna a lista de capacidades suportadas pelo conector Gemini.
        
        Returns:
            Lista de capacidades
        """
        return ["text-generation", "image-understanding", "code-generation"]
        
    def _extract_capabilities(self, model) -> List[str]:
        """
        Extrai as capacidades de um modelo Gemini.
        
        Args:
            model: Objeto de modelo da API Gemini
            
        Returns:
            Lista de capacidades
        """
        capabilities = ["text-generation"]
        
        # Verificar suporte a imagens
        if hasattr(model, "supported_generation_methods"):
            if "generateContent" in model.supported_generation_methods:
                if hasattr(model, "input_content_types") and "image" in model.input_content_types:
                    capabilities.append("image-understanding")
                    
        # Verificar suporte a código
        if "code" in model.name.lower():
            capabilities.append("code-generation")
            
        return capabilities
