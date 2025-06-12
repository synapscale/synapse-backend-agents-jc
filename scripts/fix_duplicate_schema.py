#!/usr/bin/env python3
"""
Script para corrigir parâmetros duplicados (schema) nas migrações do Alembic.
Remove parâmetros duplicados nos comandos create_index.
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
    backup_path = f"{filepath}.bak3"
    with open(filepath, "r", encoding="utf-8") as f_src:
        with open(backup_path, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
    print(f"Backup criado: {backup_path}")
    return backup_path

def fix_duplicate_schema(file_path):
    """
    Corrige parâmetros duplicados (schema) nos comandos create_index.
    """
    # Criar backup do arquivo original
    backup_file(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Padrão para encontrar parâmetros schema duplicados
    pattern = r"(op\.f\('[^']+', schema='synapscale_db'\))(.*?)(schema='synapscale_db',\s+schema='synapscale_db')"
    replacement = r"\1\2schema='synapscale_db'"
    content, count1 = re.subn(pattern, replacement, content)
    
    # Outro padrão para encontrar parâmetros schema duplicados
    pattern2 = r"(op\.create_index[^,]+,[^,]+,[^,]+,[^,]+, schema='synapscale_db'), schema='synapscale_db'\)"
    replacement2 = r"\1)"
    content, count2 = re.subn(pattern2, replacement2, content)
    
    # Mais um padrão para parâmetros schema duplicados
    pattern3 = r"(op\.create_index\(op\.f\('[^']+'\),[^,]+,[^,]+,[^,]+, schema='synapscale_db'), schema='synapscale_db'\)"
    replacement3 = r"\1)"
    content, count3 = re.subn(pattern3, replacement3, content)
    
    changes_count = count1 + count2 + count3
    
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
    
    # Corrigir parâmetros duplicados
    changes = fix_duplicate_schema(MIGRATION_FILE)
    
    print(f"Correção concluída! Total de alterações: {changes}")
    print("Agora execute: python -m alembic -c config/alembic.ini downgrade base")
    print("E depois: python -m alembic -c config/alembic.ini upgrade head")
