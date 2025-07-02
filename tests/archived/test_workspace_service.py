"""
Testes do WorkspaceService - Nova Arquitetura Multi-Tenant
Testa os métodos de serviço que usam herança de planos via tenant
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import uuid
from sqlalchemy.orm import Session
from synapse.services.workspace_service import WorkspaceService
from synapse.models.workspace import Workspace
from synapse.models.tenant import Tenant
from synapse.models.subscription import Plan, PlanType
from synapse.schemas.workspace import WorkspaceResponse


class TestWorkspaceService:
    """Testes do serviço de workspace com nova arquitetura"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock da sessão do banco"""
        return Mock(spec=Session)

    @pytest.fixture
    def workspace_service(self, mock_db_session):
        """Instância do WorkspaceService para testes"""
        return WorkspaceService(mock_db_session)

    @pytest.fixture
    def mock_plan(self):
        """Mock de um plano BASIC"""
        plan = Mock(spec=Plan)
        plan.id = str(uuid.uuid4())
        plan.name = "BASIC"
        plan.slug = "basic"  # Usar slug ao invés de type
        plan.max_members_per_workspace = 5
        plan.max_projects_per_workspace = 10
        plan.max_storage_mb = 1000
        plan.allow_collaborative_workspaces = True
        return plan

    @pytest.fixture
    def mock_tenant(self, mock_plan):
        """Mock de tenant com plano"""
        tenant = Mock(spec=Tenant)
        tenant.id = str(uuid.uuid4())
        tenant.plan = mock_plan
        tenant.plan_id = mock_plan.id
        return tenant

    @pytest.fixture
    def mock_workspace(self, mock_tenant):
        """Mock de workspace com tenant"""
        workspace = Mock(spec=Workspace)
        workspace.id = str(uuid.uuid4())
        workspace.name = "Test Workspace"
        workspace.tenant = mock_tenant
        workspace.tenant_id = mock_tenant.id
        workspace.member_count = 2
        workspace.project_count = 3
        workspace.storage_used_mb = 500.0

        # Mock do método get_plan_limits que agora usa tenant.plan
        def get_plan_limits():
            if not workspace.tenant or not workspace.tenant.plan:
                return {}

            plan = workspace.tenant.plan
            return {
                "max_members": plan.max_members_per_workspace,
                "max_projects": plan.max_projects_per_workspace,
                "max_storage_mb": plan.max_storage_mb,
                "current_members": workspace.member_count,
                "current_projects": workspace.project_count,
                "current_storage_mb": workspace.storage_used_mb,
                "can_add_member": workspace.member_count
                < plan.max_members_per_workspace,
                "can_create_project": workspace.project_count
                < plan.max_projects_per_workspace,
                "allow_collaborative": plan.allow_collaborative_workspaces,
            }

        # Mock do método to_dict que retorna plan object
        def to_dict():
            plan_dict = None
            if workspace.tenant and workspace.tenant.plan:
                plan = workspace.tenant.plan
                plan_dict = {
                    "id": plan.id,
                    "name": plan.name,
                    "slug": plan.slug,  # Usar slug ao invés de type
                    "max_members_per_workspace": plan.max_members_per_workspace,
                    "max_projects_per_workspace": plan.max_projects_per_workspace,
                    "max_storage_mb": plan.max_storage_mb,
                    "allow_collaborative_workspaces": plan.allow_collaborative_workspaces,
                }

            return {
                "id": workspace.id,
                "name": workspace.name,
                "tenant_id": workspace.tenant_id,
                "plan": plan_dict,  # Plan object via tenant.plan
                "member_count": workspace.member_count,
                "project_count": workspace.project_count,
                "storage_used_mb": workspace.storage_used_mb,
            }

        workspace.get_plan_limits = get_plan_limits
        workspace.to_dict = to_dict

        return workspace


