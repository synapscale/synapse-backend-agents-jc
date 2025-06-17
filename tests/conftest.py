import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from fastapi.testclient import TestClient
import uuid
from synapse.models.user import User
from synapse.database import SessionLocal
import pytest_asyncio
from synapse.models.workflow import Workflow, WorkflowStatus
from synapse.models.node import Node, NodeType
from synapse.models.agent import Agent

from synapse.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_workflow_data():
    return {
        "name": "Workflow de Teste",
        "description": "Workflow criado para testes automatizados.",
        "category": "test",
        "tags": ["test", "automated"],
        "definition": {
            "nodes": [],
            "connections": []
        }
    }


@pytest.fixture(scope="session")
def auth_headers(client):
    # Dados do usuário de teste
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "username": "testuser"
    }
    # Tenta registrar (ignora se já existe)
    client.post("/api/v1/auth/register", json=user_data)
    # Faz login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200, f"Login falhou: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_workspace_data():
    return {
        "name": "Workspace de Teste",
        "description": "Workspace criado para testes automatizados.",
        "is_active": True
    }


import asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def async_client():
    from synapse.main import app
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest_asyncio.fixture
async def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest_asyncio.fixture
async def test_user(db_session):
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User(
        email=unique_email,
        username=unique_username,
        full_name="Test User",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    user.set_password("TestPassword123!")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

class TestUtils:
    def __init__(self, db_session):
        self.db = db_session

    async def create_test_workflow(self, db_session, user):
        workflow = Workflow(
            name=f"Test Workflow {uuid.uuid4().hex[:6]}",
            description="Workflow de teste",
            definition={"nodes": [], "connections": []},
            user_id=user.id,
            is_public=True,
            category="test",
            tags=["test"],
            version="1.0.0",
            status=WorkflowStatus.DRAFT,
        )
        db_session.add(workflow)
        db_session.commit()
        db_session.refresh(workflow)
        return workflow

    async def create_test_node(self, db_session, user):
        node = Node(
            name=f"Test Node {uuid.uuid4().hex[:6]}",
            category="test",
            type=NodeType.OPERATION.value,
            status="draft",
            user_id=user.id,
            version="1.0.0",
            definition={},
            code_template="# Código de exemplo",
            input_schema={},
            output_schema={},
            parameters_schema={},
            description="Node de teste",
            is_public=True,
            icon="🔧",
            color="#6366f1",
            documentation=None,
            examples=[],
        )
        db_session.add(node)
        db_session.commit()
        db_session.refresh(node)
        return node

    async def create_test_agent(self, db_session, user):
        agent = Agent(
            name=f"Test Agent {uuid.uuid4().hex[:6]}",
            provider="openai",
            model="gpt-3.5-turbo",
            user_id=user.id,
        )
        db_session.add(agent)
        db_session.commit()
        db_session.refresh(agent)
        return agent

@pytest_asyncio.fixture
async def test_utils(db_session):
    return TestUtils(db_session)

class MockWebSocket:
    async def accept(self):
        import asyncio; await asyncio.sleep(0)
    async def close(self, code=None):
        import asyncio; await asyncio.sleep(0)
    async def send_json(self, data):
        import asyncio; await asyncio.sleep(0)
    async def receive_json(self):
        import asyncio; await asyncio.sleep(0)
        return {}
    async def send_text(self, data):
        import asyncio; await asyncio.sleep(0)
    def __getattr__(self, name):
        print(f"[MockWebSocket] Método inesperado acessado: {name}")
        raise AttributeError(f"MockWebSocket não implementa '{name}'")

@pytest_asyncio.fixture
async def mock_websocket():
    return MockWebSocket()