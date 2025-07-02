#!/usr/bin/env python3
"""
Validação COMPLETA da estrutura do banco vs modelos
Verifica TODAS as 103 tabelas e seus modelos correspondentes
"""

import sys
import os
sys.path.insert(0, '/Users/joaovictormiranda/backend/synapse-backend-agents-jc')

# Configurar env mínimas
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret')
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')

from synapse.database import sync_engine, DATABASE_SCHEMA
from sqlalchemy import text
import glob
import importlib

def get_real_table_structure():
    """Obtém a estrutura real de TODAS as tabelas do banco"""
    structures = {}
    
    with sync_engine.connect() as conn:
        # Obter todas as tabelas
        result = conn.execute(text('''
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = :schema 
            ORDER BY table_name
        '''), {'schema': DATABASE_SCHEMA})
        
        tables = [row[0] for row in result.fetchall()]
        
        # Para cada tabela, obter estrutura detalhada
        for table in tables:
            column_result = conn.execute(text('''
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default,
                    character_maximum_length,
                    numeric_precision
                FROM information_schema.columns 
                WHERE table_schema = :schema AND table_name = :table
                ORDER BY ordinal_position
            '''), {'schema': DATABASE_SCHEMA, 'table': table})
            
            columns = []
            for row in column_result.fetchall():
                col_name, data_type, nullable, default, max_len, precision = row
                columns.append({
                    'name': col_name,
                    'type': data_type,
                    'nullable': nullable == 'YES',
                    'default': default,
                    'max_length': max_len,
                    'precision': precision
                })
            
            structures[table] = columns
    
    return structures

def get_model_files():
    """Obtém todos os arquivos de modelo"""
    model_files = glob.glob('/Users/joaovictormiranda/backend/synapse-backend-agents-jc/src/synapse/models/*.py')
    model_files = [f for f in model_files if not f.endswith('__init__.py')]
    return {os.path.basename(f).replace('.py', ''): f for f in model_files}

def find_model_for_table(table_name, model_files):
    """Encontra o arquivo de modelo correspondente a uma tabela"""
    # Mapeamentos diretos
    direct_mappings = {
        'users': 'user',
        'tenants': 'tenant',
        'agents': 'agent',
        'workspaces': 'workspace',
        'workflows': 'workflow',
        'refresh_tokens': 'refresh_token',
        'llms_conversations': 'conversation',
        'llms_messages': 'message',
        'llms': 'llm',
        'rbac_permissions': 'rbac_permission',
        'rbac_roles': 'rbac_role',
        'rbac_role_permissions': 'rbac_role_permission',
    }
    
    if table_name in direct_mappings:
        return direct_mappings[table_name]
    
    # Tentar encontrar por nome similar
    for model_name in model_files.keys():
        if table_name.replace('_', '') == model_name.replace('_', ''):
            return model_name
        if table_name.startswith(model_name.replace('_', '')):
            return model_name
    
    return None

def validate_table_vs_model(table_name, table_structure, model_name, model_files):
    """Valida uma tabela específica contra seu modelo"""
    if not model_name or model_name not in model_files:
        return {
            'status': 'missing_model',
            'message': f'Modelo não encontrado para tabela {table_name}'
        }
    
    try:
        # Importar o modelo
        module_path = f'src.synapse.models.{model_name}'
        module = importlib.import_module(module_path)
        
        # Encontrar a classe do modelo
        class_name = None
        model_class = None
        
        # Tentar nomes comuns
        possible_names = [
            table_name.title().replace('_', ''),  # user_variables -> UserVariables
            model_name.title().replace('_', ''),  # user_variable -> UserVariable
            table_name.replace('_', ' ').title().replace(' ', ''),  # user_variables -> UserVariables
        ]
        
        for name in possible_names:
            if hasattr(module, name):
                class_name = name
                model_class = getattr(module, name)
                break
        
        if not model_class or not hasattr(model_class, '__table__'):
            return {
                'status': 'no_model_class',
                'message': f'Classe de modelo não encontrada em {model_name}.py'
            }
        
        # Comparar estruturas
        model_columns = [col.name for col in model_class.__table__.columns]
        table_columns = [col['name'] for col in table_structure]
        
        missing_in_model = set(table_columns) - set(model_columns)
        extra_in_model = set(model_columns) - set(table_columns)
        
        if not missing_in_model and not extra_in_model:
            return {
                'status': 'perfect',
                'message': 'Perfeitamente alinhado',
                'model_class': class_name,
                'columns': len(model_columns)
            }
        else:
            return {
                'status': 'misaligned',
                'message': 'Estrutura divergente',
                'model_class': class_name,
                'missing_in_model': list(missing_in_model),
                'extra_in_model': list(extra_in_model),
                'table_columns': len(table_columns),
                'model_columns': len(model_columns)
            }
    
    except Exception as e:
        return {
            'status': 'import_error',
            'message': f'Erro ao importar: {str(e)[:100]}'
        }

