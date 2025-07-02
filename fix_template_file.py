#!/usr/bin/env python3
"""
Script para corrigir o arquivo template.py removendo definições malformadas
"""

import re

def fix_template_file():
    file_path = "src/synapse/models/template.py"
    
    print(f"Corrigindo arquivo {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover todas as linhas malformadas que contêm relationship dentro de docstrings e classes
    # Padrão para detectar as linhas problemáticas
    patterns_to_remove = [
        r'\s*workflow_templates = relationship\(".*?", back_populates=".*?"\)\s*# gerado autom\.\n',
        r'\s*reviews = relationship\(".*?", back_populates=".*?"\)\s*# gerado autom\.\n',
        r'\s*downloads = relationship\(".*?", back_populates=".*?"\)\s*# gerado autom\.\n',
        r'\s*favorites = relationship\(".*?", back_populates=".*?"\)\s*# gerado autom\.\n',
    ]
    
    original_content = content
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Limpar docstrings que ficaram só com """
    content = re.sub(r'"""\s*"""', '"""Docstring vazia"""', content)
    
    # Verificar se houve mudanças
    if content != original_content:
        # Backup do arquivo original
        with open(f"{file_path}.backup", 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Escrever o arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Arquivo {file_path} corrigido com sucesso!")
        print(f"📦 Backup salvo como {file_path}.backup")
        
        # Contar quantas linhas foram removidas
        original_lines = len(original_content.splitlines())
        new_lines = len(content.splitlines())
        removed_lines = original_lines - new_lines
        print(f"🗑️  Removidas {removed_lines} linhas malformadas")
        
    else:
        print("ℹ️  Nenhuma correção necessária")
    
    return True

if __name__ == "__main__":
    fix_template_file() 