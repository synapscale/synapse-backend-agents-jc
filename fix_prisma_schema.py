#!/usr/bin/env python3
"""
Script para corrigir tipos UUID no schema do Prisma
Converte Unsupported("uuid") para String apropriadamente
"""

import re

def fix_prisma_schema():
    schema_path = "/workspaces/synapse-backend-agents-jc/prisma/schema.prisma"
    
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Substituir Unsupported("uuid") por String
    content = re.sub(r'Unsupported\("uuid"\)', 'String', content)
    
    # Substituir Unsupported("json") por String (para SQLite)
    content = re.sub(r'Unsupported\("json"\)', 'String', content)
    
    # Remover comentários sobre modelos ignorados se necessário
    # Manter os @@ignore onde apropriado
    
    with open(schema_path, 'w') as f:
        f.write(content)
    
    print("✅ Schema do Prisma corrigido!")
    print("- Converteu Unsupported('uuid') para String")
    print("- Converteu Unsupported('json') para String")
    print("- Manteve configurações de relacionamento")

if __name__ == "__main__":
    fix_prisma_schema()
