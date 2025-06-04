#!/usr/bin/env python3
"""
Script inteligente para migrar TODAS as 49 tabelas do PostgreSQL
"""

import psycopg2
import os
import re


def postgresql_type_to_prisma(postgresql_type):
    """Converte tipos PostgreSQL para tipos Prisma"""
    if not postgresql_type:
        return 'String'
    
    postgresql_type = postgresql_type.upper()
    
    if 'VARCHAR' in postgresql_type or 'TEXT' in postgresql_type or 'CHAR' in postgresql_type:
        return 'String'
    elif 'INTEGER' in postgresql_type or 'INT' in postgresql_type:
        return 'Int'
    elif 'REAL' in postgresql_type or 'FLOAT' in postgresql_type or 'DOUBLE' in postgresql_type or 'NUMERIC' in postgresql_type:
        return 'Float'
    elif 'BOOLEAN' in postgresql_type or 'BOOL' in postgresql_type:
        return 'Boolean'
    elif 'DATETIME' in postgresql_type or 'TIMESTAMP' in postgresql_type:
        return 'DateTime'
    elif 'DATE' in postgresql_type:
        return 'DateTime'
    elif 'JSON' in postgresql_type:
        return 'Json'
    else:
        return 'String'


def clean_column_name(name):
    """Limpa e formata o nome da coluna"""
    # Remove caracteres inválidos e substitui por underscore
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Se começar com número, adiciona underscore
    if cleaned[0].isdigit():
        cleaned = '_' + cleaned
    return cleaned


def get_table_structure(cursor, table_name):
    """Obtém a estrutura da tabela"""
    cursor.execute(
        "SELECT column_name, data_type, is_nullable, column_default, "
        "ordinal_position, character_maximum_length "
        "FROM information_schema.columns WHERE table_name = %s",
        (table_name,)
    )
    columns = cursor.fetchall()
    
    cursor.execute(f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_name='{table_name}' AND tc.constraint_type='FOREIGN KEY'
    """)
    foreign_keys = cursor.fetchall()
    
    cursor.execute(f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '{table_name}'")
    indexes = cursor.fetchall()
    
    return columns, foreign_keys, indexes


def process_columns(columns):
    """Processa as colunas de uma tabela"""
    schema = ""
    for col in columns:
        name, type_str, not_null, default_value, ordinal_position, char_max_length = col
        
        # Limpar nome da coluna
        clean_name = clean_column_name(name)
        prisma_type = postgresql_type_to_prisma(type_str)
        
        # Adicionar ? se nullable (exceto PKs)
        if not not_null:
            prisma_type += "?"
        
        # Linha do campo
        field_line = f"  {clean_name:<25} {prisma_type:<15}"
        
        # Atributos
        attributes = []
        if ordinal_position == 1:  # Supondo que a primeira coluna é sempre a PK
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
    
    return schema


def generate_complete_schema():
    """Gera o esquema completo do PostgreSQL"""
    
    # Conectar ao PostgreSQL
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Obter TODAS as tabelas (exceto sistema)
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"🔍 Encontradas {len(tables)} tabelas:")
    for i, table in enumerate(tables, 1):
        print(f"  {i:2d}. {table}")
    
    # Schema base
    schema = '''// Prisma Schema Completo - SynapScale PostgreSQL
// Auto-gerado a partir do PostgreSQL com TODAS as tabelas

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
        schema += process_columns(columns)
        
        # Índices únicos compostos
        unique_indexes = []
        for idx in indexes:
            idx_name, idx_def = idx
            if 'UNIQUE' in idx_def:
                # Extrair colunas do índice
                idx_columns = re.findall(r'\((.*?)\)', idx_def)
                if idx_columns:
                    idx_columns = idx_columns[0].split(',')
                    idx_columns = [clean_column_name(col.strip()) for col in idx_columns]
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
    print("🚀 Iniciando migração completa PostgreSQL")
    print("=" * 50)
    
    count = generate_complete_schema()
    
    print("=" * 50)
    print(f"🎉 SUCESSO! {count} tabelas migradas para PostgreSQL")
    print("\n📋 Próximos passos:")
    print("1. Aplicar migração: prisma migrate dev")
    print("2. Gerar cliente: prisma generate")
    print("3. Testar conexão")
    print("4. Migrar dados do SQLite")
