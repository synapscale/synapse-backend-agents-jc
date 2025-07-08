#!/usr/bin/env python3
"""
Script para corrigir automaticamente problemas de sincronização
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set
import shutil
from datetime import datetime

class SyncFixer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.models_path = self.project_root / "src" / "synapse" / "models"
        self.schemas_path = self.project_root / "src" / "synapse" / "schemas"
        self.endpoints_path = self.project_root / "src" / "synapse" / "api" / "v1" / "endpoints"
        self.backup_dir = self.project_root / "backups" / f"sync_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Carregar mapeamentos de campos válidos
        self.field_mappings = {
            "LLM": {
                "is_public": "is_active",  # Mapear is_public -> is_active
                "user_id": "tenant_id",    # Mapear user_id -> tenant_id
            },
            "User": {
                "password": "hashed_password",
            },
            "Agent": {
                "owner_id": "user_id",
            }
        }
        
        # Campos que devem ser removidos (não existem e não têm substituto)
        self.fields_to_remove = {
            "LLM": ["is_public", "user_id"],
            "User": ["password"],
        }

    def create_backup(self):
        """Cria backup dos arquivos que serão modificados"""
        print(f"📦 Criando backup em: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup dos endpoints
        endpoint_backup = self.backup_dir / "endpoints"
        endpoint_backup.mkdir(exist_ok=True)
        for endpoint_file in self.endpoints_path.glob("*.py"):
            shutil.copy2(endpoint_file, endpoint_backup)
        
        print(f"✅ Backup criado com sucesso!")

    def get_model_fields(self, model_name: str) -> Set[str]:
        """Obtém campos válidos de um model"""
        model_file = self.models_path / f"{model_name.lower()}.py"
        if not model_file.exists():
            return set()
        
        fields = set()
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar Column definitions
        column_pattern = r'(\w+)\s*=\s*Column\('
        for match in re.finditer(column_pattern, content):
            field_name = match.group(1)
            if not field_name.startswith('_'):
                fields.add(field_name)
        
        # Buscar mapped_column (SQLAlchemy 2.0)
        mapped_pattern = r'(\w+):\s*Mapped\[.*?\]\s*=\s*mapped_column\('
        for match in re.finditer(mapped_pattern, content):
            field_name = match.group(1)
            if not field_name.startswith('_'):
                fields.add(field_name)
        
        return fields

    def fix_endpoint_references(self, endpoint_file: Path):
        """Corrige referências inválidas em um endpoint"""
        print(f"🔧 Corrigindo {endpoint_file.name}...")
        
        with open(endpoint_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Corrigir referências específicas conhecidas
        fixes = {
            # LLM fixes
            r'LLM\.is_public\s*==\s*True': 'LLM.is_active == True',
            r'LLM\.user_id\s*==\s*current_user\.id': 'LLM.tenant_id == current_user.tenant_id',
            r'or_\(LLM\.is_public\s*==\s*True,\s*LLM\.user_id\s*==\s*current_user\.id\)': 'LLM.tenant_id == current_user.tenant_id',
            
            # User fixes
            r'User\.password': 'User.hashed_password',
            
            # Agent fixes
            r'Agent\.owner_id': 'Agent.user_id',
            
            # Workspace fixes
            r'Workspace\.owner_id': 'Workspace.user_id',
            
            # Generic tenant-based access patterns
            r'or_\(\w+\.is_public\s*==\s*True,\s*\w+\.user_id\s*==\s*current_user\.id\)': 
                lambda m: f"{m.group().split('.')[0]}.tenant_id == current_user.tenant_id",
        }
        
        for pattern, replacement in fixes.items():
            if callable(replacement):
                # Para replacements complexos
                matches = list(re.finditer(pattern, content))
                for match in reversed(matches):  # Reverse para não afetar índices
                    new_text = replacement(match)
                    content = content[:match.start()] + new_text + content[match.end():]
                    fixes_applied.append(f"Pattern: {pattern} -> {new_text}")
            else:
                # Para replacements simples
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes_applied.append(f"{pattern} -> {replacement}")
        
        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(endpoint_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {len(fixes_applied)} correções aplicadas")
            for fix in fixes_applied:
                print(f"    - {fix}")
        else:
            print(f"  ⚪ Nenhuma correção necessária")

    def fix_all_endpoints(self):
        """Corrige todos os endpoints"""
        print("\n🔧 CORRIGINDO ENDPOINTS...")
        
        for endpoint_file in self.endpoints_path.glob("*.py"):
            if endpoint_file.name != "__init__.py":
                self.fix_endpoint_references(endpoint_file)

    def validate_fixes(self):
        """Valida se as correções foram aplicadas corretamente"""
        print("\n🔍 VALIDANDO CORREÇÕES...")
        
        issues_found = []
        
        for endpoint_file in self.endpoints_path.glob("*.py"):
            if endpoint_file.name == "__init__.py":
                continue
                
            with open(endpoint_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se ainda existem referências problemáticas
            problematic_patterns = [
                r'LLM\.is_public',
                r'LLM\.user_id',
                r'User\.password(?!_)',  # password mas não hashed_password
                r'Agent\.owner_id',
                r'Workspace\.owner_id',
            ]
            
            for pattern in problematic_patterns:
                if re.search(pattern, content):
                    issues_found.append({
                        "file": endpoint_file.name,
                        "pattern": pattern,
                        "line": self.get_line_number(content, pattern)
                    })
        
        if issues_found:
            print("❌ Problemas ainda encontrados:")
            for issue in issues_found:
                print(f"  - {issue['file']}: {issue['pattern']} (linha ~{issue['line']})")
        else:
            print("✅ Todas as correções foram aplicadas com sucesso!")
        
        return len(issues_found) == 0

    def get_line_number(self, content: str, pattern: str) -> int:
        """Obtém número aproximado da linha onde padrão foi encontrado"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return 0

    def run_full_fix(self):
        """Executa processo completo de correção"""
        print("🚀 INICIANDO CORREÇÃO SISTEMÁTICA DE SINCRONIZAÇÃO")
        print("="*60)
        
        # 1. Criar backup
        self.create_backup()
        
        # 2. Corrigir endpoints
        self.fix_all_endpoints()
        
        # 3. Validar correções
        success = self.validate_fixes()
        
        # 4. Relatório final
        if success:
            print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Todos os endpoints foram sincronizados")
            print("✅ Backup criado em:", self.backup_dir)
        else:
            print("\n⚠️  CORREÇÃO PARCIAL")
            print("❌ Alguns problemas ainda precisam de correção manual")
            print("📂 Backup disponível em:", self.backup_dir)
        
        return success

if __name__ == "__main__":
    fixer = SyncFixer()
    fixer.run_full_fix()
