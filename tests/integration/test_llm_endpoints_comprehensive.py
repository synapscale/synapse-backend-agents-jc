"""
Testes de integração para os endpoints de LLM.

Este módulo contém testes de integração para os endpoints de LLM,
garantindo que as rotas, autenticação e fluxos completos funcionem corretamente.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.synapse.main import app
from src.synapse.core.llm.unified import UnifiedLLMService
from src.synapse.core.auth.jwt import create_access_token


@pytest.fixture
def test_client():
    """Fixture para cliente de teste."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock para sessão de banco de dados."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    
    # Patch para o get_db dependency
    with patch("synapse.api.deps.get_db", return_value=session):
        yield session


@pytest.fixture
def auth_headers():
    """Fixture para headers de autenticação."""
    # Criar token de acesso para usuário de teste
    token = create_access_token(
        data={
            "sub": "test_user",
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_unified_service():
    """Mock para o serviço unificado de LLM."""
    with patch("synapse.api.v1.endpoints.llm.routes.unified_service") as mock_service:
        yield mock_service


def test_generate_text(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de geração de texto."""
    # Configurar mock para o serviço
    mock_unified_service.generate_text = AsyncMock(return_value={
        "text": "Resposta gerada pelo modelo",
        "model": "claude-3-sonnet",
        "provider": "claude",
        "tokens": {
            "prompt": 10,
            "completion": 20,
            "total": 30
        },
        "processing_time": 1.5
    })
    
    # Dados da requisição
    request_data = {
        "prompt": "Explique o conceito de machine learning em termos simples.",
        "provider": "claude",
        "model": "claude-3-sonnet",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    # Fazer requisição
    response = test_client.post(
        "/api/v1/llm/generate",
        json=request_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Resposta gerada pelo modelo"
    assert data["model"] == "claude-3-sonnet"
    assert data["provider"] == "claude"
    assert "tokens" in data
    assert data["tokens"]["total"] == 30
    
    # Verificar chamada ao serviço
    mock_unified_service.generate_text.assert_called_once()
    args, kwargs = mock_unified_service.generate_text.call_args
    assert kwargs["prompt"] == request_data["prompt"]
    assert kwargs["provider"] == request_data["provider"]
    assert kwargs["model"] == request_data["model"]
    assert kwargs["max_tokens"] == request_data["max_tokens"]
    assert kwargs["temperature"] == request_data["temperature"]


def test_generate_text_unauthorized(test_client, mock_db_session):
    """Testa o endpoint de geração de texto sem autenticação."""
    # Dados da requisição
    request_data = {
        "prompt": "Explique o conceito de machine learning em termos simples.",
        "provider": "claude",
        "model": "claude-3-sonnet",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    # Fazer requisição sem token
    response = test_client.post(
        "/api/v1/llm/generate",
        json=request_data
    )
    
    # Verificar resposta
    assert response.status_code == 401


def test_generate_text_with_provider(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de geração de texto com provedor específico."""
    # Configurar mock para o serviço
    mock_unified_service.generate_text = AsyncMock(return_value={
        "text": "Resposta gerada pelo Gemini",
        "model": "gemini-1.5-pro",
        "provider": "gemini",
        "tokens": {
            "prompt": 10,
            "completion": 20,
            "total": 30
        },
        "processing_time": 1.5
    })
    
    # Dados da requisição
    request_data = {
        "prompt": "Explique o conceito de machine learning em termos simples.",
        "model": "gemini-1.5-pro",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    # Fazer requisição
    response = test_client.post(
        "/api/v1/llm/gemini/generate",
        json=request_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Resposta gerada pelo Gemini"
    assert data["model"] == "gemini-1.5-pro"
    assert data["provider"] == "gemini"
    
    # Verificar chamada ao serviço
    mock_unified_service.generate_text.assert_called_once()
    args, kwargs = mock_unified_service.generate_text.call_args
    assert kwargs["prompt"] == request_data["prompt"]
    assert kwargs["provider"] == "gemini"  # Provedor do path
    assert kwargs["model"] == request_data["model"]


def test_count_tokens(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de contagem de tokens."""
    # Configurar mock para o serviço
    mock_unified_service.count_tokens = AsyncMock(return_value={
        "token_count": 42,
        "model": "claude-3-sonnet",
        "provider": "claude"
    })
    
    # Dados da requisição
    request_data = {
        "text": "Este é um exemplo de texto para contar tokens.",
        "provider": "claude",
        "model": "claude-3-sonnet"
    }
    
    # Fazer requisição
    response = test_client.post(
        "/api/v1/llm/count-tokens",
        json=request_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["token_count"] == 42
    assert data["model"] == "claude-3-sonnet"
    assert data["provider"] == "claude"
    
    # Verificar chamada ao serviço
    mock_unified_service.count_tokens.assert_called_once()
    args, kwargs = mock_unified_service.count_tokens.call_args
    assert kwargs["text"] == request_data["text"]
    assert kwargs["provider"] == request_data["provider"]
    assert kwargs["model"] == request_data["model"]


def test_count_tokens_with_provider(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de contagem de tokens com provedor específico."""
    # Configurar mock para o serviço
    mock_unified_service.count_tokens = AsyncMock(return_value={
        "token_count": 42,
        "model": "gpt-4o",
        "provider": "openai"
    })
    
    # Dados da requisição
    request_data = {
        "text": "Este é um exemplo de texto para contar tokens.",
        "model": "gpt-4o"
    }
    
    # Fazer requisição
    response = test_client.post(
        "/api/v1/llm/openai/count-tokens",
        json=request_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["token_count"] == 42
    assert data["model"] == "gpt-4o"
    assert data["provider"] == "openai"
    
    # Verificar chamada ao serviço
    mock_unified_service.count_tokens.assert_called_once()
    args, kwargs = mock_unified_service.count_tokens.call_args
    assert kwargs["text"] == request_data["text"]
    assert kwargs["provider"] == "openai"  # Provedor do path
    assert kwargs["model"] == request_data["model"]


def test_list_models(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de listagem de modelos."""
    # Configurar mock para o serviço
    mock_unified_service.list_models = AsyncMock(return_value={
        "providers": {
            "claude": {
                "models": [
                    {"name": "claude-3-sonnet", "context_window": 200000},
                    {"name": "claude-3-opus", "context_window": 200000}
                ]
            },
            "gemini": {
                "models": [
                    {"name": "gemini-1.5-pro", "context_window": 1000000},
                    {"name": "gemini-1.5-flash", "context_window": 1000000}
                ]
            }
        }
    })
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/llm/models",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "claude" in data["providers"]
    assert "gemini" in data["providers"]
    assert len(data["providers"]["claude"]["models"]) == 2
    assert len(data["providers"]["gemini"]["models"]) == 2
    
    # Verificar chamada ao serviço
    mock_unified_service.list_models.assert_called_once()
    args, kwargs = mock_unified_service.list_models.call_args
    assert kwargs["provider"] is None


def test_list_models_with_provider(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de listagem de modelos com provedor específico."""
    # Configurar mock para o serviço
    mock_unified_service.list_models = AsyncMock(return_value={
        "providers": {
            "claude": {
                "models": [
                    {"name": "claude-3-sonnet", "context_window": 200000},
                    {"name": "claude-3-opus", "context_window": 200000}
                ]
            }
        }
    })
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/llm/claude/models",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "claude" in data["providers"]
    assert len(data["providers"]["claude"]["models"]) == 2
    
    # Verificar chamada ao serviço
    mock_unified_service.list_models.assert_called_once()
    args, kwargs = mock_unified_service.list_models.call_args
    assert kwargs["provider"] == "claude"


def test_list_providers(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o endpoint de listagem de provedores."""
    # Configurar mock para o serviço
    mock_unified_service.list_providers = MagicMock(return_value={
        "providers": [
            {
                "name": "claude",
                "capabilities": ["text_generation", "token_counting"]
            },
            {
                "name": "gemini",
                "capabilities": ["text_generation", "token_counting", "image_understanding"]
            },
            {
                "name": "grok",
                "capabilities": ["text_generation", "token_counting"]
            }
        ],
        "default_provider": "claude"
    })
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/llm/providers",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert len(data["providers"]) == 3
    assert data["default_provider"] == "claude"
    
    # Verificar chamada ao serviço
    mock_unified_service.list_providers.assert_called_once()


def test_error_handling(test_client, mock_db_session, auth_headers, mock_unified_service):
    """Testa o tratamento de erros nos endpoints."""
    # Configurar mock para o serviço
    mock_unified_service.generate_text = AsyncMock(side_effect=Exception("Erro no serviço"))
    
    # Dados da requisição
    request_data = {
        "prompt": "Explique o conceito de machine learning em termos simples.",
        "provider": "claude",
        "model": "claude-3-sonnet",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    # Fazer requisição
    response = test_client.post(
        "/api/v1/llm/generate",
        json=request_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Erro no serviço" in data["detail"]
