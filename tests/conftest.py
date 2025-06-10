"""
Configuração de testes para SynapScale
Implementação completa de testes automatizados
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.synapse.core.auth import get_current_user
from src.synapse.core.cache import CacheConfig, CacheManager, get_cache_manager
from src.synapse.database import Base, get_db

# Importações do projeto
from src.synapse.main import app
from src.synapse.models.user import User

# Configuração do banco de dados de teste
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Engine de teste
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

# Session maker de teste
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator:
    """Setup do banco de dados de teste"""
    # Criar todas as tabelas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Limpar banco após testes
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Sessão de banco de dados para testes"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override da dependência de banco de dados"""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Usuário de teste"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_here",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def override_get_current_user(test_user: User):
    """Override da dependência de usuário atual"""

    async def _override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = _override_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db, override_get_current_user) -> TestClient:
    """Cliente de teste síncrono"""
    return TestClient(app)


@pytest.fixture
async def async_client(
    override_get_db, override_get_current_user
) -> AsyncGenerator[AsyncClient, None]:
    """Cliente de teste assíncrono"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def cache_manager() -> AsyncGenerator[CacheManager, None]:
    """Gerenciador de cache para testes"""
    config = CacheConfig(
        redis_url="redis://localhost:6379/1",  # DB diferente para testes
        default_ttl=300,
        max_memory_cache_size=100,
    )

    cache = CacheManager(config)
    await cache.initialize()

    # Override da dependência
    app.dependency_overrides[get_cache_manager] = lambda: cache

    yield cache

    # Limpar cache após teste
    await cache.clear()
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock do Redis para testes sem dependência externa"""
    mock = AsyncMock()
    mock.ping.return_value = True
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.keys.return_value = []
    mock.info.return_value = {"used_memory": 1024}
    return mock


@pytest.fixture
def mock_llm_client():
    """Mock do cliente LLM para testes"""
    mock = AsyncMock()
    mock.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(content="Test response from LLM", role="assistant"),
                finish_reason="stop",
            )
        ],
        usage=Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    return mock


@pytest.fixture
def mock_websocket():
    """Mock do WebSocket para testes"""
    mock = AsyncMock()
    mock.accept.return_value = None
    mock.send_text.return_value = None
    mock.send_json.return_value = None
    mock.receive_text.return_value = '{"type": "ping"}'
    mock.receive_json.return_value = {"type": "ping"}
    mock.close.return_value = None
    return mock


# Fixtures para dados de teste


@pytest.fixture
def sample_workflow_data():
    """Dados de exemplo para workflow"""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for testing purposes",
        "is_active": True,
        "nodes": [
            {
                "name": "Start Node",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "config": {},
            },
            {
                "name": "LLM Node",
                "type": "llm",
                "position": {"x": 200, "y": 0},
                "config": {"model": "gpt-3.5-turbo", "prompt": "Hello, world!"},
            },
        ],
    }


@pytest.fixture
def sample_template_data():
    """Dados de exemplo para template"""
    return {
        "name": "Test Template",
        "description": "A test template",
        "category": "automation",
        "tags": ["test", "automation"],
        "is_public": True,
        "license": "free",
        "workflow_data": {"nodes": [], "edges": []},
    }


@pytest.fixture
def sample_marketplace_component():
    """Dados de exemplo para componente do marketplace"""
    return {
        "name": "Test Component",
        "description": "A test component for marketplace",
        "category": "automation",
        "type": "workflow",
        "price": 0.0,
        "is_free": True,
        "tags": ["test", "component"],
        "component_data": {"nodes": [], "config": {}},
    }


@pytest.fixture
def sample_workspace_data():
    """Dados de exemplo para workspace"""
    return {
        "name": "Test Workspace",
        "description": "A test workspace for collaboration",
        "is_public": False,
        "settings": {"allow_public_projects": False, "require_approval": True},
    }


