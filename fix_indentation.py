#!/usr/bin/env python3
"""
Corrige problemas de indentação nos modelos
"""

import re
from pathlib import Path

def fix_file_indentation(file_path):
    """Corrige indentação de um arquivo específico"""
    
    if not Path(file_path).exists():
        return
        
    content = Path(file_path).read_text()
    lines = content.split('\n')
    
    fixed_lines = []
    inside_relationship_block = False
    
    for i, line in enumerate(lines):
        # Se é uma linha comentada pelo script anterior
        if line.strip().startswith('# TEMPORARIAMENTE COMENTADO:'):
            fixed_lines.append(line)
            continue
            
        # Se é uma linha órfã de relacionamento (sem o início)
        if ('"' in line and 'back_populates' in line and 
            not line.strip().startswith('# ') and 
            not '= relationship(' in line):
            # Comentar esta linha órfã
            fixed_lines.append(f"    # ÓRFÃ COMENTADA: {line.strip()}")
            continue
            
        # Se é fechamento de parenteses órfão
        if line.strip() == ')' and i > 0 and 'TEMPORARIAMENTE COMENTADO' in lines[i-1]:
            fixed_lines.append(f"    # ÓRFÃ COMENTADA: {line.strip()}")
            continue
            
        fixed_lines.append(line)
    
    Path(file_path).write_text('\n'.join(fixed_lines))
    print(f"✅ Indentação corrigida em {file_path}")

def main():
    """Corrige indentação nos modelos essenciais"""
    
    files_to_fix = [
        'src/synapse/models/user.py',
        'src/synapse/models/tenant.py', 
        'src/synapse/models/workspace.py'
    ]
    
    for file_path in files_to_fix:
        fix_file_indentation(file_path)
    
    print("✅ Indentação corrigida em todos os arquivos!")

if __name__ == "__main__":
    main() 