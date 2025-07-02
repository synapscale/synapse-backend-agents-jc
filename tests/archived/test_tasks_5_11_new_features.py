#!/usr/bin/env python3
"""
Comprehensive Tests for New Fields and Functionalities (Tasks 5-11)
Tests all new fields, security features, tracking capabilities, and configuration options
"""
import pytest
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from synapse.main import app
from synapse.models.user import User
from synapse.models.workspace import Workspace, WorkspaceType
from synapse.models.workspace_member import WorkspaceMember, WorkspaceRole
from synapse.models.workspace_activity import WorkspaceActivity
from synapse.models.tenant import Tenant
from synapse.models.subscription import Plan, UserSubscription, SubscriptionStatus
from synapse.database import get_db
from tests.conftest import override_get_db, test_db

client = TestClient(app)

# Use existing user from database
EXISTING_USER_EMAIL = "testuser@example.com"
EXISTING_USER_ID = "785b0699-81c7-4285-a62c-f8a2aab3edbf"
EXISTING_TENANT_ID = "e3004808-9927-444d-b11e-5503e25de230"


class TestUserProfileEnhancements:
    """Test User Profile Enhancement features"""

    @pytest.mark.asyncio
    async def test_user_creation_with_new_fields(self, user_service, test_user_data):
        """Test creating users with new profile fields using UserService"""
        user = user_service.create_user(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password=test_user_data["password"],
            full_name=test_user_data["full_name"],
            bio="Test bio",
            profile_image_url="https://example.com/profile.jpg",
            status="active",
        )

        assert user.email == test_user_data["email"]
        assert user.username == test_user_data["username"]
        assert user.full_name == test_user_data["full_name"]
        assert user.bio == "Test bio"
        assert user.profile_image_url == "https://example.com/profile.jpg"
        assert user.status == "active"

    @pytest.mark.asyncio
    async def test_user_metadata_fields(self, user_service, test_user_data):
        """Test user metadata and timestamp fields using UserService"""
        user = user_service.create_user(**test_user_data)

        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.last_login_at is None  # Should be None until first login
        assert user.login_count == 0

    @pytest.mark.asyncio
    async def test_user_tracking_fields(self, user_service, test_user_data):
        """Test user tracking fields using UserService"""
        user = user_service.create_user(**test_user_data)

        # Update tracking fields
        user = user_service.update_user(
            user.id, login_count=5, total_workspaces=3, total_agents=10
        )

        assert user.login_count == 5
        assert user.total_workspaces == 3
        assert user.total_agents == 10


class TestTenantConfigurationEnhancements:
    """Test Tenant Configuration Enhancement features"""

    @pytest.mark.asyncio
    async def test_tenant_creation_with_new_fields(
        self, tenant_service, test_tenant_data
    ):
        """Test creating tenants with configuration fields using TenantService"""
        tenant = tenant_service.create_tenant(
            name=test_tenant_data["name"],
            max_workspaces=100,
            max_members=500,
            max_storage_mb=10000,
            is_active=True,
            subscription_tier="premium",
        )

        assert tenant.name == test_tenant_data["name"]
        assert tenant.max_workspaces == 100
        assert tenant.max_members == 500
        assert tenant.max_storage_mb == 10000
        assert tenant.is_active is True
        assert tenant.subscription_tier == "premium"

    @pytest.mark.asyncio
    async def test_subscription_integration(
        self, plan_service, subscription_service, user_service, test_user_data
    ):
        """Test subscription system integration using service layers"""
        # Create plan using service
        plan = plan_service.create_plan(
            name="Test Plan",
            price=29.99,
            max_workspaces=10,
            max_members_per_workspace=50,
            max_api_calls_per_day=10000,
            max_storage_mb=1000,
        )

        # Create user using service
        user = user_service.create_user(**test_user_data)

        # Create subscription using service
        subscription = subscription_service.create_subscription(
            user_id=user.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            starts_at=datetime.now(timezone.utc),
            ends_at=datetime.now(timezone.utc) + timedelta(days=30),
        )

        assert subscription.user_id == user.id
        assert subscription.plan_id == plan.id
        assert subscription.status == SubscriptionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_tenant_billing_fields(self, tenant_service, test_tenant_data):
        """Test tenant billing and financial tracking using TenantService"""
        tenant = tenant_service.create_tenant(
            name=test_tenant_data["name"],
            billing_email="billing@test.com",
            monthly_spend_limit=1000.00,
            current_usage_cost=250.50,
        )

        assert tenant.billing_email == "billing@test.com"
        assert tenant.monthly_spend_limit == 1000.00
        assert tenant.current_usage_cost == 250.50


