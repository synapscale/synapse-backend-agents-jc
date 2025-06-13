#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Conexão bem sucedida!")
    
    # Verificar se o schema synapscale_db existe
    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = 'synapscale_db'
    """)
    
    schema_exists = cur.fetchone()
    print(f"Schema 'synapscale_db' existe: {schema_exists is not None}")
    
    if not schema_exists:
        print("Criando schema synapscale_db...")
        cur.execute("CREATE SCHEMA IF NOT EXISTS synapscale_db")
        conn.commit()
        print("Schema synapscale_db criado!")
    
    # Verificar tabelas no schema synapscale_db
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'synapscale_db'
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    print(f"Tabelas no schema 'synapscale_db': {[t[0] for t in tables]}")
    print(f"Total de tabelas: {len(tables)}")
    
    # Verificar tabela alembic_version
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'synapscale_db'
            AND table_name = 'alembic_version'
        )
    """)
    
    result = cur.fetchone()
    alembic_exists = result[0] if result else False
    print(f"Tabela alembic_version no schema synapscale_db: {alembic_exists}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Erro na conexão: {e}")
