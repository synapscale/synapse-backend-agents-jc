#!/usr/bin/env python3
"""
🧪 Script de Teste: Logs de Autenticação Melhorados

Este script testa se os logs de login estão sendo exibidos 
de forma organizada e visualmente destacada.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_auth_logs():
    """Testa os logs de autenticação melhorados"""
    
    print("🧪 TESTE: Logs de Autenticação Melhorados")
    print("=" * 50)
    
    # Teste 1: Login com sucesso (JSON)
    print("\n1️⃣ Teste de Login com Sucesso (JSON)")
    print("-" * 30)
    
    success_data = {
        "username": "joaovictor@liderimobiliaria.com.br",
        "password": "@Teste123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=success_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Login com sucesso - verificar logs!")
            result = response.json()
            print(f"   Token obtido: {result['data']['access_token'][:50]}...")
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    time.sleep(1)
    
    # Teste 2: Login com senha incorreta
    print("\n2️⃣ Teste de Login com Senha Incorreta")
    print("-" * 30)
    
    wrong_password_data = {
        "username": "joaovictor@liderimobiliaria.com.br",
        "password": "senha_errada"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=wrong_password_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            print("✅ Falha de login detectada - verificar logs!")
        else:
            print(f"❓ Resposta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    time.sleep(1)
    
    # Teste 3: Login com usuário inexistente  
    print("\n3️⃣ Teste de Login com Usuário Inexistente")
    print("-" * 30)
    
    nonexistent_user_data = {
        "username": "usuario_inexistente@teste.com",
        "password": "qualquer_senha"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=nonexistent_user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            print("✅ Usuário não encontrado - verificar logs!")
        else:
            print(f"❓ Resposta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("✅ TESTES CONCLUÍDOS!")
    print("📋 Verificar os logs do servidor para:")
    print("   - 🔐 ✅ LOGIN SUCCESS (log de sucesso)")
    print("   - 🔐 ❌ LOGIN FAILED (logs de falha)")
    print("   - Ausência de logs desnecessários (current-url, identity)")

if __name__ == "__main__":
    test_auth_logs() 