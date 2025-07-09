#!/usr/bin/env python3
"""
Test script to debug workflow endpoint import issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing workflow endpoint imports...")
    
    # Test individual imports
    print("1. Testing basic imports...")
    from synapse.models.workflow import Workflow
    print("   ✓ Workflow model imported")
    
    from synapse.schemas.workflow import WorkflowCreate
    print("   ✓ WorkflowCreate schema imported")
    
    print("2. Testing workflow endpoint import...")
    from synapse.api.v1.endpoints.workflows import router
    print("   ✓ Workflow router imported")
    
    print("✓ All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
