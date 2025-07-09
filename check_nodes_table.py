#!/usr/bin/env python3
"""
Script para verificar a estrutura real da tabela nodes
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from sqlalchemy import text

async def check_nodes_table():
    """Check actual nodes table structure"""
    try:
        async for db in get_async_db():
            # Check if nodes table exists
            print("Checking if nodes table exists...")
            query = text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'synapscale_db' 
                    AND table_name = 'nodes'
                )
            """)
            result = await db.execute(query)
            exists = result.scalar()
            print(f"Nodes table exists: {exists}")
            
            if exists:
                # Get table structure
                print("Getting table structure...")
                structure_query = text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'synapscale_db'
                    AND table_name = 'nodes'
                    ORDER BY ordinal_position
                """)
                
                structure_result = await db.execute(structure_query)
                columns = structure_result.fetchall()
                
                print("Table structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                
                # Count records
                count_query = text("SELECT COUNT(*) FROM synapscale_db.nodes")
                count_result = await db.execute(count_query)
                count = count_result.scalar()
                print(f"Total records: {count}")
                
                if count > 0:
                    # Sample data
                    sample_query = text("SELECT * FROM synapscale_db.nodes LIMIT 3")
                    sample_result = await db.execute(sample_query)
                    samples = sample_result.fetchall()
                    print("Sample data:")
                    for row in samples:
                        print(f"  - {dict(row._mapping)}")
            
            break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_nodes_table())
