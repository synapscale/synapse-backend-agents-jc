#!/usr/bin/env python3
"""
Wrapper para executar scripts com ambiente virtual e configuração correta
Simula o ambiente do dev.sh para os scripts das tools
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Configura o ambiente exatamente como no dev.sh"""
    root_dir = Path(__file__).parent.parent.parent
    
    # Verificar se venv existe
    if os.name == "nt":
        venv_python = root_dir / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = root_dir / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Ambiente virtual não encontrado. Execute primeiro: python3.11 -m venv venv")
        return None, None
    
    # Configurar variáveis de ambiente exatamente como no dev.sh
    env = os.environ.copy()
    env["PYTHONPATH"] = "./src"  # Exatamente como no dev.sh
    
    return str(venv_python), env

def run_script(script_path, *args):
    """Executa script com ambiente configurado"""
    venv_python, env = setup_environment()
    if not venv_python:
        return False
    
    try:
        result = subprocess.run(
            [venv_python, script_path] + list(args),
            env=env,
            cwd=Path(__file__).parent.parent.parent
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar {script_path}: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python run_with_venv.py <script.py> [args...]")
        print("\nExemplos:")
        print("  python run_with_venv.py generate_test_token.py")
        print("  python run_with_venv.py verify_env_usage.py")
        return False
    
    script_name = sys.argv[1]
    script_args = sys.argv[2:]
    
    # Resolver caminho do script
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name
    
    if not script_path.exists():
        print(f"❌ Script não encontrado: {script_path}")
        return False
    
    print(f"🚀 Executando {script_name} com ambiente virtual...")
    success = run_script(str(script_path), *script_args)
    
    if success:
        print("✅ Script executado com sucesso!")
    else:
        print("❌ Script falhou!")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
