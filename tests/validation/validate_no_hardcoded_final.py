#!/usr/bin/env python3
"""
Script para validar que não há valores hardcoded no sistema
Garante que tudo vem do .env
"""

import os
import re
import glob
from typing import List, Tuple


def scan_for_hardcoded_values() -> List[Tuple[str, str, int, str]]:
    """
    Escaneia arquivos Python em busca de valores hardcoded
    Retorna lista de (arquivo, padrão, linha, conteúdo)
    """

    findings = []

    # Padrões a procurar (valores hardcoded suspeitos)
    patterns = {
        "api_keys": r"(sk-[a-zA-Z0-9-_]{20,})",  # OpenAI API keys
        "base64_keys": r"[A-Za-z0-9+/]{32,}={0,2}(?![A-Za-z0-9+/=])",  # Chaves base64 longas
        "secret_assignments": r'(SECRET_KEY|JWT_SECRET_KEY|ENCRYPTION_KEY)\s*=\s*["\'][^"\']{8,}["\']',  # Assignments diretos
        "fernet_keys": r'Fernet\(["\'][A-Za-z0-9+/=]{32,}["\']',  # Fernet com chave hardcoded
    }

    # Arquivos a ignorar (são de teste ou exemplo)
    ignore_patterns = [
        "*.example",
        "*.template",
        "**/venv/**",
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/logs/**",
        "**/temp/**",
        ".git/**",
        "validate_no_hardcoded_final.py",  # Este próprio arquivo
    ]

    # Buscar arquivos Python
    python_files = []
    for pattern in ["**/*.py", "*.py"]:
        python_files.extend(glob.glob(pattern, recursive=True))

    # Filtrar arquivos ignorados
    filtered_files = []
    for file in python_files:
        should_ignore = False
        for ignore_pattern in ignore_patterns:
            if file.endswith(".example") or file.endswith(".template"):
                should_ignore = True
                break
            if (
                "venv" in file
                or "__pycache__" in file
                or ".git" in file
                or "_temp.py" in file
            ):
                should_ignore = True
                break
        if not should_ignore:
            filtered_files.append(file)

    # Escanear cada arquivo
    for file_path in filtered_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_clean = line.strip()

                # Pular comentários e docstrings
                if (
                    line_clean.startswith("#")
                    or line_clean.startswith('"""')
                    or line_clean.startswith("'''")
                ):
                    continue

                # Verificar cada padrão
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, line)
                    if matches:
                        # Verificar se não é um caso válido
                        if is_valid_usage(line, pattern_name, file_path):
                            continue

                        findings.append(
                            (file_path, pattern_name, line_num, line.strip())
                        )

        except Exception as e:
            print(f"⚠️ Erro ao ler {file_path}: {e}")

    return findings


def is_valid_usage(line: str, pattern_name: str, file_path: str) -> bool:
    """
    Verifica se o uso é válido (não hardcoded)
    """

    # Casos válidos para chaves secretas
    if pattern_name == "secret_assignments":
        # Se está lendo do os.getenv, é válido
        if "os.getenv(" in line or "getenv(" in line:
            return True
        # Se está em arquivos de configuração usando Field(), é válido
        if "Field(" in line and (
            "config" in file_path.lower() or "settings" in file_path.lower()
        ):
            return True

    # Casos válidos para API keys
    if pattern_name == "api_keys":
        # Se é uma função que gera chave de teste baseada no ambiente
        if "generate_test" in line.lower() or "hash" in line.lower():
            return True
        # Se está em comentário ou string de exemplo
        if "#" in line or "example" in line.lower() or "test" in line.lower():
            return True

    # Casos válidos para chaves base64
    if pattern_name == "base64_keys":
        # Se está gerando a chave dinamicamente
        if (
            "generate" in line.lower()
            or "hash" in line.lower()
            or "random" in line.lower()
        ):
            return True
        # Se está em uma função de teste que gera chaves
        if "def generate" in line or "def create" in line:
            return True
        # Se é exemplo de documentação (JWT tokens de exemplo)
        if "eyJ" in line and ("example" in line.lower() or '"' in line):
            return True
        # Se é URL ou path de arquivo
        if "/" in line and ("workspaces" in line or "api" in line):
            return True
        # Se é hash MD5/SHA (32 caracteres hexadecimais)
        if re.match(r"^[a-f0-9]{32}$", line.strip('"').strip("'")):
            return True

    return False


def check_env_usage() -> List[str]:
    """
    Verifica se os arquivos estão usando corretamente as variáveis do .env
    """

    issues = []

    # Arquivos críticos que devem usar .env
    critical_files = [
        "src/synapse/models/user_variable.py",
        "src/synapse/config.py",
        "src/synapse/core/auth/jwt.py",
    ]

    for file_path in critical_files:
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Verificar se usa os.getenv para chaves importantes
            required_patterns = [
                ("ENCRYPTION_KEY", r'os\.getenv\(["\']ENCRYPTION_KEY["\']'),
                ("SECRET_KEY", r'os\.getenv\(["\']SECRET_KEY["\']'),
            ]

            for key_name, pattern in required_patterns:
                if key_name in content and not re.search(pattern, content):
                    # Verificar se está usando settings (também válido)
                    if (
                        f"settings.{key_name}" not in content
                        and f"settings.JWT_{key_name}" not in content
                    ):
                        issues.append(
                            f"{file_path}: {key_name} pode não estar usando .env corretamente"
                        )

        except Exception as e:
            issues.append(f"Erro ao verificar {file_path}: {e}")

    return issues


def main():
    """Função principal"""
    print("🔍 VALIDAÇÃO DE VALORES HARDCODED")
    print("=" * 50)

    # Escanear por valores hardcoded
    print("📝 Escaneando arquivos Python...")
    findings = scan_for_hardcoded_values()

    if findings:
        print(f"\n❌ Encontrados {len(findings)} possíveis valores hardcoded:")
        print("-" * 50)

        for file_path, pattern_name, line_num, line_content in findings:
            print(f"📁 {file_path}:{line_num}")
            print(f"🔍 Padrão: {pattern_name}")
            print(f"📝 Linha: {line_content}")
            print()
    else:
        print("✅ Nenhum valor hardcoded encontrado!")

    # Verificar uso do .env
    print("\n🔧 Verificando uso correto do .env...")
    env_issues = check_env_usage()

    if env_issues:
        print(f"\n⚠️ Encontrados {len(env_issues)} problemas no uso do .env:")
        for issue in env_issues:
            print(f"  • {issue}")
    else:
        print("✅ Uso do .env está correto!")

    # Resultado final
    total_issues = len(findings) + len(env_issues)

    print("\n" + "=" * 50)
    if total_issues == 0:
        print("🎉 VALIDAÇÃO PASSOU! Nenhum valor hardcoded encontrado.")
        print("✅ Todos os valores vêm do .env conforme esperado.")
        return True
    else:
        print(f"❌ VALIDAÇÃO FALHOU! {total_issues} problemas encontrados.")
        print("🔧 Corrija os problemas antes de prosseguir.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
