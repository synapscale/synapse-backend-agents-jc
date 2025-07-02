#!/usr/bin/env python3
"""
Test Data Cleanup Script for Synapse Backend

This script provides comprehensive tools to clean test data from the database
that was created through test scripts. It identifies and removes test data
based on patterns and naming conventions used in tests.
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

# Import database and models
from synapse.database import SessionLocal, get_database_config
from synapse.models.user import User
from synapse.models.workspace import Workspace
from synapse.models.tenant import Tenant
from synapse.models.conversation import Conversation
from synapse.models.subscription import Plan, UserSubscription
from synapse.models.workspace_activity import WorkspaceActivity
from synapse.models.agent import Agent
from synapse.models.workflow import Workflow
from synapse.models.node import Node


class TestDataCleaner:
    """Clean test data from the database based on patterns and naming conventions"""

    def __init__(self, db_session: Session = None):
        """Initialize the cleaner with a database session"""
        self.db = db_session or SessionLocal()
        self.cleanup_stats = {
            "users": 0,
            "workspaces": 0,
            "tenants": 0,
            "conversations": 0,
            "plans": 0,
            "subscriptions": 0,
            "activities": 0,
            "agents": 0,
            "workflows": 0,
            "nodes": 0,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "db") and self.db:
            self.db.close()

    def identify_test_users(self) -> List[User]:
        """Identify users that appear to be test data"""
        patterns = [
            r"test.*@example\.com",
            r"testuser_[a-f0-9]{8}@example\.com",
            r".*_[a-f0-9]{8}@example\.com",
            r"test@.*",
            r"demo@.*",
        ]

        test_users = []
        for pattern in patterns:
            users = self.db.query(User).filter(User.email.regexp(pattern)).all()
            test_users.extend(users)

        # Also check for test usernames
        username_patterns = [r"testuser_[a-f0-9]{8}", r"test.*user", r"demo.*user"]

        for pattern in username_patterns:
            users = self.db.query(User).filter(User.username.regexp(pattern)).all()
            test_users.extend(users)

        # Remove duplicates
        return list(set(test_users))

    def identify_test_workspaces(self) -> List[Workspace]:
        """Identify workspaces that appear to be test data"""
        patterns = [
            r"Test Workspace.*",
            r"Workspace de Teste.*",
            r".*[a-f0-9]{6}.*",  # Contains hex strings
            r"test-workspace-.*",
        ]

        test_workspaces = []
        for pattern in patterns:
            workspaces = (
                self.db.query(Workspace).filter(Workspace.name.regexp(pattern)).all()
            )
            test_workspaces.extend(workspaces)

        return list(set(test_workspaces))

    def identify_test_tenants(self) -> List[Tenant]:
        """Identify tenants that appear to be test data"""
        patterns = [r"Test Tenant.*", r".*[a-f0-9]{6}.*", r"test-tenant-.*"]

        test_tenants = []
        for pattern in patterns:
            tenants = self.db.query(Tenant).filter(Tenant.name.regexp(pattern)).all()
            test_tenants.extend(tenants)

        return list(set(test_tenants))

    def identify_test_plans(self) -> List[Plan]:
        """Identify plans that appear to be test data"""
        patterns = [r"Test Plan.*", r".*test.*", r"Demo.*"]

        test_plans = []
        for pattern in patterns:
            plans = self.db.query(Plan).filter(Plan.name.regexp(pattern)).all()
            test_plans.extend(plans)

        return list(set(test_plans))

    def clean_by_age(self, days: int = 7) -> Dict[str, int]:
        """Clean test data older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Clean old test users
        old_test_users = (
            self.db.query(User)
            .filter(
                User.created_at < cutoff_date,
                User.email.like("%test%") | User.email.like("%example.com%"),
            )
            .all()
        )

        for user in old_test_users:
            self._clean_user_data(user)

        return self.cleanup_stats

    def clean_by_pattern(
        self, email_pattern: str = None, name_pattern: str = None
    ) -> Dict[str, int]:
        """Clean test data matching specific patterns"""
        if email_pattern:
            users = self.db.query(User).filter(User.email.regexp(email_pattern)).all()
            for user in users:
                self._clean_user_data(user)

        if name_pattern:
            workspaces = (
                self.db.query(Workspace)
                .filter(Workspace.name.regexp(name_pattern))
                .all()
            )
            for workspace in workspaces:
                self._clean_workspace_data(workspace)

        return self.cleanup_stats

    def clean_all_test_data(self, dry_run: bool = True) -> Dict[str, int]:
        """Clean all identified test data"""
        print(
            f"{'DRY RUN: ' if dry_run else ''}Starting comprehensive test data cleanup..."
        )

        # Get all test entities
        test_users = self.identify_test_users()
        test_workspaces = self.identify_test_workspaces()
        test_tenants = self.identify_test_tenants()
        test_plans = self.identify_test_plans()

        print(f"Found {len(test_users)} test users")
        print(f"Found {len(test_workspaces)} test workspaces")
        print(f"Found {len(test_tenants)} test tenants")
        print(f"Found {len(test_plans)} test plans")

        if dry_run:
            print(
                "\nDRY RUN - No data will be deleted. Run with dry_run=False to actually delete."
            )
            return {
                "users": len(test_users),
                "workspaces": len(test_workspaces),
                "tenants": len(test_tenants),
                "plans": len(test_plans),
            }

        # Clean users and their related data
        for user in test_users:
            self._clean_user_data(user)

        # Clean orphaned workspaces
        for workspace in test_workspaces:
            self._clean_workspace_data(workspace)

        # Clean orphaned tenants
        for tenant in test_tenants:
            self._clean_tenant_data(tenant)

        # Clean test plans
        for plan in test_plans:
            self._clean_plan_data(plan)

        # Commit all changes
        self.db.commit()

        return self.cleanup_stats

    def _clean_user_data(self, user: User):
        """Clean a user and all related data"""
        print(f"Cleaning user: {user.email}")

        # Clean user's conversations
        conversations = (
            self.db.query(Conversation).filter(Conversation.user_id == user.id).all()
        )
        for conv in conversations:
            self.db.delete(conv)
            self.cleanup_stats["conversations"] += 1

        # Clean user's subscriptions
        subscriptions = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user.id)
            .all()
        )
        for sub in subscriptions:
            self.db.delete(sub)
            self.cleanup_stats["subscriptions"] += 1

        # Clean user's workspaces (where they're the owner)
        workspaces = (
            self.db.query(Workspace).filter(Workspace.owner_id == user.id).all()
        )
        for workspace in workspaces:
            self._clean_workspace_data(workspace)

        # Clean user's activities
        activities = (
            self.db.query(WorkspaceActivity)
            .filter(WorkspaceActivity.user_id == user.id)
            .all()
        )
        for activity in activities:
            self.db.delete(activity)
            self.cleanup_stats["activities"] += 1

        # Clean user's agents
        agents = self.db.query(Agent).filter(Agent.user_id == user.id).all()
        for agent in agents:
            self.db.delete(agent)
            self.cleanup_stats["agents"] += 1

        # Clean user's workflows
        workflows = self.db.query(Workflow).filter(Workflow.user_id == user.id).all()
        for workflow in workflows:
            # Clean workflow nodes first
            nodes = self.db.query(Node).filter(Node.workflow_id == workflow.id).all()
            for node in nodes:
                self.db.delete(node)
                self.cleanup_stats["nodes"] += 1

            self.db.delete(workflow)
            self.cleanup_stats["workflows"] += 1

        # Finally, delete the user
        self.db.delete(user)
        self.cleanup_stats["users"] += 1

    def _clean_workspace_data(self, workspace: Workspace):
        """Clean workspace and related data"""
        print(f"Cleaning workspace: {workspace.name}")

        # Clean workspace activities
        activities = (
            self.db.query(WorkspaceActivity)
            .filter(WorkspaceActivity.workspace_id == workspace.id)
            .all()
        )
        for activity in activities:
            self.db.delete(activity)
            self.cleanup_stats["activities"] += 1

        # Delete the workspace
        self.db.delete(workspace)
        self.cleanup_stats["workspaces"] += 1

    def _clean_tenant_data(self, tenant: Tenant):
        """Clean tenant and related data"""
        print(f"Cleaning tenant: {tenant.name}")

        # Clean tenant's workspaces
        workspaces = (
            self.db.query(Workspace).filter(Workspace.tenant_id == tenant.id).all()
        )
        for workspace in workspaces:
            self._clean_workspace_data(workspace)

        # Delete the tenant
        self.db.delete(tenant)
        self.cleanup_stats["tenants"] += 1

    def _clean_plan_data(self, plan: Plan):
        """Clean plan and related data"""
        print(f"Cleaning plan: {plan.name}")

        # Clean plan's subscriptions
        subscriptions = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.plan_id == plan.id)
            .all()
        )
        for sub in subscriptions:
            self.db.delete(sub)
            self.cleanup_stats["subscriptions"] += 1

        # Delete the plan
        self.db.delete(plan)
        self.cleanup_stats["plans"] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about test data in the database"""
        stats = {}

        # Count test users
        test_user_count = (
            self.db.query(func.count(User.id))
            .filter(
                User.email.like("%test%")
                | User.email.like("%example.com%")
                | User.username.like("%test%")
            )
            .scalar()
        )
        stats["test_users"] = test_user_count

        # Count test workspaces
        test_workspace_count = (
            self.db.query(func.count(Workspace.id))
            .filter(Workspace.name.like("%Test%") | Workspace.name.like("%test%"))
            .scalar()
        )
        stats["test_workspaces"] = test_workspace_count

        # Count test tenants
        test_tenant_count = (
            self.db.query(func.count(Tenant.id))
            .filter(Tenant.name.like("%Test%") | Tenant.name.like("%test%"))
            .scalar()
        )
        stats["test_tenants"] = test_tenant_count

        return stats


def main():
    """Main function to run cleanup operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Clean test data from the database")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Actually delete the data (overrides --dry-run)",
    )
    parser.add_argument(
        "--email-pattern", type=str, help="Delete users matching this email pattern"
    )
    parser.add_argument(
        "--days-old",
        type=int,
        default=7,
        help="Delete test data older than this many days",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show statistics, do not delete anything",
    )

    args = parser.parse_args()

    # Override dry_run if force is specified
    dry_run = args.dry_run and not args.force

    with TestDataCleaner() as cleaner:
        if args.stats_only:
            stats = cleaner.get_statistics()
            print("Test Data Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            return

        if args.email_pattern:
            result = cleaner.clean_by_pattern(email_pattern=args.email_pattern)
        else:
            result = cleaner.clean_all_test_data(dry_run=dry_run)

        print("\nCleanup Results:")
        for entity_type, count in result.items():
            if count > 0:
                print(f"  {entity_type}: {count}")


if __name__ == "__main__":
    main()
