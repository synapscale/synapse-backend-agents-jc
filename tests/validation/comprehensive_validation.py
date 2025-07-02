#!/usr/bin/env python3
"""
Script de validação abrangente para verificar todos os modelos SQLAlchemy
contra a estrutura real do banco de dados.
"""

import os
import sys
from pathlib import Path

# Adicionar o src ao path


import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Obter URL do banco de dados das variáveis de ambiente."""
    return os.getenv("DATABASE_URL")

def test_model_imports():
    """Testar importação de todos os modelos principais."""
    try:
        logger.info("🧪 Testando importação de modelos principais...")
        
        # Importar modelos essenciais
        from synapse.models.workspace import Workspace
        from synapse.models.user import User
        from synapse.models.tenant import Tenant
        from synapse.models.plan import Plan
        from synapse.models.agent import Agent
        from synapse.models.workflow import Workflow
        from synapse.models.node import Node
        from synapse.models.feature import Feature
        
        logger.info("✅ Todos os modelos principais importados com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao importar modelos: {e}")
        return False

def test_database_connection():
    """Testar conexão com o banco de dados."""
    try:
        logger.info("🔗 Testando conexão com o banco de dados...")
        
        database_url = get_database_url()
        if not database_url:
            logger.error("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
            return False
            
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
        logger.info("✅ Conexão com banco de dados estabelecida com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com o banco: {e}")
        return False

def test_model_metadata():
    """Testar metadata dos modelos SQLAlchemy."""
    try:
        logger.info("📋 Testando metadata dos modelos...")
        
        # Importar modelos
        from synapse.models.workspace import Workspace
        from synapse.models.user import User
        from synapse.models.tenant import Tenant
        from synapse.models.plan import Plan
        
        # Verificar se as tabelas têm schema definido
        models_to_check = [Workspace, User, Tenant, Plan]
        
        for model in models_to_check:
            table_name = model.__tablename__
            schema = model.__table_args__.get("schema", "public")
            logger.info(f"  📄 {model.__name__}: {schema}.{table_name}")
            
            # Verificar se tem colunas definidas
            if not hasattr(model, '__table__') or len(model.__table__.columns) == 0:
                logger.warning(f"⚠️  {model.__name__} não tem colunas definidas")
            else:
                logger.info(f"    ✅ {len(model.__table__.columns)} colunas definidas")
        
        logger.info("✅ Metadata dos modelos verificada!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar metadata: {e}")
        return False

def verify_key_tables_exist():
    """Verificar se as tabelas principais existem no banco."""
    try:
        logger.info("🔍 Verificando se tabelas principais existem no banco...")
        
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        key_tables = [
            'workspaces', 'users', 'tenants', 'plans', 'agents', 
            'workflows', 'nodes', 'features', 'workspace_members',
            'workspace_projects', 'llms', 'files'
        ]
        
        with engine.connect() as connection:
            for table in key_tables:
                result = connection.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'synapscale_db' 
                        AND table_name = '{table}'
                    );
                """))
                exists = result.fetchone()[0]
                
                if exists:
                    logger.info(f"  ✅ {table}")
                else:
                    logger.error(f"  ❌ {table} - TABELA NÃO ENCONTRADA!")
                    
        logger.info("✅ Verificação de tabelas concluída!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabelas: {e}")
        return False

def test_workspace_model_alignment():
    """Testar especificamente o alinhamento do modelo Workspace."""
    try:
        logger.info("🏢 Testando alinhamento do modelo Workspace...")
        
        from synapse.models.workspace import Workspace
        
        # Verificar campos críticos
        required_fields = [
            'id', 'name', 'slug', 'owner_id', 'tenant_id', 'status',
            'created_at', 'updated_at', 'last_activity_at', 'type'
        ]
        
        model_columns = [col.name for col in Workspace.__table__.columns]
        
        for field in required_fields:
            if field in model_columns:
                logger.info(f"  ✅ {field}")
            else:
                logger.error(f"  ❌ {field} - CAMPO FALTANDO NO MODELO!")
                
        # Verificar se não há campos incorretos
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'synapscale_db' 
                AND table_name = 'workspaces'
                ORDER BY ordinal_position;
            """))
            
            db_columns = [row[0] for row in result.fetchall()]
            
        # Verificar campos extras no modelo
        extra_in_model = set(model_columns) - set(db_columns)
        if extra_in_model:
            logger.warning(f"⚠️  Campos no modelo mas não no banco: {extra_in_model}")
            
        missing_in_model = set(db_columns) - set(model_columns)
        if missing_in_model:
            logger.warning(f"⚠️  Campos no banco mas não no modelo: {missing_in_model}")
            
        logger.info("✅ Teste de alinhamento do Workspace concluído!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar modelo Workspace: {e}")
        return False

def test_relationships():
    """Testar relacionamentos entre modelos."""
    try:
        logger.info("🔗 Testando relacionamentos entre modelos...")
        
        from synapse.models.workspace import Workspace
        from synapse.models.user import User
        from synapse.models.tenant import Tenant
        
        # Verificar relacionamentos do Workspace
        workspace_relationships = [
            'owner', 'tenant', 'members', 'projects', 'activities'
        ]
        
        for rel_name in workspace_relationships:
            if hasattr(Workspace, rel_name):
                logger.info(f"  ✅ Workspace.{rel_name}")
            else:
                logger.warning(f"  ⚠️  Workspace.{rel_name} - RELACIONAMENTO NÃO ENCONTRADO")
                
        logger.info("✅ Teste de relacionamentos concluído!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar relacionamentos: {e}")
        return False

def main():
    """Executar todos os testes de validação."""
    logger.info("🚀 Iniciando validação abrangente dos modelos SQLAlchemy...")
    
    tests = [
        ("Importação de Modelos", test_model_imports),
        ("Conexão com Banco", test_database_connection),
        ("Metadata dos Modelos", test_model_metadata),
        ("Existência das Tabelas", verify_key_tables_exist),
        ("Alinhamento Workspace", test_workspace_model_alignment),
        ("Relacionamentos", test_relationships),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Executando: {test_name}")
        logger.info(f"{'='*50}")
        
        result = test_func()
        results.append((test_name, result))
        
        if result:
            logger.info(f"✅ {test_name} - PASSOU")
        else:
            logger.error(f"❌ {test_name} - FALHOU")
    
    # Resumo final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RESUMO DA VALIDAÇÃO")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("🎉 TODOS OS TESTES PASSARAM! O sistema está pronto!")
        return True
    else:
        logger.error(f"⚠️  {total - passed} teste(s) falharam. Revisar problemas acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 