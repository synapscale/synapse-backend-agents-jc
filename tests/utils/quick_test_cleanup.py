#!/usr/bin/env python3
"""
Quick Test Data Cleanup Script

A simple script for common test data cleanup operations.
Use this for quick cleanups during development.
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from sqlalchemy.orm import Session
from synapse.database import SessionLocal
from synapse.models.user import User
from synapse.models.workspace import Workspace
from synapse.models.tenant import Tenant


def clean_test_users_by_email_pattern(pattern: str = "%test%", dry_run: bool = True):
    """Clean users matching email pattern"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.email.like(pattern)).all()

        print(f"Found {len(users)} users matching pattern '{pattern}':")
        for user in users:
            print(f"  - {user.email} (ID: {user.id})")

        if not dry_run and users:
            for user in users:
                db.delete(user)
            db.commit()
            print(f"Deleted {len(users)} users")
        elif dry_run:
            print("DRY RUN - No users deleted. Use dry_run=False to actually delete.")

        return len(users)
    finally:
        db.close()


def clean_test_workspaces_by_name_pattern(
    pattern: str = "%Test%", dry_run: bool = True
):
    """Clean workspaces matching name pattern"""
    db = SessionLocal()
    try:
        workspaces = db.query(Workspace).filter(Workspace.name.like(pattern)).all()

        print(f"Found {len(workspaces)} workspaces matching pattern '{pattern}':")
        for workspace in workspaces:
            print(f"  - {workspace.name} (ID: {workspace.id})")

        if not dry_run and workspaces:
            for workspace in workspaces:
                db.delete(workspace)
            db.commit()
            print(f"Deleted {len(workspaces)} workspaces")
        elif dry_run:
            print(
                "DRY RUN - No workspaces deleted. Use dry_run=False to actually delete."
            )

        return len(workspaces)
    finally:
        db.close()


def clean_test_tenants_by_name_pattern(pattern: str = "%Test%", dry_run: bool = True):
    """Clean tenants matching name pattern"""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.name.like(pattern)).all()

        print(f"Found {len(tenants)} tenants matching pattern '{pattern}':")
        for tenant in tenants:
            print(f"  - {tenant.name} (ID: {tenant.id})")

        if not dry_run and tenants:
            for tenant in tenants:
                db.delete(tenant)
            db.commit()
            print(f"Deleted {len(tenants)} tenants")
        elif dry_run:
            print("DRY RUN - No tenants deleted. Use dry_run=False to actually delete.")

        return len(tenants)
    finally:
        db.close()


def clean_recent_test_data(hours: int = 24, dry_run: bool = True):
    """Clean test data created in the last N hours"""
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Find recent test users
        recent_users = (
            db.query(User)
            .filter(
                User.created_at >= cutoff,
                (User.email.like("%test%") | User.email.like("%example.com%")),
            )
            .all()
        )

        print(
            f"Found {len(recent_users)} test users created in the last {hours} hours:"
        )
        for user in recent_users:
            print(f"  - {user.email} (created: {user.created_at})")

        if not dry_run and recent_users:
            for user in recent_users:
                db.delete(user)
            db.commit()
            print(f"Deleted {len(recent_users)} recent test users")
        elif dry_run:
            print("DRY RUN - No data deleted. Use dry_run=False to actually delete.")

        return len(recent_users)
    finally:
        db.close()


def show_test_data_summary():
    """Show a summary of test data in the database"""
    db = SessionLocal()
    try:
        print("=== Test Data Summary ===")

        # Count test users
        test_users = (
            db.query(User)
            .filter(
                User.email.like("%test%")
                | User.email.like("%example.com%")
                | User.username.like("%test%")
            )
            .count()
        )
        print(f"Test Users: {test_users}")

        # Count test workspaces
        test_workspaces = (
            db.query(Workspace)
            .filter(Workspace.name.like("%Test%") | Workspace.name.like("%test%"))
            .count()
        )
        print(f"Test Workspaces: {test_workspaces}")

        # Count test tenants
        test_tenants = (
            db.query(Tenant)
            .filter(Tenant.name.like("%Test%") | Tenant.name.like("%test%"))
            .count()
        )
        print(f"Test Tenants: {test_tenants}")

        print("=========================")

        return {
            "users": test_users,
            "workspaces": test_workspaces,
            "tenants": test_tenants,
        }
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Quick test data cleanup")
    parser.add_argument(
        "command",
        choices=["users", "workspaces", "tenants", "recent", "summary"],
        help="What type of cleanup to perform",
    )
    parser.add_argument(
        "--pattern", type=str, help="Pattern to match (for users/workspaces/tenants)"
    )
    parser.add_argument(
        "--hours", type=int, default=24, help="Hours for recent cleanup (default: 24)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Actually delete the data (default is dry run)",
    )

    args = parser.parse_args()
    dry_run = not args.force

    if args.command == "users":
        pattern = args.pattern or "%test%"
        clean_test_users_by_email_pattern(pattern, dry_run)
    elif args.command == "workspaces":
        pattern = args.pattern or "%Test%"
        clean_test_workspaces_by_name_pattern(pattern, dry_run)
    elif args.command == "tenants":
        pattern = args.pattern or "%Test%"
        clean_test_tenants_by_name_pattern(pattern, dry_run)
    elif args.command == "recent":
        clean_recent_test_data(args.hours, dry_run)
    elif args.command == "summary":
        show_test_data_summary()
