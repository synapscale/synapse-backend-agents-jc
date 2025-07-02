#!/usr/bin/env python3
"""
Verificação detalhada dos modelos principais vs estrutura real do banco
"""

import sys
import os
sys.path.insert(0, '/Users/joaovictormiranda/backend/synapse-backend-agents-jc')
os.chdir('/Users/joaovictormiranda/backend/synapse-backend-agents-jc')

from synapse.database import sync_engine, DATABASE_SCHEMA
from sqlalchemy import text

def get_table_columns(table_name):
    """Obtém colunas reais de uma tabela do banco"""
    with sync_engine.connect() as conn:
        result = conn.execute(text('''
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_schema = :schema AND table_name = :table
            ORDER BY ordinal_position
        '''), {'schema': DATABASE_SCHEMA, 'table': table_name})
        
        return [row[0] for row in result.fetchall()]

def check_model_columns(model_path):
    """Extrai nomes REAIS das colunas do banco (não variáveis Python)"""
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar por definições de colunas com mapeamento
        import re
        
        # Padrão para Column("nome_real", ...) 
        explicit_pattern = r'\w+\s*=\s*Column\(\s*["\']([^"\']+)["\']'
        explicit_matches = re.findall(explicit_pattern, content)
        
        # Padrão para Column(Type, ...) onde o nome é o da variável
        implicit_pattern = r'(\w+)\s*=\s*Column\(\s*(?!["\'])'
        implicit_matches = re.findall(implicit_pattern, content)
        
        columns = []
        
        # Adicionar colunas com nome explícito
        columns.extend(explicit_matches)
        
        # Adicionar colunas com nome implícito (excluir variáveis especiais)
        for match in implicit_matches:
            if not match.startswith('_') and match != 'Column':
                columns.append(match)
        
        return columns
    except Exception as e:
        return f"Erro: {e}"

def compare_table_model(table_name, model_file):
    """Compara tabela do banco com modelo"""
    print(f"\n🔍 COMPARANDO: {table_name} ↔ {model_file}")
    print("-" * 60)
    
    # Obter colunas do banco
    try:
        table_columns = get_table_columns(table_name)
        print(f"📊 Banco ({len(table_columns)} colunas): {table_columns}")
    except Exception as e:
        print(f"❌ Erro ao acessar tabela {table_name}: {e}")
        return
    
    # Obter colunas do modelo
    model_path = f"src/synapse/models/{model_file}"
    if not os.path.exists(model_path):
        print(f"❌ Arquivo {model_file} não encontrado!")
        return
    
    model_columns = check_model_columns(model_path)
    if isinstance(model_columns, str):  # É um erro
        print(f"❌ {model_columns}")
        return
    
    print(f"🏗️  Modelo ({len(model_columns)} colunas): {model_columns}")
    
    # Comparar
    table_set = set(table_columns)
    model_set = set(model_columns)
    
    missing_in_model = table_set - model_set
    extra_in_model = model_set - table_set
    common = table_set & model_set
    
    print(f"✅ Comuns: {len(common)} colunas")
    
    if missing_in_model:
        print(f"❌ Faltando no modelo: {missing_in_model}")
    
    if extra_in_model:
        print(f"⚠️  Extra no modelo: {extra_in_model}")
    
    if not missing_in_model and not extra_in_model:
        print("🎉 PERFEITAMENTE ALINHADO!")
        return True
    else:
        print("⚠️  NECESSITA AJUSTES")
        return False

def main():
    print("🔍 VERIFICAÇÃO DETALHADA: MODELOS vs BANCO REAL")
    print("=" * 70)
    
    # Modelos críticos para verificar
    critical_models = [
        ('users', 'user.py'),
        ('tenants', 'tenant.py'),
        ('agents', 'agent.py'),
        ('workspaces', 'workspace.py'),
        ('workflows', 'workflow.py'),
        ('refresh_tokens', 'refresh_token.py'),
        ('llms_conversations', 'conversation.py'),
        ('llms', 'llm.py'),
        ('rbac_roles', 'rbac_role.py'),
        ('audit_log', 'audit_log.py')
    ]
    
    aligned_count = 0
    total_count = len(critical_models)
    
    for table_name, model_file in critical_models:
        is_aligned = compare_table_model(table_name, model_file)
        if is_aligned:
            aligned_count += 1
    
    # Relatório final
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL:")
    print("-" * 70)
    
    success_rate = (aligned_count / total_count) * 100
    print(f"✅ Modelos alinhados: {aligned_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 PERFEITO! Todos os modelos estão alinhados!")
    elif success_rate >= 80:
        print("👍 MUITO BOM! A maioria está alinhada.")
    elif success_rate >= 60:
        print("⚠️  PRECISA ATENÇÃO! Vários modelos precisam de ajuste.")
    else:
        print("❌ CRÍTICO! Muitos modelos estão desalinhados.")
    
    return aligned_count, total_count

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
