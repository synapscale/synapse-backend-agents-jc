#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados
"""

import psycopg2

try:
    conn = psycopg2.connect(
        "postgresql://doadmin:AVNS_DDsc3wHcfGgbX_USTUt@db-banco-dados-automacoes-do-user-13851907-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
    )
    print("Conexão bem sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro na conexão: {e}")
