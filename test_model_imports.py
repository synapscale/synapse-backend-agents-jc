#!/usr/bin/env python3
"""Teste de importação dos modelos."""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

print("=== TESTE DE IMPORTAÇÃO DOS MODELOS ===")

try:
    # Importar Base primeiro
    from synapse.database import Base
    print("✅ Base importado")
    print(f"Tabelas antes das importações: {list(Base.metadata.tables.keys())}")
    
    # Importar cada modelo individualmente
    print("\n--- Importando modelos individuais ---")
    
    from synapse.models.user import User
    print(f"✅ User importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    from synapse.models.file import File
    print(f"✅ File importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    from synapse.models.workflow import Workflow
    print(f"✅ Workflow importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    from synapse.models.node import Node
    print(f"✅ Node importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    from synapse.models.agent import Agent
    print(f"✅ Agent importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    from synapse.models.conversation import Conversation
    print(f"✅ Conversation importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    from synapse.models.message import Message
    print(f"✅ Message importado. Tabelas: {list(Base.metadata.tables.keys())}")
    
    print(f"\n📋 Total de tabelas registradas: {len(Base.metadata.tables)}")
    print(f"📝 Lista completa: {list(Base.metadata.tables.keys())}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
