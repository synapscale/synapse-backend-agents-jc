"""
Testes unitários para o conector OpenAI (ChatGPT).

Este módulo contém testes para validar o funcionamento do
conector OpenAI, incluindo geração de texto, contagem de tokens
e listagem de modelos.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
import asyncio

from src.synapse.core.llm.openai import OpenAIConnector


class TestOpenAIConnector:
    """Testes para o conector OpenAI."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.connector = OpenAIConnector(api_key="test_key")
    
    @patch('synapse.core.llm.openai.requests.post')
    async def test_generate_text(self, mock_post):
        """Testa a geração de texto."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Este é um texto gerado pelo ChatGPT."
                    }
                }
            ],
            "usage": {
                "total_tokens": 15
            }
        }
        mock_post.return_value = mock_response
        
        # Executar o método
        result = await self.connector.generate_text(
            prompt="Gere um texto de exemplo",
            model="gpt-4",
            max_tokens=100
        )
        
        # Verificar o resultado
        assert result == "Este é um texto gerado pelo ChatGPT."
        mock_post.assert_called_once()
        
        # Verificar os parâmetros da chamada
        args, kwargs = mock_post.call_args
        assert "https://api.openai.com/v1/chat/completions" in args
        assert "headers" in kwargs
        assert "json" in kwargs
        assert kwargs["json"]["model"] == "gpt-4"
        assert kwargs["json"]["max_tokens"] == 100
    
    @patch('synapse.core.llm.openai.requests.post')
    async def test_count_tokens(self, mock_post):
        """Testa a contagem de tokens."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "usage": {
                "total_tokens": 10
            }
        }
        mock_post.return_value = mock_response
        
        # Executar o método
        result = await self.connector.count_tokens(
            text="Este é um texto para contar tokens",
            model="gpt-4"
        )
        
        # Verificar o resultado
        assert result == 10
        mock_post.assert_called_once()
    
    @patch('synapse.core.llm.openai.requests.get')
    async def test_get_models(self, mock_get):
        """Testa a listagem de modelos."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "gpt-4",
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "openai"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "openai"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Executar o método
        result = await self.connector.get_models()
        
        # Verificar o resultado
        assert len(result) == 2
        assert result[0]["id"] == "gpt-4"
        assert result[0]["provider"] == "OpenAI"
        assert result[1]["id"] == "gpt-3.5-turbo"
        mock_get.assert_called_once()
    
    def test_provider_name(self):
        """Testa o nome do provedor."""
        assert self.connector.provider_name() == "openai"
    
    def test_default_model(self):
        """Testa o modelo padrão."""
        assert self.connector.default_model() == "gpt-4"
    
    def test_is_available(self):
        """Testa a disponibilidade do provedor."""
        assert self.connector.is_available() is True
        
        # Teste com chave de API não configurada
        connector_without_key = OpenAIConnector(api_key=None)
        assert connector_without_key.is_available() is False
    
    def test_capabilities(self):
        """Testa as capacidades do provedor."""
        capabilities = self.connector.capabilities()
        assert "text-generation" in capabilities
        assert isinstance(capabilities, list)
