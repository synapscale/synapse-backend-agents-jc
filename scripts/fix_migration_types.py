#!/usr/bin/env python3
"""
Script para corrigir incompatibilidades de tipos nas migrações do Alembic.

Este script procura por todas as referências onde uma coluna do tipo INTEGER ou String
está referenciando uma coluna do tipo UUID em uma chave estrangeira,
e corrige automaticamente o tipo para UUID.
"""

import re
import sys

# Caminho para o arquivo de migração
MIGRATION_FILE = "/workspaces/synapse-backend-agents-jc/alembic/versions/294dba6f3a38_init.py"


def fix_foreign_key_types():
    """Corrige todas as incompatibilidades de tipos nas chaves estrangeiras."""
    with open(MIGRATION_FILE, "r") as f:
        content = f.read()

    # 1. Encontra todas as definições de tabelas e seus campos
    table_definitions = {}
    table_pattern = r"op\.create_table\('([^']+)',(.*?)(?:schema='[^']+'\n\s*\)|primary_key=\('id'\)\n\s*\))"
    table_matches = re.finditer(table_pattern, content, re.DOTALL)
    
    for match in table_matches:
        table_name = match.group(1)
        table_content = match.group(2)
        
        # Captura a coluna id e seu tipo
        id_match = re.search(r"sa\.Column\('id',\s*sa\.([^(]+)\(", table_content)
        if id_match:
            id_type = id_match.group(1).strip()
            table_definitions[table_name] = {"id_type": id_type}
            print(f"Tabela: {table_name}, Tipo da ID: {id_type}")
    
    print(f"Encontradas {len(table_definitions)} definições de tabelas.")
    
    # 2. Encontra todas as chaves estrangeiras
    fk_pattern = r"sa\.ForeignKeyConstraint\(\['([^']+)'\],\s*\['([^']+)\.([^']+)\.([^']+)'\]"
    fk_references = []
    
    for match in re.finditer(fk_pattern, content):
        source_column = match.group(1)
        target_schema = match.group(2)
        target_table = match.group(3)
        target_column = match.group(4)
        
        # Guarda as informações da chave estrangeira
        fk_references.append({
            "source_column": source_column,
            "target_schema": target_schema,
            "target_table": target_table,
            "target_column": target_column
        })
    
    # 3. Analisa todas as colunas procurando incompatibilidades
    column_pattern = r"sa\.Column\('([^']+)',\s*sa\.([^(]+)\(\)"
    replacements = []
    
    for match in re.finditer(column_pattern, content):
        column_name = match.group(1)
        column_type = match.group(2)
        
        # Verifica se esta coluna é uma chave estrangeira
        for fk in fk_references:
            if fk["source_column"] == column_name:
                target_table = fk["target_table"]
                target_column = fk["target_column"]
                
                # Verifica se a tabela alvo existe e se a coluna alvo é a 'id'
                if target_table in table_definitions and target_column == 'id':
                    target_type = table_definitions[target_table]["id_type"]
                    
                    # Se o tipo da coluna alvo for UUID mas o tipo da coluna fonte não for, corrige
                    if target_type == "UUID" and column_type != "UUID":
                        old_text = match.group(0)
                        new_text = f"sa.Column('{column_name}', sa.UUID()"
                        replacements.append((old_text, new_text))
                        print(f"Incompatibilidade: {column_name} ({column_type}) -> {target_table}.{target_column} ({target_type})")
    
    # 4. Aplica todas as substituições
    new_content = content
    for old_text, new_text in replacements:
        new_content = new_content.replace(old_text, new_text)
    
    # 5. Verifica especificamente os casos de workflow_id
    # Isso é necessário porque essa coluna aparece em vários lugares e às vezes é difícil de detectar
    workflow_id_pattern = r"sa\.Column\('workflow_id',\s*sa\.Integer\(\)"
    if "workflows" in table_definitions and table_definitions["workflows"]["id_type"] == "UUID":
        workflow_id_replacements = []
        for match in re.finditer(workflow_id_pattern, new_content):
            old_text = match.group(0)
            new_text = "sa.Column('workflow_id', sa.UUID()"
            workflow_id_replacements.append((old_text, new_text))
            print(f"Corrigindo workflow_id de Integer para UUID")
        
        for old_text, new_text in workflow_id_replacements:
            new_content = new_content.replace(old_text, new_text)
        
        replacements.extend(workflow_id_replacements)
    
    # 6. Verifica casos específicos conhecidos que causam problemas
    specific_fixes = [
        ("sa.Column('workflow_execution_id', sa.Integer()", "sa.Column('workflow_execution_id', sa.UUID()"),
        ("sa.Column('node_id', sa.Integer()", "sa.Column('node_id', sa.UUID()"),
        ("sa.Column('conversation_id', sa.String", "sa.Column('conversation_id', sa.UUID"),
        ("sa.Column('user_id', sa.Integer()", "sa.Column('user_id', sa.UUID()"),
    ]
    
    for old_pattern, new_pattern in specific_fixes:
        if old_pattern in new_content:
            print(f"Aplicando correção específica: {old_pattern} -> {new_pattern}")
            new_content = new_content.replace(old_pattern, new_pattern)
            replacements.append((old_pattern, new_pattern))
    
    # 7. Escreve o arquivo corrigido
    with open(MIGRATION_FILE, "w") as f:
        f.write(new_content)
    
    print(f"Corrigidas {len(replacements)} incompatibilidades de tipo.")
    return len(replacements)


if __name__ == "__main__":
    try:
        num_fixes = fix_foreign_key_types()
        print(f"Script executado com sucesso. {num_fixes} problemas corrigidos.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)
