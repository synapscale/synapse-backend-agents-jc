#!/usr/bin/env python3
"""
Script para verificar em quais schemas as tabelas foram criadas
"""

import psycopg2
import os
from dotenv import load_dotenv

# SEGURANÇA: Carregar DATABASE_URL do .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERRO: DATABASE_URL não encontrada no arquivo .env")
    print("Configure a variável DATABASE_URL no seu arquivo .env")
    exit(1)

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
