#!/usr/bin/env python3
"""
SynapScale Database Structure Analysis

This script analyzes the PostgreSQL database structure to verify:
1. Database connectivity using environment variables
2. Schema structure (synapscale_db)
3. Table structure and relationships
4. Index status
5. Foreign key constraints
"""

import os
import json
import psycopg2
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    return {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'DATABASE_SCHEMA': os.getenv('DATABASE_SCHEMA', 'synapscale_db'),
        'POSTGRES_USER': os.getenv('POSTGRES_USER'),
        'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'POSTGRES_DB': os.getenv('POSTGRES_DB')
    }


def connect_to_database(config: Dict[str, str]):
    """Connect to PostgreSQL database using environment configuration"""
    try:
        # Use DATABASE_URL if available, otherwise construct from components
        if config['DATABASE_URL']:
            conn = psycopg2.connect(config['DATABASE_URL'])
        else:
            # Fallback to individual components (not available in current .env)
            conn = psycopg2.connect(
                host=config.get('DB_HOST', 'localhost'),
                port=config.get('DB_PORT', 5432),
                database=config.get('POSTGRES_DB', 'defaultdb'),
                user=config.get('POSTGRES_USER'),
                password=config.get('POSTGRES_PASSWORD')
            )
        
        print("✅ Database connection successful!")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def get_schema_tables(conn, schema_name: str) -> List[Dict[str, Any]]:
    """Get all tables in the specified schema"""
    query = """
    SELECT 
        table_name,
        table_type,
        table_schema
    FROM information_schema.tables 
    WHERE table_schema = %s
    ORDER BY table_name;
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query, (schema_name,))
        columns = [desc[0] for desc in cursor.description]
        tables = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return tables


def get_table_columns(conn, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
    """Get column information for a specific table"""
    query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length,
        numeric_precision,
        numeric_scale,
        ordinal_position
    FROM information_schema.columns 
    WHERE table_schema = %s AND table_name = %s
    ORDER BY ordinal_position;
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query, (schema_name, table_name))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_foreign_keys(conn, schema_name: str) -> List[Dict[str, Any]]:
    """Get foreign key relationships"""
    query = """
    SELECT
        tc.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name,
        tc.constraint_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = %s
    ORDER BY tc.table_name, kcu.column_name;
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query, (schema_name,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_indexes(conn, schema_name: str) -> List[Dict[str, Any]]:
    """Get index information"""
    query = """
    SELECT
        schemaname,
        tablename,
        indexname,
        indexdef
    FROM pg_indexes
    WHERE schemaname = %s
    ORDER BY tablename, indexname;
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query, (schema_name,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_table_statistics(conn, schema_name: str) -> List[Dict[str, Any]]:
    """Get table statistics"""
    query = """
    SELECT
        schemaname,
        relname as tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_live_tup as live_tuples,
        n_dead_tup as dead_tuples
    FROM pg_stat_user_tables
    WHERE schemaname = %s
    ORDER BY relname;
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query, (schema_name,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def analyze_database_structure():
    """Main function to analyze database structure"""
    print("🔍 Starting SynapScale Database Structure Analysis")
    print("=" * 60)
    
    # Load environment
    config = load_environment()
    print(f"📊 Database Schema: {config['DATABASE_SCHEMA']}")
    print(f"👤 Database User: {config['POSTGRES_USER']}")
    
    # Connect to database
    conn = connect_to_database(config)
    if not conn:
        return
    
    try:
        schema_name = config['DATABASE_SCHEMA']
        
        # Get tables
        print(f"\n📋 Analyzing tables in schema '{schema_name}'...")
        tables = get_schema_tables(conn, schema_name)
        print(f"Found {len(tables)} tables")
        
        # Get foreign keys
        print(f"\n🔗 Analyzing foreign key relationships...")
        foreign_keys = get_foreign_keys(conn, schema_name)
        print(f"Found {len(foreign_keys)} foreign key constraints")
        
        # Get indexes
        print(f"\n📇 Analyzing indexes...")
        indexes = get_indexes(conn, schema_name)
        print(f"Found {len(indexes)} indexes")
        
        # Get statistics
        print(f"\n📈 Getting table statistics...")
        statistics = get_table_statistics(conn, schema_name)
        
        # Build comprehensive analysis
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'database_config': {
                'schema': schema_name,
                'user': config['POSTGRES_USER'],
                'database': config['POSTGRES_DB']
            },
            'summary': {
                'total_tables': len(tables),
                'total_foreign_keys': len(foreign_keys),
                'total_indexes': len(indexes)
            },
            'tables': {}
        }
        
        # Detailed table analysis
        for table in tables:
            table_name = table['table_name']
            print(f"  📊 Analyzing table: {table_name}")
            
            # Get columns
            columns = get_table_columns(conn, schema_name, table_name)
            
            # Get table-specific foreign keys
            table_fks = [fk for fk in foreign_keys if fk['table_name'] == table_name]
            
            # Get table-specific indexes
            table_indexes = [idx for idx in indexes if idx['tablename'] == table_name]
            
            # Get table statistics
            table_stats = next((stat for stat in statistics if stat['tablename'] == table_name), {})
            
            analysis['tables'][table_name] = {
                'table_info': table,
                'columns': columns,
                'foreign_keys': table_fks,
                'indexes': table_indexes,
                'statistics': table_stats,
                'column_count': len(columns),
                'foreign_key_count': len(table_fks),
                'index_count': len(table_indexes)
            }
        
        # Save analysis to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_structure_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: {filename}")
        
        # Print summary
        print(f"\n📊 ANALYSIS SUMMARY")
        print(f"=" * 30)
        print(f"Schema: {schema_name}")
        print(f"Total Tables: {len(tables)}")
        print(f"Total Foreign Keys: {len(foreign_keys)}")
        print(f"Total Indexes: {len(indexes)}")
        
        print(f"\n📋 Main Tables Found:")
        core_tables = ['users', 'workspaces', 'agents', 'conversations', 'messages', 
                      'workflows', 'nodes', 'llms', 'files', 'workflow_executions']
        
        for table_name in core_tables:
            status = "✅" if table_name in [t['table_name'] for t in tables] else "❌"
            print(f"  {status} {table_name}")
        
        print(f"\n🔗 Foreign Key Relationships:")
        relationship_summary = {}
        for fk in foreign_keys:
            source = fk['table_name']
            target = fk['foreign_table_name']
            if source not in relationship_summary:
                relationship_summary[source] = []
            relationship_summary[source].append(target)
        
        for source, targets in relationship_summary.items():
            print(f"  📤 {source} → {', '.join(set(targets))}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None
    
    finally:
        conn.close()
        print(f"\n🔒 Database connection closed")


if __name__ == "__main__":
    analysis = analyze_database_structure()
    if analysis:
        print(f"\n✅ Database structure analysis completed successfully!")
    else:
        print(f"\n❌ Database structure analysis failed!") 