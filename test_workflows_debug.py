#!/usr/bin/env python3
"""
Debug script para testar o endpoint de workflows
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from synapse.models.workflow import Workflow
from synapse.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def test_workflows_query():
    """Test workflows query directly"""
    try:
        async for db in get_async_db():
            # Test basic query
            print("Testing basic workflow query...")
            query = select(Workflow)
            result = await db.execute(query)
            workflows = result.scalars().all()
            print(f"Found {len(workflows)} workflows")
            
            # Test user query
            print("Testing user query...")
            user_query = select(User).where(User.email == "joaovictor@liderimobiliaria.com.br")
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if user:
                print(f"User found: {user.email} (tenant: {user.tenant_id})")
                
                # Test workflows for this user
                workflow_query = select(Workflow).where(
                    Workflow.tenant_id == user.tenant_id
                )
                workflow_result = await db.execute(workflow_query)
                user_workflows = workflow_result.scalars().all()
                print(f"User workflows: {len(user_workflows)}")
                
                for workflow in user_workflows:
                    print(f"  - {workflow.name} (ID: {workflow.id})")
            else:
                print("User not found!")
            
            break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflows_query())
