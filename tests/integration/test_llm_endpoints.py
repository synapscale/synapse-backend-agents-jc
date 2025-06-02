"""
Testes de integração para os endpoints de LLM.

Este módulo contém testes de integração para os endpoints da API de LLM,
verificando o comportamento completo dos endpoints com mocks para as APIs externas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.synapse.main import app
from src.synapse.core.llm import unified_service


@pytest.fixture
def client():
    """Cliente de teste para a API."""
    return TestClient(app)


@pytest.fixture
def mock_generate_text():
    """Mock para o método generate_text do serviço unificado."""
    with patch.object(unified_service, "generate_text") as mock:
        mock.return_value = {
            "text": "Resposta simulada do LLM",
            "provider": "claude",
            "model": "claude-3-sonnet-20240229",
            "execution_time": 1.5,
            "cached": False
        }
        yield mock


@pytest.fixture
def mock_count_tokens():
    """Mock para o método count_tokens do serviço unificado."""
    with patch.object(unified_service, "count_tokens") as mock:
        mock.return_value = {
            "token_count": 42,
            "provider": "claude",
            "model": "claude-3-sonnet-20240229"
        }
        yield mock


@pytest.fixture
def mock_list_models():
    """Mock para o método list_models do serviço unificado."""
    with patch.object(unified_service, "list_models") as mock:
        mock.return_value = {
            "providers": {
                "claude": {
                    "available": True,
                    "models": [
                        {
                            "id": "claude-3-sonnet-20240229",
                            "name": "Claude 3 Sonnet",
                            "context_window": 200000,
                            "capabilities": ["text-generation", "image-understanding"]
                        }
                    ]
                }
            }
        }
        yield mock


@pytest.fixture
def mock_list_providers():
    """Mock para o método list_providers do serviço unificado."""
    with patch.object(unified_service, "list_providers") as mock:
        mock.return_value = {
            "providers": [
                {
                    "name": "claude",
                    "available": True,
                    "capabilities": ["text-generation", "image-understanding"],
                    "default_model": "claude-3-sonnet-20240229"
                }
            ],
            "default_provider": "claude"
        }
        yield mock


@pytest.fixture
def mock_auth():
    """Mock para autenticação."""
    with patch("synapse.api.deps.get_current_user", return_value={"id": 1, "email": "test@example.com"}):
        yield


def test_generate_text(client, mock_generate_text, mock_auth):
    """Testa o endpoint de geração de texto."""
    response = client.post(
        "/api/v1/llm/generate",
        json={
            "prompt": "Teste",
            "provider": "claude",
            "max_tokens": 100
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Resposta simulada do LLM"
    assert data["provider"] == "claude"
    assert data["model"] == "claude-3-sonnet-20240229"
    assert "execution_time" in data
    assert "cached" in data
    
    mock_generate_text.assert_called_once()
    args, kwargs = mock_generate_text.call_args
    assert kwargs["prompt"] == "Teste"
    assert kwargs["provider"] == "claude"
    assert kwargs["max_tokens"] == 100


def test_count_tokens(client, mock_count_tokens, mock_auth):
    """Testa o endpoint de contagem de tokens."""
    response = client.post(
        "/api/v1/llm/count-tokens",
        json={
            "text": "Teste",
            "provider": "claude"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["token_count"] == 42
    assert data["provider"] == "claude"
    assert data["model"] == "claude-3-sonnet-20240229"
    
    mock_count_tokens.assert_called_once()
    args, kwargs = mock_count_tokens.call_args
    assert kwargs["text"] == "Teste"
    assert kwargs["provider"] == "claude"


def test_list_models(client, mock_list_models, mock_auth):
    """Testa o endpoint de listagem de modelos."""
    response = client.get("/api/v1/llm/models")
    
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "claude" in data["providers"]
    assert data["providers"]["claude"]["available"] is True
    assert len(data["providers"]["claude"]["models"]) == 1
    
    mock_list_models.assert_called_once()


def test_list_models_with_provider(client, mock_list_models, mock_auth):
    """Testa o endpoint de listagem de modelos com filtro de provedor."""
    response = client.get("/api/v1/llm/models?provider=claude")
    
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "claude" in data["providers"]
    
    mock_list_models.assert_called_once()
    args, kwargs = mock_list_models.call_args
    assert kwargs["provider"] == "claude"


def test_list_providers(client, mock_list_providers, mock_auth):
    """Testa o endpoint de listagem de provedores."""
    response = client.get("/api/v1/llm/providers")
    
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert len(data["providers"]) == 1
    assert data["providers"][0]["name"] == "claude"
    assert "default_provider" in data
    
    mock_list_providers.assert_called_once()


def test_generate_text_with_provider(client, mock_generate_text, mock_auth):
    """Testa o endpoint de geração de texto com provedor específico."""
    response = client.post(
        "/api/v1/llm/claude/generate",
        json={
            "prompt": "Teste",
            "max_tokens": 100
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Resposta simulada do LLM"
    
    mock_generate_text.assert_called_once()
    args, kwargs = mock_generate_text.call_args
    assert kwargs["prompt"] == "Teste"
    assert kwargs["provider"] == "claude"
    assert kwargs["max_tokens"] == 100


def test_unauthorized_access(client):
    """Testa acesso não autorizado aos endpoints."""
    # Sem o mock de autenticação, o acesso deve ser negado
    response = client.get("/api/v1/llm/providers")
    assert response.status_code == 401 or response.status_code == 403
    
    response = client.post(
        "/api/v1/llm/generate",
        json={"prompt": "Teste"}
    )
    assert response.status_code == 401 or response.status_code == 403
