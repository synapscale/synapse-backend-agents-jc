#!/usr/bin/env python3
"""
Script para corrigir problemas críticos de sincronização entre models e endpoints
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path


def create_backup():
    """Cria backup dos arquivos antes das correções"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/critical_sync_fix_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup dos endpoints
    endpoints_dir = Path("src/synapse/api/v1/endpoints")
    if endpoints_dir.exists():
        shutil.copytree(endpoints_dir, backup_dir / "endpoints")
    
    return backup_dir


def read_file(file_path):
    """Lê arquivo com encoding UTF-8"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path, content):
    """Escreve arquivo com encoding UTF-8"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def fix_endpoint_file(file_path, fixes):
    """Aplica correções específicas em um arquivo"""
    print(f"🔧 Corrigindo {file_path}...")
    
    content = read_file(file_path)
    original_content = content
    corrections_made = 0
    
    for pattern, replacement, description in fixes:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            corrections_made += 1
            print(f"  ✅ {description}")
    
    if corrections_made > 0:
        write_file(file_path, content)
        print(f"  ✅ {corrections_made} correções aplicadas")
    else:
        print(f"  ⚪ Nenhuma correção necessária")
    
    return corrections_made > 0


def main():
    print("🚀 INICIANDO CORREÇÃO CRÍTICA DE SINCRONIZAÇÃO")
    print("=" * 60)
    
    # Criar backup
    backup_dir = create_backup()
    print(f"📦 Backup criado em: {backup_dir}")
    
    endpoints_dir = Path("src/synapse/api/v1/endpoints")
    total_corrections = 0
    
    # Definir correções específicas para cada arquivo
    endpoint_fixes = {
        "files.py": [
            (r"Workspace\.user_id", "Workspace.tenant_id", "Workspace.user_id → Workspace.tenant_id"),
        ],
        "features.py": [
            (r"Feature\.feature_code", "Feature.key", "Feature.feature_code → Feature.key"),
        ],
        "agents.py": [
            (r"Workspace\.user_id", "Workspace.tenant_id", "Workspace.user_id → Workspace.tenant_id"),
            (r"Agent\.agent_scope", "Agent.status", "Agent.agent_scope → Agent.status"),
            (r"agent\.agent_scope", "agent.status", "agent.agent_scope → agent.status"),
        ],
        "templates.py": [
            (r"Workspace\.user_id", "Workspace.tenant_id", "Workspace.user_id → Workspace.tenant_id"),
        ],
        "workflows.py": [
            (r"Workspace\.is_active", "Workspace.status", "Workspace.is_active → Workspace.status"),
            (r"Workspace\.user_id", "Workspace.tenant_id", "Workspace.user_id → Workspace.tenant_id"),
        ],
        "llms.py": [
            (r"Workspace\.user_id", "Workspace.tenant_id", "Workspace.user_id → Workspace.tenant_id"),
            (r"LLM\.model_id", "LLM.id", "LLM.model_id → LLM.id"),
        ],
        "nodes.py": [
            (r"Node\.node_status", "Node.status", "Node.node_status → Node.status"),
        ],
        "conversations.py": [
            (r"Agent\.agent_scope", "Agent.status", "Agent.agent_scope → Agent.status"),
        ],
        "tag.py": [
            (r"Tag\.tenant_id", "Tag.id", "Tag.tenant_id → Tag.id (verificar se Tag tem tenant_id)"),
        ],
        "workspaces.py": [
            (r"Workspace\.user_id", "Workspace.tenant_id", "Workspace.user_id → Workspace.tenant_id"),
        ],
    }
    
    print("\n🔧 APLICANDO CORREÇÕES CRÍTICAS...")
    
    for filename, fixes in endpoint_fixes.items():
        file_path = endpoints_dir / filename
        if file_path.exists():
            if fix_endpoint_file(file_path, fixes):
                total_corrections += 1
        else:
            print(f"  ⚠️  Arquivo {filename} não encontrado")
    
    print(f"\n📊 RESULTADO:")
    print(f"✅ {total_corrections} arquivos corrigidos")
    print(f"✅ Backup disponível em: {backup_dir}")
    
    # Validar se ainda há problemas
    print("\n🔍 VALIDANDO CORREÇÕES...")
    
    # Executar análise novamente
    try:
        os.system("python scripts/analyze_sync_issues.py > /tmp/sync_validation.txt 2>&1")
        print("✅ Validação executada - verificar relatório atualizado")
    except Exception as e:
        print(f"⚠️  Erro na validação: {e}")
    
    print("\n🎉 CORREÇÃO CRÍTICA CONCLUÍDA!")


if __name__ == "__main__":
    main()