@pytest.fixture
def sample_analytics_event():
    """Dados de exemplo para evento de analytics"""
    return {
        "event_type": "user_action",
        "event_name": "workflow_executed",
        "properties": {"workflow_id": 1, "execution_time": 1.5, "success": True},
        "user_agent": "test-client",
        "ip_address": "127.0.0.1",
    }


# Utilitários para testes


class TestUtils:
    """Utilitários para testes"""

    @staticmethod
    async def create_test_workflow(
        db_session: AsyncSession, user: User, data: dict = None
    ):
        """Cria workflow de teste"""
        from src.synapse.models.workflow import Workflow

        workflow_data = data or {
            "name": "Test Workflow",
            "description": "Test workflow",
            "is_active": True,
        }

        workflow = Workflow(user_id=user.id, **workflow_data)

        db_session.add(workflow)
        await db_session.commit()
        await db_session.refresh(workflow)
        return workflow

    @staticmethod
    async def create_test_execution(
        db_session: AsyncSession, workflow, data: dict = None
    ):
        """Cria execução de teste"""
        from src.synapse.models.workflow_execution import (
            ExecutionStatus,
            WorkflowExecution,
        )

        execution_data = data or {
            "status": ExecutionStatus.PENDING,
            "config": {},
            "metadata": {},
        }

        execution = WorkflowExecution(
            workflow_id=workflow.id, user_id=workflow.user_id, **execution_data
        )

        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)
        return execution

    @staticmethod
    async def create_test_template(
        db_session: AsyncSession, user: User, data: dict = None
    ):
        """Cria template de teste"""
        from src.synapse.models.template import (
            TemplateLicense,
            TemplateStatus,
            WorkflowTemplate,
        )

        template_data = data or {
            "name": "Test Template",
            "description": "Test template",
            "category": "automation",
            "status": TemplateStatus.PUBLISHED,
            "license": TemplateLicense.FREE,
            "is_public": True,
            "workflow_data": {},
        }

        template = WorkflowTemplate(author_id=user.id, **template_data)

        db_session.add(template)
        await db_session.commit()
        await db_session.refresh(template)
        return template

    @staticmethod
    async def create_test_agent(
        db_session: AsyncSession, user: User, data: dict = None
    ):
        """Cria agente de teste"""
        from src.synapse.models.agent import Agent, AgentType

        agent_data = data or {
            "name": "Test Agent",
            "description": "Agent for tests",
            "agent_type": AgentType.ASSISTANT,
            "model_provider": "openai",
            "model_name": "gpt-3.5-turbo",
        }

        agent = Agent(user_id=user.id, **agent_data)
        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)
        return agent

    @staticmethod
    async def create_test_node(db_session: AsyncSession, user: User, data: dict = None):
        """Cria node de teste"""
        from src.synapse.models.node import Node, NodeType

        node_data = data or {
            "name": "Test Node",
            "description": "Node for tests",
            "type": NodeType.LLM,
            "category": "test",
            "code_template": "print('hello')",
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {"type": "object", "properties": {}},
        }

        node = Node(user_id=user.id, **node_data)
        db_session.add(node)
        await db_session.commit()
        await db_session.refresh(node)
        return node


@pytest.fixture
def test_utils():
    """Fixture para utilitários de teste"""
    return TestUtils


# Markers personalizados para organização dos testes


def pytest_configure(config):
    """Configuração personalizada do pytest"""
    config.addinivalue_line("markers", "unit: marca testes unitários")
    config.addinivalue_line("markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "performance: marca testes de performance")
    config.addinivalue_line("markers", "slow: marca testes lentos")
    config.addinivalue_line("markers", "auth: marca testes de autenticação")
    config.addinivalue_line("markers", "database: marca testes de banco de dados")
    config.addinivalue_line("markers", "api: marca testes de API")
    config.addinivalue_line("markers", "websocket: marca testes de WebSocket")
    config.addinivalue_line("markers", "cache: marca testes de cache")


# Configuração de logging para testes
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Desabilitar logs verbosos durante testes
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
