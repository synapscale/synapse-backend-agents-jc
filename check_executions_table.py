#!/usr/bin/env python3
"""
Script para verificar a estrutura real da tabela executions
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from sqlalchemy import text

async def check_executions_table():
    """Check actual executions table structure"""
    try:
        async for db in get_async_db():
            # Check if executions table exists
            print("Checking tables with 'execution' in name...")
            query = text("""
                SELECT table_name
                FROM information_schema.tables 
                WHERE table_schema = 'synapscale_db' 
                AND table_name LIKE '%execution%'
            """)
            result = await db.execute(query)
            tables = result.fetchall()
            
            for table in tables:
                print(f"Found table: {table[0]}")
                
                # Get table structure
                structure_query = text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'synapscale_db'
                    AND table_name = '{table[0]}'
                    ORDER BY ordinal_position
                """)
                
                structure_result = await db.execute(structure_query)
                columns = structure_result.fetchall()
                
                print(f"Table {table[0]} structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                print()
            
            break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_executions_table())
