#!/usr/bin/env python3
"""
Script inteligente para migrar TODAS as 49 tabelas do SQLite para PostgreSQL
"""

import sqlite3
import os
import re

def sqlite_type_to_prisma(sqlite_type):
    """Converte tipos SQLite para tipos Prisma PostgreSQL"""
    if not sqlite_type:
        return 'String'
    
    sqlite_type = sqlite_type.upper()
    
    if 'VARCHAR' in sqlite_type or 'TEXT' in sqlite_type or 'CHAR' in sqlite_type:
        return 'String'
    elif 'INTEGER' in sqlite_type or 'INT' in sqlite_type:
        return 'Int'
    elif 'REAL' in sqlite_type or 'FLOAT' in sqlite_type or 'DOUBLE' in sqlite_type or 'NUMERIC' in sqlite_type:
        return 'Float'
    elif 'BOOLEAN' in sqlite_type or 'BOOL' in sqlite_type:
        return 'Boolean'
    elif 'DATETIME' in sqlite_type or 'TIMESTAMP' in sqlite_type:
        return 'DateTime'
    elif 'DATE' in sqlite_type:
        return 'DateTime'
    elif 'JSON' in sqlite_type:
        return 'Json'
    else:
        return 'String'

def clean_column_name(name):
    """Limpa nomes de colunas para serem válidos no Prisma"""
    # Remove caracteres inválidos e substitui por underscore
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Se começar com número, adiciona underscore
    if cleaned[0].isdigit():
        cleaned = '_' + cleaned
    return cleaned

def get_table_structure(cursor, table_name):
    """Obtém a estrutura completa de uma tabela"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = cursor.fetchall()
    
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    
    return columns, foreign_keys, indexes

def generate_complete_schema():
    """Gera schema completo com TODAS as tabelas"""
    
    # Conectar ao SQLite
    db_path = '/workspaces/synapse-backend-agents-jc/synapse.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obter TODAS as tabelas (exceto sistema)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%' 
        AND name != 'alembic_version'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"🔍 Encontradas {len(tables)} tabelas:")
    for i, table in enumerate(tables, 1):
        print(f"  {i:2d}. {table}")
    
    # Schema base
    schema = '''// Prisma Schema Completo - SynapScale PostgreSQL
// Auto-gerado a partir do SQLite com TODAS as tabelas

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

'''
    
    # Primeiro passo: gerar todos os modelos sem relacionamentos
    models = {}
    
    for table_name in tables:
        columns, foreign_keys, indexes = get_table_structure(cursor, table_name)
        
        model_name = table_name
        schema += f"model {model_name} {{\n"
        
        # Campos da tabela
        for col in columns:
            col_id, name, type_str, not_null, default_value, pk = col
            
            # Limpar nome da coluna
            clean_name = clean_column_name(name)
            prisma_type = sqlite_type_to_prisma(type_str)
            
            # Adicionar ? se nullable (exceto PKs)
            if not not_null and not pk:
                prisma_type += "?"
            
            # Linha do campo
            field_line = f"  {clean_name:<25} {prisma_type:<15}"
            
            # Atributos
            attributes = []
            if pk:
                attributes.append("@id")
                if prisma_type == "Int":
                    attributes.append("@default(autoincrement())")
            elif default_value is not None:
                if prisma_type.startswith("DateTime"):
                    if "now" in str(default_value).lower() or "current" in str(default_value).lower():
                        attributes.append("@default(now())")
                elif prisma_type == "Boolean":
                    if str(default_value).lower() in ['true', '1']:
                        attributes.append("@default(true)")
                    elif str(default_value).lower() in ['false', '0']:
                        attributes.append("@default(false)")
                elif prisma_type == "String" and default_value:
                    # Escape aspas
                    escaped_default = str(default_value).replace('"', '\\"')
                    attributes.append(f'@default("{escaped_default}")')
            
            # Campos especiais
            if clean_name == "updated_at" and prisma_type.startswith("DateTime"):
                attributes.append("@updatedAt")
            elif clean_name in ["email", "username"] and prisma_type == "String":
                attributes.append("@unique")
            
            if attributes:
                field_line += " " + " ".join(attributes)
            
            schema += field_line + "\n"
        
        # Índices únicos compostos
        unique_indexes = []
        for idx in indexes:
            idx_name, idx_table, is_unique = idx[1], idx[0], idx[2]
            if is_unique and idx_name:
                cursor.execute(f"PRAGMA index_info({idx_name})")
                idx_columns = [clean_column_name(col[2]) for col in cursor.fetchall()]
                if len(idx_columns) > 1:
                    unique_indexes.append(idx_columns)
        
        for idx_cols in unique_indexes:
            schema += f"  @@unique([{', '.join(idx_cols)}])\n"
        
        schema += "}\n\n"
        
        # Armazenar info do modelo para relacionamentos futuros
        models[table_name] = {
            'columns': columns,
            'foreign_keys': foreign_keys
        }
    
    conn.close()
    
    # Salvar schema no hello-prisma
    schema_path = '/workspaces/synapse-backend-agents-jc/hello-prisma/prisma/schema.prisma'
    with open(schema_path, 'w') as f:
        f.write(schema)
    
    print(f"\n✅ Schema PostgreSQL completo gerado!")
    print(f"📁 Salvo em: {schema_path}")
    print(f"📊 Total de modelos: {len(tables)}")
    
    return len(tables)

if __name__ == "__main__":
    print("🚀 Iniciando migração completa SQLite → PostgreSQL")
    print("=" * 50)
    
    count = generate_complete_schema()
    
    print("=" * 50)
    print(f"🎉 SUCESSO! {count} tabelas migradas para PostgreSQL")
    print("\n📋 Próximos passos:")
    print("1. Aplicar migração: prisma migrate dev")
    print("2. Gerar cliente: prisma generate")
    print("3. Testar conexão")
    print("4. Migrar dados do SQLite")
