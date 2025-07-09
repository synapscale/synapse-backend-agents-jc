#!/usr/bin/env python3
"""
Teste direto do endpoint workflows
"""
import asyncio
import sys
sys.path.append('src')

from fastapi.testclient import TestClient
from synapse.main import app
from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from unittest.mock import AsyncMock

# Mock user for testing
mock_user = User(
    id="33415ea8-6992-4db7-b18b-b2f405f35429",
    email="joaovictor@liderimobiliaria.com.br",
    username="joaovictor",
    tenant_id="70a833a5-1698-4ca5-b3fd-39287b1823c6",
    is_active=True,
    is_verified=True
)

async def mock_get_current_user():
    return mock_user

# Override the dependency
app.dependency_overrides[get_current_active_user] = mock_get_current_user

def test_workflows_endpoint():
    """Test workflows endpoint directly"""
    client = TestClient(app)
    
    try:
        print("Testing workflows endpoint...")
        response = client.get("/api/v1/workflows")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("Error response:", response.json())
        else:
            data = response.json()
            print(f"Success! Found {len(data)} workflows")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflows_endpoint()
