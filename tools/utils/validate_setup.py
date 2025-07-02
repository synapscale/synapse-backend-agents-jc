#!/usr/bin/env python3
"""
Validador Final do SynapScale Backend
Verifica se toda a configuração está correta e funcionando
"""

import os
import sys
import subprocess
import requests
import time
import signal
from pathlib import Path
from typing import List, Tuple, Optional


class SynapScaleValidator:
    def __init__(self):
        self.root_path = Path.cwd()
        self.errors = []
        self.warnings = []

    def print_header(self):
        print("=" * 60)
        print("🔍 SYNAPSCALE BACKEND - VALIDAÇÃO FINAL")
        print("=" * 60)
        print("Verificando se tudo está configurado corretamente...")
        print("=" * 60)

    def check_files_exist(self) -> bool:
        """Verifica se arquivos essenciais existem"""
        print("\n📁 Verificando arquivos essenciais...")

        required_files = [
            ".env",
            "requirements.txt",
            "src/synapse/main.py",
            "alembic.ini",
            "venv",
            "start_dev_auto.sh",
            "start_prod_auto.sh",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.root_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.errors.append(f"Arquivos não encontrados: {', '.join(missing_files)}")
            print(f"❌ Arquivos não encontrados: {', '.join(missing_files)}")
            return False
        else:
            print("✅ Todos os arquivos essenciais encontrados")
            return True

    def check_env_variables(self) -> bool:
        """Verifica variáveis de ambiente críticas"""
        print("\n🔑 Verificando variáveis de ambiente...")

        env_file = self.root_path / ".env"
        if not env_file.exists():
            self.errors.append("Arquivo .env não encontrado")
            print("❌ Arquivo .env não encontrado")
            return False

        # Carregar variáveis do .env
        env_vars = {}
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

        # Verificar variáveis críticas
        critical_vars = {
            "SECRET_KEY": "Chave secreta principal",
            "JWT_SECRET_KEY": "Chave JWT",
            "ENCRYPTION_KEY": "Chave de criptografia",
        }

        missing_critical = []
        for var, desc in critical_vars.items():
            if not env_vars.get(var) or len(env_vars.get(var, "")) < 10:
                missing_critical.append(f"{var} ({desc})")

        if missing_critical:
            self.errors.append(
                f"Variáveis críticas não configuradas: {', '.join(missing_critical)}"
            )
            print(
                f"❌ Variáveis críticas não configuradas: {', '.join(missing_critical)}"
            )
            return False

        # Verificar DATABASE_URL
        database_url = env_vars.get("DATABASE_URL", "")
        if not database_url or "postgresql" not in database_url:
            self.warnings.append("DATABASE_URL não configurada ou não é PostgreSQL")
            print("⚠️ DATABASE_URL não configurada corretamente")
        else:
            print("✅ DATABASE_URL configurada")

        print("✅ Variáveis críticas configuradas")
        return True

    def check_virtual_environment(self) -> bool:
        """Verifica ambiente virtual"""
        print("\n🐍 Verificando ambiente virtual...")

        venv_path = self.root_path / "venv"
        if not venv_path.exists():
            self.errors.append("Ambiente virtual não encontrado")
            print("❌ Ambiente virtual não encontrado")
            return False

        # Verificar executável Python no venv
        if os.name == "nt":  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            python_exe = venv_path / "bin" / "python"

        if not python_exe.exists():
            self.errors.append("Executável Python não encontrado no ambiente virtual")
            print("❌ Executável Python não encontrado no venv")
            return False

        print("✅ Ambiente virtual configurado")
        return True

    def check_dependencies(self) -> bool:
        """Verifica dependências Python"""
        print("\n📦 Verificando dependências...")

        # Ativar venv e verificar dependências
        if os.name == "nt":
            python_exe = self.root_path / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.root_path / "venv" / "bin" / "python"

        critical_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "alembic",
            "python-dotenv",
        ]
        
        # Verificar drivers PostgreSQL (opcional)
        postgres_packages = ["psycopg2", "psycopg", "psycopg2-binary"]

        missing_packages = []
        for package in critical_packages:
            try:
                result = subprocess.run(
                    [str(python_exe), "-c", f"import {package.replace('-', '_')}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    missing_packages.append(package)
            except Exception:
                missing_packages.append(package)

        # Verificar PostgreSQL driver (pelo menos um deve estar disponível)
        postgres_available = False
        for pg_package in postgres_packages:
            try:
                result = subprocess.run(
                    [str(python_exe), "-c", f"import {pg_package.replace('-', '_')}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    postgres_available = True
                    print(f"✅ Driver PostgreSQL encontrado: {pg_package}")
                    break
            except Exception:
                continue

        if not postgres_available:
            self.warnings.append("Nenhum driver PostgreSQL encontrado (psycopg2, psycopg)")
            print("⚠️ Nenhum driver PostgreSQL encontrado")

        if missing_packages:
            self.errors.append(f"Pacotes não instalados: {', '.join(missing_packages)}")
            print(f"❌ Pacotes não instalados: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ Dependências críticas instaladas")
            return True

    def check_import_main(self) -> bool:
        """Verifica se consegue importar a aplicação principal"""
        print("\n🔄 Testando importação da aplicação...")

        if os.name == "nt":
            python_exe = self.root_path / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.root_path / "venv" / "bin" / "python"

        # Script de teste exatamente como no dev.sh
        test_script = """
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Configurar PYTHONPATH exatamente como no dev.sh
root_dir = Path.cwd()
os.environ['PYTHONPATH'] = './src'
sys.path.insert(0, str(root_dir / 'src'))

# Carregar .env exatamente como no dev.sh
load_dotenv('.env')

try:
    # Importar exatamente como no dev.sh: from synapse.main import app
    from synapse.main import app
    print("✅ Import OK")
except Exception as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [str(python_exe), "-c", test_script],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root_path,
            )

            if result.returncode == 0:
                print("✅ Aplicação importada com sucesso")
                return True
            else:
                self.errors.append(f"Erro na importação: {result.stderr}")
                print(f"❌ Erro na importação: {result.stderr}")
                return False

        except Exception as e:
            self.errors.append(f"Erro na importação: {e}")
            print(f"❌ Erro na importação: {e}")
            return False

    def check_server_startup(self) -> bool:
        """Testa se o servidor consegue iniciar"""
        print("\n🚀 Testando inicialização do servidor...")

        if os.name == "nt":
            python_exe = self.root_path / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.root_path / "venv" / "bin" / "python"

        # Iniciar servidor exatamente como no dev.sh
        try:
            # Configurar ambiente exatamente como no dev.sh
            env = os.environ.copy()
            env["PYTHONPATH"] = "./src"  # Exatamente como no dev.sh
            
            process = subprocess.Popen(
                [
                    str(python_exe),
                    "-m",
                    "uvicorn",
                    "src.synapse.main:app",  # Exatamente como no dev.sh
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8001",
                ],
                cwd=self.root_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Aguardar servidor inicializar
            time.sleep(5)

            # Testar endpoint de health
            try:
                response = requests.get("http://127.0.0.1:8001/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Servidor iniciou e respondeu corretamente")
                    result = True
                else:
                    print(f"❌ Servidor respondeu com status {response.status_code}")
                    result = False
            except requests.RequestException as e:
                print(f"❌ Erro ao conectar ao servidor: {e}")
                result = False

            # Parar servidor
            process.terminate()
            process.wait(timeout=5)

            return result

        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False

    def check_database_connection(self) -> bool:
        """Testa conexão com banco de dados"""
        print("\n🗄️ Testando conexão com banco de dados...")

        if os.name == "nt":
            python_exe = self.root_path / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.root_path / "venv" / "bin" / "python"

        test_script = """
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Configurar exatamente como no dev.sh
root_dir = Path.cwd()
os.environ['PYTHONPATH'] = './src'
sys.path.insert(0, str(root_dir / 'src'))

# Carregar .env exatamente como no dev.sh
load_dotenv('.env')
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL não configurada")
    sys.exit(1)

try:
    # Usar configuração das settings do projeto
    from synapse.core.config import settings
    
    # Verificar se as configurações básicas estão corretas
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        print("⚠️ SECRET_KEY não configurada adequadamente")
    
    # Testar conexão com SQLAlchemy
    engine = create_engine(database_url, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Conexão com banco OK")
        
        # Verificar se tabelas principais existem
        try:
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' LIMIT 5"))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"✅ Tabelas encontradas: {', '.join(tables[:3])}...")
            else:
                print("⚠️ Nenhuma tabela encontrada - execute migrações")
        except Exception:
            print("⚠️ Não foi possível verificar tabelas")
            
except Exception as e:
    print(f"⚠️ Erro de conexão: {e}")
    print("(Normal se o banco ainda não estiver configurado)")
"""

        try:
            result = subprocess.run(
                [str(python_exe), "-c", test_script],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=self.root_path,
            )

            print(result.stdout.strip())
            return "✅" in result.stdout

        except Exception as e:
            print(f"⚠️ Erro ao testar banco: {e}")
            return False

    def run_validation(self) -> bool:
        """Executa validação completa"""
        self.print_header()

        checks = [
            ("Arquivos essenciais", self.check_files_exist),
            ("Variáveis de ambiente", self.check_env_variables),
            ("Ambiente virtual", self.check_virtual_environment),
            ("Dependências", self.check_dependencies),
            ("Importação da aplicação", self.check_import_main),
            ("Inicialização do servidor", self.check_server_startup),
            ("Conexão com banco", self.check_database_connection),
        ]

        passed_checks = 0
        total_checks = len(checks)

        for check_name, check_func in checks:
            try:
                if check_func():
                    passed_checks += 1
            except Exception as e:
                self.errors.append(f"Erro em '{check_name}': {e}")
                print(f"❌ Erro em '{check_name}': {e}")

        # Resultado final
        print("\n" + "=" * 60)
        print("📊 RESULTADO DA VALIDAÇÃO")
        print("=" * 60)

        success_rate = (passed_checks / total_checks) * 100
        print(
            f"✅ Testes passaram: {passed_checks}/{total_checks} ({success_rate:.1f}%)"
        )

        if self.errors:
            print(f"\n❌ ERROS ENCONTRADOS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")

        if self.warnings:
            print(f"\n⚠️ AVISOS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        if success_rate >= 85:
            print("\n🎉 CONFIGURAÇÃO APROVADA!")
            print("O backend está pronto para uso!")
            if self.warnings:
                print("Configure os itens com aviso para funcionalidade completa.")
        elif success_rate >= 70:
            print("\n⚠️ CONFIGURAÇÃO PARCIAL")
            print("O backend pode funcionar, mas há problemas a resolver.")
        else:
            print("\n❌ CONFIGURAÇÃO FALHADA")
            print("Resolva os erros antes de usar o backend.")

        print("=" * 60)

        return success_rate >= 85


if __name__ == "__main__":
    validator = SynapScaleValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)
