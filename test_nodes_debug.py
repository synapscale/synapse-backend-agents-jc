#!/usr/bin/env python3
"""
Debug script para testar o endpoint de nodes
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from synapse.models.node import Node
from synapse.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def test_nodes_query():
    """Test nodes query directly"""
    try:
        async for db in get_async_db():
            # Test basic query
            print("Testing basic node query...")
            query = select(Node)
            result = await db.execute(query)
            nodes = result.scalars().all()
            print(f"Found {len(nodes)} nodes")
            
            # Test user query
            print("Testing user query...")
            user_query = select(User).where(User.email == "joaovictor@liderimobiliaria.com.br")
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if user:
                print(f"User found: {user.email} (tenant: {user.tenant_id})")
                
                # Test nodes for this user
                node_query = select(Node).where(
                    Node.tenant_id == user.tenant_id
                )
                node_result = await db.execute(node_query)
                user_nodes = node_result.scalars().all()
                print(f"User nodes: {len(user_nodes)}")
                
                for node in user_nodes:
                    print(f"  - {node.name} (ID: {node.id})")
            else:
                print("User not found!")
            
            break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nodes_query())
