#!/usr/bin/env python3
"""
Script para verificar em quais schemas as tabelas foram criadas
"""

import psycopg2

DATABASE_URL = "postgresql://doadmin:AVNS_DDsc3wHcfGgbX_USTUt@db-banco-dados-automacoes-do-user-13851907-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🔍 Verificando todos os schemas...")
    
    # Verificar todos os schemas
    cur.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT LIKE 'pg_%' 
        AND schema_name != 'information_schema'
        ORDER BY schema_name
    """)
    
    schemas = cur.fetchall()
    print(f"\n📊 Schemas disponíveis: {[s[0] for s in schemas]}")
    
    # Verificar tabelas em cada schema
    for schema in schemas:
        schema_name = schema[0]
        print(f"\n🔸 Schema: {schema_name}")
        
        cur.execute(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{schema_name}' 
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"   Total: {len(tables)} tabelas")
        
        if len(tables) > 0:
            for table in tables:
                print(f"   ✓ {table[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
