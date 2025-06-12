#!/usr/bin/env python3
"""
Script para corrigir múltiplos heads no Alembic
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório src ao sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

def main():
    """Corrigir múltiplos heads no Alembic."""
    print("\n🔧 Corrigindo múltiplos heads no Alembic...\n")
    
    # Listar arquivos de migração
    versions_dir = BASE_DIR / "alembic" / "versions"
    migration_files = list(versions_dir.glob("*.py"))
    
    if not migration_files:
        print("❌ Nenhum arquivo de migração encontrado.")
        return
    
    print(f"📄 Encontrados {len(migration_files)} arquivos de migração:")
    for file in migration_files:
        print(f"   - {file.name}")
    
    # Verificar arquivos com down_revision = None (heads)
    heads = []
    for file_path in migration_files:
        with open(file_path, 'r') as f:
            content = f.read()
            if "down_revision: Union[str, None] = None" in content or "down_revision = None" in content:
                heads.append(file_path)
    
    print(f"\n🔍 Encontrados {len(heads)} arquivos de migração com down_revision = None:")
    for head in heads:
        print(f"   - {head.name}")
    
    if len(heads) <= 1:
        print("\n✅ Não há múltiplos heads para corrigir.")
        return
    
    # Escolher o arquivo mais completo para manter como head principal
    # Vamos escolher o arquivo com mais linhas, presumindo que ele tem mais tabelas
    main_head = max(heads, key=lambda f: len(open(f, 'r').readlines()))
    other_heads = [h for h in heads if h != main_head]
    
    print(f"\n📌 Mantendo como head principal: {main_head.name}")
    
    # Obter revision ID do head principal
    main_revision = None
    with open(main_head, 'r') as f:
        for line in f:
            if line.strip().startswith("revision"):
                main_revision = line.split("=")[1].strip().strip("'").strip('"')
                break
    
    if not main_revision:
        print("❌ Não foi possível encontrar o ID de revisão do head principal.")
        return
    
    # Modificar outros heads para apontar para o head principal
    for other_head in other_heads:
        print(f"\n🔄 Modificando {other_head.name} para apontar para {main_head.name}...")
        
        with open(other_head, 'r') as f:
            content = f.readlines()
        
        new_content = []
        for line in content:
            if line.strip().startswith("down_revision"):
                new_content.append(f"down_revision: Union[str, None] = '{main_revision}'\n")
            else:
                new_content.append(line)
        
        with open(other_head, 'w') as f:
            f.writelines(new_content)
        
        print(f"✅ {other_head.name} modificado com sucesso!")
    
    print("\n✅ Correção de múltiplos heads concluída com sucesso!")
    print("\n🔄 Execute novamente o script de recriação das tabelas para aplicar as migrações.")

if __name__ == "__main__":
    main()
