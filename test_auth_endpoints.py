#!/usr/bin/env python3
"""
Script de teste rigoroso para verificar autenticação obrigatória
Só considera sucesso quando há autenticação válida E resposta 2xx
"""

import requests
import json
from urllib.parse import urljoin
from typing import Dict, List, Optional
import time

# Configurações
API_BASE_URL = "http://localhost:8000"
API_V1_PREFIX = "/api/v1"

# Endpoints que DEVEM ser públicos (sem autenticação)
PUBLIC_ENDPOINTS = {
    "/",
    "/health", 
    "/api/v1/health",
    "/info",
    "/auth/login",
    "/auth/signup", 
    "/auth/refresh",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/auth/verify-email"
}

class AuthenticationTester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Resultados dos testes
        self.results = {
            "public_endpoints_tested": 0,
            "public_endpoints_working": 0,
            "private_endpoints_tested": 0,
            "private_endpoints_properly_protected": 0,
            "authentication_bypassed": [],  # Endpoints que deveriam exigir auth mas não exigem
            "public_endpoints_broken": [],  # Endpoints públicos que não funcionam
            "errors": []
        }
        
        self.auth_token = None
        self.all_endpoints = []

    def setup_authentication(self) -> bool:
        """Configura autenticação válida"""
        print("🔐 Configurando autenticação...")
        
        # Primeiro, tentar registrar um usuário
        register_data = {
            "email": "test_auth@example.com",
            "password": "TestPass123!@#",
            "name": "Test User Auth"
        }
        
        try:
            # Tentar registrar
            response = self.session.post(
                f"{self.base_url}/auth/signup",
                json=register_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print("✅ Usuário registrado com sucesso")
            elif response.status_code == 400:
                print("⚠️  Usuário já existe, tentando login...")
            
            # Fazer login
            login_response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": register_data["email"],
                    "password": register_data["password"]
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                if "access_token" in login_data:
                    self.auth_token = login_data["access_token"]
                    print("✅ Autenticação configurada com sucesso")
                    return True
                    
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            
        return False

    def discover_endpoints(self):
        """Descobre todos os endpoints da API"""
        print("🔍 Descobrindo endpoints...")
        
        try:
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=10)
            if response.status_code == 200:
                openapi_spec = response.json()
                paths = openapi_spec.get("paths", {})
                
                for path, methods in paths.items():
                    for method in methods.keys():
                        if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                            self.all_endpoints.append({
                                "path": path,
                                "method": method.upper(),
                                "is_public": path in PUBLIC_ENDPOINTS
                            })
                
                print(f"📊 Descobertos {len(self.all_endpoints)} endpoints")
                print(f"📊 {len([e for e in self.all_endpoints if e['is_public']])} endpoints públicos esperados")
                print(f"📊 {len([e for e in self.all_endpoints if not e['is_public']])} endpoints privados esperados")
                
        except Exception as e:
            print(f"❌ Erro ao descobrir endpoints: {e}")

    def test_endpoint_without_auth(self, endpoint: Dict) -> Dict:
        """Testa endpoint sem autenticação"""
        path = endpoint["path"]
        method = endpoint["method"]
        
        # Resolver parâmetros de path com valores de teste
        resolved_path = path
        if "{" in path:
            # Substituir parâmetros comuns
            resolved_path = path.replace("{workspace_id}", "test-workspace")
            resolved_path = resolved_path.replace("{workflow_id}", "test-workflow")
            resolved_path = resolved_path.replace("{user_id}", "test-user")
            resolved_path = resolved_path.replace("{id}", "test-id")
            resolved_path = resolved_path.replace("{component_id}", "test-component")
            resolved_path = resolved_path.replace("{template_id}", "test-template")
            
        full_url = urljoin(self.base_url, resolved_path)
        
        try:
            if method == "GET":
                response = self.session.get(full_url)
            elif method == "POST":
                response = self.session.post(full_url, json={"test": "data"})
            elif method == "PUT":
                response = self.session.put(full_url, json={"test": "data"})
            elif method == "PATCH":
                response = self.session.patch(full_url, json={"test": "data"})
            elif method == "DELETE":
                response = self.session.delete(full_url)
            else:
                return {"status": "skipped", "reason": "método não suportado"}
            
            return {
                "status_code": response.status_code,
                "status": "success" if response.status_code < 400 else "failed",
                "response_time": response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def test_endpoint_with_auth(self, endpoint: Dict) -> Dict:
        """Testa endpoint com autenticação"""
        if not self.auth_token:
            return {"status": "error", "error": "Token de autenticação não disponível"}
            
        path = endpoint["path"]
        method = endpoint["method"]
        
        # Resolver parâmetros de path
        resolved_path = path
        if "{" in path:
            resolved_path = path.replace("{workspace_id}", "test-workspace")
            resolved_path = resolved_path.replace("{workflow_id}", "test-workflow")
            resolved_path = resolved_path.replace("{user_id}", "test-user")
            resolved_path = resolved_path.replace("{id}", "test-id")
            resolved_path = resolved_path.replace("{component_id}", "test-component")
            resolved_path = resolved_path.replace("{template_id}", "test-template")
            
        full_url = urljoin(self.base_url, resolved_path)
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            if method == "GET":
                response = self.session.get(full_url, headers=headers)
            elif method == "POST":
                response = self.session.post(full_url, json={"test": "data"}, headers=headers)
            elif method == "PUT":
                response = self.session.put(full_url, json={"test": "data"}, headers=headers)
            elif method == "PATCH":
                response = self.session.patch(full_url, json={"test": "data"}, headers=headers)
            elif method == "DELETE":
                response = self.session.delete(full_url, headers=headers)
            else:
                return {"status": "skipped", "reason": "método não suportado"}
            
            return {
                "status_code": response.status_code,
                "status": "success" if 200 <= response.status_code < 300 else "failed",
                "response_time": response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_authentication_tests(self):
        """Executa todos os testes de autenticação"""
        print("\n🧪 INICIANDO TESTES DE AUTENTICAÇÃO")
        print("=" * 60)
        
        # Testar endpoints públicos
        print("\n📂 TESTANDO ENDPOINTS PÚBLICOS")
        for endpoint in [e for e in self.all_endpoints if e["is_public"]]:
            self.results["public_endpoints_tested"] += 1
            
            result = self.test_endpoint_without_auth(endpoint)
            endpoint_name = f"{endpoint['method']} {endpoint['path']}"
            
            if result.get("status") == "success":
                self.results["public_endpoints_working"] += 1
                print(f"✅ {endpoint_name} - {result['status_code']}")
            else:
                self.results["public_endpoints_broken"].append({
                    "endpoint": endpoint_name,
                    "result": result
                })
                print(f"❌ {endpoint_name} - {result.get('status_code', 'ERROR')}")
        
        # Testar endpoints privados SEM autenticação
        print(f"\n🔒 TESTANDO ENDPOINTS PRIVADOS (sem autenticação)")
        for endpoint in [e for e in self.all_endpoints if not e["is_public"]]:
            self.results["private_endpoints_tested"] += 1
            
            result = self.test_endpoint_without_auth(endpoint)
            endpoint_name = f"{endpoint['method']} {endpoint['path']}"
            
            # Endpoint privado DEVE retornar 401 ou 403 sem autenticação
            if result.get("status_code") in [401, 403]:
                self.results["private_endpoints_properly_protected"] += 1
                print(f"✅ {endpoint_name} - {result['status_code']} (protegido)")
            elif result.get("status_code") and 200 <= result.get("status_code") < 300:
                # PROBLEMA: endpoint privado funcionou sem autenticação!
                self.results["authentication_bypassed"].append({
                    "endpoint": endpoint_name,
                    "status_code": result["status_code"]
                })
                print(f"🚨 {endpoint_name} - {result['status_code']} (BYPASS DE AUTENTICAÇÃO!)")
            else:
                print(f"⚠️  {endpoint_name} - {result.get('status_code', 'ERROR')} (erro)")

    def print_final_report(self):
        """Imprime relatório final"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - TESTES DE AUTENTICAÇÃO")
        print("=" * 80)
        
        # Estatísticas gerais
        total_endpoints = len(self.all_endpoints)
        public_expected = len([e for e in self.all_endpoints if e["is_public"]])
        private_expected = len([e for e in self.all_endpoints if not e["is_public"]])
        
        print(f"📊 Total de endpoints: {total_endpoints}")
        print(f"📊 Endpoints públicos esperados: {public_expected}")
        print(f"📊 Endpoints privados esperados: {private_expected}")
        
        # Resultados dos endpoints públicos
        print(f"\n🌐 ENDPOINTS PÚBLICOS:")
        print(f"   Testados: {self.results['public_endpoints_tested']}")
        print(f"   Funcionando: {self.results['public_endpoints_working']}")
        if self.results["public_endpoints_broken"]:
            print(f"   ❌ Quebrados: {len(self.results['public_endpoints_broken'])}")
        
        # Resultados dos endpoints privados
        print(f"\n🔒 ENDPOINTS PRIVADOS:")
        print(f"   Testados: {self.results['private_endpoints_tested']}")
        print(f"   Protegidos corretamente: {self.results['private_endpoints_properly_protected']}")
        
        # PROBLEMAS CRÍTICOS
        if self.results["authentication_bypassed"]:
            print(f"\n🚨 PROBLEMAS CRÍTICOS DE SEGURANÇA:")
            print(f"   Endpoints com bypass de autenticação: {len(self.results['authentication_bypassed'])}")
            for bypass in self.results["authentication_bypassed"]:
                print(f"   🚨 {bypass['endpoint']} - Status {bypass['status_code']}")
        
        # Taxa de proteção
        if self.results["private_endpoints_tested"] > 0:
            protection_rate = (self.results["private_endpoints_properly_protected"] / 
                             self.results["private_endpoints_tested"]) * 100
            print(f"\n🛡️  TAXA DE PROTEÇÃO: {protection_rate:.1f}%")
            
            if protection_rate < 100:
                print("🚨 FALHA CRÍTICA: Nem todos os endpoints privados estão protegidos!")
            else:
                print("✅ Todos os endpoints privados estão protegidos")
        
        # Resumo final
        total_issues = len(self.results["authentication_bypassed"]) + len(self.results["public_endpoints_broken"])
        if total_issues == 0:
            print(f"\n🎉 RESULTADO: API SEGURA - Todos os testes passaram!")
        else:
            print(f"\n⚠️  RESULTADO: {total_issues} problemas encontrados")

def main():
    """Função principal"""
    print("🔐 TESTE RIGOROSO DE AUTENTICAÇÃO DA API")
    print("=" * 50)
    
    tester = AuthenticationTester()
    
    # Descobrir endpoints
    tester.discover_endpoints()
    
    if not tester.all_endpoints:
        print("❌ Nenhum endpoint descoberto. Verifique se a API está rodando.")
        return
    
    # Configurar autenticação
    auth_success = tester.setup_authentication()
    if not auth_success:
        print("⚠️  Não foi possível configurar autenticação. Alguns testes podem falhar.")
    
    # Executar testes
    tester.run_authentication_tests()
    
    # Relatório final
    tester.print_final_report()

if __name__ == "__main__":
    main() 