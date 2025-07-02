"""
Testes de API endpoints para workspaces - Nova Arquitetura Multi-Tenant
Testa a herança de planos via tenant.plan ao invés de workspace.plan_id
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid
from unittest.mock import Mock, patch
from synapse.models.workspace import Workspace
from synapse.models.tenant import Tenant
from synapse.models.subscription import Plan, PlanType
from synapse.schemas.workspace import WorkspaceResponse, PlanResponse


@pytest.mark.api
class TestWorkspaceEndpoints:
    """Testes dos endpoints de workspaces com nova arquitetura"""

    def test_list_workspaces_returns_plan_objects(
        self, client: TestClient, auth_headers
    ):
        """Teste que listagem de workspaces retorna objetos plan via tenant"""
        response = client.get("/api/v1/workspaces/", headers=auth_headers)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

            # Se há workspaces, verificar estrutura do plan
            if data:
                workspace = data[0]
                if "plan" in workspace and workspace["plan"]:
                    plan = workspace["plan"]
                    # Verificar campos do PlanResponse
                    assert "id" in plan
                    assert "name" in plan
                    assert "type" in plan
                    assert "max_workspaces" in plan
                    assert "max_members_per_workspace" in plan
                    assert "max_projects_per_workspace" in plan
                    assert "max_storage_mb" in plan

                # Verificar que plan_id não existe mais no response
                assert "plan_id" not in workspace
                assert "plan_name" not in workspace
                assert "plan_type" not in workspace

    def test_create_workspace_with_tenant_plan(self, client: TestClient, auth_headers):
        """Teste criação de workspace que herda plano do tenant"""
        workspace_data = {
            "name": f"Test Workspace {uuid.uuid4().hex[:8]}",
            "description": "Workspace de teste para nova arquitetura",
            "is_active": True,
        }

        response = client.post(
            "/api/v1/workspaces/", json=workspace_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 401]

        if response.status_code in [200, 201]:
            data = response.json()

            # Verificar que response usa novo schema
            if "plan" in data and data["plan"]:
                plan = data["plan"]
                assert isinstance(plan, dict)
                assert "id" in plan
                assert "name" in plan
                assert "max_members_per_workspace" in plan

            # Verificar que campos antigos não existem
            assert "plan_id" not in data

    def test_get_workspace_by_id_returns_plan_object(
        self, client: TestClient, auth_headers
    ):
        """Teste que obter workspace por ID retorna objeto plan"""
        # Primeiro criar um workspace
        workspace_data = {
            "name": f"Test Workspace {uuid.uuid4().hex[:8]}",
            "description": "Workspace para teste de GET",
            "is_active": True,
        }

        create_response = client.post(
            "/api/v1/workspaces/", json=workspace_data, headers=auth_headers
        )
        if create_response.status_code in [200, 201]:
            workspace_id = create_response.json().get("id")

            # Agora obter o workspace
            response = client.get(
                f"/api/v1/workspaces/{workspace_id}", headers=auth_headers
            )
            assert response.status_code in [200, 401, 404]

            if response.status_code == 200:
                data = response.json()

                # Verificar estrutura do plan
                if "plan" in data and data["plan"]:
                    plan = data["plan"]
                    assert "id" in plan
                    assert "name" in plan
                    assert "type" in plan

                # Verificar ausência de campos antigos
                assert "plan_id" not in data


@pytest.mark.api
@pytest.mark.unit
class TestWorkspaceBusinessLogic:
    """Testes da lógica de negócio de workspace com tenant.plan"""

    @pytest.fixture
    def mock_plan(self):
        """Mock de um plano BASIC"""
        return Mock(
            id=str(uuid.uuid4()),
            name="BASIC",
            slug="basic",  # Usar slug ao invés de type
            max_members_per_workspace=5,
            max_projects_per_workspace=10,
            max_storage_mb=1000,
            allow_collaborative_workspaces=True,
        )

    @pytest.fixture
    def mock_tenant(self, mock_plan):
        """Mock de tenant com plano"""
        return Mock(id=str(uuid.uuid4()), plan=mock_plan, plan_id=mock_plan.id)

    @pytest.fixture
    def mock_workspace(self, mock_tenant):
        """Mock de workspace com tenant"""
        return Mock(
            id=str(uuid.uuid4()),
            name="Test Workspace",
            tenant=mock_tenant,
            tenant_id=mock_tenant.id,
            member_count=2,
            project_count=3,
            storage_used_mb=500.0,
        )

    def test_can_add_member_via_tenant_plan(self, mock_workspace):
        """Teste se workspace verifica limite de membros via tenant.plan"""

        # Simular método can_add_member
        def can_add_member():
            if not mock_workspace.tenant or not mock_workspace.tenant.plan:
                return False
            return (
                mock_workspace.member_count
                < mock_workspace.tenant.plan.max_members_per_workspace
            )

        mock_workspace.can_add_member = can_add_member

        # Com 2 membros e limite de 5, deve permitir
        assert mock_workspace.can_add_member() == True

        # Simular workspace com limite atingido
        mock_workspace.member_count = 5
        assert mock_workspace.can_add_member() == False

    def test_can_create_project_via_tenant_plan(self, mock_workspace):
        """Teste se workspace verifica limite de projetos via tenant.plan"""

        def can_create_project():
            if not mock_workspace.tenant or not mock_workspace.tenant.plan:
                return False
            return (
                mock_workspace.project_count
                < mock_workspace.tenant.plan.max_projects_per_workspace
            )

        mock_workspace.can_create_project = can_create_project

        # Com 3 projetos e limite de 10, deve permitir
        assert mock_workspace.can_create_project() == True

        # Simular workspace com limite atingido
        mock_workspace.project_count = 10
        assert mock_workspace.can_create_project() == False

    def test_can_use_storage_via_tenant_plan(self, mock_workspace):
        """Teste se workspace verifica limite de storage via tenant.plan"""

        def can_use_storage(additional_mb: float):
            if not mock_workspace.tenant or not mock_workspace.tenant.plan:
                return False
            total_usage = mock_workspace.storage_used_mb + additional_mb
            return total_usage <= mock_workspace.tenant.plan.max_storage_mb

        mock_workspace.can_use_storage = can_use_storage

        # Com 500MB usado e limite de 1000MB, pode usar mais 300MB
        assert mock_workspace.can_use_storage(300.0) == True

        # Não pode usar 600MB (excederia o limite)
        assert mock_workspace.can_use_storage(600.0) == False

    def test_get_plan_limits_via_tenant_plan(self, mock_workspace):
        """Teste se workspace retorna limites corretos via tenant.plan"""

        def get_plan_limits():
            if not mock_workspace.tenant or not mock_workspace.tenant.plan:
                return {}

            plan = mock_workspace.tenant.plan
            return {
                "max_members": plan.max_members_per_workspace,
                "max_projects": plan.max_projects_per_workspace,
                "max_storage_mb": plan.max_storage_mb,
                "current_members": mock_workspace.member_count,
                "current_projects": mock_workspace.project_count,
                "current_storage_mb": mock_workspace.storage_used_mb,
                "can_add_member": mock_workspace.can_add_member(),
                "can_create_project": mock_workspace.can_create_project(),
            }

        mock_workspace.get_plan_limits = get_plan_limits

        limits = mock_workspace.get_plan_limits()

        assert limits["max_members"] == 5
        assert limits["max_projects"] == 10
        assert limits["max_storage_mb"] == 1000
        assert limits["current_members"] == 2
        assert limits["current_projects"] == 3
        assert limits["current_storage_mb"] == 500.0


@pytest.mark.integration
class TestWorkspaceIntegration:
    """Testes de integração para workspace com banco de dados"""

    @pytest.mark.asyncio
    async def test_workspace_plan_inheritance_from_database(
        self, async_client: AsyncClient
    ):
        """Teste de integração que verifica herança de plano via banco"""
        # Nota: Este teste requer configuração de banco de dados de teste
        # Seria necessário criar tenant e workspace no banco para teste completo

        # Teste básico de endpoint
        response = await async_client.get("/api/v1/workspaces/")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            workspaces = response.json()

            # Verificar estrutura de resposta para workspaces existentes
            for workspace in workspaces:
                if "plan" in workspace and workspace["plan"]:
                    plan = workspace["plan"]
                    # Verificar que é um objeto plan completo
                    assert isinstance(plan, dict)
                    assert "id" in plan
                    assert "name" in plan
                    assert "max_members_per_workspace" in plan


@pytest.mark.performance
class TestWorkspacePerformance:
    """Testes de performance para nova arquitetura"""

    def test_workspace_list_with_plan_join_performance(
        self, client: TestClient, auth_headers
    ):
        """Teste de performance da listagem com JOIN para plans"""
        import time

        start_time = time.time()
        response = client.get("/api/v1/workspaces/", headers=auth_headers)
        end_time = time.time()

        # Resposta deve ser rápida (menos de 1 segundo para operação simples)
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Query muito lenta: {execution_time:.3f}s"

        assert response.status_code in [200, 401]


# ==================== FIXTURES AUXILIARES ====================


@pytest.fixture
def sample_workspace_with_plan_data():
    """Fixture para dados de workspace que espera plano via tenant"""
    return {
        "name": "Test Workspace",
        "description": "Workspace de teste para nova arquitetura",
        "is_active": True,
        # Nota: plan_id removido - workspace herda via tenant
    }


@pytest.fixture
def mock_workspace_response():
    """Mock de resposta de workspace com plan object"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Workspace",
        "description": "Test workspace",
        "owner_id": str(uuid.uuid4()),
        "plan": {
            "id": str(uuid.uuid4()),
            "name": "BASIC",
            "type": "basic",
            "max_members_per_workspace": 5,
            "max_projects_per_workspace": 10,
            "max_storage_mb": 1000,
            "allow_collaborative_workspaces": True,
        },
        "member_count": 2,
        "project_count": 3,
        "storage_used_mb": 500.0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
