#!/usr/bin/env python3
"""
Script para executar testes do SynapScale Backend
Suporta diferentes tipos de testes e configurações
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def run_command(cmd, description=""):
    """Executa um comando e imprime a saída em tempo real."""
    print(f"\n🔄 {description}")
    print(f"Executando: {' '.join(cmd)}")

    # Usar Popen para transmitir saída ao vivo
    try:
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Ler linhas conforme são emitidas
        for line in process.stdout:
            print(line, end="")

        process.wait()

        if process.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Falhou (código {process.returncode})")
            return False

    except Exception as e:
        print(f"❌ Erro ao executar {description}: {e}")
        return False

def install_dependencies():
    """Instala dependências necessárias"""
    print("📦 Instalando dependências...")
    
    commands = [
        (["pip", "install", "-r", "requirements.txt"], "Instalando requirements.txt"),
        (["pip", "install", "pytest-timeout"], "Instalando pytest-timeout"),
        (["pip", "install", "pytest-xdist"], "Instalando pytest-xdist para testes paralelos")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"⚠️ Falha ao instalar dependências: {desc}")
            return False
    
    return True

def run_unit_tests():
    """Executa testes unitários"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "unit",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Executando testes unitários")

def run_integration_tests():
    """Executa testes de integração"""
    cmd = [
        "python", "-m", "pytest",
        "tests/test_llm_integration.py",
        "-m", "integration",
        "--tb=short",
        "-v",
        "--timeout=60"
    ]
    return run_command(cmd, "Executando testes de integração")

def run_llm_tests():
    """Executa testes específicos de LLM"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "llm",
        "--tb=short",
        "-v",
        "--timeout=120"
    ]
    return run_command(cmd, "Executando testes de LLM")

def run_metrics_tests():
    """Executa testes de métricas"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "metrics",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Executando testes de métricas")

def run_all_tests():
    """Executa todos os testes"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--tb=short",
        "-v",
        "--cov=src/synapse",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--maxfail=5",
        "--timeout=300"
    ]
    return run_command(cmd, "Executando todos os testes")

def run_fast_tests():
    """Executa apenas testes rápidos"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "not slow",
        "--tb=short",
        "-v",
        "--maxfail=3"
    ]
    return run_command(cmd, "Executando testes rápidos")

def run_parallel_tests():
    """Executa testes em paralelo"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-n", "auto",  # Usa todos os cores disponíveis
        "--tb=short",
        "-v",
        "--maxfail=5"
    ]
    return run_command(cmd, "Executando testes em paralelo")

def generate_coverage_report():
    """Gera relatório de cobertura"""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=src/synapse",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
        "--cov-fail-under=70"
    ]
    success = run_command(cmd, "Gerando relatório de cobertura")
    
    if success:
        print(f"\n📊 Relatório de cobertura gerado:")
        print(f"   - HTML: {project_root}/htmlcov/index.html")
        print(f"   - XML: {project_root}/coverage.xml")
    
    return success

def setup_test_environment():
    """Configura ambiente de teste"""
    print("🔧 Configurando ambiente de teste...")
    env_test_path = project_root / ".env.test"
    if not env_test_path.exists():
        print("❌ Arquivo .env.test não encontrado. Copie de .env.example e configure antes de rodar os testes.")
        sys.exit(1)
    os.makedirs(project_root / "logs", exist_ok=True)
    os.makedirs(project_root / "htmlcov", exist_ok=True)
    print("✅ Ambiente de teste configurado")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes do SynapScale Backend")
    parser.add_argument("--type", choices=[
        "unit", "integration", "llm", "metrics", "all", "fast", "parallel", "coverage"
    ], default="all", help="Tipo de teste a executar")
    parser.add_argument("--install", action="store_true", help="Instalar dependências antes dos testes")
    parser.add_argument("--setup", action="store_true", help="Configurar ambiente de teste")
    parser.add_argument("--no-cov", action="store_true", help="Executar sem cobertura de código")
    
    args = parser.parse_args()
    
    print("🧪 SynapScale Backend - Executor de Testes")
    print("=" * 50)
    
    # Configurar ambiente se solicitado
    if args.setup:
        setup_test_environment()
    
    # Instalar dependências se solicitado
    if args.install:
        if not install_dependencies():
            print("❌ Falha ao instalar dependências")
            sys.exit(1)
    
    # Executar testes baseado no tipo
    success = False
    
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "llm":
        success = run_llm_tests()
    elif args.type == "metrics":
        success = run_metrics_tests()
    elif args.type == "fast":
        success = run_fast_tests()
    elif args.type == "parallel":
        success = run_parallel_tests()
    elif args.type == "coverage":
        success = generate_coverage_report()
    else:  # all
        success = run_all_tests()
    
    # Resultado final
    if success:
        print("\n🎉 Todos os testes passaram!")
        print("📊 Verifique o relatório de cobertura em htmlcov/index.html")
    else:
        print("\n❌ Alguns testes falharam")
        sys.exit(1)

if __name__ == "__main__":
    main() 