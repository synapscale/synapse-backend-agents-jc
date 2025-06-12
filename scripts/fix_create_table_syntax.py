#!/usr/bin/env python3
"""
Script para corrigir erros de sintaxe nas migrações do Alembic.
Reorganiza os parâmetros dos comandos create_table para que os parâmetros nomeados
venham depois dos parâmetros posicionais.
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
    backup_path = f"{filepath}.bak2"
    with open(filepath, "r", encoding="utf-8") as f_src:
        with open(backup_path, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
    print(f"Backup criado: {backup_path}")
    return backup_path

def fix_create_table_syntax(file_path):
    """
    Corrige a sintaxe dos comandos create_table no arquivo de migração.
    Move o parâmetro schema para depois dos parâmetros posicionais.
    """
    # Criar backup do arquivo original
    backup_file(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    changes_count = 0
    in_create_table = False
    table_lines = []
    
    for line in lines:
        if "op.create_table(" in line and "schema='synapscale_db'" in line:
            in_create_table = True
            # Extrai o nome da tabela e outros parâmetros
            match = re.search(r"op\.create_table\('([^']+)', schema='synapscale_db', (.*)", line)
            if match:
                table_name = match.group(1)
                rest_of_line = match.group(2)
                # Reorganiza a linha com o schema no final
                new_line = f"    op.create_table('{table_name}', {rest_of_line}\n"
                table_lines = [new_line]
                changes_count += 1
                continue
        elif in_create_table:
            table_lines.append(line)
            # Se a linha contém schema='synapscale_db' no final da tabela
            if " schema='synapscale_db'" in line and (')' in line or '),\n' in line):
                in_create_table = False
                # Reorganiza a última linha para mover o schema para o final
                for i in range(len(table_lines) - 1, -1, -1):
                    if "schema='synapscale_db'" in table_lines[i]:
                        line = table_lines[i]
                        if "),\n" in line:
                            line = line.replace("schema='synapscale_db', ", "")
                            line = line.replace("),\n", ", schema='synapscale_db'),\n")
                        elif ")" in line:
                            line = line.replace("schema='synapscale_db', ", "")
                            line = line.replace(")", ", schema='synapscale_db')")
                        table_lines[i] = line
                        changes_count += 1
                        break
                new_lines.extend(table_lines)
                table_lines = []
                continue
        else:
            new_lines.append(line)
    
    # Se ainda houver linhas de tabela pendentes
    if table_lines:
        new_lines.extend(table_lines)
    
    # Salvar o arquivo atualizado
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"Arquivo {file_path} atualizado com sucesso!")
    print(f"Total de alterações: {changes_count}")
    
    return changes_count

if __name__ == "__main__":
    # Verificar se o arquivo de migração existe
    if not os.path.isfile(MIGRATION_FILE):
        print(f"Arquivo de migração não encontrado: {MIGRATION_FILE}")
        sys.exit(1)
    
    # Corrigir a sintaxe dos comandos create_table
    changes = fix_create_table_syntax(MIGRATION_FILE)
    
    print(f"Correção concluída! Total de alterações: {changes}")
    print("Agora execute: python -m alembic -c config/alembic.ini downgrade base")
    print("E depois: python -m alembic -c config/alembic.ini upgrade head")
