#!/usr/bin/env python3
"""
Script para corrigir todas as referências de schema nas migrações do Alembic,
trocando 'public' por 'synapscale_db'.

Este script:
1. Localiza todas as ocorrências de schema='public' no arquivo de migração
2. Substitui por schema='synapscale_db'
3. Corrige referências em ForeignKeyConstraint que apontam para public
4. Corrige referências em índices (create_index)

O objetivo é garantir que todas as tabelas sejam criadas no schema correto.
"""

import os
import re
from pathlib import Path


def fix_migration_file(filepath):
    """Corrige as referências de schema em um arquivo de migração."""
    with open(filepath, 'r') as file:
        content = file.read()

    # Contador para acompanhar o número de alterações
    changes = 0

    # 1. Substituir schema='public' por schema='synapscale_db'
    pattern = r"schema='public'"
    replacement = r"schema='synapscale_db'"
    content, count = re.subn(pattern, replacement, content)
    changes += count
    print(f"- Substituídas {count} ocorrências de schema='public' por schema='synapscale_db'")

    # 2. Corrigir referências em ForeignKeyConstraint
    pattern = r"\['public\.(.*?)\.(.*?)'\]"
    replacement = r"['synapscale_db.\1.\2']"
    content, count = re.subn(pattern, replacement, content)
    changes += count
    print(f"- Substituídas {count} ocorrências de referências ForeignKeyConstraint para public")

    # 3. Corrigir referências em create_index
    pattern = r"op\.f\('ix_public_(.*?)'\)"
    replacement = r"op.f('ix_synapscale_db_\1')"
    content, count = re.subn(pattern, replacement, content)
    changes += count
    print(f"- Substituídas {count} ocorrências de referências ix_public em create_index")

    # 4. Corrigir referências em drop_index
    pattern = r"table_name='(.*?)', schema='public'"
    replacement = r"table_name='\1', schema='synapscale_db'"
    content, count = re.subn(pattern, replacement, content)
    changes += count
    print(f"- Substituídas {count} ocorrências de schema='public' em drop_index")

    # 5. Corrigir comentários com "public" schema
    pattern = r"# ### commands auto generated by Alembic - public schema"
    replacement = r"# ### commands auto generated by Alembic - synapscale_db schema"
    content, count = re.subn(pattern, replacement, content)
    changes += count

    # Salvar o arquivo atualizado
    with open(filepath, 'w') as file:
        file.write(content)

    return changes


def main():
    """Função principal."""
    print("🔍 Procurando arquivo de migração para corrigir...")
    
    # Obter o diretório base
    base_dir = Path(__file__).parent.parent
    versions_dir = base_dir / "alembic" / "versions"
    
    # Encontrar o arquivo de migração init.py
    target_file = versions_dir / "294dba6f3a38_init.py"
    
    if not target_file.exists():
        print(f"❌ Arquivo de migração {target_file} não encontrado!")
        return
    
    print(f"✅ Arquivo de migração encontrado: {target_file}")
    print("\n🔧 Corrigindo referências de schema...")
    
    # Corrigir o arquivo
    changes = fix_migration_file(target_file)
    
    print(f"\n✅ Concluído! {changes} alterações feitas no arquivo de migração.")
    print("\nAgora você pode executar o comando de migração para aplicar as alterações:")
    print("  cd /workspaces/synapse-backend-agents-jc")
    print("  python -m alembic -c config/alembic.ini upgrade head")


if __name__ == "__main__":
    main()
