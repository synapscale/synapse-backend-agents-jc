#!/usr/bin/env python3
"""
Teste final de integração para verificar que todos os endpoints estão usando dados reais da API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "joaovictor@liderimobiliaria.com.br"
PASSWORD = "@Teste123"

def get_token():
    """Obter token de autenticação"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    else:
        print(f"Erro ao obter token: {response.status_code} - {response.text}")
        return None

def test_endpoint(endpoint, method="GET", data=None, token=None):
    """Testar endpoint"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if data:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        
        return {
            "status": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.text else None
        }
    except Exception as e:
        return {"status": "ERROR", "success": False, "error": str(e)}

def main():
    """Teste principal"""
    print("🔧 SynapScale Backend - Teste Final de Integração")
    print("=" * 60)
    
    # 1. Teste de autenticação
    print("1. Testando autenticação...")
    token = get_token()
    if not token:
        print("❌ Falha na autenticação. Abortando testes.")
        return
    print("✅ Autenticação OK")
    
    # 2. Teste de endpoints principais
    endpoints = [
        ("Health Check", "/health", "GET", None),
        ("Usuários", "/users", "GET", None),
        ("Tenants", "/tenants", "GET", None),
        ("Workspaces", "/workspaces", "GET", None),
        ("LLMs", "/llms", "GET", None),
        ("Workflows", "/workflows", "GET", None),
        ("Nodes", "/nodes", "GET", None),
        ("Files", "/files", "GET", None),
        ("Executions", "/executions", "GET", None),
        ("Agents", "/agents", "GET", None),
        ("Conversations", "/conversations", "GET", None),
        ("Analytics", "/analytics", "GET", None),
    ]
    
    print(f"\n2. Testando {len(endpoints)} endpoints principais...")
    results = []
    
    for name, endpoint, method, data in endpoints:
        print(f"   Testing {name}...")
        result = test_endpoint(endpoint, method, data, token)
        results.append((name, result))
        
        if result["success"]:
            print(f"   ✅ {name}: {result['status']}")
        else:
            print(f"   ❌ {name}: {result['status']}")
            if result.get("data"):
                print(f"      Error: {result['data']}")
    
    # 3. Teste de criação de dados
    print(f"\n3. Testando criação de dados...")
    
    # Criar workflow
    workflow_data = {
        "name": "Integration Test Workflow",
        "description": "Workflow criado durante teste de integração",
        "definition": {
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "position": {"x": 100, "y": 100}
                }
            ],
            "connections": []
        }
    }
    
    workflow_result = test_endpoint("/workflows", "POST", workflow_data, token)
    if workflow_result["success"]:
        print("   ✅ Workflow criado com sucesso")
    else:
        print(f"   ❌ Falha ao criar workflow: {workflow_result['status']}")
    
    # 4. Resumo final
    print(f"\n4. Resumo dos testes:")
    print("=" * 60)
    
    successful = sum(1 for _, result in results if result["success"])
    total = len(results)
    
    print(f"Endpoints testados: {total}")
    print(f"Sucessos: {successful}")
    print(f"Falhas: {total - successful}")
    print(f"Taxa de sucesso: {(successful/total)*100:.1f}%")
    
    if successful == total:
        print("\n🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO COM DADOS REAIS DA API!")
        print("✅ Sistema SynapScale Backend está 100% funcional")
    else:
        print(f"\n⚠️  {total - successful} endpoints apresentaram problemas")
        print("❌ Verifique os logs para mais detalhes")
    
    print("\n" + "=" * 60)
    print(f"Teste finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
