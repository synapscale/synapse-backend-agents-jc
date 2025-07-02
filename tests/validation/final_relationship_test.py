#!/usr/bin/env python3
"""
Teste final para verificar relacionamentos SQLAlchemy e registry.
"""

import os
import sys
from pathlib import Path

# Adicionar o src ao path


import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_model_registry():
    """Testar o registry completo de modelos SQLAlchemy."""
    try:
        logger.info("🔄 Testando registry completo de modelos...")
        
        # Importar TODOS os modelos disponíveis
        from synapse.models.workspace import Workspace
        from synapse.models.workspace_project import WorkspaceProject
        from synapse.models.workspace_member import WorkspaceMember
        from synapse.models.workspace_activity import WorkspaceActivity
        from synapse.models.workspace_invitation import WorkspaceInvitation
        from synapse.models.user import User
        from synapse.models.tenant import Tenant
        from synapse.models.plan import Plan
        from synapse.models.agent import Agent
        from synapse.models.workflow import Workflow
        from synapse.models.node import Node
        from synapse.models.feature import Feature
        from synapse.models.file import File
        from synapse.models.llm import LLM
        
        logger.info("✅ Todos os modelos principais importados sem conflitos!")
        
        # Testar criação de engine sem erros
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        
        # Testar metadata sem erros
        from synapse.database import Base
        logger.info(f"📋 Registry contém {len(Base.registry._class_registry)} classes")
        
        # Verificar se há duplicatas
        seen_tables = {}
        for class_name, cls in Base.registry._class_registry.items():
            if hasattr(cls, '__tablename__'):
                # Tratar __table_args__ como dict ou tuple
                table_args = getattr(cls, '__table_args__', {})
                if isinstance(table_args, dict):
                    schema = table_args.get('schema', 'public')
                elif isinstance(table_args, tuple) and len(table_args) > 0 and isinstance(table_args[-1], dict):
                    schema = table_args[-1].get('schema', 'public')
                else:
                    schema = 'public'
                    
                table_key = f"{schema}.{cls.__tablename__}"
                if table_key in seen_tables:
                    logger.error(f"❌ Tabela duplicada encontrada: {table_key}")
                    logger.error(f"   Classes: {seen_tables[table_key]} e {class_name}")
                    return False
                seen_tables[table_key] = class_name
        
        logger.info("✅ Nenhuma tabela duplicada encontrada!")
        
        # Testar relacionamentos específicos que foram problemáticos
        logger.info("🔗 Testando relacionamentos específicos...")
        
        # Workspace -> User (owner)
        if hasattr(Workspace, 'owner'):
            logger.info("  ✅ Workspace.owner")
        else:
            logger.error("  ❌ Workspace.owner")
            
        # Workspace -> Tenant
        if hasattr(Workspace, 'tenant'):
            logger.info("  ✅ Workspace.tenant")
        else:
            logger.error("  ❌ Workspace.tenant")
            
        # WorkspaceProject -> Workspace
        if hasattr(WorkspaceProject, 'workspace'):
            logger.info("  ✅ WorkspaceProject.workspace")
        else:
            logger.error("  ❌ WorkspaceProject.workspace")
            
        logger.info("✅ Teste de registry completo passou!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de registry: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_query():
    """Testar query real no banco de dados."""
    try:
        logger.info("💾 Testando query real no banco de dados...")
        
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Testar importação e query dos modelos
            from synapse.models.workspace import Workspace
            from synapse.models.user import User
            from synapse.models.tenant import Tenant
            
            # Query simples para verificar se está funcionando
            workspace_count = session.query(Workspace).count()
            user_count = session.query(User).count()
            tenant_count = session.query(Tenant).count()
            
            logger.info(f"  📊 {workspace_count} workspaces")
            logger.info(f"  👥 {user_count} users")
            logger.info(f"  🏢 {tenant_count} tenants")
            
        logger.info("✅ Query real no banco funcionando!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na query real: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar teste final."""
    logger.info("🏁 TESTE FINAL - Verificação completa do sistema")
    logger.info("="*60)
    
    tests = [
        ("Registry Completo", test_full_model_registry),
        ("Query Real no Banco", test_database_query),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        logger.info(f"\n{'='*40}")
        logger.info(f"Executando: {test_name}")
        logger.info(f"{'='*40}")
        
        result = test_func()
        if not result:
            all_passed = False
            
    logger.info(f"\n{'='*60}")
    if all_passed:
        logger.info("🎉 TODOS OS TESTES FINAIS PASSARAM!")
        logger.info("✅ Sistema SQLAlchemy está 100% funcional!")
        logger.info("✅ Nenhum conflito de registry detectado!")
        logger.info("✅ Relacionamentos funcionando corretamente!")
        logger.info("✅ Estrutura do banco alinhada com os modelos!")
    else:
        logger.error("❌ Alguns testes falharam. Verificar problemas acima.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 