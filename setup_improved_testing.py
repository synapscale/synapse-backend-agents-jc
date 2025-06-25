#!/usr/bin/env python3
"""
Script para configurar ambiente de teste melhorado
Instala dependências e valida configuração
"""
import subprocess
import sys
import os

def install_dependencies():
    """Instala dependências necessárias"""
    print("🔧 Instalando dependências para teste melhorado...")
    
    dependencies = [
        "jsonschema>=4.0.0",
        "requests>=2.25.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"   Instalando {dep}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Erro ao instalar {dep}")
            return False
    
    return True

def validate_environment():
    """Valida ambiente de teste"""
    print("\n🔍 Validando ambiente...")
    
    try:
        import jsonschema
        import requests
        print("   ✅ Todas as dependências estão disponíveis")
        
        # Verificar se API está acessível
        try:
            response = requests.get("http://localhost:8000", timeout=5)
            print("   ✅ API SynapScale está acessível")
        except:
            print("   ⚠️  API SynapScale não está rodando em localhost:8000")
            print("      Execute 'python main.py' ou 'uvicorn main:app --reload' primeiro")
        
        return True
    except ImportError as e:
        print(f"   ❌ Dependência faltando: {e}")
        return False

def create_test_config():
    """Cria arquivo de configuração de teste"""
    config = {
        "api_base_url": "http://localhost:8000",
        "timeout_seconds": 30,
        "test_user_prefix": "improved_test_",
        "cleanup_resources": True,
        "validate_schemas": True,
        "performance_threshold": 10.0,
        "success_rate_threshold": 90.0
    }
    
    try:
        import json
        with open("test_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("   ✅ Arquivo test_config.json criado")
    except Exception as e:
        print(f"   ⚠️  Erro ao criar configuração: {e}")

def main():
    print("🚀 CONFIGURAÇÃO DO AMBIENTE DE TESTE MELHORADO")
    print("=" * 50)
    
    # 1. Instalar dependências
    if not install_dependencies():
        print("\n❌ Falha na instalação de dependências")
        return 1
    
    # 2. Validar ambiente
    if not validate_environment():
        print("\n❌ Ambiente não está válido")
        return 1
    
    # 3. Criar configuração
    create_test_config()
    
    print("\n✅ AMBIENTE CONFIGURADO COM SUCESSO!")
    print("\nPróximos passos:")
    print("1. Execute: python test_endpoints_unified_improved.py --verbose")
    print("2. Para salvar relatório JSON: python test_endpoints_unified_improved.py --output-json")
    print("3. Para usar URL diferente: python test_endpoints_unified_improved.py --base-url http://sua-url")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 