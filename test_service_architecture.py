"""
Simple Service Layer Architecture Test.

This test validates that all the service layer components are properly
structured and can be imported without errors.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_service_layer_imports():
    """Test that all service layer components can be imported."""
    
    print("🧪 Testing Service Layer Architecture...")
    
    try:
        # Test base service import
        print("1️⃣ Testing BaseService import...")
        from synapse.core.services.base_service import BaseService
        print("✅ BaseService imported successfully")
        
        # Test repository import
        print("2️⃣ Testing Repository imports...")
        from synapse.core.services.repository import IRepository, BaseRepository, UnitOfWork
        print("✅ Repository components imported successfully")
        
        # Test dependency injection import
        print("3️⃣ Testing Dependency Injection imports...")
        from synapse.core.services.dependency_container import ServiceContainer, ServiceLifetime, ServiceDescriptor
        print("✅ Dependency Injection components imported successfully")
        
        # Test service configuration import
        print("4️⃣ Testing Service Configuration import...")
        from synapse.core.services.service_configuration import configure_services
        print("✅ Service Configuration imported successfully")
        
        # Test main services module import
        print("5️⃣ Testing Main Services module import...")
        from synapse.core.services import BaseService as ImportedBaseService, get_container, configure_services as config_services
        print("✅ Main services module imported successfully")
        
        # Test user service import (example implementation)
        print("6️⃣ Testing UserService import...")
        from synapse.services.user_service import UserService
        print("✅ UserService imported successfully")
        
        print("🎉 All service layer components imported successfully!")
        
        # Test basic architecture validation
        print("7️⃣ Validating service architecture...")
        
        # Validate BaseService has expected methods
        expected_methods = ['get', 'list', 'create', 'update', 'delete', 'count', 'exists']
        for method in expected_methods:
            assert hasattr(BaseService, method), f"BaseService should have {method} method"
        print("✅ BaseService has all expected methods")
        
        # Validate IRepository has expected methods
        expected_repo_methods = ['get', 'get_multi', 'create', 'update', 'delete', 'count']
        for method in expected_repo_methods:
            assert hasattr(IRepository, method), f"IRepository should have {method} method"
        print("✅ IRepository has all expected methods")
        
        # Validate ServiceContainer has expected methods
        expected_container_methods = ['register', 'get', 'create_scope']
        for method in expected_container_methods:
            assert hasattr(ServiceContainer, method), f"ServiceContainer should have {method} method"
        print("✅ ServiceContainer has all expected methods")
        
        print("🎉 Service layer architecture validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Service layer architecture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    success = test_service_layer_imports()
    
    if success:
        print("\n✅ SERVICE LAYER ARCHITECTURE TEST PASSED!")
        print("🎯 Service Layer Foundation is properly implemented:")
        print("   ✅ BaseService: Available")
        print("   ✅ Repository Pattern: Available")
        print("   ✅ Dependency Injection: Available") 
        print("   ✅ Service Configuration: Available")
        print("   ✅ User Service Example: Available")
        print("\n🚀 Ready for database integration and testing!")
    else:
        print("\n❌ SERVICE LAYER ARCHITECTURE TEST FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main() 