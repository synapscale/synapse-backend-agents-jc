#!/usr/bin/env python3
"""
SCRIPT UNIFICADO DE TESTE DE ENDPOINTS - SYNAPSCALE API
Este script consolida todas as funcionalidades de teste de endpoints em uma única ferramenta
"""
import argparse
import requests
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import re

# Configurações
API_BASE_URL = "http://localhost:8000"
API_V1_PREFIX = "/api/v1"

class UnifiedEndpointTester:
    def __init__(self, base_url: str = API_BASE_URL, verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.session = requests.Session()
        self.auth_headers = {}
        self.all_endpoints = []
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_endpoints": 0,
            "tested_endpoints": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "by_method": {},
            "by_category": {},
            "detailed_results": [],
            "errors": [],
            "execution_time": 0,
            "success_rate": 0
        }
        
        # Dados de teste reutilizáveis
        self.test_data = {
            "user_id": None,
            "workspace_id": None,
            "workflow_id": None
        }

    def log_message(self, message: str, level: str = "info"):
        """Log de mensagens com níveis"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "error":
            print(f"❌ [{timestamp}] {message}")
        elif level == "warning":
            print(f"⚠️  [{timestamp}] {message}")
        elif level == "success":
            print(f"✅ [{timestamp}] {message}")
        else:
            print(f"ℹ️  [{timestamp}] {message}")

    def discover_all_endpoints(self):
        """Descobre todos os endpoints via OpenAPI"""
        self.log_message("Descobrindo endpoints via OpenAPI...")
        
        try:
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code != 200:
                self.log_message("Falha ao obter especificação OpenAPI", "error")
                return False
            
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            for path, methods in paths.items():
                for method, method_info in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                        category = self.categorize_endpoint(path, method_info)
                        requires_auth = self.requires_authentication(method_info)
                        path_params = self.extract_path_params(path)
                        
                        endpoint_info = {
                            "path": path,
                            "method": method.upper(),
                            "category": category,
                            "requires_auth": requires_auth,
                            "path_params": path_params,
                            "summary": method_info.get("summary", "")
                        }
                        
                        self.all_endpoints.append(endpoint_info)
            
            self.test_results["total_endpoints"] = len(self.all_endpoints)
            self.log_message(f"Descobertos {len(self.all_endpoints)} endpoints", "success")
            return True
            
        except Exception as e:
            self.log_message(f"Erro ao descobrir endpoints: {str(e)}", "error")
            return False

    def categorize_endpoint(self, path: str, method_info: Dict) -> str:
        """Categoriza um endpoint baseado no path e tags"""
        tags = method_info.get("tags", [])
        if tags:
            return tags[0].lower()
        
        if "/auth/" in path:
            return "authentication"
        elif "/workspace" in path:
            return "workspaces"
        elif "/workflow" in path:
            return "workflows"
        elif "/llm" in path:
            return "llm"
        elif "/analytics" in path:
            return "analytics"
        elif "/marketplace" in path:
            return "marketplace"
        elif "/health" in path or path == "/":
            return "system"
        else:
            return "general"

    def requires_authentication(self, method_info: Dict) -> bool:
        """Verifica se um endpoint requer autenticação"""
        return len(method_info.get("security", [])) > 0

    def extract_path_params(self, path: str) -> List[str]:
        """Extrai parâmetros do path"""
        return re.findall(r'\{([^}]+)\}', path)

    def setup_authentication(self):
        """Configura autenticação para testes"""
        self.log_message("Configurando autenticação...")
        
        unique_id = uuid.uuid4().hex[:8]
        test_user = {
            "email": f"unified_test_{unique_id}@example.com",
            "password": "TestPass123!@#",
            "full_name": f"Unified Test User {unique_id}",
            "username": f"unified_test_{unique_id}"
        }
        
        try:
            # Registrar usuário
            response = self.session.post(
                f"{self.base_url}{API_V1_PREFIX}/auth/register",
                json=test_user
            )
            
            # Fazer login
            login_data = {
                "username": test_user["email"],
                "password": test_user["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}{API_V1_PREFIX}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                
                if token:
                    self.auth_headers = {"Authorization": f"Bearer {token}"}
                    self.log_message("Autenticação configurada com sucesso!", "success")
                    return True
            
            self.log_message(f"Login falhou: {response.status_code}", "error")
            return False
            
        except Exception as e:
            self.log_message(f"Erro na autenticação: {str(e)}", "error")
            return False

    def resolve_path_parameters(self, path: str, path_params: List[str]) -> str:
        """Resolve parâmetros do path com valores de teste"""
        resolved_path = path
        for param in path_params:
            resolved_path = resolved_path.replace(f"{{{param}}}", "1")
        return resolved_path

    def generate_test_data(self, endpoint_info: Dict) -> Optional[Dict]:
        """Gera dados de teste para o endpoint"""
        method = endpoint_info["method"]
        category = endpoint_info["category"]
        
        if method == "GET":
            return None
        
        if category == "workflows":
            return {
                "name": f"Test Workflow {uuid.uuid4().hex[:6]}",
                "description": "Workflow de teste",
                "category": "test",
                "definition": {"nodes": [], "connections": []}
            }
        elif category == "llm":
            return {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10
            }
        else:
            return {"name": f"Test Item {uuid.uuid4().hex[:6]}"}

    def test_single_endpoint(self, endpoint_info: Dict):
        """Testa um único endpoint"""
        path = endpoint_info["path"]
        method = endpoint_info["method"]
        category = endpoint_info["category"]
        requires_auth = endpoint_info["requires_auth"]
        path_params = endpoint_info["path_params"]
        
        resolved_path = self.resolve_path_parameters(path, path_params)
        full_url = urljoin(self.base_url, resolved_path)
        
        headers = {}
        if requires_auth and self.auth_headers:
            headers.update(self.auth_headers)
        
        test_data = self.generate_test_data(endpoint_info)
        
        try:
            if method == "GET":
                response = self.session.get(full_url, headers=headers)
            elif method == "POST":
                response = self.session.post(full_url, json=test_data, headers=headers)
            elif method == "PUT":
                response = self.session.put(full_url, json=test_data, headers=headers)
            elif method == "PATCH":
                response = self.session.patch(full_url, json=test_data, headers=headers)
            elif method == "DELETE":
                response = self.session.delete(full_url, headers=headers)
            else:
                return
            
            status_code = response.status_code
            
            success_codes = {
                "GET": [200, 401, 403, 404],
                "POST": [200, 201, 400, 401, 403, 422],
                "PUT": [200, 204, 400, 401, 403, 404, 422],
                "PATCH": [200, 204, 400, 401, 403, 404, 422],
                "DELETE": [200, 204, 401, 403, 404]
            }
            
            expected_codes = success_codes.get(method, [200, 400, 401, 403, 404, 422])
            success = status_code in expected_codes
            
            if status_code == 500:
                success = False
                details = "ERRO INTERNO DO SERVIDOR"
            elif status_code == 200:
                details = "Sucesso"
            elif status_code == 201:
                details = "Criado"
            elif status_code in [401, 403, 404, 422]:
                details = "Resposta esperada"
            else:
                details = f"Código {status_code}"
            
            self.log_result(resolved_path, method, success, status_code, details, category)
            
        except Exception as e:
            self.log_result(resolved_path, method, False, 0, f"Exceção: {str(e)}", category)

    def log_result(self, endpoint: str, method: str, success: bool, status_code: int, 
                   details: str = "", category: str = "general"):
        """Registra resultado de um teste"""
        self.test_results["tested_endpoints"] += 1
        
        if success:
            self.test_results["passed_tests"] += 1
            if self.verbose:
                self.log_message(f"{method:6} {endpoint:40} - {status_code} - {details}", "success")
        else:
            self.test_results["failed_tests"] += 1
            self.test_results["errors"].append({
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "details": details,
                "category": category
            })
            if self.verbose:
                self.log_message(f"{method:6} {endpoint:40} - {status_code} - {details}", "error")
        
        # Estatísticas por método
        if method not in self.test_results["by_method"]:
            self.test_results["by_method"][method] = {"passed": 0, "failed": 0}
        
        if success:
            self.test_results["by_method"][method]["passed"] += 1
        else:
            self.test_results["by_method"][method]["failed"] += 1
            
        # Estatísticas por categoria
        if category not in self.test_results["by_category"]:
            self.test_results["by_category"][category] = {"passed": 0, "failed": 0}
        
        if success:
            self.test_results["by_category"][category]["passed"] += 1
        else:
            self.test_results["by_category"][category]["failed"] += 1

    def test_all_endpoints(self):
        """Testa todos os endpoints descobertos"""
        self.log_message(f"Iniciando teste de {len(self.all_endpoints)} endpoints...")
        
        start_time = time.time()
        
        by_category = {}
        for endpoint in self.all_endpoints:
            category = endpoint["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(endpoint)
        
        for category, endpoints in sorted(by_category.items()):
            if not self.verbose:
                print(f"\n📂 Testando: {category.upper()} ({len(endpoints)} endpoints)")
            
            for endpoint in sorted(endpoints, key=lambda x: (x["path"], x["method"])):
                self.test_single_endpoint(endpoint)
        
        end_time = time.time()
        self.test_results["execution_time"] = end_time - start_time
        
        if self.test_results["tested_endpoints"] > 0:
            self.test_results["success_rate"] = (
                self.test_results["passed_tests"] / self.test_results["tested_endpoints"]
            ) * 100

    def print_final_report(self):
        """Imprime relatório final"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DO TESTE UNIFICADO DE ENDPOINTS")
        print("=" * 80)
        print(f"⏱️  Tempo total: {self.test_results['execution_time']:.2f} segundos")
        print(f"📈 Endpoints descobertos: {self.test_results['total_endpoints']}")
        print(f"🧪 Endpoints testados: {self.test_results['tested_endpoints']}")
        print(f"✅ Testes aprovados: {self.test_results['passed_tests']}")
        print(f"❌ Testes falharam: {self.test_results['failed_tests']}")
        print(f"🎯 Taxa de sucesso: {self.test_results['success_rate']:.1f}%")
        
        # Estatísticas por método
        print(f"\n📊 RESULTADOS POR MÉTODO HTTP:")
        for method, stats in sorted(self.test_results["by_method"].items()):
            total = stats["passed"] + stats["failed"]
            rate = (stats["passed"] / total * 100) if total > 0 else 0
            print(f"   {method:7}: {stats['passed']:3}✅ {stats['failed']:3}❌ ({rate:5.1f}%)")
        
        # Estatísticas por categoria
        print(f"\n📊 RESULTADOS POR CATEGORIA:")
        for category, stats in sorted(self.test_results["by_category"].items()):
            total = stats["passed"] + stats["failed"]
            rate = (stats["passed"] / total * 100) if total > 0 else 0
            print(f"   {category:15}: {stats['passed']:3}✅ {stats['failed']:3}❌ ({rate:5.1f}%)")
        
        # Erros críticos
        critical_errors = [e for e in self.test_results["errors"] if e["status_code"] == 500]
        if critical_errors:
            print(f"\n🚨 ERROS CRÍTICOS (500) - {len(critical_errors)} encontrados:")
            for error in critical_errors[:10]:
                print(f"   • {error['method']} {error['endpoint']}")

    def save_json_report(self, filename: str = "endpoint_test_results.json"):
        """Salva relatório detalhado em JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        self.log_message(f"Relatório JSON salvo em: {filename}", "success")

    def run_unified_test(self, save_json: bool = False):
        """Executa o teste unificado completo"""
        print("🔬 TESTE UNIFICADO DE ENDPOINTS - SYNAPSCALE API")
        print("=" * 80)
        
        # 1. Verificar servidor
        try:
            response = requests.get(self.base_url, timeout=10)
            self.log_message(f"Servidor detectado em {self.base_url}", "success")
        except Exception as e:
            self.log_message(f"Servidor não acessível: {str(e)}", "error")
            return 3
        
        # 2. Descobrir endpoints
        if not self.discover_all_endpoints():
            return 1
        
        # 3. Configurar autenticação
        self.setup_authentication()
        
        # 4. Testar endpoints
        self.test_all_endpoints()
        
        # 5. Relatório final
        self.print_final_report()
        
        # 6. Salvar JSON
        if save_json:
            self.save_json_report()
        
        # 7. Código de saída
        success_rate = self.test_results["success_rate"]
        
        if success_rate >= 90:
            self.log_message("EXCELENTE! Endpoints funcionando bem!", "success")
            return 0
        elif success_rate >= 75:
            self.log_message("BOM! Maioria dos endpoints OK.", "success")
            return 0
        elif success_rate >= 50:
            self.log_message("ATENÇÃO! Alguns endpoints precisam correção.", "warning")
            return 1
        else:
            self.log_message("CRÍTICO! Muitos problemas encontrados!", "error")
            return 2

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Teste unificado de endpoints da API SynapScale")
    parser.add_argument("--verbose", "-v", action="store_true", help="Output detalhado")
    parser.add_argument("--output-json", "-j", action="store_true", help="Salvar relatório JSON")
    parser.add_argument("--base-url", "-u", default=API_BASE_URL, help="URL base da API")
    
    args = parser.parse_args()
    
    tester = UnifiedEndpointTester(base_url=args.base_url, verbose=args.verbose)
    return tester.run_unified_test(save_json=args.output_json)

if __name__ == "__main__":
    sys.exit(main()) 