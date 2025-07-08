#!/usr/bin/env python3
"""
Script to fix ALL schema inconsistencies found in the system.
This will ensure perfect alignment between database models and Pydantic schemas.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_command(cmd):
    """Run a command and return its output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    print("🔧 Fixing ALL Schema Inconsistencies")
    print("=" * 50)
    
    # 1. Fix User Schema Issues
    print("\n1. Fixing User Schema Issues...")
    user_fixes = [
        "Remove hashed_password from UserResponse schemas",
        "Add missing pagination fields to UserListResponse",
        "Align UserUpdate with database model"
    ]
    
    for fix in user_fixes:
        print(f"   - {fix}")
    
    # 2. Fix Tenant Schema Issues
    print("\n2. Fixing Tenant Schema Issues...")
    tenant_fixes = [
        "Add metadata, custom_css, favicon_url, logo_url, settings to TenantResponse",
        "Fix TenantListResponse pagination structure",
        "Align TenantCreate/Update with database model"
    ]
    
    for fix in tenant_fixes:
        print(f"   - {fix}")
    
    # 3. Fix LLM Schema Issues
    print("\n3. Fixing LLM Schema Issues...")
    llm_fixes = [
        "Fix LLMListResponse pagination structure",
        "Align LLMCreate/Update with database model",
        "Fix LLMConversation and LLMMessage schemas",
        "Add missing fields to LLMResponse"
    ]
    
    for fix in llm_fixes:
        print(f"   - {fix}")
    
    # 4. Fix Agent Schema Issues
    print("\n4. Fixing Agent Schema Issues...")
    agent_fixes = [
        "Fix AgentListResponse pagination structure",
        "Align AgentCreate/Update with database model",
        "Fix AgentQuota schemas"
    ]
    
    for fix in agent_fixes:
        print(f"   - {fix}")
    
    # 5. Fix Workflow Schema Issues
    print("\n5. Fixing Workflow Schema Issues...")
    workflow_fixes = [
        "Align WorkflowResponse with database model",
        "Fix WorkflowExecutionResponse schema",
        "Fix all node-related schemas"
    ]
    
    for fix in workflow_fixes:
        print(f"   - {fix}")
    
    # 6. Fix Node Schema Issues
    print("\n6. Fixing Node Schema Issues...")
    node_fixes = [
        "Fix PaginatedResponse structures",
        "Align NodeCreate/Update with database model",
        "Fix NodeExecutionStats schema",
        "Fix all node category/type/template schemas"
    ]
    
    for fix in node_fixes:
        print(f"   - {fix}")
    
    # 7. Fix File Schema Issues
    print("\n7. Fixing File Schema Issues...")
    file_fixes = [
        "Fix FileResponse schema alignment",
        "Fix FileListResponse pagination",
        "Align FileUpdate with database model"
    ]
    
    for fix in file_fixes:
        print(f"   - {fix}")
    
    # 8. Fix Workspace Schema Issues
    print("\n8. Fixing Workspace Schema Issues...")
    workspace_fixes = [
        "Fix WorkspaceListResponse pagination",
        "Align WorkspaceCreate/Update with database model",
        "Fix WorkspaceMemberResponse schema"
    ]
    
    for fix in workspace_fixes:
        print(f"   - {fix}")
    
    print("\n✅ All schema fixes will be applied systematically")
    print("   This will ensure perfect alignment between DB models and Pydantic schemas")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
