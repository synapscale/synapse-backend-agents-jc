#!/usr/bin/env python3
"""
Test file upload endpoint
"""
import asyncio
import sys
sys.path.append('src')

from fastapi.testclient import TestClient
from synapse.main import app
from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from unittest.mock import AsyncMock
import io

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

def test_file_upload():
    """Test file upload endpoint"""
    client = TestClient(app)
    
    try:
        print("Testing file upload endpoint...")
        
        # Create a test file
        test_file_content = b"Test file content for API upload"
        test_file = io.BytesIO(test_file_content)
        
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"description": "Test upload via API"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Upload successful! File ID: {data.get('id')}")
        else:
            print("Upload failed:", response.json())
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_file_upload()
