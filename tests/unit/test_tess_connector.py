"""
Testes unitários para o conector Tess AI.

Este módulo contém testes unitários para o conector Tess AI,
verificando sua integração com o backend SynapScale.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
import os

from synapse.core.llm.tess import TessAIConnector


class TestTessAIConnector:
    """Testes para o conector Tess AI."""
    
    @pytest.fixture
    def mock_response(self):
        """Fixture para simular resposta da API."""
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {
            "content": "Esta é uma resposta de teste da Tess AI.",
            "model": "gpt-4o"
        }
        return mock
    
    @pytest.fixture
    def mock_agents_response(self):
        """Fixture para simular resposta de listagem de agentes."""
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {
            "data": [
                {
                    "id": 123,
                    "title": "Assistente de Chat",
                    "type": "chat",
                    "description": "Assistente de chat com suporte a múltiplos modelos"
                },
                {
                    "id": 456,
                    "title": "Gerador de Texto",
                    "type": "text",
                    "description": "Gerador de texto para diversos fins"
                }
            ]
        }
        return mock
    
    @pytest.fixture
    def mock_agent_details_response(self):
        """Fixture para simular resposta de detalhes do agente."""
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {
            "id": 123,
            "title": "Assistente de Chat",
            "type": "chat",
            "description": "Assistente de chat com suporte a múltiplos modelos",
            "questions": [
                {
                    "name": "prompt",
                    "type": "textarea",
                    "required": True,
                    "label": "Pergunta"
                },
                {
                    "name": "model",
                    "type": "select",
                    "required": False,
                    "label": "Modelo",
                    "options": [
                        {"label": "GPT-4o", "value": "gpt-4o"},
                        {"label": "Claude 3 Opus", "value": "claude-3-opus"}
                    ]
                }
            ]
        }
        return mock
    
    @pytest.mark.asyncio
    @patch('requests.post')
    @patch('requests.get')
    async def test_generate_text(self, mock_get, mock_post, mock_response, mock_agents_response, mock_agent_details_response):
        """Testa a geração de texto com o conector Tess AI."""
        # Configura os mocks
        mock_post.return_value = mock_response
        mock_get.side_effect = [mock_agents_response, mock_agent_details_response]
        
        # Cria o conector
        connector = TessAIConnector(api_key="test_key")
        
        # Testa a geração de texto
        result = await connector.generate_text(
            prompt="Teste de geração de texto",
            model="gpt-4o",
            max_tokens=100,
            temperature=0.7
        )
        
        # Verifica o resultado
        assert result == "Esta é uma resposta de teste da Tess AI."
        
        # Verifica se as chamadas foram feitas corretamente
        assert mock_get.call_count == 2
        assert mock_post.call_count == 1
        
        # Verifica os parâmetros da chamada POST
        args, kwargs = mock_post.call_args
        assert "agents/123/execute" in args[0]
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"
        assert "prompt" in kwargs["json"]
        assert kwargs["json"]["prompt"] == "Teste de geração de texto"
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_list_models(self, mock_get, mock_agents_response, mock_agent_details_response):
        """Testa a listagem de modelos com o conector Tess AI."""
        # Configura o mock para retornar detalhes do agente
        mock_get.side_effect = [mock_agents_response, mock_agent_details_response]
        
        # Cria o conector
        connector = TessAIConnector(api_key="test_key")
        
        # Testa a listagem de modelos
        result = await connector.list_models()
        
        # Verifica o resultado
        assert len(result) == 2
        assert result[0]["id"] == "gpt-4o"
        assert result[0]["provider"] == "OpenAI"
        assert result[1]["id"] == "claude-3-opus"
        assert result[1]["provider"] == "Anthropic"
        
        # Verifica se as chamadas foram feitas corretamente
        assert mock_get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_count_tokens(self):
        """Testa a contagem de tokens com o conector Tess AI."""
        # Cria o conector
        connector = TessAIConnector(api_key="test_key")
        
        # Testa a contagem de tokens
        result = await connector.count_tokens("Este é um texto de teste com aproximadamente 20 tokens.")
        
        # Verifica se o resultado é um número positivo
        assert isinstance(result, int)
        assert result > 0
        
        # Testa com texto vazio
        result_empty = await connector.count_tokens("")
        assert result_empty == 1  # Deve retornar pelo menos 1 token