def main():
    print('🔍 VALIDAÇÃO COMPLETA: BANCO vs MODELOS')
    print('=' * 80)
    
    # Obter estrutura real do banco
    print('📊 Obtendo estrutura real do banco...')
    real_structures = get_real_table_structure()
    print(f'✅ {len(real_structures)} tabelas encontradas no banco')
    
    # Obter arquivos de modelo
    print('📁 Obtendo arquivos de modelo...')
    model_files = get_model_files()
    print(f'✅ {len(model_files)} arquivos de modelo encontrados')
    
    # Validar cada tabela
    print('\\n🔍 VALIDANDO CADA TABELA:')
    print('-' * 80)
    
    results = {
        'perfect': [],
        'misaligned': [],
        'missing_model': [],
        'import_error': [],
        'no_model_class': []
    }
    
    for table_name, table_structure in sorted(real_structures.items()):
        model_name = find_model_for_table(table_name, model_files)
        result = validate_table_vs_model(table_name, table_structure, model_name, model_files)
        
        status = result['status']
        results[status].append((table_name, result))
        
        # Imprimir resultado
        if status == 'perfect':
            print(f'✅ {table_name:<30} → {result["model_class"]:<20} ({result["columns"]} cols)')
        elif status == 'misaligned':
            print(f'⚠️  {table_name:<30} → {result["model_class"]:<20} (T:{result["table_columns"]} M:{result["model_columns"]})')
        elif status == 'missing_model':
            print(f'❌ {table_name:<30} → SEM MODELO')
        elif status == 'import_error':
            print(f'💥 {table_name:<30} → ERRO: {result["message"][:30]}...')
        elif status == 'no_model_class':
            print(f'🔍 {table_name:<30} → CLASSE NÃO ENCONTRADA')
    
    # Relatório final
    print('\\n' + '=' * 80)
    print('📊 RELATÓRIO FINAL:')
    print('-' * 80)
    
    total_tables = len(real_structures)
    
    for status, items in results.items():
        count = len(items)
        percentage = (count / total_tables) * 100
        
        status_names = {
            'perfect': '✅ Perfeitamente Alinhadas',
            'misaligned': '⚠️  Com Divergências', 
            'missing_model': '❌ Sem Modelo',
            'import_error': '💥 Erro de Importação',
            'no_model_class': '🔍 Sem Classe de Modelo'
        }
        
        print(f'{status_names[status]:<25}: {count:3d} ({percentage:5.1f}%)')
    
    print(f'\\nTOTAL DE TABELAS: {total_tables}')
    
    # Detalhes dos problemas
    if results['misaligned']:
        print('\\n⚠️  DETALHES DAS DIVERGÊNCIAS:')
        print('-' * 50)
        for table_name, result in results['misaligned'][:10]:  # Mostrar apenas 10 primeiros
            print(f'\\n🔧 {table_name}:')
            if result.get('missing_in_model'):
                print(f'  Faltando no modelo: {result["missing_in_model"]}')
            if result.get('extra_in_model'):
                print(f'  Extra no modelo: {result["extra_in_model"]}')
    
    # Tabelas sem modelo
    if results['missing_model']:
        print('\\n❌ TABELAS SEM MODELO:')
        print('-' * 30)
        for table_name, result in results['missing_model']:
            print(f'  • {table_name}')
    
    # Calcular score geral
    perfect_count = len(results['perfect'])
    success_rate = (perfect_count / total_tables) * 100
    
    print(f'\\n🎯 TAXA DE SUCESSO: {success_rate:.1f}% ({perfect_count}/{total_tables})')
    
    if success_rate >= 80:
        print('🎉 EXCELENTE! A maioria dos modelos está alinhada.')
    elif success_rate >= 60:
        print('👍 BOM! Ainda há alguns ajustes necessários.')
    else:
        print('⚠️  ATENÇÃO! Muitos modelos precisam de correção.')
    
    return results

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'❌ ERRO CRÍTICO: {e}')
        import traceback
        traceback.print_exc()
