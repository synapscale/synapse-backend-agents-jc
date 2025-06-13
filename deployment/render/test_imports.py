#!/usr/bin/env python3
"""
Script de teste para verificar se todas as importações estão funcionando
antes do deploy no Render
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def test_imports():
    """Testa todas as importações críticas"""
    print("🔍 Testando importações...")
    
    try:
        # Testar importação básica
        import synapse  # noqa: F401
        print("✅ synapse importado com sucesso")
        
        # Testar importação do main
        from synapse.main import app  # noqa: F401
        print("✅ synapse.main.app importado com sucesso")
        
        # Testar importação das configurações
        from synapse.core.config_new import settings  # noqa: F401
        print("✅ synapse.core.config_new.settings importado com sucesso")
        
        # Testar importação do database
        from synapse.database import init_db, get_db  # noqa: F401
        print("✅ synapse.database importado com sucesso")
        
        # Testar importação dos routers
        from synapse.api.v1.router import api_router  # noqa: F401
        print("✅ synapse.api.v1.router importado com sucesso")
        
        print("\n✅ Todos os testes de importação passaram!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando testes de importação...")
    success = test_imports()
    
    if success:
        print("\n🎉 Projeto pronto para deploy!")
        sys.exit(0)
    else:
        print("\n💥 Falha nos testes. Verifique as importações antes do "
              "deploy.")
        sys.exit(1)
