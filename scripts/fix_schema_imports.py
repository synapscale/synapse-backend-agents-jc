#!/usr/bin/env python3
"""
Script para corrigir imports problemáticos nos schemas.
"""

import os
import re
import ast
from pathlib import Path

def fix_schema_imports():
    """Corrigir imports problemáticos no __init__.py dos schemas."""
    
    schemas_path = Path('src/synapse/schemas')
    init_file = schemas_path / '__init__.py'
    
    print("🔧 CORRIGINDO IMPORTS DOS SCHEMAS")
    print("=" * 60)
    
    # Ler arquivo __init__.py
    content = init_file.read_text()
    
    # Problemas conhecidos para corrigir
    fixes = [
        ('NodeRatingRead', 'NodeRatingResponse'),
        ('NodeCategoryRead', 'NodeCategoryResponse'),
        ('InvoiceList', 'InvoiceListResponse'),
        ('UserInsightAction', None),  # Remover
        ('UserInsightActionResponse', None),  # Remover
        ('UserInsightBatch', None),  # Remover
        ('UserInsightStatistics', None),  # Remover
        ('UserInsightFilter', None),  # Remover
        ('UserInsightExport', None),  # Remover
        ('UserFeedback', None),  # Remover
    ]
    
    original_content = content
    
    for old_name, new_name in fixes:
        if old_name in content:
            if new_name:
                # Substituir por novo nome
                content = content.replace(old_name, new_name)
                print(f"✅ Substituído: {old_name} → {new_name}")
            else:
                # Remover import
                # Remover linha da importação
                lines = content.split('\n')
                filtered_lines = []
                for line in lines:
                    if old_name in line and ('import' in line or line.strip().startswith('"')):
                        print(f"❌ Removido: {line.strip()}")
                        continue
                    filtered_lines.append(line)
                content = '\n'.join(filtered_lines)
    
    # Remover linhas vazias extras
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Salvar se houve mudanças
    if content != original_content:
        init_file.write_text(content)
        print(f"✅ Arquivo {init_file} atualizado")
    else:
        print("ℹ️  Nenhuma mudança necessária")
    
    return content != original_content

def verify_schema_classes():
    """Verificar se todas as classes importadas realmente existem."""
    
    schemas_path = Path('src/synapse/schemas')
    init_file = schemas_path / '__init__.py'
    
    print("\n🔍 VERIFICANDO CLASSES DOS SCHEMAS")
    print("=" * 60)
    
    # Ler arquivo __init__.py
    content = init_file.read_text()
    
    # Encontrar todos os imports
    import_pattern = r'from \.(\w+) import \((.*?)\)'
    matches = re.findall(import_pattern, content, re.DOTALL)
    
    errors = []
    
    for module_name, imports_str in matches:
        module_file = schemas_path / f"{module_name}.py"
        
        if not module_file.exists():
            continue
            
        try:
            # Ler arquivo do módulo
            module_content = module_file.read_text()
            
            # Extrair classes definidas no módulo
            tree = ast.parse(module_content)
            defined_classes = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    defined_classes.add(node.name)
            
            # Verificar cada import
            imports = re.findall(r'(\w+)', imports_str)
            for class_name in imports:
                if class_name not in defined_classes:
                    errors.append(f"❌ {module_name}.py: Classe '{class_name}' não existe")
                    
        except Exception as e:
            errors.append(f"❌ Erro ao verificar {module_name}.py: {e}")
    
    if errors:
        print(f"⚠️  Encontrados {len(errors)} problemas:")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ Todos os imports estão corretos")
    
    return len(errors) == 0

def main():
    print("🚀 CORREÇÃO AUTOMÁTICA DE IMPORTS")
    print("=" * 60)
    
    # Corrigir imports conhecidos
    fixed = fix_schema_imports()
    
    # Verificar se ainda há problemas
    all_good = verify_schema_classes()
    
    if fixed and all_good:
        print("\n🎉 TODOS OS PROBLEMAS CORRIGIDOS!")
        print("✅ Agora você pode testar a aplicação:")
        print("   python3 -c \"import sys; sys.path.insert(0, 'src'); from synapse.main import app; print('Funcionando!')\"")
    elif fixed:
        print("\n⚠️  Alguns imports foram corrigidos, mas ainda há problemas")
    else:
        print("\n✅ Nenhuma correção necessária")

if __name__ == "__main__":
    main()
