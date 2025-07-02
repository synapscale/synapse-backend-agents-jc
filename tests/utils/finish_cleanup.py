#!/usr/bin/env python3
"""
Finish Test Data Cleanup

Finalize the cleanup of remaining test data that was causing FK constraints.
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from sqlalchemy import text
from synapse.database import SessionLocal


def finish_cleanup():
    """Finish cleaning remaining test data."""
    db = SessionLocal()
    try:
        print("🧹 Finishing test data cleanup...")

        # Get remaining test users that reference test tenants
        result = db.execute(
            text(
                """
            SELECT u.id as user_id, u.email, t.name as tenant_name
            FROM synapscale_db.users u 
            JOIN synapscale_db.tenants t ON u.tenant_id = t.id
            WHERE t.name LIKE '%test%' OR t.name LIKE '%Test%'
        """
            )
        )
        remaining_users = result.fetchall()

        if remaining_users:
            print(f"Found {len(remaining_users)} remaining test users to clean:")
            for user in remaining_users:
                print(f"  - {user.email} (tenant: {user.tenant_name})")

            # Extract user IDs
            user_ids = [str(user.user_id) for user in remaining_users]
            user_ids_str = "'" + "','".join(user_ids) + "'"

            # Delete these specific users
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.users 
                WHERE id IN ({user_ids_str})
            """
                )
            )
            deleted_users = result.rowcount
            print(f"✅ Deleted {deleted_users} remaining test users")

        # Now delete test tenants
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

        # Commit changes
        db.commit()
        print("\n🎉 Cleanup completed successfully!")

        # Final verification
        result = db.execute(
            text(
                """
            SELECT COUNT(*) as count 
            FROM synapscale_db.users 
            WHERE email LIKE '%test%' 
               OR email LIKE '%apitest%' 
               OR email LIKE '%wstest%'
               OR email LIKE '%flow_%'
               OR email LIKE '%login_%'
               OR email LIKE '%refresh_%'
        """
            )
        )
        remaining_test_users = result.fetchone()[0]

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
        remaining_test_tenants = result.fetchone()[0]

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
        remaining_test_workspaces = result.fetchone()[0]

        print("\n📊 Final Status:")
        print(f"Remaining test users: {remaining_test_users}")
        print(f"Remaining test tenants: {remaining_test_tenants}")
        print(f"Remaining test workspaces: {remaining_test_workspaces}")

        if (
            remaining_test_users == 0
            and remaining_test_tenants == 0
            and remaining_test_workspaces == 0
        ):
            print("✅ All test data successfully cleaned!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    finish_cleanup()