class TestWorkspaceTrackingEnhancements:
    """Test Workspace Activity Tracking Enhancement features"""

    @pytest.mark.asyncio
    async def test_workspace_creation_with_tracking(
        self,
        workspace_service,
        user_service,
        tenant_service,
        test_user_data,
        test_tenant_data,
    ):
        """Test creating workspaces with tracking fields using service layers"""
        # Create dependencies using services
        tenant = tenant_service.create_tenant(**test_tenant_data)
        user = user_service.create_user(**test_user_data)

        # Create workspace using service
        workspace = workspace_service.create_workspace(
            name="Test Workspace",
            tenant_id=tenant.id,
            owner_id=user.id,
            type=WorkspaceType.PERSONAL,
            last_activity_at=datetime.now(timezone.utc),
            total_members=5,
            total_activity_count=25,
        )

        assert workspace.name == "Test Workspace"
        assert workspace.tenant_id == tenant.id
        assert workspace.owner_id == user.id
        assert workspace.type == WorkspaceType.PERSONAL
        assert workspace.total_members == 5
        assert workspace.total_activity_count == 25

    @pytest.mark.asyncio
    async def test_workspace_activity_logging(
        self,
        activity_service,
        workspace_service,
        user_service,
        tenant_service,
        test_user_data,
        test_tenant_data,
    ):
        """Test workspace activity logging using service layers"""
        # Create dependencies using services
        tenant = tenant_service.create_tenant(**test_tenant_data)
        user = user_service.create_user(**test_user_data)
        workspace = workspace_service.create_workspace(
            name="Activity Test Workspace", tenant_id=tenant.id, owner_id=user.id
        )

        # Create activity using service
        activity = activity_service.create_activity(
            workspace_id=workspace.id,
            user_id=user.id,
            action="workspace_created",
            metadata={"workspace_name": workspace.name},
        )

        assert activity.workspace_id == workspace.id
        assert activity.user_id == user.id
        assert activity.action == "workspace_created"
        assert activity.metadata["workspace_name"] == workspace.name

    @pytest.mark.asyncio
    async def test_workspace_member_tracking(
        self,
        workspace_service,
        user_service,
        tenant_service,
        test_user_data,
        test_tenant_data,
    ):
        """Test workspace member tracking using service layers"""
        # Create dependencies using services
        tenant = tenant_service.create_tenant(**test_tenant_data)
        user = user_service.create_user(**test_user_data)
        workspace = workspace_service.create_workspace(
            name="Member Test Workspace",
            tenant_id=tenant.id,
            owner_id=user.id,
            total_members=1,
            total_admins=1,
        )

        assert workspace.total_members == 1
        assert workspace.total_admins == 1


class TestValidationAndConstraints:
    """Test enhanced validation and constraint features"""

    @pytest.mark.asyncio
    async def test_required_field_validation(self, user_service):
        """Test that required fields are properly validated through service layer"""
        # Test missing email
        with pytest.raises(ValueError, match="Email is required"):
            user_service.create_user(
                email="",
                username="testuser",
                password="password123",
                full_name="Test User",
            )

        # Test missing username
        with pytest.raises(ValueError, match="Username is required"):
            user_service.create_user(
                email="test@example.com",
                username="",
                password="password123",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_unique_constraint_validation(self, user_service, test_user_data):
        """Test unique constraint validation through service layer"""
        # Create first user
        user_service.create_user(**test_user_data)

        # Attempt to create user with same email should fail
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(
                email=test_user_data["email"],
                username="different_username",
                password="password123",
                full_name="Different User",
            )

        # Attempt to create user with same username should fail
        with pytest.raises(ValueError, match="Username already exists"):
            user_service.create_user(
                email="different@example.com",
                username=test_user_data["username"],
                password="password123",
                full_name="Different User",
            )

    @pytest.mark.asyncio
    async def test_workspace_name_validation(
        self,
        workspace_service,
        user_service,
        tenant_service,
        test_user_data,
        test_tenant_data,
    ):
        """Test workspace name validation through service layer"""
        # Create dependencies
        tenant = tenant_service.create_tenant(**test_tenant_data)
        user = user_service.create_user(**test_user_data)

        # Create first workspace
        workspace_service.create_workspace(
            name="Test Workspace", tenant_id=tenant.id, owner_id=user.id
        )

        # Attempt to create workspace with same name in same tenant should fail
        with pytest.raises(
            ValueError, match="Workspace name already exists in this tenant"
        ):
            workspace_service.create_workspace(
                name="Test Workspace", tenant_id=tenant.id, owner_id=user.id
            )


class TestIntegrationScenarios:
    """Test complete integration scenarios using service layers"""

    @pytest.mark.asyncio
    async def test_complete_multi_service_workflow(
        self,
        user_service,
        tenant_service,
        workspace_service,
        plan_service,
        subscription_service,
    ):
        """Test complete workflow using multiple service layers"""
        # Create plan
        plan = plan_service.create_plan(
            name="Integration Test Plan",
            price=49.99,
            max_workspaces=5,
            max_members_per_workspace=25,
            max_api_calls_per_day=5000,
            max_storage_mb=500,
        )

        # Create tenant
        tenant = tenant_service.create_tenant(
            name="Integration Test Tenant",
            max_workspaces=plan.max_workspaces,
            max_members=100,
            subscription_tier="premium",
        )

        # Create user
        user = user_service.create_user(
            email="integration@test.com",
            username="integration_user",
            password="secure_password",
            full_name="Integration Test User",
            bio="Integration test user bio",
        )

        # Create subscription
        subscription = subscription_service.create_subscription(
            user_id=user.id, plan_id=plan.id, status=SubscriptionStatus.ACTIVE
        )

        # Create workspace
        workspace = workspace_service.create_workspace(
            name="Integration Test Workspace",
            tenant_id=tenant.id,
            owner_id=user.id,
            type=WorkspaceType.TEAM,
        )

        # Verify all relationships
        assert subscription.user_id == user.id
        assert subscription.plan_id == plan.id
        assert workspace.tenant_id == tenant.id
        assert workspace.owner_id == user.id
        assert tenant.max_workspaces == plan.max_workspaces

    @pytest.mark.asyncio
    async def test_error_handling_in_service_layer(self, user_service):
        """Test proper error handling in service layer"""
        # Test invalid email format
        with pytest.raises(ValueError):
            user_service.create_user(
                email="invalid-email",
                username="testuser",
                password="password123",
                full_name="Test User",
            )

        # Test empty required fields
        with pytest.raises(ValueError):
            user_service.create_user(email="", username="", password="", full_name="")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
