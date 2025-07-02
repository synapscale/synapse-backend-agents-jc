#!/usr/bin/env python3
"""
Cleanup users with @example.com domains - final test data cleanup
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from sqlalchemy import text
from synapse.database import SessionLocal


def cleanup_example_users():
    """Clean users with @example.com domains."""
    db = SessionLocal()
    try:
        print("🧹 Cleaning @example.com users...")

        # Get users with @example.com
        result = db.execute(
            text(
                """
            SELECT email, id, full_name
            FROM synapscale_db.users 
            WHERE email LIKE '%@example.com'
            ORDER BY created_at DESC
        """
            )
        )
        example_users = result.fetchall()

        if example_users:
            print(f"Found {len(example_users)} @example.com users:")
            for user in example_users:
                print(f"  - {user.email} ({user.full_name})")

            # Delete these users
            result = db.execute(
                text(
                    """
                DELETE FROM synapscale_db.users 
                WHERE email LIKE '%@example.com'
            """
                )
            )
            deleted_users = result.rowcount
            print(f"✅ Deleted {deleted_users} @example.com users")

            # Commit changes
            db.commit()
            print("🎉 @example.com users cleanup completed!")
        else:
            print("No @example.com users found.")

        # Final verification
        result = db.execute(
            text(
                """
            SELECT COUNT(*) as count 
            FROM synapscale_db.users 
            WHERE email LIKE '%@example.com'
        """
            )
        )
        remaining = result.fetchone()[0]

        print(f"\n📊 Remaining @example.com users: {remaining}")

        if remaining == 0:
            print("✅ ALL TEST DATA COMPLETELY CLEANED! 🎉")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    cleanup_example_users()
