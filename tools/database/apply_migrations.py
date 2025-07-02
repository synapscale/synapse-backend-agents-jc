#!/usr/bin/env python3
"""
Script para executar as migrações adicionais no schema synapscale_db
"""

import psycopg2
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# URL do banco de dados - obtida do .env
DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA = os.getenv("DATABASE_SCHEMA", "synapscale_db")


def execute_migration_file(filename):
    """Executa um arquivo de migração Python"""
    print(f"\n🔄 Executando migração: {filename}")

    try:
        with open(f"migrations/{filename}", "r") as f:
            content = f.read()

        # Executa o conteúdo do arquivo Python
        exec_globals = {
            "DATABASE_URL": DATABASE_URL,
            "SCHEMA": SCHEMA,
            "__name__": "__main__",
        }

        exec(content, exec_globals)
        print(f"✅ Migração {filename} executada com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao executar {filename}: {e}")
        return False

    return True


def main():
    print("🚀 Iniciando execução das migrações adicionais...")
    print(f"📊 Schema de destino: {SCHEMA}")

    # Lista de migrações na ordem correta
    migrations = [
        "001_create_user_variables.py",
        "002_create_workflow_executions.py",
        "003_create_templates.py",
        "004_create_executor_configs.py",
        "005_create_fase4_tables.py",
    ]

    success_count = 0

    for migration in migrations:
        if execute_migration_file(migration):
            success_count += 1

    print(
        f"\n🏁 Concluído! {success_count}/{len(migrations)} migrações executadas com sucesso."
    )

    # Verificar tabelas finais
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{SCHEMA}' 
            ORDER BY table_name
        """
        )

        tables = cur.fetchall()
        print(f"\n📊 Total de tabelas no schema '{SCHEMA}': {len(tables)}")
        for table in tables:
            print(f"  ✓ {table[0]}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao verificar tabelas finais: {e}")


if __name__ == "__main__":
    main()
