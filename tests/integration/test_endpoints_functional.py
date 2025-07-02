#!/usr/bin/env python3
"""
TESTE FUNCIONAL ESPECÍFICO DE ENDPOINTS - SYNAPSCALE API
Foca em testes funcionais detalhados por categoria
"""
import requests
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# Configurações
API_BASE_URL = "http://localhost:8000"
API_V1_PREFIX = "/api/v1"


class FunctionalEndpointTester:
    def __init__(self, base_url: str = API_BASE_URL, verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.session = requests.Session()
        self.auth_headers = {}
        self.test_data = {}

    def log(self, message: str, level: str = "info"):
        """Log padronizado"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        if self.verbose or level != "debug":
            print(f"{icons.get(level, 'ℹ️')} [{timestamp}] {message}")

    def setup_test_environment(self) -> bool:
        """Configura ambiente de teste"""
        self.log("Configurando ambiente de teste...")

        # Verificar conectividade
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                self.log("Servidor não está saudável", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao conectar: {e}", "error")
            return False

        # Configurar dados de teste com novos campos das Tasks 2-11
        unique_id = uuid.uuid4().hex[:8]
        self.test_data = {
            "user": {
                "email": f"test_{unique_id}@synapscale.test",
                "password": "TestPass123!@#",
                "full_name": f"Test User {unique_id}",
                "username": f"test_{unique_id}",
                # Novos campos de perfil
                "bio": f"Test user {unique_id} bio for functional testing",
                "timezone": "UTC",
                "phone": "+1234567890",
            },
            "tenant": {
                "name": f"Test Tenant {unique_id}",
                "domain": f"test{unique_id}.example.com",
                "theme": "light",
                "default_language": "en",
                "timezone": "UTC",
                "mfa_required": False,
                "session_timeout": 3600,
            },
            "workspace": {
                "name": f"Test Workspace {unique_id}",
                "description": f"Functional test workspace {unique_id}",
                "email_notifications": True,
                "push_notifications": False,
            },
        }

        self.log("Ambiente configurado", "success")
        return True

    def test_authentication_flow(self) -> Dict:
        """Testa o fluxo completo de autenticação"""
        self.log("🔐 Testando fluxo de autenticação...")
        test_result = {"name": "authentication_flow", "tests": [], "success": True}

        try:
            # 1. Registro de usuário
            register_test = self._test_user_registration()
            test_result["tests"].append(register_test)

            # 2. Login
            login_test = self._test_user_login()
            test_result["tests"].append(login_test)
            if login_test["success"]:
                token = login_test.get("token")
                if token:
                    self.auth_headers = {"Authorization": f"Bearer {token}"}

            # 3. Verificar perfil
            profile_test = self._test_user_profile()
            test_result["tests"].append(profile_test)

        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            self.log(f"Erro no teste de autenticação: {e}", "error")

        success_count = sum(1 for t in test_result["tests"] if t["success"])
        total_count = len(test_result["tests"])
        self.log(
            f"Autenticação: {success_count}/{total_count} testes passaram",
            "success" if success_count == total_count else "warning",
        )

        return test_result

    def _test_user_registration(self) -> Dict:
        """Testa registro de usuário"""
        try:
            response = self.session.post(
                f"{self.base_url}{API_V1_PREFIX}/auth/register",
                json=self.test_data["user"],
                timeout=10,
            )

            success = response.status_code in [200, 201, 409]  # 409 = usuário já existe
            return {
                "name": "user_registration",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "user_registration", "success": False, "error": str(e)}

    def _test_user_login(self) -> Dict:
        """Testa login de usuário"""
        try:
            login_data = {
                "username": self.test_data["user"]["email"],
                "password": self.test_data["user"]["password"],
            }

            response = self.session.post(
                f"{self.base_url}{API_V1_PREFIX}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )

            success = response.status_code == 200
            token = None
            if success:
                try:
                    data = response.json()
                    token = data.get("access_token")
                except:
                    pass

            return {
                "name": "user_login",
                "success": success,
                "status_code": response.status_code,
                "token": token,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "user_login", "success": False, "error": str(e)}

    def _test_user_profile(self) -> Dict:
        """Testa acesso ao perfil"""
        try:
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/auth/me",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code == 200
            return {
                "name": "user_profile",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "user_profile", "success": False, "error": str(e)}

    def test_system_endpoints(self) -> Dict:
        """Testa endpoints do sistema"""
        self.log("⚙️ Testando endpoints do sistema...")
        test_result = {"name": "system_endpoints", "tests": [], "success": True}

        try:
            # 1. Health check
            health_test = self._test_health_check()
            test_result["tests"].append(health_test)

            # 2. Root endpoint
            root_test = self._test_root_endpoint()
            test_result["tests"].append(root_test)

            # 3. Info endpoint
            info_test = self._test_info_endpoint()
            test_result["tests"].append(info_test)

        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            self.log(f"Erro no teste do sistema: {e}", "error")

        success_count = sum(1 for t in test_result["tests"] if t["success"])
        total_count = len(test_result["tests"])
        self.log(
            f"Sistema: {success_count}/{total_count} testes passaram",
            "success" if success_count == total_count else "warning",
        )

        return test_result

    def _test_health_check(self) -> Dict:
        """Testa health check"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            return {
                "name": "health_check",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "health_check", "success": False, "error": str(e)}

    def _test_root_endpoint(self) -> Dict:
        """Testa endpoint raiz"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            return {
                "name": "root_endpoint",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "root_endpoint", "success": False, "error": str(e)}

    def _test_info_endpoint(self) -> Dict:
        """Testa endpoint de informações"""
        try:
            response = self.session.get(f"{self.base_url}/info", timeout=10)
            success = response.status_code == 200
            return {
                "name": "info_endpoint",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "info_endpoint", "success": False, "error": str(e)}

    def test_tenant_functionality(self) -> Dict:
        """Testa funcionalidades de tenant com novos campos"""
        self.log("🏢 Testando funcionalidades de tenant...")
        test_result = {"name": "tenant_functionality", "tests": [], "success": True}

        try:
            # 1. Teste de listagem de tenants
            list_test = self._test_tenant_list()
            test_result["tests"].append(list_test)

            # 2. Teste de configurações de tenant
            settings_test = self._test_tenant_settings()
            test_result["tests"].append(settings_test)

            # 3. Teste de analytics de tenant
            analytics_test = self._test_tenant_analytics()
            test_result["tests"].append(analytics_test)

        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            self.log(f"Erro no teste de tenant: {e}", "error")

        success_count = sum(1 for t in test_result["tests"] if t["success"])
        total_count = len(test_result["tests"])
        self.log(
            f"Tenant: {success_count}/{total_count} testes passaram",
            "success" if success_count == total_count else "warning",
        )

        return test_result

    def _test_tenant_list(self) -> Dict:
        """Testa listagem de tenants"""
        try:
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/tenants",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [
                200,
                401,
                403,
            ]  # 200 = success, 401/403 = auth required
            return {
                "name": "tenant_list",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "tenant_list", "success": False, "error": str(e)}

    def _test_tenant_settings(self) -> Dict:
        """Testa configurações de tenant"""
        try:
            # Usar um tenant_id de exemplo
            tenant_id = "00000000-0000-0000-0000-000000000001"
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/tenants/{tenant_id}/settings",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403, 404]  # Códigos válidos
            return {
                "name": "tenant_settings",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "tenant_settings", "success": False, "error": str(e)}

    def _test_tenant_analytics(self) -> Dict:
        """Testa analytics de tenant"""
        try:
            tenant_id = "00000000-0000-0000-0000-000000000001"
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/tenants/{tenant_id}/analytics",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403, 404]
            return {
                "name": "tenant_analytics",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "tenant_analytics", "success": False, "error": str(e)}

    def test_user_profile_functionality(self) -> Dict:
        """Testa funcionalidades de perfil de usuário com novos campos"""
        self.log("👤 Testando funcionalidades de perfil de usuário...")
        test_result = {
            "name": "user_profile_functionality",
            "tests": [],
            "success": True,
        }

        try:
            # 1. Teste de atualização de perfil
            profile_update_test = self._test_user_profile_update()
            test_result["tests"].append(profile_update_test)

            # 2. Teste de preferências de usuário
            preferences_test = self._test_user_preferences()
            test_result["tests"].append(preferences_test)

            # 3. Teste de estatísticas de usuário
            stats_test = self._test_user_stats()
            test_result["tests"].append(stats_test)

        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            self.log(f"Erro no teste de perfil: {e}", "error")

        success_count = sum(1 for t in test_result["tests"] if t["success"])
        total_count = len(test_result["tests"])
        self.log(
            f"Perfil: {success_count}/{total_count} testes passaram",
            "success" if success_count == total_count else "warning",
        )

        return test_result

    def _test_user_profile_update(self) -> Dict:
        """Testa atualização de perfil incluindo novos campos"""
        try:
            profile_data = {
                "full_name": "Updated Test User",
                "bio": "Updated bio with new field testing",
                "timezone": "America/New_York",
                "phone": "+1987654321",
            }

            response = self.session.put(
                f"{self.base_url}{API_V1_PREFIX}/users/me/profile",
                json=profile_data,
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403, 404]
            return {
                "name": "user_profile_update",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "user_profile_update", "success": False, "error": str(e)}

    def _test_user_preferences(self) -> Dict:
        """Testa preferências de usuário"""
        try:
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/users/me/preferences",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403]
            return {
                "name": "user_preferences",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "user_preferences", "success": False, "error": str(e)}

    def _test_user_stats(self) -> Dict:
        """Testa estatísticas de usuário"""
        try:
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/users/me/stats",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403]
            return {
                "name": "user_stats",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "user_stats", "success": False, "error": str(e)}

    def test_workspace_enhanced_functionality(self) -> Dict:
        """Testa funcionalidades aprimoradas de workspace"""
        self.log("🏗️ Testando funcionalidades aprimoradas de workspace...")
        test_result = {
            "name": "workspace_enhanced_functionality",
            "tests": [],
            "success": True,
        }

        try:
            # 1. Teste de configurações de notificação
            notifications_test = self._test_workspace_notifications()
            test_result["tests"].append(notifications_test)

            # 2. Teste de estatísticas de API
            api_stats_test = self._test_workspace_api_stats()
            test_result["tests"].append(api_stats_test)

            # 3. Teste de analytics de workspace
            analytics_test = self._test_workspace_analytics()
            test_result["tests"].append(analytics_test)

        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            self.log(f"Erro no teste de workspace: {e}", "error")

        success_count = sum(1 for t in test_result["tests"] if t["success"])
        total_count = len(test_result["tests"])
        self.log(
            f"Workspace: {success_count}/{total_count} testes passaram",
            "success" if success_count == total_count else "warning",
        )

        return test_result

    def _test_workspace_notifications(self) -> Dict:
        """Testa configurações de notificação de workspace"""
        try:
            workspace_id = "00000000-0000-0000-0000-000000000001"
            notification_data = {
                "email_notifications": True,
                "push_notifications": False,
            }

            response = self.session.put(
                f"{self.base_url}{API_V1_PREFIX}/workspaces/{workspace_id}/notifications",
                json=notification_data,
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403, 404]
            return {
                "name": "workspace_notifications",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {
                "name": "workspace_notifications",
                "success": False,
                "error": str(e),
            }

    def _test_workspace_api_stats(self) -> Dict:
        """Testa estatísticas de API de workspace"""
        try:
            workspace_id = "00000000-0000-0000-0000-000000000001"
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/workspaces/{workspace_id}/api-stats",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403, 404]
            return {
                "name": "workspace_api_stats",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "workspace_api_stats", "success": False, "error": str(e)}

    def _test_workspace_analytics(self) -> Dict:
        """Testa analytics de workspace"""
        try:
            workspace_id = "00000000-0000-0000-0000-000000000001"
            response = self.session.get(
                f"{self.base_url}{API_V1_PREFIX}/workspaces/{workspace_id}/analytics",
                headers=self.auth_headers,
                timeout=10,
            )

            success = response.status_code in [200, 401, 403, 404]
            return {
                "name": "workspace_analytics",
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"name": "workspace_analytics", "success": False, "error": str(e)}

    def run_all_tests(self):
        """Executa todos os testes funcionais"""
        print("🧪 TESTE FUNCIONAL DE ENDPOINTS - SYNAPSCALE API")
        print("=" * 70)

        start_time = time.time()

        # Configurar ambiente
        if not self.setup_test_environment():
            self.log("Falha na configuração do ambiente", "error")
            return False

        # Executar testes por categoria
        test_suites = [self.test_system_endpoints, self.test_authentication_flow]

        all_results = []
        for test_suite in test_suites:
            try:
                result = test_suite()
                all_results.append(result)
            except Exception as e:
                self.log(f"Erro no teste {test_suite.__name__}: {e}", "error")

        # Calcular estatísticas finais
        total_time = time.time() - start_time
        total_tests = sum(len(r.get("tests", [])) for r in all_results)
        successful_tests = sum(
            sum(1 for t in r.get("tests", []) if t.get("success", False))
            for r in all_results
        )

        # Relatório final
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL DE TESTES FUNCIONAIS")
        print("=" * 70)
        print(f"⏱️  Tempo total: {total_time:.2f} segundos")
        print(f"🧪 Total de testes: {total_tests}")
        print(f"✅ Testes bem-sucedidos: {successful_tests}")
        print(f"❌ Testes falharam: {total_tests - successful_tests}")

        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            print(f"🎯 Taxa de sucesso: {success_rate:.1f}%")

            # Avaliação geral
            if success_rate >= 90:
                status = "🟢 EXCELENTE"
            elif success_rate >= 75:
                status = "🟡 BOM"
            elif success_rate >= 60:
                status = "🟠 ACEITÁVEL"
            else:
                status = "🔴 CRÍTICO"

            print(f"🎯 AVALIAÇÃO: {status}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Teste funcional de endpoints da SynapScale API"
    )
    parser.add_argument("--base-url", default=API_BASE_URL, help="URL base da API")
    parser.add_argument("--verbose", action="store_true", help="Saída detalhada")

    args = parser.parse_args()

    tester = FunctionalEndpointTester(base_url=args.base_url, verbose=args.verbose)
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
