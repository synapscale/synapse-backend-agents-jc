#!/usr/bin/env python3
"""
Script para gerar um token JWT de teste para demonstração da API.
"""

import os
import sys
from datetime import datetime, timedelta

# Configurar exatamente como no dev.sh
root_dir = os.path.join(os.path.dirname(__file__), "..", "..")
os.environ['PYTHONPATH'] = './src'
sys.path.insert(0, os.path.join(root_dir, "src"))

# Carregar .env exatamente como no dev.sh
from dotenv import load_dotenv
load_dotenv('.env')

from synapse.core.auth.jwt import create_access_token


def main():
    """Gera um token JWT de teste para demonstração."""
    
    try:
        # Verificar se as configurações estão corretas
        from synapse.core.config import settings
        
        if not settings.JWT_SECRET_KEY or len(settings.JWT_SECRET_KEY) < 32:
            print("❌ JWT_SECRET_KEY não configurada adequadamente no .env")
            print("Execute primeiro: python tools/utilities/generate_secure_keys.py")
            return False
            
        print("✅ Configurações JWT carregadas corretamente")
        
        # Dados do usuário de teste - usando formato compatível com o sistema real
        test_user_data = {
            "sub": "demo_user_123",
            "email": "demo@example.com", 
            "username": "demo_user",
            "role": "user",
            "user_id": "demo_user_123",
            "scopes": ["files:read", "files:write", "llm:use"],
            "is_active": True,
            "is_verified": True
        }

        # Gerar token usando a função utilitária (sem expires_delta pois a função não aceita)
        token = create_access_token(data=test_user_data)

        print("\n🔑 Token JWT de Teste Gerado:")
        print("=" * 60)
        print(token)
        print("=" * 60)
        
        # Validar o token gerado
        try:
            from synapse.core.auth.jwt import verify_token
            payload = verify_token(token)
            print("\n✅ Token validado com sucesso!")
            print(f"   Expira em: {datetime.fromtimestamp(payload['exp'])} UTC")
        except Exception as e:
            print(f"\n⚠️ Erro na validação do token: {e}")
        
        print("\n📋 Exemplos de Uso:")
        print("1. Testar endpoint de providers:")
        print(f'   curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/providers')
        print("\n2. Testar endpoint de health:")
        print(f'   curl -H "Authorization: Bearer {token}" http://localhost:8000/health')
        print("\n3. Acessar documentação com autenticação:")
        print("   Use o token no botão 'Authorize' em http://localhost:8000/docs")
        
        print(f"\n⏰ Válido por: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
        print("👤 Usuário: demo@example.com")
        print("🏷️ Role: user")
        print("🔐 Scopes: files:read, files:write, llm:use")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Certifique-se de que o ambiente virtual está ativado e as dependências instaladas.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
