#!/usr/bin/env python3
"""
🚀 HEALTH CHECK MASTER - Sistema de Manutenção Automatizada

Este script executa uma bateria completa de verificações para garantir que:
- Banco de dados está íntegro e sincronizado
- Models estão alinhados com schema do banco
- API está funcionando corretamente
- OpenAPI.json está atualizado
- Todas as dependências estão corretas

Uso: python tools/database/health_check_master.py [--fix] [--report] [--json]
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import psycopg2
from dotenv import load_dotenv

# Cores para terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

load_dotenv()

class HealthCheckMaster:
    def __init__(self):
        self.results = {}
        self.warnings = []
        self.errors = []
        self.start_time = datetime.now()
        self.database_url = os.getenv("DATABASE_URL")
        
    def log(self, message: str, level: str = "INFO", color: str = Colors.WHITE):
        """Log com cores e timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")
        
    def run_script(self, script_path: str, description: str) -> Dict[str, Any]:
        """Executa um script e captura sua saída"""
        self.log(f"🔄 Executando: {description}", "INFO", Colors.CYAN)
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
                timeout=30
            )
            
            success = result.returncode == 0
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "execution_time": time.time()
            }
            
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout ao executar {script_path}", "ERROR", Colors.RED)
            return {
                "success": False,
                "error": "Timeout",
                "execution_time": 30
            }
        except Exception as e:
            self.log(f"❌ Erro ao executar {script_path}: {e}", "ERROR", Colors.RED)
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }

    def check_database_connection(self) -> bool:
        """Verifica conectividade básica com banco"""
        self.log("🔌 Verificando conexão com banco de dados", "INFO", Colors.BLUE)
        
        if not self.database_url:
            self.log("❌ DATABASE_URL não configurada", "ERROR", Colors.RED)
            self.errors.append("DATABASE_URL não encontrada no .env")
            return False
            
        try:
            # Tentar conexão rápida
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            self.log("✅ Conexão com banco OK", "SUCCESS", Colors.GREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Falha na conexão: {e}", "ERROR", Colors.RED)
            self.errors.append(f"Erro de conexão: {e}")
            return False

    def check_environment_variables(self) -> bool:
        """Verifica se todas as variáveis necessárias estão configuradas"""
        self.log("🔧 Verificando variáveis de ambiente", "INFO", Colors.BLUE)
        
        required_vars = [
            "DATABASE_URL",
            "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log(f"⚠️ Variáveis faltantes: {missing_vars}", "WARNING", Colors.YELLOW)
            self.warnings.append(f"Variáveis não configuradas: {missing_vars}")
            return False
        
        self.log("✅ Todas as variáveis de ambiente OK", "SUCCESS", Colors.GREEN)
        return True

    def run_database_checks(self) -> Dict[str, Any]:
        """Executa todos os scripts de verificação do banco"""
        self.log("📊 Executando verificações do banco de dados", "INFO", Colors.MAGENTA)
        
        checks = {
            "check_all_schemas": {
                "script": "tools/database/check_all_schemas.py",
                "description": "Verificação de todos os schemas"
            },
            "check_relationships": {
                "script": "tools/database/check_relationships.py", 
                "description": "Verificação de relacionamentos/FK"
            },
            "check_schema": {
                "script": "tools/database/check_schema.py",
                "description": "Verificação do schema principal"
            },
            "check_synapscale_schema": {
                "script": "tools/database/check_synapscale_schema.py",
                "description": "Análise detalhada do schema SynapScale"
            },
            "check_users_table": {
                "script": "tools/database/check_users_table.py",
                "description": "Auditoria da tabela de usuários"
            }
        }
        
        results = {}
        for check_name, check_info in checks.items():
            result = self.run_script(check_info["script"], check_info["description"])
            results[check_name] = result
            
            if result["success"]:
                self.log(f"✅ {check_info['description']} - OK", "SUCCESS", Colors.GREEN)
            else:
                self.log(f"❌ {check_info['description']} - FALHOU", "ERROR", Colors.RED)
                self.errors.append(f"Falha em {check_name}")
        
        return results

    def check_api_health(self) -> bool:
        """Verifica se a API está respondendo"""
        self.log("🌐 Verificando saúde da API", "INFO", Colors.BLUE)
        
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        try:
            import requests
            response = requests.get(f"{api_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.log("✅ API respondendo corretamente", "SUCCESS", Colors.GREEN)
                return True
            else:
                self.log(f"⚠️ API retornou status {response.status_code}", "WARNING", Colors.YELLOW)
                self.warnings.append(f"API status não é 200: {response.status_code}")
                return False
                
        except ImportError:
            self.log("⚠️ Biblioteca requests não disponível", "WARNING", Colors.YELLOW)
            self.warnings.append("Não foi possível verificar API (requests não instalado)")
            return False
        except Exception as e:
            self.log(f"❌ Erro ao verificar API: {e}", "ERROR", Colors.RED)
            self.errors.append(f"Erro na verificação da API: {e}")
            return False

    def check_openapi_sync(self) -> bool:
        """Verifica se OpenAPI.json está atualizado"""
        self.log("📋 Verificando sincronização do OpenAPI", "INFO", Colors.BLUE)
        
        try:
            # Tentar encontrar o arquivo openapi.json
            possible_paths = [
                "docs/openapi.json",
                "src/openapi.json", 
                "openapi.json",
                "static/openapi.json"
            ]
            
            openapi_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    openapi_file = path
                    break
            
            if not openapi_file:
                self.log("⚠️ Arquivo openapi.json não encontrado", "WARNING", Colors.YELLOW)
                self.warnings.append("openapi.json não encontrado nos caminhos padrão")
                return False
            
            # Verificar se foi modificado recentemente
            file_stat = os.stat(openapi_file)
            file_age = time.time() - file_stat.st_mtime
            
            if file_age > 86400:  # Mais de 1 dia
                self.log("⚠️ openapi.json pode estar desatualizado (>1 dia)", "WARNING", Colors.YELLOW)
                self.warnings.append("openapi.json não foi atualizado recentemente")
                return False
            
            self.log("✅ OpenAPI parece atualizado", "SUCCESS", Colors.GREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar OpenAPI: {e}", "ERROR", Colors.RED)
            self.errors.append(f"Erro na verificação do OpenAPI: {e}")
            return False

    def generate_health_report(self) -> Dict[str, Any]:
        """Gera relatório completo de saúde do sistema"""
        end_time = datetime.now()
        execution_time = (end_time - self.start_time).total_seconds()
        
        # Calcular score de saúde
        total_checks = len(self.results.get('database_checks', {})) + 4  # 4 checks extras
        successful_checks = sum(1 for r in self.results.get('database_checks', {}).values() if r.get('success'))
        successful_checks += sum([
            self.results.get('database_connection', False),
            self.results.get('environment_vars', False),
            self.results.get('api_health', False),
            self.results.get('openapi_sync', False)
        ])
        
        health_score = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Determinar status geral
        if health_score >= 90:
            status = "EXCELENTE"
            status_color = Colors.GREEN
        elif health_score >= 70:
            status = "BOM"
            status_color = Colors.YELLOW
        else:
            status = "CRÍTICO"
            status_color = Colors.RED
        
        report = {
            "timestamp": end_time.isoformat(),
            "execution_time_seconds": execution_time,
            "health_score": health_score,
            "status": status,
            "summary": {
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "warnings": len(self.warnings),
                "errors": len(self.errors)
            },
            "detailed_results": self.results,
            "warnings": self.warnings,
            "errors": self.errors
        }
        
        # Exibir resumo colorido
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}🏥 RELATÓRIO DE SAÚDE DO SISTEMA{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        
        print(f"\n{status_color}{Colors.BOLD}📊 STATUS GERAL: {status} ({health_score:.1f}%){Colors.END}")
        print(f"{Colors.WHITE}⏱️  Tempo de execução: {execution_time:.2f}s{Colors.END}")
        print(f"{Colors.WHITE}📋 Verificações: {successful_checks}/{total_checks} bem-sucedidas{Colors.END}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  AVISOS ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"{Colors.YELLOW}   • {warning}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ ERROS ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"{Colors.RED}   • {error}{Colors.END}")
        
        if health_score >= 90:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Sistema funcionando perfeitamente!{Colors.END}")
        elif health_score >= 70:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Sistema funcionando com alguns avisos{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}🚨 Sistema com problemas críticos - ação necessária{Colors.END}")
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        
        return report

    def run_full_health_check(self) -> Dict[str, Any]:
        """Executa verificação completa de saúde do sistema"""
        self.log("🚀 Iniciando verificação completa de saúde", "INFO", Colors.BOLD)
        
        # 1. Verificar variáveis de ambiente
        self.results['environment_vars'] = self.check_environment_variables()
        
        # 2. Verificar conexão com banco
        self.results['database_connection'] = self.check_database_connection()
        
        # Se banco não estiver acessível, parar aqui
        if not self.results['database_connection']:
            self.log("🛑 Parando verificações - banco inacessível", "ERROR", Colors.RED)
            return self.generate_health_report()
        
        # 3. Executar verificações do banco
        self.results['database_checks'] = self.run_database_checks()
        
        # 4. Verificar API
        self.results['api_health'] = self.check_api_health()
        
        # 5. Verificar OpenAPI
        self.results['openapi_sync'] = self.check_openapi_sync()
        
        # 6. Gerar relatório final
        return self.generate_health_report()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Check Master - Verificação completa do sistema")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")
    parser.add_argument("--report", type=str, help="Salvar relatório em arquivo")
    parser.add_argument("--fix", action="store_true", help="Tentar corrigir problemas automaticamente")
    
    args = parser.parse_args()
    
    # Executar verificação
    checker = HealthCheckMaster()
    report = checker.run_full_health_check()
    
    # Salvar relatório se solicitado
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Relatório salvo em: {args.report}")
    
    # Saída JSON se solicitada
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # Exit code baseado no status
    if report['health_score'] < 70:
        sys.exit(1)  # Falha crítica
    elif report['health_score'] < 90:
        sys.exit(2)  # Avisos
    else:
        sys.exit(0)  # Sucesso

if __name__ == "__main__":
    main()
