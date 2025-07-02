#!/usr/bin/env python3
"""
Script para verificar os relacionamentos entre tabelas no schema synapscale_db
"""

import psycopg2
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("🔍 Verificando relacionamentos no schema synapscale_db...")

    # Verificar chaves estrangeiras
    cur.execute(
        """
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'synapscale_db'
        ORDER BY tc.table_name;
    """
    )

    relationships = cur.fetchall()
    print(f"\n📊 Total de relacionamentos encontrados: {len(relationships)}")
    for rel in relationships:
        print(f"  ✓ {rel[0]}.{rel[1]} -> {rel[2]}.{rel[3]}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Erro: {e}")
