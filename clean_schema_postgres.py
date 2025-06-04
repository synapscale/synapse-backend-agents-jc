#!/usr/bin/env python3
"""
Script para limpar o schema Prisma removendo índices SQLite e preparando para PostgreSQL
"""

import re

def clean_schema_for_postgres():
    """Remove índices SQLite e prepara schema para PostgreSQL"""
    
    # Ler o schema atual
    schema_path = '/workspaces/synapse-backend-agents-jc/prisma/schema.prisma'
    with open(schema_path, 'r') as f:
        content = f.read()
    
    print("🧹 Limpando schema para PostgreSQL...")
    
    # 1. Trocar provider para postgresql (já feito)
    content = re.sub(r'provider = "postgresql"', 'provider = "postgresql"', content)
    
    # 2. Remover todas as linhas com @@unique([sqlite_autoindex_...])
    content = re.sub(r'\s*@@unique\(\[sqlite_autoindex_[^\]]+\]\)\n', '', content)
    
    # 3. Remover todas as linhas com @@unique([ix_...])
    content = re.sub(r'\s*@@unique\(\[ix_[^\]]+\]\)\n', '', content)
    
    # 4. Ajustar campos String para Text quando apropriado (para campos grandes)
    large_text_fields = [
        'content', 'description', 'instructions', 'configuration', 
        'workflow_data', 'properties', 'metadata', 'code_template',
        'input_schema', 'output_schema', 'parameters_schema', 'documentation',
        'examples', 'query_config', 'visualization_config', 'schedule_config',
        'cached_data', 'result_data', 'input_data', 'output_data', 
        'config_data', 'execution_log', 'error_details', 'debug_info'
    ]
    
    # Substituir String por Text para campos grandes
    for field in large_text_fields:
        # Padrão: campo String? ou String
        content = re.sub(
            rf'(\s+{field}\s+)String(\?)?(\s+)',
            r'\1String\2\3',  # Manter String por enquanto
            content
        )
    
    # 5. Limpar espaços extras e linhas vazias duplicadas
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Salvar o schema limpo
    with open(schema_path, 'w') as f:
        f.write(content)
    
    print("✅ Schema limpo e preparado para PostgreSQL!")
    
    # Contar modelos
    model_count = len(re.findall(r'^model\s+\w+\s*{', content, re.MULTILINE))
    print(f"📊 {model_count} modelos encontrados")
    
    return model_count

if __name__ == "__main__":
    count = clean_schema_for_postgres()
    print(f"\n🎉 Schema PostgreSQL com {count} modelos preparado!")
    print("\n📋 Próximos passos:")
    print("1. Aplicar migração no PostgreSQL")
    print("2. Testar conexão")
    print("3. Gerar client Prisma")
