"""
Testes de API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid


@pytest.mark.api
class TestWorkflowEndpoints:
    """Testes dos endpoints de workflows"""

    def test_list_workflows(self, client: TestClient, auth_headers):
        """Teste de listagem de workflows"""
        response = client.get("/api/v1/workflows/", headers=auth_headers)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_create_workflow(
        self, client: TestClient, sample_workflow_data, auth_headers
    ):
        """Teste de criação de workflow"""
        response = client.post(
            "/api/v1/workflows/", json=sample_workflow_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 401]

    def test_get_workflow_by_id(self, client: TestClient, auth_headers):
        """Teste de obtenção de workflow por ID"""
        response = client.get("/api/v1/workflows/1", headers=auth_headers)
        assert response.status_code in [200, 401, 404]


@pytest.mark.api
class TestAgentEndpoints:
    """Testes dos endpoints de agentes"""

    def test_list_agents(self, client: TestClient, auth_headers):
        """Teste de listagem de agentes"""
        response = client.get("/api/v1/agents/", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_create_agent(self, client: TestClient, auth_headers):
        """Teste de criação de agente"""
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "agent_type": "GENERAL",
            "model_provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        response = client.post("/api/v1/agents/", json=agent_data, headers=auth_headers)
        assert response.status_code in [200, 201, 401]


@pytest.mark.api
class TestFileEndpoints:
    """Testes dos endpoints de arquivos"""

    def test_list_files(self, client: TestClient, auth_headers):
        """Teste de listagem de arquivos"""
        response = client.get("/api/v1/files/", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_upload_file_endpoint_exists(self, client: TestClient, auth_headers):
        """Teste se endpoint de upload existe"""
        # Teste com arquivo vazio para verificar se endpoint existe
        response = client.post("/api/v1/files/upload", headers=auth_headers)
        assert response.status_code in [
            400,
            401,
            422,
        ]  # Bad request, unauthorized, or validation error


@pytest.mark.api
class TestMarketplaceEndpoints:
    """Testes dos endpoints do marketplace"""

    def test_list_templates(self, client: TestClient, auth_headers):
        """Teste de listagem de templates"""
        response = client.get("/api/v1/templates/", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_list_components(self, client: TestClient, auth_headers):
        """Teste de listagem de componentes"""
        response = client.get("/api/v1/marketplace/components/", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_get_template_by_id(self, client: TestClient, auth_headers):
        """Teste de obtenção de template por ID"""
        response = client.get("/api/v1/marketplace/templates/1", headers=auth_headers)
        assert response.status_code in [200, 401, 404]


@pytest.mark.api
class TestAnalyticsEndpoints:
    """Testes dos endpoints de analytics"""

    def test_analytics_overview(self, client: TestClient, auth_headers):
        """Teste do overview de analytics"""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "period" in data
            assert "user_metrics" in data
            assert "performance_metrics" in data
            assert "business_metrics" in data
            assert "trends" in data
            assert "anomalies" in data
            assert "generated_at" in data

    def test_analytics_metrics(self, client: TestClient, auth_headers):
        """Teste das métricas de analytics"""
        response = client.get(
            "/api/v1/analytics/metrics/business", headers=auth_headers
        )
        assert response.status_code in [200, 401, 403]


@pytest.mark.api
class TestLLMEndpoints:
    """Testes dos endpoints de LLM"""

    def test_list_llm_providers(self, client: TestClient, auth_headers):
        """Teste de listagem de provedores LLM"""
        response = client.get("/api/v1/llm/providers", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_list_llm_models(self, client: TestClient, auth_headers):
        """Teste de listagem de modelos LLM"""
        response = client.get("/api/v1/llm/models", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_llm_generate_endpoint(self, client: TestClient, auth_headers):
        """Teste do endpoint de geração LLM"""
        generate_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello, world!"}],
        }

        response = client.post(
            "/api/v1/llm/generate", json=generate_data, headers=auth_headers
        )
        assert response.status_code in [200, 401, 422]


@pytest.mark.api
class TestWorkspaceEndpoints:
    """Testes dos endpoints de workspaces - Nova Arquitetura Multi-Tenant"""

    def test_list_workspaces(self, client: TestClient, auth_headers):
        """Teste de listagem de workspaces retorna objetos plan via tenant"""
        response = client.get("/api/v1/workspaces/", headers=auth_headers)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

            # Se há workspaces, verificar nova estrutura do plan
            if data:
                workspace = data[0]
                # Verificar que plan_id não existe mais no response
                assert "plan_id" not in workspace
                assert "plan_name" not in workspace
                assert "plan_type" not in workspace

                # Se há plan, deve ser um objeto completo
                if "plan" in workspace and workspace["plan"]:
                    plan = workspace["plan"]
                    assert isinstance(plan, dict)
                    assert "id" in plan
                    assert "name" in plan
                    assert "type" in plan
                    assert "max_members_per_workspace" in plan

    def test_create_workspace(
        self, client: TestClient, sample_workspace_data, auth_headers
    ):
        """Teste de criação de workspace que herda plano do tenant"""
        response = client.post(
            "/api/v1/workspaces/", json=sample_workspace_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 401]

        if response.status_code in [200, 201]:
            data = response.json()

            # Verificar que response usa novo schema
            assert "plan_id" not in data  # Campo antigo removido

            # Se há plan, deve ser objeto completo
            if "plan" in data and data["plan"]:
                plan = data["plan"]
                assert isinstance(plan, dict)
                assert "id" in plan
                assert "name" in plan
                assert "max_members_per_workspace" in plan


@pytest.mark.api
class TestUserVariableEndpoints:
    """Testes dos endpoints de variáveis de usuário"""

    def test_list_user_variables(self, client: TestClient, auth_headers):
        """Teste de listagem de variáveis"""
        response = client.get("/api/v1/user-variables/", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_create_user_variable(self, client: TestClient, auth_headers):
        """Teste de criação de variável"""
        variable_data = {
            "key": f"test_variable_{uuid.uuid4().hex[:8]}",
            "value": "test_value",
            "description": "A test variable",
            "category": "general",
        }
        response = client.post(
            "/api/v1/user-variables/", json=variable_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 401]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["category"] == "general"


@pytest.mark.api
@pytest.mark.integration
class TestAPIIntegration:
    """Testes de integração da API"""

    @pytest.mark.asyncio
    async def test_api_endpoints_respond(self, async_client: AsyncClient):
        """Teste se todos os endpoints principais respondem"""
        endpoints = [
            "/api/v1/auth/auth/me",
            "/api/v1/workflows/",
            "/api/v1/agents/",
            "/api/v1/files/",
            "/api/v1/marketplace/templates/",
            "/api/v1/analytics/overview",
            "/api/v1/llm/providers",
            "/api/v1/workspaces/",
            "/api/v1/user-variables/",
        ]

        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            # Todos devem responder (mesmo que com 401)
            assert response.status_code < 500  # Não deve haver erro de servidor

    def test_api_documentation_accessible(self, client: TestClient):
        """Teste se documentação da API está acessível"""
        # Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200

        # ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200

        # OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
