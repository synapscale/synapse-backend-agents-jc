"""
Testes unitários para os conectores de LLM.

Este módulo contém testes unitários para os conectores de LLM,
usando mocks para simular as APIs externas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.synapse.core.llm.base import BaseLLMConnector
from src.synapse.core.llm.claude import ClaudeConnector
from src.synapse.core.llm.gemini import GeminiConnector
from src.synapse.core.llm.grok import GrokConnector
from src.synapse.core.llm.deepseek import DeepSeekConnector


@pytest.fixture
def mock_claude_response():
    """Mock para resposta da API Claude."""
    mock = MagicMock()
    mock.content = [MagicMock()]
    mock.content[0].text = "Resposta simulada do Claude"
    return mock


@pytest.fixture
def mock_gemini_response():
    """Mock para resposta da API Gemini."""
    mock = MagicMock()
    mock.text = "Resposta simulada do Gemini"
    return mock


@pytest.fixture
def mock_grok_response():
    """Mock para resposta da API Grok."""
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message = MagicMock()
    mock.choices[0].message.content = "Resposta simulada do Grok"
    return mock


@pytest.fixture
def mock_deepseek_response():
    """Mock para resposta da API DeepSeek."""
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message = MagicMock()
    mock.choices[0].message.content = "Resposta simulada do DeepSeek"
    return mock


@pytest.mark.asyncio
@patch("anthropic.Anthropic")
async def test_claude_generate_text(mock_anthropic, mock_claude_response):
    """Testa a geração de texto com o conector Claude."""
    # Configurar o mock
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_claude_response)
    mock_anthropic.return_value = mock_client
    
    # Criar o conector e chamar o método
    connector = ClaudeConnector(api_key="test_key")
    result = await connector.generate_text(
        prompt="Teste",
        model="claude-3-sonnet-20240229",
        max_tokens=100
    )
    
    # Verificar o resultado
    assert result == "Resposta simulada do Claude"
    mock_client.messages.create.assert_called_once()
    args, kwargs = mock_client.messages.create.call_args
    assert kwargs["model"] == "claude-3-sonnet-20240229"
    assert kwargs["max_tokens"] == 100
    assert kwargs["messages"][0]["content"] == "Teste"


@pytest.mark.asyncio
@patch("google.generativeai.GenerativeModel")
async def test_gemini_generate_text(mock_generative_model, mock_gemini_response):
    """Testa a geração de texto com o conector Gemini."""
    # Configurar o mock
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_gemini_response)
    mock_generative_model.return_value = mock_model
    
    # Criar o conector e chamar o método
    with patch("google.generativeai.configure") as mock_configure:
        connector = GeminiConnector(api_key="test_key")
        result = await connector.generate_text(
            prompt="Teste",
            model="gemini-1.5-pro-latest",
            max_tokens=100
        )
    
    # Verificar o resultado
    assert result == "Resposta simulada do Gemini"
    mock_model.generate_content_async.assert_called_once()
    mock_configure.assert_called_once_with(api_key="test_key")


@pytest.mark.asyncio
@patch("xai.Client")
async def test_grok_generate_text(mock_xai_client, mock_grok_response):
    """Testa a geração de texto com o conector Grok."""
    # Configurar o mock
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_grok_response)
    mock_xai_client.return_value = mock_client
    
    # Criar o conector e chamar o método
    connector = GrokConnector(api_key="test_key")
    result = await connector.generate_text(
        prompt="Teste",
        model="grok-1",
        max_tokens=100
    )
    
    # Verificar o resultado
    assert result == "Resposta simulada do Grok"
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "grok-1"
    assert kwargs["max_tokens"] == 100
    assert kwargs["messages"][0]["content"] == "Teste"


@pytest.mark.asyncio
@patch("deepseek.Client")
async def test_deepseek_generate_text(mock_deepseek_client, mock_deepseek_response):
    """Testa a geração de texto com o conector DeepSeek."""
    # Configurar o mock
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_deepseek_response)
    mock_deepseek_client.return_value = mock_client
    
    # Criar o conector e chamar o método
    connector = DeepSeekConnector(api_key="test_key")
    result = await connector.generate_text(
        prompt="Teste",
        model="deepseek-coder",
        max_tokens=100
    )
    
    # Verificar o resultado
    assert result == "Resposta simulada do DeepSeek"
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "deepseek-coder"
    assert kwargs["max_tokens"] == 100
    assert kwargs["messages"][0]["content"] == "Teste"
