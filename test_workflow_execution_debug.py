#!/usr/bin/env python3
"""
Debug script para testar o modelo WorkflowExecution
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from synapse.models.workflow_execution import WorkflowExecution
from synapse.models.user import User
from sqlalchemy import select

async def test_workflow_execution_query():
    """Test workflow execution query directly"""
    try:
        async for db in get_async_db():
            # Test basic query
            print("Testing basic WorkflowExecution query...")
            query = select(WorkflowExecution)
            result = await db.execute(query)
            executions = result.scalars().all()
            print(f"Found {len(executions)} workflow executions")
            
            # Test user query
            print("Testing user query...")
            user_query = select(User).where(User.email == "joaovictor@liderimobiliaria.com.br")
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if user:
                print(f"User found: {user.email} (tenant: {user.tenant_id})")
                
                # Test executions for this user
                execution_query = select(WorkflowExecution).where(
                    WorkflowExecution.user_id == user.id
                )
                execution_result = await db.execute(execution_query)
                user_executions = execution_result.scalars().all()
                print(f"User executions: {len(user_executions)}")
                
                for execution in user_executions:
                    print(f"  - {execution.id} (status: {execution.status})")
            else:
                print("User not found!")
            
            break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow_execution_query())
