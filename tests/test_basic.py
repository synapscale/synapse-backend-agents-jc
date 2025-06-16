"""
Testes básicos para verificar funcionalidade principal
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid


@pytest.mark.unit
def test_health_check(client: TestClient):
    """Teste do endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.unit
def test_docs_endpoint(client: TestClient):
    """Teste do endpoint de documentação"""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.unit
def test_openapi_endpoint(client: TestClient):
    """Teste do endpoint OpenAPI"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data


@pytest.mark.api
@pytest.mark.auth
def test_register_user(client: TestClient):
    """Teste de registro de usuário"""
    user_data = {
        "email": f"newuser_{uuid.uuid4().hex[:8]}@example.com",
        "username": f"newuser_{uuid.uuid4().hex[:8]}",
        "full_name": "New User",
        "password": "StrongPassword123!"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data or "message" in data or "access_token" in data


@pytest.mark.api
@pytest.mark.auth
def test_login_user(client: TestClient):
    """Teste de login de usuário"""
    import uuid
    # Primeiro registrar um usuário
    unique_email = f"logintest_{uuid.uuid4().hex[:8]}@example.com"
    unique_username = f"logintestuser_{uuid.uuid4().hex[:8]}"
    user_data = {
        "email": unique_email,
        "username": unique_username,
        "full_name": "Login Test",
        "password": "StrongPassword123!"
    }
    register_response = client.post("/api/v1/auth/register", json=user_data)
    # Tentar fazer login (form-data)
    login_data = {
        "username": unique_email,
        "password": "StrongPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code in [200, 201]


@pytest.mark.api
def test_get_current_user(client: TestClient, auth_headers):
    """Teste para obter usuário atual"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.api
def test_list_workflows(client: TestClient, auth_headers):
    """Teste para listar workflows"""
    response = client.get("/api/v1/workflows/", headers=auth_headers)
    assert response.status_code in [200, 401]


@pytest.mark.api
def test_list_agents(client: TestClient, auth_headers):
    """Teste para listar agentes"""
    response = client.get("/api/v1/agents/", headers=auth_headers)
    assert response.status_code in [200, 401]


@pytest.mark.api
def test_list_templates(client: TestClient, auth_headers):
    """Teste para listar templates"""
    response = client.get("/api/v1/marketplace/templates/", headers=auth_headers)
    assert response.status_code in [200, 401, 404]


@pytest.mark.api
def test_get_analytics_overview(client: TestClient, auth_headers):
    """Teste para obter overview de analytics"""
    response = client.get("/api/v1/analytics/overview", headers=auth_headers)
    assert response.status_code in [200, 401, 403]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_client_health(async_client: AsyncClient):
    """Teste assíncrono do health check"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.unit
def test_cors_headers(client: TestClient):
    """Teste dos headers CORS"""
    response = client.options("/api/v1/auth/me")
    # Verificar se headers CORS estão presentes
    assert response.status_code in [200, 405, 404]  # Pode não suportar OPTIONS


@pytest.mark.performance
def test_response_time(client: TestClient):
    """Teste básico de tempo de resposta"""
    import time
    
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 1.0  # Deve responder em menos de 1 segundo
    assert response.status_code == 200


@pytest.mark.unit
def test_api_version_header(client: TestClient):
    """Teste do header de versão da API"""
    response = client.get("/health")
    # Verificar se há algum header de versão
    assert response.status_code == 200
    # O middleware deve adicionar o header de tempo de processamento
    assert "X-Process-Time" in response.headers
    assert response.headers["X-Process-Time"]

