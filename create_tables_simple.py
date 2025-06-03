#!/usr/bin/env python3
"""Script simples para criar tabelas."""
print("=== SCRIPT INICIADO ===")

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from synapse.database import Base, create_tables
    print("✅ Database importado")
    
    # Importar explicitamente cada modelo para registrá-los
    from synapse.models.user import User
    from synapse.models.file import File
    from synapse.models.workflow import Workflow
    from synapse.models.node import Node
    from synapse.models.agent import Agent
    from synapse.models.conversation import Conversation
    from synapse.models.message import Message
    print("✅ Modelos importados")
    
    print(f"📋 Modelos registrados: {list(Base.metadata.tables.keys())}")
    
    print("🔧 Criando tabelas...")
    create_tables()
    print("✅ Tabelas criadas!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("=== SCRIPT FINALIZADO ===")
