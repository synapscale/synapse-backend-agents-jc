#!/usr/bin/env python3
"""
Teste abrangente para detectar todos os problemas de modelos
"""

import os
import sys
import glob
import importlib
sys.path.insert(0, '/Users/joaovictormiranda/backend/synapse-backend-agents-jc')

# Configurar env mínimas
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret')
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')

def test_individual_model_imports():
    """Testar importação individual de cada modelo"""
    print('🔍 TESTANDO IMPORTAÇÃO INDIVIDUAL DE MODELOS')
    print('=' * 60)
    
    model_files = glob.glob('/Users/joaovictormiranda/backend/synapse-backend-agents-jc/src/synapse/models/*.py')
    model_files = [f for f in model_files if not f.endswith('__init__.py')]
    
    successful_imports = []
    failed_imports = []
    
    for file_path in sorted(model_files):
        model_name = os.path.basename(file_path).replace('.py', '')
        
        try:
            module_path = f'src.synapse.models.{model_name}'
            module = importlib.import_module(module_path)
            
            # Verificar se há classes SQLAlchemy definidas
            sqlalchemy_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, '__table__') and hasattr(attr, '__tablename__'):
                    sqlalchemy_classes.append(attr_name)
            
            successful_imports.append({
                'file': model_name,
                'classes': sqlalchemy_classes
            })
            print(f'✅ {model_name:<25} → {len(sqlalchemy_classes)} classes')
            
        except Exception as e:
            failed_imports.append({
                'file': model_name,
                'error': str(e)
            })
            print(f'❌ {model_name:<25} → {str(e)[:50]}...')
    
    print(f'\n📊 RESUMO:')
    print(f'✅ Sucessos: {len(successful_imports)}')
    print(f'❌ Falhas: {len(failed_imports)}')
    
    if failed_imports:
        print(f'\n💥 ERROS DETALHADOS:')
        print('-' * 40)
        for fail in failed_imports:
            print(f'{fail["file"]}: {fail["error"]}')
    
    return successful_imports, failed_imports

def test_reserved_words_in_action():
    """Testar palavras reservadas em ação"""
    print(f'\n🔍 TESTANDO PALAVRAS RESERVADAS EM AÇÃO')
    print('=' * 60)
    
    # Testar se conseguimos importar modelos que usam 'query' diretamente
    problematic_models = [
        'analytics_export',
        'analytics_report', 
        'analytics'
    ]
    
    for model_name in problematic_models:
        try:
            module_path = f'src.synapse.models.{model_name}'
            module = importlib.import_module(module_path)
            print(f'⚠️  {model_name} importou mas pode ter problemas com "query"')
        except Exception as e:
            print(f'❌ {model_name}: {e}')

def test_relationship_conflicts():
    """Testar conflitos de relacionamentos"""
    print(f'\n🔍 TESTANDO CONFLITOS DE RELACIONAMENTOS')
    print('=' * 60)
    
    try:
        # Importar modelos que sabemos que têm relacionamentos
        from synapse.models.user import User
        from synapse.models.workspace import Workspace
        from synapse.models.agent import Agent
        from synapse.models.workflow import Workflow
        from synapse.models.node import Node
        
        # Verificar se os relacionamentos podem ser acessados
        test_relationships = [
            (User, 'workflows'),
            (User, 'agents'),
            (Workspace, 'owner'),
            (Workspace, 'tenant'),
            (Agent, 'user'),
            (Workflow, 'user'),
        ]
        
        for model_class, rel_name in test_relationships:
            try:
                rel = getattr(model_class, rel_name, None)
                if rel:
                    print(f'✅ {model_class.__name__}.{rel_name}')
                else:
                    print(f'⚠️  {model_class.__name__}.{rel_name} não encontrado')
            except Exception as e:
                print(f'❌ {model_class.__name__}.{rel_name}: {e}')
                
        print('✅ Relacionamentos básicos testados')
        
    except Exception as e:
        print(f'❌ Erro ao testar relacionamentos: {e}')
        import traceback
        traceback.print_exc()

def main():
    print('🏁 TESTE ABRANGENTE DE MODELOS')
    print('=' * 70)
    
    # Teste 1: Importações individuais
    successful_imports, failed_imports = test_individual_model_imports()
    
    # Teste 2: Palavras reservadas
    test_reserved_words_in_action()
    
    # Teste 3: Relacionamentos
    test_relationship_conflicts()
    
    print(f'\n' + '=' * 70)
    print('📊 RESUMO FINAL:')
    print(f'✅ Modelos importados: {len(successful_imports)}')
    print(f'❌ Modelos com erro: {len(failed_imports)}')
    
    if failed_imports:
        print(f'\n🔧 AÇÃO NECESSÁRIA: Corrigir {len(failed_imports)} modelos com problemas')
        return False
    else:
        print(f'\n🎉 TODOS OS MODELOS FUNCIONANDO!')
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
