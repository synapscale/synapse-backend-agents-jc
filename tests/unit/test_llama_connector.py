"""
Testes unitários para o conector LLaMA (Meta).

Este módulo contém testes para validar o funcionamento do
conector LLaMA, incluindo geração de texto, contagem de tokens
e listagem de modelos.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
import asyncio

from synapse.core.llm.llama import LlamaConnector


class TestLlamaConnector:
    """Testes para o conector LLaMA."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.connector = LlamaConnector(api_key="test_key")
    
    @patch('synapse.core.llm.llama.requests.post')
    async def test_generate_text(self, mock_post):
        """Testa a geração de texto."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "content": "Este é um texto gerado pelo LLaMA."
            }
        }
        mock_post.return_value = mock_response
        
        # Executar o método
        result = await self.connector.generate_text(
            prompt="Gere um texto de exemplo",
            model="llama-3-70b-instruct",
            max_tokens=100
        )
        
        # Verificar o resultado
        assert result == "Este é um texto gerado pelo LLaMA."
        mock_post.assert_called_once()
        
        # Verificar os parâmetros da chamada
        args, kwargs = mock_post.call_args
        assert "completions" in args[0]
        assert "headers" in kwargs
        assert "json" in kwargs
        assert kwargs["json"]["model"] == "llama-3-70b-instruct"
        assert kwargs["json"]["max_tokens"] == 100
    
    @patch('synapse.core.llm.llama.requests.post')
    async def test_count_tokens(self, mock_post):
        """Testa a contagem de tokens."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token_count": 12
        }
        mock_post.return_value = mock_response
        
        # Executar o método
        result = await self.connector.count_tokens(
            text="Este é um texto para contar tokens",
            model="llama-3-70b-instruct"
        )
        
        # Verificar o resultado
        assert result == 12
        mock_post.assert_called_once()
    
    @patch('synapse.core.llm.llama.requests.get')
    async def test_get_models(self, mock_get):
        """Testa a listagem de modelos."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {
                    "id": "llama-3-70b-instruct",
                    "name": "Llama 3 70B Instruct"
                },
                {
                    "id": "llama-3-8b-instruct",
                    "name": "Llama 3 8B Instruct"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Executar o método
        result = await self.connector.get_models()
        
        # Verificar o resultado
        assert len(result) == 2
        assert result[0]["id"] == "llama-3-70b-instruct"
        assert result[0]["provider"] == "Meta"
        assert result[1]["id"] == "llama-3-8b-instruct"
        mock_get.assert_called_once()
    
    def test_provider_name(self):
        """Testa o nome do provedor."""
        assert self.connector.provider_name() == "llama"
    
    def test_default_model(self):
        """Testa o modelo padrão."""
        assert self.connector.default_model() == "llama-3-70b-instruct"
    
    def test_is_available(self):
        """Testa a disponibilidade do provedor."""
        assert self.connector.is_available() is True
        
        # Teste com chave de API não configurada
        connector_without_key = LlamaConnector(api_key=None)
        assert connector_without_key.is_available() is False
    
    def test_capabilities(self):
        """Testa as capacidades do provedor."""
        capabilities = self.connector.capabilities()
        assert "text-generation" in capabilities
        assert isinstance(capabilities, list)
    
    def test_format_prompt(self):
        """Testa a formatação do prompt."""
        # Teste para modelo instruct
        formatted_prompt = self.connector._format_prompt("Olá, como vai?")
        assert "<|begin_of_text|>" in formatted_prompt
        assert "<|user|>" in formatted_prompt
        assert "<|assistant|>" in formatted_prompt
        
        # Alterar para modelo chat e testar
        self.connector._default_model = "llama-2-70b-chat"
        formatted_prompt = self.connector._format_prompt("Olá, como vai?")
        assert "<|user|>" in formatted_prompt
        assert "<|assistant|>" in formatted_prompt
