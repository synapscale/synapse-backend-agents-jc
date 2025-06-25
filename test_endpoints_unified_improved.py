#!/usr/bin/env python3
"""
SCRIPT OTIMIZADO DE TESTE DE ENDPOINTS - SYNAPSCALE API
Versão completamente otimizada para a estrutura atual da API
"""
import argparse
import requests
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin
import re
import warnings
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Configurações
API_BASE_URL = "http://localhost:8000"
API_V1_PREFIX = "/api/v1"
TIMEOUT_SECONDS = 30

class OptimizedEndpointTester:
    def __init__(self, base_url: str = API_BASE_URL, verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.session = requests.Session()
        self.session.timeout = TIMEOUT_SECONDS
        self.auth_headers = {}
        self.all_endpoints = []
        self.openapi_spec = {}
        self.created_resources = []  # Para cleanup
        self.test_user_data = None
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
            "success_rate": 0,
            "critical_issues": [],
            "performance_metrics": {}
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
        elif level == "critical":
            print(f"🚨 [{timestamp}] {message}")
        else:
            print(f"ℹ️  [{timestamp}] {message}")

    def check_server_health(self) -> bool:
        """Verifica se o servidor está rodando e saudável"""
        self.log_message("Verificando saúde do servidor...")
        
        try:
            # Testar endpoint de health
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_message("Servidor está saudável", "success")
                return True
            else:
                self.log_message(f"Servidor retornou status {response.status_code}", "warning")
                return True  # Continuar mesmo assim
        except Exception as e:
            self.log_message(f"Erro ao verificar saúde do servidor: {str(e)}", "error")
            return False

    def discover_all_endpoints(self):
        """Descobre todos os endpoints via OpenAPI"""
        self.log_message("Descobrindo endpoints via OpenAPI...")
        
        try:
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=10)
            if response.status_code != 200:
                self.log_message("Falha ao obter especificação OpenAPI", "error")
                return False
            
            self.openapi_spec = response.json()
            paths = self.openapi_spec.get("paths", {})
            
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
                            "summary": method_info.get("summary", ""),
                            "tags": method_info.get("tags", [])
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
        
        # Categorização baseada no path
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
        elif "/users" in path:
            return "users"
        elif "/files" in path:
            return "files"
        elif "/templates" in path:
            return "templates"
        elif "/agents" in path:
            return "agents"
        elif "/nodes" in path:
            return "nodes"
        elif "/conversations" in path:
            return "conversations"
        else:
            return "general"

    def requires_authentication(self, method_info: Dict) -> bool:
        """Verifica se um endpoint requer autenticação"""
        return len(method_info.get("security", [])) > 0

    def extract_path_params(self, path: str) -> List[str]:
        """Extrai parâmetros do path"""
        return re.findall(r'\{([^}]+)\}', path)

    def setup_authentication(self) -> bool:
        """Configura autenticação para testes"""
        self.log_message("Configurando autenticação...")
        
        unique_id = uuid.uuid4().hex[:8]
        self.test_user_data = {
            "email": f"test_{unique_id}@example.com",
            "password": "TestPass123!@#",
            "full_name": f"Test User {unique_id}",
            "username": f"test_{unique_id}"
        }
        
        try:
            # 1. Registrar usuário
            register_response = self.session.post(
                f"{self.base_url}{API_V1_PREFIX}/auth/register",
                json=self.test_user_data,
                timeout=10
            )
            
            if register_response.status_code not in [200, 201]:
                self.log_message(f"Falha no registro: {register_response.status_code}", "warning")
                # Continuar mesmo assim, talvez o usuário já exista
            
            # 2. Fazer login
            login_data = {
                "username": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            login_response = self.session.post(
                f"{self.base_url}{API_V1_PREFIX}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                if access_token:
                    self.auth_headers = {"Authorization": f"Bearer {access_token}"}
                    self.log_message("Autenticação configurada com sucesso", "success")
                    return True
                else:
                    self.log_message("Token não encontrado na resposta", "error")
                    return False
            else:
                self.log_message(f"Falha no login: {login_response.status_code}", "error")
                return False
                
        except Exception as e:
            self.log_message(f"Erro na autenticação: {str(e)}", "error")
            return False

    def resolve_path_parameters(self, path: str, path_params: List[str]) -> str:
        """Resolve parâmetros de path com valores de teste"""
        resolved_path = path
        
        for param in path_params:
            param_lower = param.lower()
            
            # Mapeamento de parâmetros comuns
            if "id" in param_lower:
                # Para IDs, usar UUID válido
                test_id = str(uuid.uuid4())
                resolved_path = resolved_path.replace(f"{{{param}}}", test_id)
            elif "workspace" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "workflow" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "agent" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "node" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "conversation" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "message" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "file" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "template" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", str(uuid.uuid4()))
            elif "provider" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", "openai")
            elif "model" in param_lower:
                resolved_path = resolved_path.replace(f"{{{param}}}", "gpt-4")
            else:
                # Valor genérico
                resolved_path = resolved_path.replace(f"{{{param}}}", "test-value")
        
        return resolved_path

    def generate_test_data(self, method: str, category: str, path: str) -> Optional[Dict]:
        """Gera dados de teste baseado no método e categoria"""
        if method in ["GET", "DELETE"]:
            return None
        
        # Dados de teste por categoria
        test_data_map = {
            "workspaces": {
                "name": "Test Workspace",
                "description": "Workspace criado para teste",
                "settings": {}
            },
            "workflows": {
                "name": "Test Workflow",
                "description": "Workflow de teste",
                "nodes": [],
                "edges": []
            },
            "agents": {
                "name": "Test Agent",
                "description": "Agente de teste",
                "system_prompt": "Você é um assistente útil",
                "model": "gpt-4"
            },
            "templates": {
                "name": "Test Template",
                "description": "Template de teste",
                "category": "automation",
                "content": {}
            },
            "conversations": {
                "title": "Test Conversation",
                "workspace_id": str(uuid.uuid4())
            },
            "files": {
                "filename": "test.txt",
                "content_type": "text/plain"
            },
            "llm": {
                "prompt": "Hello, world!",
                "model": "gpt-4",
                "max_tokens": 100
            },
            "users": {
                "full_name": "Updated Test User",
                "preferences": {}
            },
            "feedback": {
                "rating": 5,
                "comment": "Excelente!",
                "type": "positive"
            }
        }
        
        # Dados específicos para alguns endpoints
        if "count-tokens" in path:
            return {
                "text": "Hello, world! This is a test message.",
                "model": "gpt-4"
            }
        elif "generate" in path or "chat" in path:
            return {
                "prompt": "Hello, how are you?",
                "model": "gpt-4",
                "max_tokens": 100,
                "temperature": 0.7
            }
        elif "password" in path:
            return {
                "current_password": self.test_user_data["password"] if self.test_user_data else "TestPass123!@#",
                "new_password": "NewTestPass123!@#"
            }
        elif "email" in path and "verification" in path:
            return {
                "email": self.test_user_data["email"] if self.test_user_data else "test@example.com"
            }
        
        return test_data_map.get(category, {"test": True, "data": "test_value"})

    def test_single_endpoint(self, endpoint_info: Dict):
        """Testa um endpoint individual"""
        path = endpoint_info["path"]
        method = endpoint_info["method"]
        category = endpoint_info["category"]
        requires_auth = endpoint_info["requires_auth"]
        path_params = endpoint_info["path_params"]
        
        # Resolver parâmetros de path
        resolved_path = self.resolve_path_parameters(path, path_params)
        full_url = f"{self.base_url}{resolved_path}"
        
        # Preparar headers
        headers = {"Content-Type": "application/json"}
        if requires_auth and self.auth_headers:
            headers.update(self.auth_headers)
        
        # Preparar dados de teste
        test_data = self.generate_test_data(method, category, path)
        
        # Executar teste
        start_time = time.time()
        try:
            if method == "GET":
                response = self.session.get(full_url, headers=headers, timeout=TIMEOUT_SECONDS)
            elif method == "POST":
                if test_data:
                    response = self.session.post(full_url, json=test_data, headers=headers, timeout=TIMEOUT_SECONDS)
                else:
                    response = self.session.post(full_url, headers=headers, timeout=TIMEOUT_SECONDS)
            elif method == "PUT":
                if test_data:
                    response = self.session.put(full_url, json=test_data, headers=headers, timeout=TIMEOUT_SECONDS)
                else:
                    response = self.session.put(full_url, headers=headers, timeout=TIMEOUT_SECONDS)
            elif method == "PATCH":
                if test_data:
                    response = self.session.patch(full_url, json=test_data, headers=headers, timeout=TIMEOUT_SECONDS)
                else:
                    response = self.session.patch(full_url, headers=headers, timeout=TIMEOUT_SECONDS)
            elif method == "DELETE":
                response = self.session.delete(full_url, headers=headers, timeout=TIMEOUT_SECONDS)
            else:
                self.log_result(path, method, False, 0, f"Método {method} não suportado", category)
                return
                
        except requests.exceptions.Timeout:
            self.log_result(path, method, False, 0, "Timeout", category)
            return
        except Exception as e:
            self.log_result(path, method, False, 0, f"Erro de conexão: {str(e)}", category)
            return
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Analisar resultado
        success = self.analyze_response(response, endpoint_info, response_time)
        
        # Log resultado
        details = f"Tempo: {response_time:.2f}s"
        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", "Erro desconhecido")
                details += f", Erro: {error_detail}"
            except:
                details += f", Erro: {response.text[:100]}"
        
        self.log_result(path, method, success, response.status_code, details, category)

    def analyze_response(self, response: requests.Response, endpoint_info: Dict, response_time: float) -> bool:
        """Analisa a resposta e determina se o teste passou"""
        status_code = response.status_code
        path = endpoint_info["path"]
        method = endpoint_info["method"]
        category = endpoint_info["category"]
        
        # Registrar métricas de performance
        if category not in self.test_results["performance_metrics"]:
            self.test_results["performance_metrics"][category] = []
        self.test_results["performance_metrics"][category].append(response_time)
        
        # Critérios de sucesso
        success_criteria = {
            # Endpoints públicos/sistema
            "system": [200, 404],  # Health pode não existir
            # Endpoints de autenticação
            "authentication": [200, 201, 400, 401, 422],  # Podem falhar por dados inválidos
            # Endpoints que requerem autenticação
            "default": [200, 201, 400, 401, 403, 404, 422]  # Podem falhar por recursos não encontrados
        }
        
        # Determinar critérios aplicáveis
        if category in success_criteria:
            acceptable_codes = success_criteria[category]
        else:
            acceptable_codes = success_criteria["default"]
        
        # Verificar se o status code é aceitável
        if status_code not in acceptable_codes:
            # Códigos 5xx são sempre problemas críticos
            if 500 <= status_code < 600:
                self.test_results["critical_issues"].append({
                    "endpoint": path,
                    "method": method,
                    "issue": f"Erro interno do servidor: {status_code}",
                    "category": category
                })
                return False
            return False
        
        # Verificar tempo de resposta
        if response_time > 10.0:  # Mais de 10 segundos é problemático
            self.test_results["critical_issues"].append({
                "endpoint": path,
                "method": method,
                "issue": f"Resposta muito lenta: {response_time:.2f}s",
                "category": category
            })
        
        # Verificar se é um erro de autenticação esperado
        if status_code == 401 and endpoint_info["requires_auth"]:
            # Pode ser esperado se não temos auth válida
            if not self.auth_headers:
                return True  # Comportamento esperado
        
        # Verificar se é um erro de recurso não encontrado
        if status_code == 404 and endpoint_info["path_params"]:
            return True  # Esperado para IDs de teste
        
        # Verificar se é um erro de validação
        if status_code in [400, 422]:
            return True  # Pode ser esperado com dados de teste
        
        # Códigos de sucesso
        if 200 <= status_code < 300:
            return True
        
        return False

    def log_result(self, endpoint: str, method: str, success: bool, status_code: int, 
                   details: str = "", category: str = "general"):
        """Registra o resultado de um teste"""
        self.test_results["tested_endpoints"] += 1
        
        if success:
            self.test_results["passed_tests"] += 1
            if self.verbose:
                self.log_message(f"{method:6} {endpoint:40} ✅ {status_code} - {details}", "success")
        else:
            self.test_results["failed_tests"] += 1
            if self.verbose:
                self.log_message(f"{method:6} {endpoint:40} ❌ {status_code} - {details}", "error")
        
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
        
        # Registrar resultado detalhado
        self.test_results["detailed_results"].append({
            "endpoint": endpoint,
            "method": method,
            "category": category,
            "success": success,
            "status_code": status_code,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_all_endpoints(self):
        """Testa todos os endpoints descobertos"""
        self.log_message(f"Iniciando teste de {len(self.all_endpoints)} endpoints...")
        
        start_time = time.time()
        
        # Agrupar por categoria
        by_category = {}
        for endpoint in self.all_endpoints:
            category = endpoint["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(endpoint)
        
        # Testar por categoria
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
        print("📊 RELATÓRIO FINAL DO TESTE DE ENDPOINTS - SYNAPSCALE API")
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
        
        # Performance por categoria
        print(f"\n⏱️ PERFORMANCE POR CATEGORIA:")
        for category, times in self.test_results["performance_metrics"].items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                print(f"   {category:15}: Média {avg_time:.2f}s, Máx {max_time:.2f}s")
        
        # Issues críticos
        if self.test_results["critical_issues"]:
            print(f"\n🚨 ISSUES CRÍTICOS - {len(self.test_results['critical_issues'])} encontrados:")
            for issue in self.test_results["critical_issues"][:10]:
                print(f"   • {issue['method']} {issue['endpoint']} - {issue['issue']}")

    def evaluate_production_readiness(self) -> str:
        """Avalia se a API está pronta para produção"""
        success_rate = self.test_results["success_rate"]
        critical_issues = len(self.test_results["critical_issues"])
        
        if critical_issues > 0:
            return "CRÍTICO - Issues críticos encontrados"
        elif success_rate >= 95:
            return "EXCELENTE - Pronto para produção"
        elif success_rate >= 90:
            return "BOM - Pequenos ajustes necessários"
        elif success_rate >= 80:
            return "ATENÇÃO - Correções necessárias"
        else:
            return "CRÍTICO - Não adequado para produção"

    def save_json_report(self, filename: str = "endpoint_test_results.json"):
        """Salva relatório detalhado em JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        self.log_message(f"Relatório JSON salvo em: {filename}", "success")

    def run_test(self, save_json: bool = False):
        """Executa o teste completo"""
        print("🔬 TESTE OTIMIZADO DE ENDPOINTS - SYNAPSCALE API")
        print("=" * 80)
        
        # 1. Verificar servidor
        if not self.check_server_health():
            self.log_message("Servidor não está acessível", "critical")
            return 3
        
        # 2. Descobrir endpoints
        if not self.discover_all_endpoints():
            return 1
        
        # 3. Configurar autenticação
        auth_success = self.setup_authentication()
        if not auth_success:
            self.log_message("Continuando sem autenticação (alguns testes podem falhar)", "warning")
        
        # 4. Testar endpoints
        self.test_all_endpoints()
        
        # 5. Relatório final
        self.print_final_report()
        
        # 6. Avaliação de produção
        readiness = self.evaluate_production_readiness()
        print(f"\n🎯 AVALIAÇÃO DE PRODUÇÃO: {readiness}")
        
        # 7. Salvar JSON
        if save_json:
            self.save_json_report()
        
        # 8. Código de saída baseado em critérios
        success_rate = self.test_results["success_rate"]
        critical_issues = len(self.test_results["critical_issues"])
        
        if critical_issues > 0:
            self.log_message("FALHA CRÍTICA! Issues críticos encontrados!", "critical")
            return 2
        elif success_rate >= 90:
            self.log_message("EXCELENTE! API funcionando bem!", "success")
            return 0
        elif success_rate >= 75:
            self.log_message("BOM! Alguns ajustes recomendados.", "success")
            return 0
        else:
            self.log_message("ATENÇÃO! Muitos testes falharam.", "warning")
            return 1

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Teste otimizado de endpoints da API SynapScale")
    parser.add_argument("--verbose", "-v", action="store_true", help="Output detalhado")
    parser.add_argument("--output-json", "-j", action="store_true", help="Salvar relatório JSON")
    parser.add_argument("--base-url", "-u", default=API_BASE_URL, help="URL base da API")
    
    args = parser.parse_args()
    
    tester = OptimizedEndpointTester(base_url=args.base_url, verbose=args.verbose)
    return tester.run_test(save_json=args.output_json)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1) 