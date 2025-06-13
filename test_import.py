#!/usr/bin/env python3
"""
Script de teste para verificar se as importações estão funcionando
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, 'src')

print("Testing imports...")

try:
    from synapse.core.config_new import settings
    print("✅ Config imported successfully")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")
except Exception as e:
    print(f"❌ Error importing config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from synapse.main import app
    print("✅ Main app imported successfully")
except Exception as e:
    print(f"❌ Error importing main app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 All imports successful!")
