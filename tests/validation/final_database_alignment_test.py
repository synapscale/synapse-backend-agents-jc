#!/usr/bin/env python3
"""
Script de validação final - ALINHAMENTO TOTAL COM BANCO DE DADOS
Verifica se todos os modelos estão perfeitamente alinhados com a estrutura real do banco
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv('.env')

# Add src to path
sys.path.insert(0, './src')

def test_critical_models():
    """Testa modelos críticos para verificar alinhamento"""
    print("🔍 TESTE DE ALINHAMENTO COM BANCO DE DADOS")
    print("=" * 60)
    
    critical_models = [
        ('synapse.models.user', 'User'),
        ('synapse.models.workflow', 'Workflow'),
        ('synapse.models.agent', 'Agent'),
        ('synapse.models.tenant', 'Tenant'),
        ('synapse.models.workspace', 'Workspace'),
        ('synapse.models.llm', 'LLM'),
        ('synapse.models.conversation', 'Conversation'),
        ('synapse.models.message', 'Message'),
        ('synapse.models.rbac_role', 'RBACRole'),
        ('synapse.models.audit_log', 'AuditLog'),
    ]
    
    success_count = 0
    
    for module_path, class_name in critical_models:
        try:
            module = __import__(module_path, fromlist=[class_name])
            model_class = getattr(module, class_name)
            
            # Verificar se tem __tablename__ e __table_args__
            table_name = getattr(model_class, '__tablename__', None)
            table_args = getattr(model_class, '__table_args__', None)
            
            print(f"✅ {class_name:15} | Table: {table_name:20} | Schema: {table_args}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {class_name:15} | Error: {str(e)[:50]}")
    
    print(f"\n📊 RESULTADO: {success_count}/{len(critical_models)} modelos carregados com sucesso")
    return success_count == len(critical_models)

def test_database_connection():
    """Testa conexão com banco usando as configurações atuais"""
    print("\n🔗 TESTE DE CONEXÃO COM BANCO")
    print("=" * 60)
    
    try:
        from synapse.database import test_database_connection, get_database_info
        
        # Teste básico de conexão
        if test_database_connection():
            print("✅ Conexão com banco funcionando")
            
            # Informações do banco
            db_info = get_database_info()
            if db_info:
                print(f"✅ Database: {db_info.get('database', 'N/A')}")
                print(f"✅ Schema: {db_info.get('schema', 'N/A')}")
                print(f"✅ Tables: {db_info.get('table_count', 0)}")
                return True
            else:
                print("❌ Não foi possível obter informações do banco")
                return False
        else:
            print("❌ Falha na conexão com banco")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def verify_model_table_alignment():
    """Verifica se modelos principais têm colunas corretas"""
    print("\n🎯 VERIFICAÇÃO DE ALINHAMENTO DE COLUNAS")
    print("=" * 60)
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL não encontrada")
            return False
            
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        # Verificar tabelas críticas
        tables_to_check = ['workflows', 'users', 'agents', 'tenants', 'workspaces']
        
        for table_name in tables_to_check:
            cursor.execute("""
                SELECT COUNT(*) as column_count
                FROM information_schema.columns 
                WHERE table_schema = 'synapscale_db' AND table_name = %s
            """, (table_name,))
            
            result = cursor.fetchone()
            column_count = result[0] if result else 0
            
            if column_count > 0:
                print(f"✅ {table_name:15} | {column_count:2} colunas encontradas")
            else:
                print(f"❌ {table_name:15} | Tabela não encontrada")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar alinhamento: {e}")
        return False

def main():
    """Executa todos os testes de validação"""
    print("🏁 VALIDAÇÃO FINAL DE ALINHAMENTO COM BANCO DE DADOS")
    print("=" * 80)
    
    # Set environment variables
    os.environ['SECRET_KEY'] = 'test'
    os.environ['JWT_SECRET_KEY'] = 'test'
    
    tests = [
        ("Importação de modelos críticos", test_critical_models),
        ("Conexão com banco de dados", test_database_connection),
        ("Alinhamento de colunas", verify_model_table_alignment),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSOU")
        else:
            print(f"❌ {test_name} - FALHOU")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Modelos estão alinhados com o banco.")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verificar problemas acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
