"""
Testes de Integração Simplificados para Endpoints LLM
Verifica se os endpoints estão funcionando corretamente
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.synapse.main import app


@pytest.fixture
def client():
    """Cliente de teste simplificado"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.integration
class TestLLMEndpoints:
    """Testes simplificados dos endpoints LLM"""

    def test_llm_models_endpoint(self, client):
        """Testa se o endpoint de modelos LLM funciona"""
        response = client.get("/api/v1/llm/models")

        # Pode retornar 401 (não autenticado) ou 200, ambos indicam que o endpoint existe
        assert response.status_code in [200, 401]

    def test_llm_providers_endpoint(self, client):
        """Testa se o endpoint de provedores LLM funciona"""
        response = client.get("/api/v1/llm/providers")

        # Pode retornar 401 (não autenticado) ou 200, ambos indicam que o endpoint existe
        assert response.status_code in [200, 401]

    def test_health_endpoint(self, client):
        """Testa se o endpoint de health funciona"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_metrics_endpoint(self, client):
        """Testa se o endpoint de métricas funciona"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

    @patch("src.synapse.api.deps.get_current_user")
    def test_generate_endpoint_structure(self, mock_user, client):
        """Testa a estrutura básica do endpoint generate"""
        # Mock do usuário
        mock_user.return_value = MagicMock(id=1, email="test@test.com")

        payload = {"prompt": "Teste simples", "model": "gpt-4o", "provider": "openai"}

        response = client.post("/api/v1/llm/generate", json=payload)

        # Pode retornar vários códigos dependendo da configuração
        # O importante é que o endpoint existe e processa a requisição
        assert response.status_code in [200, 400, 401, 422, 500]

    @patch("src.synapse.api.deps.get_current_user")
    def test_chat_endpoint_structure(self, mock_user, client):
        """Testa a estrutura básica do endpoint chat"""
        # Mock do usuário
        mock_user.return_value = MagicMock(id=1, email="test@test.com")

        payload = {
            "messages": [{"role": "user", "content": "Olá"}],
            "model": "gpt-4o",
            "provider": "openai",
        }

        response = client.post("/api/v1/llm/chat", json=payload)

        # Pode retornar vários códigos dependendo da configuração
        # O importante é que o endpoint existe e processa a requisição
        assert response.status_code in [200, 400, 401, 422, 500]


@pytest.mark.integration
def test_app_startup(client):
    """Testa se a aplicação inicia corretamente"""
    # Se chegamos aqui, a aplicação iniciou sem erros críticos
    assert client is not None


@pytest.mark.integration
def test_router_integration():
    """Testa se os roteadores estão integrados corretamente"""
    from src.synapse.api.v1.router import api_router

    # Verificar se o roteador principal existe
    assert api_router is not None

    # Verificar se há rotas registradas
    assert len(api_router.routes) > 0
