#!/usr/bin/env python3
"""
Script para validar que não há mais variáveis hardcoded no projeto
"""
import os
import re
from pathlib import Path


def scan_hardcoded_vars():
    """Procura por variáveis hardcoded nos arquivos Python"""
    print("🔍 Escaneando arquivos Python em busca de variáveis hardcoded...")
    print("=" * 70)

    # Padrões a procurar
    patterns = {
        "database_url": r'postgresql://[^"\']+@[^"\']+',
        "secret_keys": r'(SECRET_KEY|JWT_SECRET_KEY)\s*=\s*["\'][^"\']{5,}["\']',
        "hardcoded_passwords": r'password\s*=\s*["\'][^"\']{3,}["\']',
    }

    # Diretórios a escanear
    scan_dirs = ["src", ".", "scripts", "migrations", "tools"]  # arquivos na raiz

    # Arquivos para ignorar (testes, templates, etc.)
    ignore_patterns = [
        "*test*",
        "*template*",
        "*example*",
        "*.md",
        "*.txt",
        "__pycache__",
        ".git",
        "verify_env_usage.py",  # este próprio arquivo
        "validate_no_hardcoded.py",  # este arquivo
    ]

    found_issues = []

    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue

        for root, dirs, files in os.walk(scan_dir):
            # Filtrar diretórios ignorados
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    d in ignore or d.startswith(".") for ignore in ignore_patterns
                )
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                # Ignorar arquivos específicos
                if any(ignore.replace("*", "") in file for ignore in ignore_patterns):
                    continue

                filepath = os.path.join(root, file)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern_name, pattern in patterns.items():
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Pular se for um comentário
                            line_start = content.rfind("\\n", 0, match.start()) + 1
                            line = content[
                                line_start : content.find("\\n", match.start())
                            ]
                            if line.strip().startswith("#"):
                                continue

                            # Pular se estiver em string de documentação
                            if '"""' in line or "'''" in line:
                                continue

                            found_issues.append(
                                {
                                    "file": filepath,
                                    "pattern": pattern_name,
                                    "match": (
                                        match.group()[:50] + "..."
                                        if len(match.group()) > 50
                                        else match.group()
                                    ),
                                    "line": line.strip(),
                                }
                            )

                except Exception as e:
                    print(f"⚠️  Erro ao ler {filepath}: {e}")

    # Relatório
    if found_issues:
        print("❌ VARIÁVEIS HARDCODED ENCONTRADAS:")
        print("-" * 70)
        for issue in found_issues:
            print(f"📁 {issue['file']}")
            print(f"   🔍 Tipo: {issue['pattern']}")
            print(f"   📄 Conteúdo: {issue['match']}")
            print(f"   📝 Linha: {issue['line']}")
            print()
    else:
        print("✅ NENHUMA VARIÁVEL HARDCODED ENCONTRADA!")
        print("🎉 Todos os arquivos estão usando variáveis do .env corretamente!")

    return len(found_issues) == 0


def check_env_file():
    """Verifica se o arquivo .env existe e está configurado"""
    print("\n📁 Verificando arquivo .env...")
    print("-" * 50)

    # Mudar para o diretório root como os outros scripts
    script_dir = os.path.dirname(__file__)
    root_dir = os.path.join(script_dir, "..", "..")
    env_path = os.path.join(root_dir, ".env")

    if not os.path.exists(env_path):
        print("❌ Arquivo .env não encontrado!")
        print("Execute: python tools/utilities/generate_secure_keys.py")
        return False

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar variáveis essenciais com valores adequados
        required_vars = {
            "DATABASE_URL": {"min_length": 20, "must_contain": "postgresql://"},
            "SECRET_KEY": {"min_length": 32, "must_contain": None},
            "JWT_SECRET_KEY": {"min_length": 32, "must_contain": None},
            "ENCRYPTION_KEY": {"min_length": 20, "must_contain": None}
        }

        missing_vars = []
        weak_vars = []
        
        for var, requirements in required_vars.items():
            # Verificar se variável existe
            if f"{var}=" not in content:
                missing_vars.append(var)
                continue
                
            # Extrair valor da variável
            for line in content.split('\n'):
                if line.startswith(f"{var}="):
                    value = line.split('=', 1)[1].strip().strip('"').strip("'")
                    
                    # Verificar comprimento mínimo
                    if len(value) < requirements["min_length"]:
                        weak_vars.append(f"{var} (muito curta: {len(value)} caracteres)")
                    
                    # Verificar conteúdo obrigatório
                    if requirements["must_contain"] and requirements["must_contain"] not in value:
                        weak_vars.append(f"{var} (formato inválido)")
                    
                    # Verificar se não é valor padrão perigoso
                    dangerous_defaults = [
                        "change-me", "your-secret", "demo-key", "test-key",
                        "GERE_UMA_CHAVE", "sua_chave", "password", "secret"
                    ]
                    if any(dangerous in value.lower() for dangerous in dangerous_defaults):
                        weak_vars.append(f"{var} (usando valor padrão perigoso)")
                    
                    break

        success = True
        
        if missing_vars:
            print(f"❌ Variáveis faltando no .env: {', '.join(missing_vars)}")
            success = False
            
        if weak_vars:
            print(f"⚠️ Variáveis com problemas: {', '.join(weak_vars)}")
            success = False
            
        if success:
            print("✅ Arquivo .env configurado corretamente!")
            
            # Verificar se o arquivo está no .gitignore
            gitignore_path = os.path.join(root_dir, ".gitignore")
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r") as f:
                    gitignore_content = f.read()
                if ".env" not in gitignore_content:
                    print("⚠️ ATENÇÃO: .env não está no .gitignore!")
                    success = False
                else:
                    print("✅ .env está protegido no .gitignore")
            
        return success

    except Exception as e:
        print(f"❌ Erro ao ler .env: {e}")
        return False


if __name__ == "__main__":
    print("🚀 VALIDAÇÃO FINAL - Verificação de Variáveis Hardcoded")
    print("=" * 70)

    no_hardcoded = scan_hardcoded_vars()
    env_ok = check_env_file()

    print("\n" + "=" * 70)
    print("🎯 RESULTADO FINAL:")
    if no_hardcoded and env_ok:
        print("✅ SUCESSO! Projeto configurado corretamente!")
        print("   - Não há variáveis hardcoded nos arquivos")
        print("   - Arquivo .env está configurado adequadamente")
        print("   - Todos os scripts usam variáveis de ambiente")
        print("   - Arquivo .env está protegido no .gitignore")
        print("\n🔒 DICAS DE SEGURANÇA:")
        print("   - Execute este script regularmente")
        print("   - Use './tools/utilities/security_scan.sh' antes de commits")
        print("   - Nunca commite arquivos .env no Git")
    else:
        print("❌ AÇÃO NECESSÁRIA!")
        if not no_hardcoded:
            print("   - Ainda há variáveis hardcoded que precisam ser corrigidas")
        if not env_ok:
            print("   - Arquivo .env precisa ser configurado adequadamente")
        print("\n🛠️ SOLUÇÕES:")
        print("   1. Execute: python tools/utilities/generate_secure_keys.py")
        print("   2. Configure as variáveis faltantes no .env") 
        print("   3. Execute novamente este script para validar")
    print("=" * 70)
