#!/usr/bin/env python3
"""
Script para corrigir todas as referências de schema nas migrações do Alembic.
Esse script muda todas as tabelas para serem criadas no schema synapscale_db em vez de public.
Também atualiza todas as referências para usar o schema correto.
"""

import re
import os
import sys

# Adiciona o diretório raiz ao sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# Arquivo de migração principal
MIGRATIONS_DIR = os.path.join(BASE_DIR, "alembic", "versions")
MIGRATION_FILE = os.path.join(MIGRATIONS_DIR, "294dba6f3a38_init.py")

def backup_file(filepath):
    """Cria uma cópia de backup do arquivo."""
    backup_path = f"{filepath}.bak"
    with open(filepath, "r", encoding="utf-8") as f_src:
        with open(backup_path, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
    print(f"Backup criado: {backup_path}")
    return backup_path

def fix_schema_references(file_path):
    """
    Corrige todas as referências de schema no arquivo de migração.
    Muda todas as tabelas para serem criadas no schema synapscale_db em vez de public.
    """
    # Criar backup do arquivo original
    backup_file(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Contador de alterações
    changes_count = 0
    
    # Padrão 1: schema='public' em create_table
    pattern1 = r"schema='public'"
    replacement1 = r"schema='synapscale_db'"
    content, count1 = re.subn(pattern1, replacement1, content)
    changes_count += count1
    
    # Padrão 2: 'public.<table_name>.<column>' em ForeignKeyConstraint
    pattern2 = r"'public\.([^']+)\.([^']+)'"
    replacement2 = r"'synapscale_db.\1.\2'"
    content, count2 = re.subn(pattern2, replacement2, content)
    changes_count += count2
    
    # Padrão 3: op.create_index(..., schema='public')
    pattern3 = r"op\.create_index\(([^,]+), '([^']+)', \[([^\]]+)\], unique=([^,]+), schema='public'\)"
    replacement3 = r"op.create_index(\1, '\2', [\3], unique=\4, schema='synapscale_db')"
    content, count3 = re.subn(pattern3, replacement3, content)
    changes_count += count3
    
    # Padrão 4: op.create_table('table_name', sem schema especificado
    pattern4 = r"op\.create_table\('([^']+)',\s*"
    replacement4 = r"op.create_table('\1', schema='synapscale_db', "
    content, count4 = re.subn(pattern4, replacement4, content)
    changes_count += count4
    
    # Padrão 5: op.drop_table('table_name', schema='public')
    pattern5 = r"op\.drop_table\('([^']+)', schema='public'\)"
    replacement5 = r"op.drop_table('\1', schema='synapscale_db')"
    content, count5 = re.subn(pattern5, replacement5, content)
    changes_count += count5
    
    # Padrão 6: op.drop_index(..., table_name='table_name', schema='public')
    pattern6 = r"op\.drop_index\(([^,]+), table_name='([^']+)', schema='public'\)"
    replacement6 = r"op.drop_index(\1, table_name='\2', schema='synapscale_db')"
    content, count6 = re.subn(pattern6, replacement6, content)
    changes_count += count6
    
    # Padrão 7: op.f('ix_public_...')
    pattern7 = r"op\.f\('ix_public_([^']+)'\)"
    replacement7 = r"op.f('ix_synapscale_db_\1')"
    content, count7 = re.subn(pattern7, replacement7, content)
    changes_count += count7

    # Salvar o arquivo atualizado
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Arquivo {file_path} atualizado com sucesso!")
    print(f"Total de alterações: {changes_count}")
    
    return changes_count

if __name__ == "__main__":
    # Verificar se o arquivo de migração existe
    if not os.path.isfile(MIGRATION_FILE):
        print(f"Arquivo de migração não encontrado: {MIGRATION_FILE}")
        sys.exit(1)
    
    # Corrigir as referências de schema
    changes = fix_schema_references(MIGRATION_FILE)
    
    print(f"Correção concluída! Total de alterações: {changes}")
    print("Agora execute: python -m alembic -c config/alembic.ini downgrade base")
    print("E depois: python -m alembic -c config/alembic.ini upgrade head")
