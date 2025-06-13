#!/usr/bin/env python3
"""
Script para criar o schema synapscale_db e aplicar migrações
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("✅ Conectado ao banco de dados")
        
        # Criar schema se não existir
        cur.execute("CREATE SCHEMA IF NOT EXISTS synapscale_db")
        print("✅ Schema 'synapscale_db' criado/verificado")
        
        # Verificar se existe
        cur.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'synapscale_db'
        """)
        
        schema_exists = cur.fetchone()
        print(f"✅ Schema existe: {schema_exists is not None}")
        
        # Verificar tabelas existentes no schema
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'synapscale_db' 
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"📋 Tabelas no schema 'synapscale_db': {[t[0] for t in tables]}")
        print(f"📊 Total: {len(tables)} tabelas")
        
        # Criar tabela alembic_version no schema correto se não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS synapscale_db.alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """)
        print("✅ Tabela alembic_version criada no schema synapscale_db")
        
        cur.close()
        conn.close()
        print("✅ Processo concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
