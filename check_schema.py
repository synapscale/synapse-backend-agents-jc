#!/usr/bin/env python3
"""
Script para verificar tabelas existentes no schema synapscale_db
"""

import psycopg2
import os

# URL direta do banco
DATABASE_URL = "postgresql://doadmin:AVNS_DDsc3wHcfGgbX_USTUt@db-banco-dados-automacoes-do-user-13851907-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🔍 Verificando schema synapscale_db...")
    
    # Verificar tabelas no schema synapscale_db
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'synapscale_db' 
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    print(f"\n📊 Tabelas existentes no schema 'synapscale_db': {len(tables)} tabelas")
    for table in tables:
        print(f"  ✓ {table[0]}")
    
    # Verificar se alembic_version existe no schema correto
    cur.execute("""
        SELECT version_num 
        FROM synapscale_db.alembic_version 
        LIMIT 1
    """)
    
    try:
        version = cur.fetchone()
        if version:
            print(f"\n🔖 Versão atual do Alembic: {version[0]}")
        else:
            print("\n⚠️  Tabela alembic_version existe mas está vazia")
    except psycopg2.Error:
        print("\n❌ Tabela alembic_version não encontrada no schema synapscale_db")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
