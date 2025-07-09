#!/usr/bin/env python3
"""
Test direct file insert into database
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from synapse.models.file import File
import uuid

async def test_file_insert():
    """Test direct file insertion"""
    try:
        async for db in get_async_db():
            # Create test file record
            file_record = File(
                id=uuid.uuid4(),
                filename="test.txt",
                original_name="test.txt",
                file_path="/tmp/test.txt",
                file_size=100,
                mime_type="text/plain",
                category="document",
                description="Test file",
                user_id="33415ea8-6992-4db7-b18b-b2f405f35429",
                tenant_id="70a833a5-1698-4ca5-b3fd-39287b1823c6",
                status="active",
                scan_status="pending",
                access_count=0,
                is_public=False
            )
            
            print("Adding file record...")
            db.add(file_record)
            
            print("Committing...")
            await db.commit()
            
            print("Refreshing...")
            await db.refresh(file_record)
            
            print(f"File inserted successfully: {file_record.id}")
            break
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_file_insert())