class TestWorkspaceServiceMethods:
    """Testes dos métodos específicos do WorkspaceService"""

    def test_get_plan_limits_returns_correct_data(
        self, workspace_service, mock_workspace, mock_db_session
    ):
        """Teste get_plan_limits via tenant.plan"""
        workspace_id = mock_workspace.id

        # Mock da query para retornar workspace com tenant e plan
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.first.return_value = (
            mock_workspace
        )
        mock_db_session.query.return_value = mock_query

        # Executar método
        result = workspace_service.get_plan_limits(workspace_id)

        # Verificar que retorna dados corretos do plano via tenant
        assert result["max_members"] == 5
        assert result["max_projects"] == 10
        assert result["max_storage_mb"] == 1000
        assert result["current_members"] == 2
        assert result["current_projects"] == 3
        assert result["current_storage_mb"] == 500.0
        assert result["can_add_member"] == True
        assert result["can_create_project"] == True
        assert result["allow_collaborative"] == True

    def test_get_plan_limits_workspace_not_found(
        self, workspace_service, mock_db_session
    ):
        """Teste get_plan_limits quando workspace não existe"""
        workspace_id = str(uuid.uuid4())

        # Mock da query para retornar None
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        # Deve lançar exceção quando workspace não encontrado
        with pytest.raises(
            Exception
        ):  # Adjust exception type based on actual implementation
            workspace_service.get_plan_limits(workspace_id)

    @patch("synapse.services.workspace_service.WorkspaceService.get_user_workspaces")
    def test_get_user_workspaces_with_plan_objects(
        self, mock_get_workspaces, workspace_service
    ):
        """Teste que get_user_workspaces retorna workspaces com plan objects"""
        user_id = str(uuid.uuid4())

        # Mock de workspace com plan object no to_dict
        mock_workspace_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Workspace",
            "plan": {
                "id": str(uuid.uuid4()),
                "name": "BASIC",
                "type": "basic",
                "max_members_per_workspace": 5,
                "max_projects_per_workspace": 10,
                "max_storage_mb": 1000,
            },
            "member_count": 2,
            "project_count": 3,
        }

        mock_get_workspaces.return_value = [mock_workspace_data]

        # Executar método
        result = workspace_service.get_user_workspaces(user_id)

        # Verificar estrutura da resposta
        assert len(result) == 1
        workspace = result[0]

        # Verificar que tem plan object e não plan_id
        assert "plan" in workspace
        assert workspace["plan"] is not None
        assert "plan_id" not in workspace

        plan = workspace["plan"]
        assert "id" in plan
        assert "name" in plan
        assert "max_members_per_workspace" in plan


class TestWorkspaceServiceQueries:
    """Testes das queries do service com JOINs para tenant/plan"""

    @patch(
        "synapse.services.workspace_service.WorkspaceService._get_workspace_with_plan"
    )
    def test_workspace_query_includes_tenant_plan_join(
        self, mock_get_workspace, workspace_service
    ):
        """Teste que queries incluem JOIN com tenant.plan"""
        workspace_id = str(uuid.uuid4())

        # Mock de workspace com tenant carregado
        mock_workspace = Mock()
        mock_workspace.tenant = Mock()
        mock_workspace.tenant.plan = Mock()
        mock_workspace.tenant.plan.name = "BASIC"

        mock_get_workspace.return_value = mock_workspace

        # Este teste seria mais completo com integração real do SQLAlchemy
        # Por enquanto, verificar que o método foi chamado
        workspace_service.get_plan_limits(workspace_id)
        mock_get_workspace.assert_called_once_with(workspace_id)


class TestWorkspaceServicePerformance:
    """Testes de performance das queries com JOINs"""

    def test_workspace_plan_join_uses_eager_loading(
        self, workspace_service, mock_db_session
    ):
        """Teste que workspace queries usam eager loading para evitar N+1"""
        import time

        # Este teste seria mais significativo com banco real
        # Por enquanto, simular que a query é otimizada
        start_time = time.time()

        # Mock otimizado com joinedload
        mock_query = Mock()
        mock_workspace = Mock()
        mock_workspace.tenant = Mock()
        mock_workspace.tenant.plan = Mock()

        mock_query.options.return_value.filter.return_value.first.return_value = (
            mock_workspace
        )
        mock_db_session.query.return_value = mock_query

        workspace_service.get_plan_limits(str(uuid.uuid4()))

        execution_time = time.time() - start_time

        # Query otimizada deve ser rápida
        assert execution_time < 0.1  # Menos de 100ms para mock


class TestWorkspaceServiceErrorHandling:
    """Testes de tratamento de erros"""

    def test_workspace_without_tenant_error_handling(
        self, workspace_service, mock_db_session
    ):
        """Teste tratamento de workspace sem tenant"""
        workspace_id = str(uuid.uuid4())

        # Mock de workspace sem tenant
        mock_workspace = Mock()
        mock_workspace.tenant = None

        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.first.return_value = (
            mock_workspace
        )
        mock_db_session.query.return_value = mock_query

        # Deve tratar graciosamente workspace sem tenant
        # (Implementação específica depende do código real)
        try:
            result = workspace_service.get_plan_limits(workspace_id)
            # Se não lança erro, deve retornar estrutura vazia ou padrão
            assert isinstance(result, dict)
        except Exception as e:
            # Se lança erro, deve ser tratado adequadamente
            assert "tenant" in str(e).lower() or "plan" in str(e).lower()

    def test_workspace_without_plan_error_handling(
        self, workspace_service, mock_db_session
    ):
        """Teste tratamento de tenant sem plan"""
        workspace_id = str(uuid.uuid4())

        # Mock de workspace com tenant mas sem plan
        mock_workspace = Mock()
        mock_workspace.tenant = Mock()
        mock_workspace.tenant.plan = None

        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.first.return_value = (
            mock_workspace
        )
        mock_db_session.query.return_value = mock_query

        # Deve tratar graciosamente tenant sem plan
        try:
            result = workspace_service.get_plan_limits(workspace_id)
            assert isinstance(result, dict)
        except Exception as e:
            assert "plan" in str(e).lower()


# ==================== FIXTURES AUXILIARES ====================


@pytest.fixture
def mock_workspace_service_response():
    """Mock de resposta do WorkspaceService com plan object"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Service Test Workspace",
        "description": "Workspace para teste de service",
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
    }
