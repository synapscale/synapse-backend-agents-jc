#!/usr/bin/env python3
"""
Script para verificar a estrutura real da tabela files
"""
import asyncio
import sys
sys.path.append('src')

from synapse.database import get_async_db
from sqlalchemy import text

async def check_files_table():
    """Check actual files table structure"""
    try:
        async for db in get_async_db():
            # Check if files table exists
            print("Checking if files table exists...")
            query = text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'synapscale_db' 
                    AND table_name = 'files'
                )
            """)
            result = await db.execute(query)
            exists = result.scalar()
            print(f"Files table exists: {exists}")
            
            if exists:
                # Get table structure
                print("Getting table structure...")
                structure_query = text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'synapscale_db'
                    AND table_name = 'files'
                    ORDER BY ordinal_position
                """)
                
                structure_result = await db.execute(structure_query)
                columns = structure_result.fetchall()
                
                print("Table structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                
                # Count records
                count_query = text("SELECT COUNT(*) FROM synapscale_db.files")
                count_result = await db.execute(count_query)
                count = count_result.scalar()
                print(f"Total records: {count}")
            
            break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_files_table())
