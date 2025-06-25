#!/usr/bin/env python3
"""
Script para testar especificamente o endpoint LLM que estava falhando
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_llm_models_endpoint():
    """Testa o endpoint /api/v1/llm/models"""
    
    async with aiohttp.ClientSession() as session:
        # Primeiro, fazer login para obter o token
        login_data = {
            "username": "test@test.com",
            "password": "test123"
        }
        
        print("🔐 Fazendo login...")
        async with session.post(f"{BASE_URL}/api/v1/auth/login", data=login_data) as response:
            if response.status == 200:
                auth_response = await response.json()
                token = auth_response.get("access_token")
                print(f"✅ Login realizado com sucesso")
            else:
                print(f"❌ Falha no login: {response.status}")
                token = None
        
        # Testar o endpoint LLM models
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        print("\n🤖 Testando endpoint /api/v1/llm/models...")
        async with session.get(f"{BASE_URL}/api/v1/llm/models", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print("✅ Sucesso!")
                print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ Falha: {response.status}")
                try:
                    error_data = await response.json()
                    print(f"Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    error_text = await response.text()
                    print(f"Erro: {error_text}")
                return False

async def test_llm_providers_endpoint():
    """Testa o endpoint /api/v1/llm/providers"""
    
    async with aiohttp.ClientSession() as session:
        # Primeiro, fazer login para obter o token
        login_data = {
            "username": "test@test.com",
            "password": "test123"
        }
        
        print("🔐 Fazendo login...")
        async with session.post(f"{BASE_URL}/api/v1/auth/login", data=login_data) as response:
            if response.status == 200:
                auth_response = await response.json()
                token = auth_response.get("access_token")
                print(f"✅ Login realizado com sucesso")
            else:
                print(f"❌ Falha no login: {response.status}")
                token = None
        
        # Testar o endpoint LLM providers
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        print("\n🏢 Testando endpoint /api/v1/llm/providers...")
        async with session.get(f"{BASE_URL}/api/v1/llm/providers", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print("✅ Sucesso!")
                print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ Falha: {response.status}")
                try:
                    error_data = await response.json()
                    print(f"Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    error_text = await response.text()
                    print(f"Erro: {error_text}")
                return False

async def main():
    """Função principal"""
    print("🧪 Testando endpoints LLM específicos\n")
    
    # Testar modelos
    models_ok = await test_llm_models_endpoint()
    
    print("\n" + "="*50 + "\n")
    
    # Testar provedores  
    providers_ok = await test_llm_providers_endpoint()
    
    print("\n" + "="*50 + "\n")
    
    if models_ok and providers_ok:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("💥 Alguns testes falharam!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 