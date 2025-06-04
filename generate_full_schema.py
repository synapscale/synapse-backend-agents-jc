#!/usr/bin/env python3
"""
Script para criar um schema Prisma completo baseado na estrutura real do banco SQLite
"""

import psycopg2
import re

def get_table_info(cursor, table_name):
    """Obtém informações sobre uma tabela"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = cursor.fetchall()
    
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    
    return columns, foreign_keys, indexes

def sqlite_type_to_prisma(sqlite_type):
    """Converte tipos SQLite para tipos Prisma"""
    sqlite_type = sqlite_type.upper()
    
    if 'VARCHAR' in sqlite_type or 'TEXT' in sqlite_type or 'CHAR' in sqlite_type:
        return 'String'
    elif 'INTEGER' in sqlite_type or 'INT' in sqlite_type:
        return 'Int'
    elif 'REAL' in sqlite_type or 'FLOAT' in sqlite_type or 'DOUBLE' in sqlite_type:
        return 'Float'
    elif 'BOOLEAN' in sqlite_type or 'BOOL' in sqlite_type:
        return 'Boolean'
    elif 'DATETIME' in sqlite_type or 'TIMESTAMP' in sqlite_type:
        return 'DateTime'
    elif 'DATE' in sqlite_type:
        return 'DateTime'
    elif 'JSON' in sqlite_type:
        return 'String'  # SQLite stores JSON as text
    else:
        return 'String'  # Default fallback

def generate_prisma_schema():
    """Gera o schema Prisma completo"""
    
    # Conectar ao banco
    conn = psycopg2.connect('/workspaces/synapse-backend-agents-jc/synapse.db')
    cursor = conn.cursor()
    
    # Obter lista de tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Encontradas {len(tables)} tabelas: {', '.join(tables)}")
    
    # Início do schema
    schema = '''// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
  output   = "../src/generated/prisma"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

'''
    
    # Gerar modelos para cada tabela
    for table in sorted(tables):
        columns, foreign_keys, indexes = get_table_info(cursor, table)
        
        schema += f"model {table} {{\n"
        
        # Gerar campos
        for col in columns:
            col_id, name, type_str, not_null, default_value, pk = col
            
            prisma_type = sqlite_type_to_prisma(type_str)
            
            # Adicionar ? se pode ser null
            if not not_null and not pk:
                prisma_type += "?"
            
            # Campo
            field_line = f"  {name:<25} {prisma_type:<15}"
            
            # Adicionar atributos
            attributes = []
            if pk:
                attributes.append("@id")
                if prisma_type == "Int":
                    attributes.append("@default(autoincrement())")
            elif default_value is not None:
                if prisma_type.startswith("DateTime"):
                    attributes.append("@default(now())")
                elif default_value == "true" or default_value == "false":
                    attributes.append(f"@default({default_value})")
            
            if attributes:
                field_line += " " + " ".join(attributes)
            
            schema += field_line + "\n"
        
        # Adicionar índices se houver
        for idx in indexes:
            if idx[2]:  # Se é único
                schema += f"  @@unique([{idx[1]}])\n"
        
        schema += "}\n\n"
    
    conn.close()
    
    # Salvar schema
    with open('/workspaces/synapse-backend-agents-jc/prisma/schema.prisma', 'w') as f:
        f.write(schema)
    
    print(f"✅ Schema Prisma gerado com {len(tables)} tabelas!")
    print("📁 Salvo em: prisma/schema.prisma")
    
    return len(tables)

if __name__ == "__main__":
    count = generate_prisma_schema()
    print(f"\n🎉 Schema completo com {count} tabelas gerado com sucesso!")
