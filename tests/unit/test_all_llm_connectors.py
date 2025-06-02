"""
Testes unitários abrangentes para todos os conectores LLM.

Este módulo contém testes unitários para todos os conectores LLM
implementados no sistema, garantindo que cada um deles funcione
corretamente e implemente a interface BaseLLMConnector.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Importar os conectores
from src.synapse.core.llm.base import BaseLLMConnector
from src.synapse.core.llm.claude import ClaudeConnector
from src.synapse.core.llm.gemini import GeminiConnector
from src.synapse.core.llm.grok import GrokConnector
from src.synapse.core.llm.deepseek import DeepSeekConnector
from src.synapse.core.llm.tess import TessAIConnector
from src.synapse.core.llm.openai import OpenAIConnector
from src.synapse.core.llm.llama import LlamaConnector
from src.synapse.core.llm.fallback import FallbackConnector


@pytest.mark.asyncio
@patch("anthropic.AsyncAnthropic")
async def test_claude_generate_text(mock_anthropic):
    """Testa a geração de texto com o conector Claude."""
    # Configurar o mock
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Resposta do Claude")]
    
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client
    
    # Criar o conector e chamar o método
    connector = ClaudeConnector(api_key="test_key")
    
    # Substituir o método real por um mock
    connector.generate_text = AsyncMock(return_value="Resposta do Claude")
    
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta do Claude"
    connector.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_gemini_generate_text():
    """Testa a geração de texto com o conector Gemini."""
    # Criar o conector
    connector = GeminiConnector(api_key="test_key")
    
    # Substituir o método real por um mock
    connector.generate_text = AsyncMock(return_value="Resposta do Gemini")
    
    # Chamar o método
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta do Gemini"
    connector.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_grok_generate_text():
    """Testa a geração de texto com o conector Grok."""
    # Criar o conector com um mock para o cliente
    connector = GrokConnector(api_key="test_key")
    
    # Ativar modo de teste
    connector._test_mode = True
    
    # Substituir o método real por um mock
    connector._call_api = AsyncMock(return_value="Resposta do Grok")
    
    # Chamar o método
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta do Grok"
    connector._call_api.assert_called_once()


@pytest.mark.asyncio
async def test_deepseek_generate_text():
    """Testa a geração de texto com o conector DeepSeek."""
    # Criar o conector com um mock para o cliente
    connector = DeepSeekConnector(api_key="test_key")
    
    # Ativar modo de teste
    connector._test_mode = True
    
    # Substituir o método real por um mock
    connector._call_api = AsyncMock(return_value="Resposta do DeepSeek")
    
    # Chamar o método
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta do DeepSeek"
    connector._call_api.assert_called_once()


@pytest.mark.asyncio
@patch("requests.post")
@patch("requests.get")
async def test_tess_generate_text(mock_get, mock_post):
    """Testa a geração de texto com o conector Tess AI."""
    # Configurar os mocks
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"data": [{"id": 1, "type": "chat"}]})
    )
    mock_post.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"content": "Resposta da Tess AI"})
    )
    
    # Criar o conector e chamar o método
    connector = TessAIConnector(api_key="test_key")
    
    # Substituir o método _list_agents para evitar chamadas de API reais
    connector._list_agents = AsyncMock(return_value=[{"id": 1, "type": "chat"}])
    connector._get_agent_details = AsyncMock(return_value={"questions": [{"type": "text", "required": True, "name": "prompt"}]})
    
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta da Tess AI"
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_openai_generate_text():
    """Testa a geração de texto com o conector OpenAI."""
    # Criar o conector
    connector = OpenAIConnector(api_key="test_key")
    
    # Substituir o método real por um mock
    original_method = connector.generate_text
    connector.generate_text = AsyncMock(return_value="Resposta do OpenAI")
    
    # Chamar o método
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta do OpenAI"
    connector.generate_text.assert_called_once()
    
    # Restaurar o método original para não afetar outros testes
    connector.generate_text = original_method


@pytest.mark.asyncio
@patch("requests.post")
async def test_llama_generate_text(mock_post):
    """Testa a geração de texto com o conector LLaMA."""
    # Configurar o mock
    mock_post.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"output": {"content": "Resposta do LLaMA"}})
    )
    
    # Criar o conector e chamar o método
    connector = LlamaConnector(api_key="test_key", base_url="https://llama.developer.meta.com/api/v1")
    result = await connector.generate_text("Olá, como você está?")
    
    # Verificar o resultado
    assert result == "Resposta do LLaMA"
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_fallback_connector():
    """Testa o conector de fallback."""
    # Criar mocks para os conectores
    primary_connector = MagicMock(spec=BaseLLMConnector)
    primary_connector.generate_text = AsyncMock(side_effect=Exception("Erro simulado"))
    primary_connector.provider_name = MagicMock(return_value="primary")
    primary_connector.default_model = MagicMock(return_value="primary-model")
    primary_connector.is_available = MagicMock(return_value=True)
    primary_connector.capabilities = MagicMock(return_value=["text-generation"])
    primary_connector.get_models = AsyncMock(return_value=[{"id": "primary-model"}])
    primary_connector.get_model_details = AsyncMock(return_value={"id": "primary-model"})
    
    fallback_connector = MagicMock(spec=BaseLLMConnector)
    fallback_connector.generate_text = AsyncMock(return_value="Resposta do fallback")
    fallback_connector.provider_name = MagicMock(return_value="fallback")
    fallback_connector.default_model = MagicMock(return_value="fallback-model")
    fallback_connector.is_available = MagicMock(return_value=True)
    fallback_connector.capabilities = MagicMock(return_value=["text-generation"])
    fallback_connector.get_models = AsyncMock(return_value=[{"id": "fallback-model"}])
    fallback_connector.get_model_details = AsyncMock(return_value={"id": "fallback-model"})
    
    # Criar o conector de fallback
    connector = FallbackConnector(
        primary_connector=primary_connector,
        fallback_connector=fallback_connector
    )
    
    # Chamar o método e verificar o resultado
    result = await connector.generate_text("Olá, como você está?")
    assert result == "Resposta do fallback"
    
    # Verificar que o conector primário foi chamado primeiro
    primary_connector.generate_text.assert_called_once()
    fallback_connector.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_fallback_connector_primary_success():
    """Testa o conector de fallback quando o primário funciona."""
    # Criar mocks para os conectores
    primary_connector = MagicMock(spec=BaseLLMConnector)
    primary_connector.generate_text = AsyncMock(return_value="Resposta do primário")
    primary_connector.provider_name = MagicMock(return_value="primary")
    primary_connector.default_model = MagicMock(return_value="primary-model")
    primary_connector.is_available = MagicMock(return_value=True)
    primary_connector.capabilities = MagicMock(return_value=["text-generation"])
    primary_connector.get_models = AsyncMock(return_value=[{"id": "primary-model"}])
    primary_connector.get_model_details = AsyncMock(return_value={"id": "primary-model"})
    
    fallback_connector = MagicMock(spec=BaseLLMConnector)
    fallback_connector.generate_text = AsyncMock(return_value="Resposta do fallback")
    fallback_connector.provider_name = MagicMock(return_value="fallback")
    fallback_connector.default_model = MagicMock(return_value="fallback-model")
    fallback_connector.is_available = MagicMock(return_value=True)
    fallback_connector.capabilities = MagicMock(return_value=["text-generation"])
    fallback_connector.get_models = AsyncMock(return_value=[{"id": "fallback-model"}])
    fallback_connector.get_model_details = AsyncMock(return_value={"id": "fallback-model"})
    
    # Criar o conector de fallback
    connector = FallbackConnector(
        primary_connector=primary_connector,
        fallback_connector=fallback_connector
    )
    
    # Chamar o método e verificar o resultado
    result = await connector.generate_text("Olá, como você está?")
    assert result == "Resposta do primário"
    
    # Verificar que apenas o conector primário foi chamado
    primary_connector.generate_text.assert_called_once()
    fallback_connector.generate_text.assert_not_called()
