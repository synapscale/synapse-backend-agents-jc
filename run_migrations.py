#!/usr/bin/env python3
"""
Script para executar migrações manuais do diretório migrations/
"""

import sys
import os
import psycopg2
from pathlib import Path

# Adicionar src ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from synapse.core.config import settings

def execute_sql_from_migration(migration_file):
    """Extrai e executa SQL de um arquivo de migração."""
    with open(migration_file, 'r') as f:
        content = f.read()
    
    # Aqui poderíamos parsear o arquivo Python e executar as operações
    # Por enquanto, vamos executar manualmente
    print(f"Processando {migration_file}...")
    
def main():
    """Executa todas as migrações pendentes."""
    migrations_dir = Path("migrations")
    
    if not migrations_dir.exists():
        print("Diretório migrations/ não encontrado")
        return
    
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()
        
        # Verificar se a tabela alembic_version existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            )
        """)
        
        if not cur.fetchone()[0]:
            print("Tabela alembic_version não encontrada. Execute 'alembic upgrade head' primeiro.")
            return
        
        # Listar migrações
        migration_files = sorted(migrations_dir.glob("*.py"))
        
        print(f"Encontradas {len(migration_files)} migrações:")
        for mig in migration_files:
            print(f"  - {mig.name}")
        
        # Verificar tabelas existentes
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        existing_tables = {row[0] for row in cur.fetchall()}
        print(f"\\nTabelas existentes: {existing_tables}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
