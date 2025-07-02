#!/usr/bin/env python3
"""
Safe Test Data Cleanup Script

Simple and safe cleanup using direct SQL to avoid ORM cascade issues.
Only removes data that clearly matches test patterns.
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from sqlalchemy import text
from synapse.database import SessionLocal


def safe_cleanup_test_data(dry_run=True):
    """
    Safely cleanup test data using direct SQL queries.
    Only removes data that clearly matches test patterns.
    """
    db = SessionLocal()
    try:
        print(f"{'DRY RUN: ' if dry_run else ''}Starting safe test data cleanup...")

        # Count test data first
        print("\n=== Current Test Data ===")

        # Count test users
        result = db.execute(
            text(
                """
            SELECT COUNT(*) as count 
            FROM synapscale_db.users 
            WHERE email LIKE '%test%' 
               OR email LIKE '%apitest%' 
               OR email LIKE '%wstest%'
        """
            )
        )
        test_users_count = result.fetchone()[0]
        print(f"Test Users: {test_users_count}")

        # Count test workspaces
        result = db.execute(
            text(
                """
            SELECT COUNT(*) as count 
            FROM synapscale_db.workspaces 
            WHERE name LIKE '%test%' 
               OR name LIKE '%Test%'
               OR description LIKE '%test%'
        """
            )
        )
        test_workspaces_count = result.fetchone()[0]
        print(f"Test Workspaces: {test_workspaces_count}")

        # Count test tenants
        result = db.execute(
            text(
                """
            SELECT COUNT(*) as count 
            FROM synapscale_db.tenants 
            WHERE name LIKE '%test%' 
               OR name LIKE '%Test%'
        """
            )
        )
        test_tenants_count = result.fetchone()[0]
        print(f"Test Tenants: {test_tenants_count}")

        print("=" * 30)

        if not dry_run:
            print("\n🗑️  Starting cleanup...")

            # First, find all test user IDs
            result = db.execute(
                text(
                    """
                SELECT id FROM synapscale_db.users 
                WHERE email LIKE '%test%' 
                   OR email LIKE '%apitest%' 
                   OR email LIKE '%wstest%'
            """
                )
            )
            test_user_ids = [row[0] for row in result.fetchall()]

            if test_user_ids:
                # Convert to string format for IN clause
                user_ids_str = "'" + "','".join(str(uid) for uid in test_user_ids) + "'"

                # Delete dependent data first (using tables that actually exist)

                # Delete LLM conversations
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.llms_conversations 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_llm_conversations = result.rowcount
                print(f"✅ Deleted {deleted_llm_conversations} test LLM conversations")

                # Delete workspace members
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.workspace_members 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_memberships = result.rowcount
                print(f"✅ Deleted {deleted_memberships} test workspace memberships")

                # Delete workspace activities
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.workspace_activities 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_activities = result.rowcount
                print(f"✅ Deleted {deleted_activities} test workspace activities")

                # Delete user subscriptions
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.user_subscriptions 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_user_subscriptions = result.rowcount
                print(
                    f"✅ Deleted {deleted_user_subscriptions} test user subscriptions"
                )

                # Delete user tenant roles
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.user_tenant_roles 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_tenant_roles = result.rowcount
                print(f"✅ Deleted {deleted_tenant_roles} test user tenant roles")

                # Delete refresh tokens
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.refresh_tokens 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_tokens = result.rowcount
                print(f"✅ Deleted {deleted_tokens} test refresh tokens")

                # Delete agents owned by test users
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.agents 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_agents = result.rowcount
                print(f"✅ Deleted {deleted_agents} test agents")

                # Delete files owned by test users
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.files 
                    WHERE user_id IN ({user_ids_str})
                """
                    )
                )
                deleted_files = result.rowcount
                print(f"✅ Deleted {deleted_files} test files")

            # Delete test workspaces and related data
            result = db.execute(
                text(
                    """
                SELECT id FROM synapscale_db.workspaces 
                WHERE name LIKE '%test%' 
                   OR name LIKE '%Test%'
                   OR description LIKE '%test%'
            """
                )
            )
            test_workspace_ids = [row[0] for row in result.fetchall()]

            if test_workspace_ids:
                workspace_ids_str = (
                    "'" + "','".join(str(wid) for wid in test_workspace_ids) + "'"
                )

                # Delete ALL workspace activities for test workspaces first
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.workspace_activities 
                    WHERE workspace_id IN ({workspace_ids_str})
                """
                    )
                )
                deleted_ws_activities = result.rowcount
                print(
                    f"✅ Deleted {deleted_ws_activities} test workspace activities (by workspace)"
                )

                # Delete workspace invitations
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.workspace_invitations 
                    WHERE workspace_id IN ({workspace_ids_str})
                """
                    )
                )
                deleted_invitations = result.rowcount
                print(f"✅ Deleted {deleted_invitations} test workspace invitations")

                # Delete workspace projects
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.workspace_projects 
                    WHERE workspace_id IN ({workspace_ids_str})
                """
                    )
                )
                deleted_projects = result.rowcount
                print(f"✅ Deleted {deleted_projects} test workspace projects")

                # Delete workspace members for test workspaces
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.workspace_members 
                    WHERE workspace_id IN ({workspace_ids_str})
                """
                    )
                )
                deleted_ws_members = result.rowcount
                print(
                    f"✅ Deleted {deleted_ws_members} test workspace members (by workspace)"
                )

            # Delete test workspaces
            result = db.execute(
                text(
                    """
                DELETE FROM synapscale_db.workspaces 
                WHERE name LIKE '%test%' 
                   OR name LIKE '%Test%'
                   OR description LIKE '%test%'
            """
                )
            )
            deleted_workspaces = result.rowcount
            print(f"✅ Deleted {deleted_workspaces} test workspaces")

            # Delete test tenants and related data
            result = db.execute(
                text(
                    """
                SELECT id FROM synapscale_db.tenants 
                WHERE name LIKE '%test%' 
                   OR name LIKE '%Test%'
            """
                )
            )
            test_tenant_ids = [row[0] for row in result.fetchall()]

            if test_tenant_ids:
                tenant_ids_str = (
                    "'" + "','".join(str(tid) for tid in test_tenant_ids) + "'"
                )

                # Delete tenant features
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.tenant_features 
                    WHERE tenant_id IN ({tenant_ids_str})
                """
                    )
                )
                deleted_tenant_features = result.rowcount
                print(f"✅ Deleted {deleted_tenant_features} test tenant features")

            # Delete test tenants
            result = db.execute(
                text(
                    """
                DELETE FROM synapscale_db.tenants 
                WHERE name LIKE '%test%' 
                   OR name LIKE '%Test%'
            """
                )
            )
            deleted_tenants = result.rowcount
            print(f"✅ Deleted {deleted_tenants} test tenants")

            # Finally delete test users
            if test_user_ids:
                result = db.execute(
                    text(
                        f"""
                    DELETE FROM synapscale_db.users 
                    WHERE id IN ({user_ids_str})
                """
                    )
                )
                deleted_users = result.rowcount
                print(f"✅ Deleted {deleted_users} test users")

            # Commit all changes
            db.commit()
            print("\n🎉 Test data cleanup completed successfully!")

        else:
            print(f"\nDRY RUN - No data deleted. Use --force to actually delete.")
            print(
                f"Would delete: {test_users_count} users, {test_workspaces_count} workspaces, {test_tenants_count} tenants"
            )

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Safe test data cleanup")
    parser.add_argument(
        "--force", action="store_true", help="Actually delete data (default is dry-run)"
    )
    args = parser.parse_args()

    dry_run = not args.force
    safe_cleanup_test_data(dry_run)


if __name__ == "__main__":
    main()
