#!/usr/bin/env python3
"""
Script para executar setup completo da otimização LLM
Executa migrações e popula dados iniciais

Uso: python scripts/run_llm_optimization_setup.py
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_command(command, description):
    """Executa comando e reporta resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso!")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro!")
        print(f"   Error: {e.stderr}")
        return False

def check_alembic_setup():
    """Verifica se Alembic está configurado"""
    print("\n🔍 Verificando configuração do Alembic...")
    
    if not os.path.exists("alembic.ini"):
        print("❌ alembic.ini não encontrado!")
        return False
        
    if not os.path.exists("alembic/versions"):
        print("❌ Pasta alembic/versions não encontrada!")
        return False
        
    print("✅ Alembic configurado!")
    return True

def run_migrations():
    """Executa as migrações"""
    print("\n📊 Executando migrações de otimização LLM...")
    
    # Lista das migrações em ordem
    migrations = [
        "a5f72854",  # Tabelas de otimização LLM principais
        "b6816ff0",  # Sistema de tagging flexível
        "c02a345b",  # Correção tipo conversation_id messages
        "d1bd1387",  # Correção tipo workspace_id conversations
    ]
    
    # Executa upgrade geral
    if not run_command("alembic upgrade head", "Upgrade das migrações"):
        return False
        
    print("✅ Todas as migrações executadas com sucesso!")
    return True

def populate_initial_data():
    """Popula dados iniciais"""
    print("\n🌱 Populando dados iniciais...")
    
    # Verifica se o script existe
    populate_script = "scripts/populate_initial_llms.py"
    if not os.path.exists(populate_script):
        print(f"⚠️  Script {populate_script} não encontrado - pulando população de dados")
        return True
        
    return run_command(f"python {populate_script}", "População de LLMs iniciais")

def verify_tables():
    """Verifica se as tabelas foram criadas"""
    print("\n🔍 Verificando tabelas criadas...")
    
    try:
        from synapse.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema='synapscale_db')
        
        required_tables = [
            'llms',
            'llms_conversations_turns', 
            'llms_usage_logs',
            'billing_events',
            'llms_message_feedbacks',
            'tags'
        ]
        
        missing_tables = []
        for table in required_tables:
            if table not in tables:
                missing_tables.append(table)
            else:
                print(f"   ✅ {table}")
                
        if missing_tables:
            print(f"❌ Tabelas faltando: {missing_tables}")
            return False
            
        print("✅ Todas as tabelas de otimização LLM criadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def create_sample_data():
    """Cria dados de exemplo para teste"""
    print("\n🧪 Criando dados de exemplo...")
    
    try:
        from synapse.database import get_db_session
        from synapse.models import LLM, Tag
        
        with get_db_session() as db:
            # Verifica se já existem LLMs
            llm_count = db.query(LLM).count()
            print(f"   LLMs cadastrados: {llm_count}")
            
            # Cria algumas tags de exemplo
            sample_tags = [
                {
                    "target_type": "system",
                    "target_id": "00000000-0000-0000-0000-000000000000",
                    "tag_name": "system_status",
                    "tag_value": "initialized",
                    "is_system_tag": True,
                },
                {
                    "target_type": "system", 
                    "target_id": "00000000-0000-0000-0000-000000000000",
                    "tag_name": "optimization_version",
                    "tag_value": "v1.0",
                    "is_system_tag": True,
                }
            ]
            
            for tag_data in sample_tags:
                # Verifica se a tag já existe
                existing = db.query(Tag).filter_by(
                    target_type=tag_data["target_type"],
                    tag_name=tag_data["tag_name"]
                ).first()
                
                if not existing:
                    tag = Tag(**tag_data)
                    db.add(tag)
                    
            db.commit()
            print("✅ Dados de exemplo criados!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 SynapScale - Setup de Otimização LLM")
    print("=" * 50)
    
    # Verifica se estamos no diretório correto
    if not os.path.exists("src/synapse"):
        print("❌ Execute este script na raiz do projeto SynapScale!")
        sys.exit(1)
    
    # Passos do setup
    steps = [
        ("Verificação do Alembic", check_alembic_setup),
        ("Execução das migrações", run_migrations),
        ("População de dados iniciais", populate_initial_data),
        ("Verificação das tabelas", verify_tables),
        ("Criação de dados de exemplo", create_sample_data),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        if step_func():
            success_count += 1
        else:
            print(f"\n❌ Falha na etapa: {step_name}")
            print("   Corrija os erros antes de continuar.")
            break
    
    # Resumo
    print(f"\n📊 Resumo do Setup")
    print("=" * 50)
    print(f"Etapas concluídas: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        print("🎉 Setup de otimização LLM concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Revisar dados criados no banco")
        print("   2. Testar integração com LLM Service")
        print("   3. Implementar endpoints de analytics")
        print("   4. Configurar billing automático")
    else:
        print("⚠️  Setup incompleto. Verifique os erros acima.")
        
    return success_count == len(steps)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 