#!/usr/bin/env python3
"""
Final Test Data Cleanup

Clean the last remaining test users that don't have tenant constraints.
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from sqlalchemy import text
from synapse.database import SessionLocal


def final_cleanup():
    """Clean the last remaining test users."""
    db = SessionLocal()
    try:
        print("🧹 Final cleanup of remaining test users...")

        # Get remaining test users
        result = db.execute(
            text(
                """
            SELECT email, id 
            FROM synapscale_db.users 
            WHERE email LIKE '%test%' 
               OR email LIKE '%apitest%' 
               OR email LIKE '%wstest%'
               OR email LIKE '%flow_%'
               OR email LIKE '%login_%'
               OR email LIKE '%refresh_%'
            ORDER BY created_at DESC
        """
            )
        )
        remaining_users = result.fetchall()

        if remaining_users:
            print(f"Found {len(remaining_users)} remaining test users:")
            for user in remaining_users:
                print(f"  - {user.email}")

            # Extract user IDs
            user_ids = [str(user.id) for user in remaining_users]
            user_ids_str = "'" + "','".join(user_ids) + "'"

            # Clean any remaining dependencies first
            print("\nCleaning dependencies...")

            # Clean user variables
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.user_variables 
                WHERE user_id IN ({user_ids_str})
            """
                )
            )
            deleted_vars = result.rowcount
            print(f"✅ Deleted {deleted_vars} user variables")

            # Clean user behavior metrics
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.user_behavior_metrics 
                WHERE user_id IN ({user_ids_str})
            """
                )
            )
            deleted_metrics = result.rowcount
            print(f"✅ Deleted {deleted_metrics} user behavior metrics")

            # Clean any remaining user subscriptions
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.user_subscriptions 
                WHERE user_id IN ({user_ids_str})
            """
                )
            )
            deleted_subs = result.rowcount
            print(f"✅ Deleted {deleted_subs} remaining user subscriptions")

            # Clean any remaining refresh tokens
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.refresh_tokens 
                WHERE user_id IN ({user_ids_str})
            """
                )
            )
            deleted_tokens = result.rowcount
            print(f"✅ Deleted {deleted_tokens} remaining refresh tokens")

            # Clean password reset tokens
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.password_reset_tokens 
                WHERE user_id IN ({user_ids_str})
            """
                )
            )
            deleted_pwd_tokens = result.rowcount
            print(f"✅ Deleted {deleted_pwd_tokens} password reset tokens")

            # Clean email verification tokens
            result = db.execute(
                text(
                    f"""
                DELETE FROM synapscale_db.email_verification_tokens 
                WHERE user_id IN ({user_ids_str})
            """
                )
            )
            deleted_email_tokens = result.rowcount
            print(f"✅ Deleted {deleted_email_tokens} email verification tokens")

            # Finally delete the users
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

        # Commit changes
        db.commit()
        print("\n🎉 Final cleanup completed successfully!")

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
        final_test_users = result.fetchone()[0]

        print(f"\n📊 Final verification: {final_test_users} test users remaining")

        if final_test_users == 0:
            print("✅ ALL TEST DATA SUCCESSFULLY CLEANED! 🎉")
        else:
            print(
                f"⚠️  Still {final_test_users} test users remaining (may need manual review)"
            )

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    final_cleanup()
