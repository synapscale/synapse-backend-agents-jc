#!/usr/bin/env python3
"""
Script para corrigir parâmetros 'schema' nos comandos op.f() nas migrações do Alembic.
Garante que não haja parâmetros duplicados de schema.
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
    backup_path = f"{filepath}.bak4"
    with open(filepath, "r", encoding="utf-8") as f_src:
        with open(backup_path, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
    print(f"Backup criado: {backup_path}")
    return backup_path

def fix_create_index_syntax(file_path):
    """
    Corrige a sintaxe dos comandos create_index no arquivo de migração.
    Garante que não haja parâmetros duplicados de schema.
    """
    # Criar backup do arquivo original
    backup_file(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Padrão para remover schema do op.f()
    pattern1 = r"op\.f\('([^']+)', schema='synapscale_db'\)"
    replacement1 = r"op.f('\1')"
    content, count1 = re.subn(pattern1, replacement1, content)
    
    # Salvar o arquivo atualizado
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Arquivo {file_path} atualizado com sucesso!")
    print(f"Total de alterações: {count1}")
    
    return count1

if __name__ == "__main__":
    # Verificar se o arquivo de migração existe
    if not os.path.isfile(MIGRATION_FILE):
        print(f"Arquivo de migração não encontrado: {MIGRATION_FILE}")
        sys.exit(1)
    
    # Corrigir a sintaxe dos comandos create_index
    changes = fix_create_index_syntax(MIGRATION_FILE)
    
    print(f"Correção concluída! Total de alterações: {changes}")
    print("Agora execute: python -m alembic -c config/alembic.ini downgrade base")
    print("E depois: python -m alembic -c config/alembic.ini upgrade head")
