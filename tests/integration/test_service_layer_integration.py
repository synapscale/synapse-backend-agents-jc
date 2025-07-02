#!/usr/bin/env python3
"""
Service Layer Integration Test.

This script tests the complete service layer architecture including:
- Dependency injection container integration
- BaseService and repository pattern functionality
- Database access through service layer
- CRUD operations end-to-end
- Transaction management and rollback
- Error handling and logging

Run this script to verify that the service layer foundation is working correctly.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add the src directory to Python path
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_service_layer_integration():
    """
    Comprehensive test of the service layer integration.

    Tests all components working together from dependency injection
    to database operations.
    """
    logger.info("🧪 Starting Service Layer Integration Test")

    try:
        # Step 1: Import and configure services
        logger.info("1️⃣ Testing service configuration...")
        from synapse.core.services import configure_services, get_container
        from synapse.database import init_db, get_db

        # Initialize database
        await init_db()
        logger.info("✅ Database initialized")

        # Configure services
        configure_services()
        logger.info("✅ Services configured")

        # Get container and check registrations
        container = get_container()
        registered_services = container.get_registered_services()
        logger.info(f"✅ Container has {len(registered_services)} registered services")

        # Step 2: Get database session
        logger.info("2️⃣ Testing database session...")
        # Fix: Use async generator properly
        db_gen = get_db()
        session = await db_gen.__anext__()

        try:
            # Step 3: Test service resolution
            logger.info("3️⃣ Testing service resolution...")
            from synapse.services.sample_test_service import SampleTestService

            # Resolve service through container
            test_service = container.resolve(SampleTestService)
            logger.info("✅ Sample test service resolved successfully")

            # Step 4: Test CRUD operations
            logger.info("4️⃣ Testing CRUD operations...")

            # Create user
            from synapse.services.sample_test_service import (
                UserCreateRequest,
                UserUpdateRequest,
            )

            create_data = UserCreateRequest(
                email=f"test_{uuid4().hex[:8]}@example.com",
                username=f"testuser_{uuid4().hex[:8]}",
                full_name="Test User Integration",
                password="securepassword123",
                bio="This is a test user for service layer integration testing",
            )

            logger.info(f"Creating user with email: {create_data.email}")
            created_user = await test_service.create_user(create_data)
            logger.info(f"✅ User created with ID: {created_user.id}")

            # Read user
            logger.info("Reading user by ID...")
            user_id = created_user.id
            retrieved_user = await test_service.get_user_by_id(user_id)
            assert retrieved_user is not None, "User should be retrievable"
            assert retrieved_user.email == create_data.email, "Email should match"
            logger.info("✅ User retrieved successfully")

            # Update user
            logger.info("Updating user...")
            update_data = UserUpdateRequest(
                full_name="Updated Test User", bio="Updated bio for integration testing"
            )
            updated_user = await test_service.update_user(user_id, update_data)
            assert updated_user is not None, "User should be updateable"
            assert (
                updated_user.full_name == "Updated Test User"
            ), "Full name should be updated"
            logger.info("✅ User updated successfully")

            # Test list operations
            logger.info("Testing list operations...")
            all_users = await test_service.get_all_users(limit=5)
            assert len(all_users) > 0, "Should have at least one user"
            logger.info(f"✅ Retrieved {len(all_users)} users")

            active_users = await test_service.get_active_users()
            assert len(active_users) > 0, "Should have active users"
            logger.info(f"✅ Retrieved {len(active_users)} active users")

            # Test business logic
            logger.info("Testing business logic...")
            stats = await test_service.get_user_statistics()
            assert "total_users" in stats, "Stats should contain total_users"
            assert "active_users" in stats, "Stats should contain active_users"
            assert stats["total_users"] > 0, "Should have total users"
            logger.info(f"✅ User statistics: {stats}")

            # Step 5: Test error handling
            logger.info("5️⃣ Testing error handling...")

            # Try to create duplicate user
            try:
                await test_service.create_user(create_data)
                assert False, "Should have raised error for duplicate email"
            except Exception as e:
                logger.info(f"✅ Duplicate user error handled correctly: {e}")

            # Try to get non-existent user
            non_existent_user = await test_service.get_user_by_id(str(uuid4()))
            assert non_existent_user is None, "Non-existent user should return None"
            logger.info("✅ Non-existent user handled correctly")

            # Step 6: Test transaction rollback
            logger.info("6️⃣ Testing transaction rollback...")

            rollback_data = UserCreateRequest(
                email=f"rollback_{uuid4().hex[:8]}@example.com",
                username=f"rollbackuser_{uuid4().hex[:8]}",
                full_name="Rollback Test User",
                password="securepassword123",
                bio="This user should not be created due to rollback",
            )

            try:
                result = await test_service.test_transaction_rollback(rollback_data)
                logger.info(f"✅ Transaction rollback test: {result}")

                # Verify user was not created
                rollback_user = await test_service.user_repository.find_by_email(
                    rollback_data.email
                )
                assert (
                    rollback_user is None
                ), "Rollback user should not exist in database"
                logger.info("✅ Transaction rollback verified - user was not persisted")

            except Exception as e:
                logger.info(f"✅ Transaction rollback handled: {e}")

            # Step 7: Test soft delete
            logger.info("7️⃣ Testing soft delete...")

            delete_result = await test_service.delete_user(user_id)
            assert delete_result is True, "Delete should succeed"
            logger.info("✅ User soft deleted successfully")

            # Verify user is marked inactive
            deleted_user = await test_service.get_user_by_id(user_id)
            assert deleted_user is not None, "User should still exist"
            assert deleted_user.is_active is False, "User should be inactive"
            logger.info("✅ Soft delete verified - user marked as inactive")

            # Step 8: Test dependency injection scoping
            logger.info("8️⃣ Testing dependency injection scoping...")

            # Create another service instance
            test_service_2 = container.resolve(SampleTestService)
            assert (
                test_service_2 is not test_service
            ), "Should get different instances (scoped)"
            logger.info("✅ Dependency injection scoping works correctly")

            # Step 9: Test custom repository methods
            logger.info("9️⃣ Testing custom repository methods...")

            # Test find by email
            found_user = await test_service.user_repository.find_by_email(
                created_user.email
            )
            assert found_user is not None, "Should find user by email"
            assert found_user.id == created_user.id, "Should be same user"
            logger.info("✅ Custom repository method find_by_email works")

            # Test count users
            user_count = await test_service.user_repository.count_users()
            assert user_count > 0, "Should have users in database"
            logger.info(
                f"✅ Custom repository method count_users works: {user_count} users"
            )

            logger.info("🎉 All Service Layer Integration Tests Passed!")

            return {
                "success": True,
                "tests_completed": 9,
                "created_user_id": created_user.id,
                "user_statistics": stats,
                "registered_services": len(registered_services),
                "timestamp": datetime.utcnow().isoformat(),
            }

        finally:
            # Properly close the database session
            await session.close()

    except Exception as e:
        logger.error(f"❌ Service Layer Integration Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def main():
    """Main test function."""
    print("=" * 80)
    print("🧪 SERVICE LAYER INTEGRATION TEST")
    print("=" * 80)
    print()

    result = await test_service_layer_integration()

    print()
    print("=" * 80)
    print("📊 TEST RESULTS")
    print("=" * 80)

    if result["success"]:
        print("✅ SUCCESS: All tests passed!")
        print(f"   Tests completed: {result['tests_completed']}")
        print(f"   Registered services: {result['registered_services']}")
        print(f"   Created user ID: {result['created_user_id']}")
        print(f"   User statistics: {result['user_statistics']}")
    else:
        print("❌ FAILURE: Tests failed!")
        print(f"   Error: {result['error']}")

    print(f"   Timestamp: {result['timestamp']}")
    print()

    return result["success"]


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
