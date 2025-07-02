#!/usr/bin/env python3
"""
Setup and Test Script for Test Data Cleanup Tools

This script helps verify that the cleanup tools are working correctly
and provides examples of how to use them.
"""

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)


def test_database_connection():
    """Test if we can connect to the database"""
    try:
        from synapse.database import test_database_connection

        result = test_database_connection()
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def test_model_imports():
    """Test if we can import all the required models"""
    try:
        from synapse.models.user import User
        from synapse.models.workspace import Workspace
        from synapse.models.tenant import Tenant
        from synapse.models.conversation import Conversation
        from synapse.models.subscription import Plan, UserSubscription
        from synapse.models.workspace_activity import WorkspaceActivity
        from synapse.models.agent import Agent
        from synapse.models.workflow import Workflow
        from synapse.models.node import Node

        print("✅ All model imports successful")
        return True
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False


def test_cleanup_tools():
    """Test if the cleanup tools can be imported and run"""
    try:
        # Test comprehensive cleaner
        from clean_test_data import TestDataCleaner

        print("✅ Comprehensive cleanup tool import successful")

        # Test quick cleanup functions
        from quick_test_cleanup import show_test_data_summary

        print("✅ Quick cleanup tool import successful")

        return True
    except Exception as e:
        print(f"❌ Cleanup tools import error: {e}")
        return False


def run_safe_demo():
    """Run a safe demonstration of the cleanup tools"""
    try:
        print("\n" + "=" * 50)
        print("RUNNING SAFE DEMO (READ-ONLY)")
        print("=" * 50)

        # Show current test data statistics
        from quick_test_cleanup import show_test_data_summary

        summary = show_test_data_summary()

        print("\n" + "-" * 30)
        print("Testing comprehensive cleaner...")

        from clean_test_data import TestDataCleaner

        with TestDataCleaner() as cleaner:
            stats = cleaner.get_statistics()
            print("Detailed statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")

        print("\n✅ Demo completed successfully!")
        print("Your cleanup tools are ready to use.")

        return True
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False


def show_usage_examples():
    """Show usage examples for the cleanup tools"""
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)

    print("\n1. CHECK TEST DATA SUMMARY:")
    print("   python tools/testing/quick_test_cleanup.py summary")

    print("\n2. SAFE CLEANUP (DRY RUN):")
    print("   python tools/testing/clean_test_data.py --dry-run")

    print("\n3. CLEAN TEST USERS:")
    print("   python tools/testing/quick_test_cleanup.py users --force")

    print("\n4. CLEAN RECENT TEST DATA:")
    print("   python tools/testing/quick_test_cleanup.py recent --hours 24 --force")

    print("\n5. COMPREHENSIVE CLEANUP:")
    print("   python tools/testing/clean_test_data.py --force")

    print("\n6. GET DETAILED STATISTICS:")
    print("   python tools/testing/clean_test_data.py --stats-only")

    print("\n" + "=" * 60)
    print("For more examples, see tools/testing/README.md")
    print("=" * 60)


def main():
    """Main setup and test function"""
    print("Test Data Cleanup Tools - Setup and Verification")
    print("=" * 55)

    # Run tests
    tests_passed = 0
    total_tests = 4

    print("\n1. Testing database connection...")
    if test_database_connection():
        tests_passed += 1

    print("\n2. Testing model imports...")
    if test_model_imports():
        tests_passed += 1

    print("\n3. Testing cleanup tools imports...")
    if test_cleanup_tools():
        tests_passed += 1

    print("\n4. Running safe demo...")
    if run_safe_demo():
        tests_passed += 1

    # Show results
    print("\n" + "=" * 55)
    print(f"SETUP RESULTS: {tests_passed}/{total_tests} tests passed")
    print("=" * 55)

    if tests_passed == total_tests:
        print("🎉 All tests passed! Your cleanup tools are ready to use.")
        show_usage_examples()

        print("\nNEXT STEPS:")
        print("1. Review the README.md for detailed usage instructions")
        print("2. Run a dry-run cleanup to see what test data exists")
        print("3. Start using the cleanup tools in your development workflow")

    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTROUBLESHOOTING:")
        print("1. Ensure your database is running and accessible")
        print("2. Check your environment variables and database configuration")
        print("3. Verify all required models are properly imported")
        print("4. Check the tools/testing/README.md for more help")

    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
