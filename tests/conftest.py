import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import pytest
from fastapi.testclient import TestClient
import uuid
from synapse.models.user import User
from synapse.database import SessionLocal
import pytest_asyncio
from synapse.models.workflow import Workflow, WorkflowStatus
from synapse.models.node import Node, NodeType
from synapse.models.agent import Agent
from sqlalchemy.orm import Session

# Import services
from synapse.services.user_service import UserService
from synapse.services.workspace_service import WorkspaceService
from synapse.services.tenant_service import TenantService

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
        "definition": {"nodes": [], "connections": []},
    }


@pytest.fixture(scope="session")
def auth_headers(client):
    # Dados do usuário de teste
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "username": "testuser",
    }
    # Tenta registrar (ignora se já existe)
    client.post("/api/v1/auth/register", json=user_data)
    # Faz login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200, f"Login falhou: {response.text}"
    response_data = response.json()
    # Handle new response format with data wrapper
    if "data" in response_data and "access_token" in response_data["data"]:
        token = response_data["data"]["access_token"]
    else:
        token = response_data["access_token"]  # Fallback to old format
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_workspace_data():
    """Dados de workspace para nova arquitetura - herda plano via tenant"""
    return {
        "name": "Workspace de Teste",
        "description": "Workspace criado para testes automatizados.",
        "is_active": True,
        # Nota: plan_id removido - workspace herda plano via tenant.plan
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
async def test_user(test_db_session):
    """Create a test user using the service layer pattern"""
    from synapse.models.user import User

    # Create user through service pattern with proper validation
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"

    # Validate required fields
    if not unique_email:
        raise ValueError("Email is required")
    if not unique_username:
        raise ValueError("Username is required")

    # Check for existing email
    existing_user = (
        test_db_session.query(User).filter(User.email == unique_email).first()
    )
    if existing_user:
        raise ValueError("Email already exists")

    # Check for existing username
    existing_username = (
        test_db_session.query(User).filter(User.username == unique_username).first()
    )
    if existing_username:
        raise ValueError("Username already exists")

    user = User(
        email=unique_email,
        username=unique_username,
        full_name="Test User",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    user.set_password("TestPassword123!")
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


class TestUtils:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def create_test_user(
        self, email: str = "test@example.com", username: str = "testuser", **kwargs
    ):
        """Create a test user using proper validation"""
        user_data = {
            "email": email,
            "username": username,
            "full_name": kwargs.get("full_name", "Test User"),
            "hashed_password": kwargs.get("hashed_password", "hashed_password"),
        }
        user_data.update(kwargs)

        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def create_test_workflow(
        self, name: str = "Test Workflow", user_id: str = None, **kwargs
    ):
        """Create a test workflow using proper validation"""
        workflow_data = {
            "name": name,
            "user_id": user_id,
            "status": kwargs.get("status", WorkflowStatus.DRAFT),
            "description": kwargs.get("description", "Test workflow description"),
        }
        workflow_data.update(kwargs)

        workflow = Workflow(**workflow_data)
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    async def create_test_node(
        self, name: str = "Test Node", workflow_id: str = None, **kwargs
    ):
        """Create a test node using proper validation"""
        node_data = {
            "name": name,
            "workflow_id": workflow_id,
            "type": kwargs.get("type", NodeType.LLM),
            "description": kwargs.get("description", "Test node description"),
        }
        node_data.update(kwargs)

        node = Node(**node_data)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    async def create_test_agent(self, user_id: str = None, **kwargs):
        """Create a test agent using proper validation"""
        agent_data = {
            "name": kwargs.get("name", "Test Agent"),
            "user_id": user_id,
            "description": kwargs.get("description", "Test agent description"),
            "type": kwargs.get("type", "default"),
        }
        agent_data.update(kwargs)

        agent = Agent(**agent_data)
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent


@pytest_asyncio.fixture
async def test_utils(db_session):
    return TestUtils(db_session)


class MockWebSocket:
    async def accept(self):
        import asyncio

        await asyncio.sleep(0)

    async def close(self, code=None):
        import asyncio

        await asyncio.sleep(0)

    async def send_json(self, data):
        import asyncio

        await asyncio.sleep(0)

    async def receive_json(self):
        import asyncio

        await asyncio.sleep(0)
        return {}

    async def send_text(self, data):
        import asyncio

        await asyncio.sleep(0)

    def __getattr__(self, name):
        print(f"[MockWebSocket] Método inesperado acessado: {name}")
        raise AttributeError(f"MockWebSocket não implementa '{name}'")


@pytest_asyncio.fixture
async def mock_websocket():
    return MockWebSocket()


# Service fixtures for consistent service layer testing
@pytest.fixture
def user_service(test_db_session):
    """Fixture to provide UserService instance"""

    # Create a sync wrapper for UserService until full async migration
    class SyncUserService:
        def __init__(self, db: Session):
            self.db = db

        def create_user(
            self, email: str, username: str, password: str, full_name: str, **kwargs
        ) -> User:
            """Create a new user with validation and business logic."""
            # Validate required fields
            if not email:
                raise ValueError("Email is required")
            if not username:
                raise ValueError("Username is required")
            if not password:
                raise ValueError("Password is required")
            if not full_name:
                raise ValueError("Full name is required")

            # Validate email uniqueness
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                raise ValueError("Email already exists")

            # Validate username uniqueness
            existing_username = (
                self.db.query(User).filter(User.username == username).first()
            )
            if existing_username:
                raise ValueError("Username already exists")

            # Create user instance
            user = User(email=email, username=username, full_name=full_name, **kwargs)
            user.set_password(password)

            # Save to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            return user

        def update_user(self, user_id: str, **updates) -> User:
            """Update user with new data"""
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            self.db.commit()
            self.db.refresh(user)
            return user

        def get_by_email(self, email: str) -> User:
            """Get user by email address."""
            return self.db.query(User).filter(User.email == email).first()

        def get_by_username(self, username: str) -> User:
            """Get user by username."""
            return self.db.query(User).filter(User.username == username).first()

    return SyncUserService(test_db_session)


@pytest.fixture
def workspace_service(test_db_session):
    """Fixture to provide WorkspaceService instance"""

    class SyncWorkspaceService:
        def __init__(self, db: Session):
            self.db = db

        def create_workspace(
            self, name: str, tenant_id: str, owner_id: str, **kwargs
        ) -> Workspace:
            """Create a new workspace with validation and business logic."""
            # Validate name uniqueness within tenant
            existing_workspace = (
                self.db.query(Workspace)
                .filter(Workspace.name == name, Workspace.tenant_id == tenant_id)
                .first()
            )
            if existing_workspace:
                raise ValueError("Workspace name already exists in this tenant")

            workspace = Workspace(
                name=name, tenant_id=tenant_id, owner_id=owner_id, **kwargs
            )
            self.db.add(workspace)
            self.db.commit()
            self.db.refresh(workspace)
            return workspace

        def get_workspace_by_id(self, workspace_id: str) -> Workspace:
            """Get workspace by ID"""
            return self.db.query(Workspace).filter(Workspace.id == workspace_id).first()

        def update_workspace(self, workspace_id: str, **updates) -> Workspace:
            """Update workspace with new data"""
            workspace = self.get_workspace_by_id(workspace_id)
            if not workspace:
                raise ValueError("Workspace not found")

            for key, value in updates.items():
                if hasattr(workspace, key):
                    setattr(workspace, key, value)

            self.db.commit()
            self.db.refresh(workspace)
            return workspace

    return SyncWorkspaceService(test_db_session)


@pytest.fixture
def tenant_service(test_db_session):
    """Fixture to provide TenantService instance"""

    class SyncTenantService:
        def __init__(self, db: Session):
            self.db = db

        def create_tenant(self, name: str, **kwargs) -> Tenant:
            """Create a new tenant with validation and business logic."""
            # Validate name uniqueness
            existing_tenant = self.db.query(Tenant).filter(Tenant.name == name).first()
            if existing_tenant:
                raise ValueError("Tenant name already exists")

            tenant = Tenant(name=name, **kwargs)
            self.db.add(tenant)
            self.db.commit()
            self.db.refresh(tenant)
            return tenant

        def get_tenant_by_id(self, tenant_id: str) -> Tenant:
            """Get tenant by ID"""
            return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()

        def update_tenant(self, tenant_id: str, **updates) -> Tenant:
            """Update tenant with new data"""
            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                raise ValueError("Tenant not found")

            for key, value in updates.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)

            self.db.commit()
            self.db.refresh(tenant)
            return tenant

    return SyncTenantService(test_db_session)


@pytest.fixture
def conversation_service(test_db_session):
    """Fixture to provide ConversationService instance"""
    from synapse.models.conversation import Conversation

    class SyncConversationService:
        def __init__(self, db: Session):
            self.db = db

        def create_conversation(
            self, user_id: str, agent_id: str, **kwargs
        ) -> Conversation:
            """Create a new conversation with validation and business logic."""
            conversation = Conversation(user_id=user_id, agent_id=agent_id, **kwargs)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation

        def get_conversation_by_id(self, conversation_id: str) -> Conversation:
            """Get conversation by ID"""
            return (
                self.db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

        def update_conversation(self, conversation_id: str, **updates) -> Conversation:
            """Update conversation with new data"""
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")

            for key, value in updates.items():
                if hasattr(conversation, key):
                    setattr(conversation, key, value)

            self.db.commit()
            self.db.refresh(conversation)
            return conversation

    return SyncConversationService(test_db_session)


@pytest.fixture
def plan_service(test_db_session):
    """Fixture to provide PlanService instance"""
    from synapse.models.subscription import Plan

    class SyncPlanService:
        def __init__(self, db: Session):
            self.db = db

        def create_plan(self, name: str, price: float, **kwargs) -> Plan:
            """Create a new plan with validation and business logic."""
            plan = Plan(name=name, price=price, **kwargs)
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            return plan

        def get_plan_by_id(self, plan_id: str) -> Plan:
            """Get plan by ID"""
            return self.db.query(Plan).filter(Plan.id == plan_id).first()

    return SyncPlanService(test_db_session)


@pytest.fixture
def subscription_service(test_db_session):
    """Fixture to provide SubscriptionService instance"""
    from synapse.models.subscription import UserSubscription

    class SyncSubscriptionService:
        def __init__(self, db: Session):
            self.db = db

        def create_subscription(
            self, user_id: str, plan_id: str, **kwargs
        ) -> UserSubscription:
            """Create a new subscription with validation and business logic."""
            subscription = UserSubscription(user_id=user_id, plan_id=plan_id, **kwargs)
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription

        def get_subscription_by_id(self, subscription_id: str) -> UserSubscription:
            """Get subscription by ID"""
            return (
                self.db.query(UserSubscription)
                .filter(UserSubscription.id == subscription_id)
                .first()
            )

    return SyncSubscriptionService(test_db_session)


@pytest.fixture
def activity_service(test_db_session):
    """Fixture to provide ActivityService instance"""
    from synapse.models.workspace_activity import WorkspaceActivity

    class SyncActivityService:
        def __init__(self, db: Session):
            self.db = db

        def create_activity(
            self, workspace_id: str, user_id: str, action: str, **kwargs
        ) -> WorkspaceActivity:
            """Create a new activity with validation and business logic."""
            activity = WorkspaceActivity(
                workspace_id=workspace_id, user_id=user_id, action=action, **kwargs
            )
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            return activity

        def get_activity_by_id(self, activity_id: str) -> WorkspaceActivity:
            """Get activity by ID"""
            return (
                self.db.query(WorkspaceActivity)
                .filter(WorkspaceActivity.id == activity_id)
                .first()
            )

    return SyncActivityService(test_db_session)


# Test data fixtures
@pytest.fixture
def test_user_data():
    """Standard test user data for consistent testing"""
    return {
        "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "bio": "This is a test user bio",
        "profile_image_url": "https://example.com/profile.jpg",
        "status": "active",
        "user_metadata": {"preferences": {"theme": "dark", "language": "en"}},
    }


@pytest.fixture
def test_tenant_data():
    """Standard test tenant data for consistent testing"""
    return {
        "name": f"Test Tenant {uuid.uuid4().hex[:6]}",
        "slug": f"test-tenant-{uuid.uuid4().hex[:6]}",
    }


@pytest.fixture
def test_workspace_data():
    """Standard test workspace data for consistent testing"""
    return {
        "name": f"Test Workspace {uuid.uuid4().hex[:6]}",
        "description": "Test workspace description",
        "type": "personal",
    }


# Missing test database fixtures
@pytest.fixture
def test_db_session():
    """Create a test database session that can be used for testing"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    """Override the get_db dependency for testing"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_db():
    """Alternative test database fixture"""
    return SessionLocal()
