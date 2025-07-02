#!/usr/bin/env python3
"""
Configurador Inteligente de Variáveis de Ambiente
Lê o .env e propaga automaticamente para todos os arquivos que precisam
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class EnvPropagator:
    def __init__(self):
        self.root_path = Path.cwd()
        self.env_file = self.root_path / ".env"
        self.env_vars = {}

    def load_env_vars(self) -> Dict[str, str]:
        """Carrega variáveis do arquivo .env"""
        print("📖 Carregando variáveis do .env...")

        if not self.env_file.exists():
            print("❌ Arquivo .env não encontrado!")
            return {}

        env_vars = {}
        with open(self.env_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    try:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Remover aspas se existirem
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        env_vars[key] = value
                    except Exception as e:
                        print(f"⚠️ Erro na linha {line_num}: {e}")

        print(f"✅ {len(env_vars)} variáveis carregadas")
        return env_vars

    def update_alembic_env(self, env_vars: Dict[str, str]):
        """Atualiza configuração do Alembic"""
        print("🔄 Atualizando Alembic...")

        alembic_env = self.root_path / "alembic" / "env.py"
        if not alembic_env.exists():
            print("⚠️ alembic/env.py não encontrado")
            return

        try:
            with open(alembic_env, "r", encoding="utf-8") as f:
                content = f.read()

            # Atualizar DATABASE_URL
            if "DATABASE_URL" in env_vars:
                database_url = env_vars["DATABASE_URL"]

                # Padrão para substituir
                patterns = [
                    r'config\.set_main_option\("sqlalchemy\.url",.*?\)',
                    r"sqlalchemy\.url\s*=.*",
                    r"url\s*=.*config\.get_main_option.*",
                ]

                replacement = (
                    f'config.set_main_option("sqlalchemy.url", "{database_url}")'
                )

                updated = False
                for pattern in patterns:
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        updated = True
                        break

                if not updated:
                    # Adicionar configuração se não existir
                    if "from dotenv import load_dotenv" not in content:
                        content = "from dotenv import load_dotenv\n" + content

                    if "load_dotenv()" not in content:
                        # Encontrar local apropriado para adicionar
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if "config = context.config" in line:
                                lines.insert(i + 1, "load_dotenv()")
                                lines.insert(
                                    i + 2,
                                    f'config.set_main_option("sqlalchemy.url", "{database_url}")',
                                )
                                content = "\n".join(lines)
                                break

                with open(alembic_env, "w", encoding="utf-8") as f:
                    f.write(content)

                print("✅ Alembic atualizado")

        except Exception as e:
            print(f"❌ Erro ao atualizar Alembic: {e}")

    def update_config_files(self, env_vars: Dict[str, str]):
        """Atualiza arquivos de configuração Python"""
        print("🔄 Atualizando arquivos de configuração...")

        config_files = [
            "src/synapse/config.py",
            "src/synapse/core/config.py",
            "src/synapse/settings.py",
        ]

        for config_file in config_files:
            config_path = self.root_path / config_file
            if config_path.exists():
                self._update_python_config(config_path, env_vars)

    def _update_python_config(self, config_path: Path, env_vars: Dict[str, str]):
        """Atualiza arquivo de configuração Python específico"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Verificar se já tem load_dotenv
            if "from dotenv import load_dotenv" not in content:
                # Adicionar import
                lines = content.split("\n")
                import_inserted = False
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        continue
                    else:
                        lines.insert(i, "from dotenv import load_dotenv")
                        import_inserted = True
                        break

                if import_inserted:
                    content = "\n".join(lines)

            # Verificar se já tem load_dotenv()
            if "load_dotenv()" not in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "class Settings" in line or "settings = " in line:
                        lines.insert(i, "load_dotenv()")
                        lines.insert(i, "")
                        content = "\n".join(lines)
                        break

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ {config_path.name} atualizado")

        except Exception as e:
            print(f"❌ Erro ao atualizar {config_path}: {e}")

    def update_docker_compose(self, env_vars: Dict[str, str]):
        """Atualiza docker-compose.yml"""
        print("🔄 Atualizando Docker Compose...")

        docker_compose = self.root_path / "docker-compose.yml"
        if not docker_compose.exists():
            print("⚠️ docker-compose.yml não encontrado")
            return

        try:
            with open(docker_compose, "r", encoding="utf-8") as f:
                content = f.read()

            # Substituir variáveis de ambiente
            for key, value in env_vars.items():
                # Padrões de substituição
                patterns = [f"{key}:.*", f"- {key}=.*", f"{key}=.*"]

                for pattern in patterns:
                    if re.search(pattern, content):
                        replacement = (
                            f"{key}: {value}" if ":" in pattern else f"{key}={value}"
                        )
                        content = re.sub(pattern, replacement, content)

            with open(docker_compose, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ Docker Compose atualizado")

        except Exception as e:
            print(f"❌ Erro ao atualizar Docker Compose: {e}")

    def update_render_yaml(self, env_vars: Dict[str, str]):
        """Atualiza render.yaml"""
        print("🔄 Atualizando Render config...")

        render_yaml = self.root_path / "render.yaml"
        if not render_yaml.exists():
            print("⚠️ render.yaml não encontrado")
            return

        try:
            with open(render_yaml, "r", encoding="utf-8") as f:
                content = f.read()

            # Adicionar env vars na seção apropriada
            env_section = "  envVars:\n"
            for key, value in env_vars.items():
                if key not in ["DATABASE_URL"]:  # Não incluir variáveis sensíveis
                    env_section += f"    - key: {key}\n      value: {value}\n"

            # Procurar onde inserir
            if "envVars:" in content:
                # Substituir seção existente
                content = re.sub(
                    r"envVars:.*?(?=\n[a-zA-Z]|\n$)",
                    env_section.rstrip(),
                    content,
                    flags=re.DOTALL,
                )
            else:
                # Adicionar nova seção
                content += "\n" + env_section

            with open(render_yaml, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ Render config atualizado")

        except Exception as e:
            print(f"❌ Erro ao atualizar Render config: {e}")

    def create_env_loader_script(self, env_vars: Dict[str, str]):
        """Cria script para carregar variáveis de ambiente"""
        print("🔄 Criando script de carregamento...")

        script_content = f'''#!/usr/bin/env python3
"""
Auto-gerado: Script de carregamento de variáveis de ambiente
Carrega automaticamente todas as variáveis do .env
"""

import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Variáveis de ambiente configuradas
ENV_VARS = {{
{chr(10).join(f'    "{key}": os.getenv("{key}", "{value}"),' for key, value in env_vars.items())}
}}

def get_env_var(key: str, default: str = ""):
    """Obtém variável de ambiente com fallback"""
    return os.getenv(key, ENV_VARS.get(key, default))

def validate_env_vars():
    """Valida se variáveis críticas estão configuradas"""
    critical_vars = ["SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL"]
    missing = [var for var in critical_vars if not get_env_var(var)]
    
    if missing:
        raise ValueError(f"Variáveis críticas não configuradas: {{', '.join(missing)}}")
        
    return True

# Exportar configurações
__all__ = ["ENV_VARS", "get_env_var", "validate_env_vars"]
'''

        with open("env_loader.py", "w", encoding="utf-8") as f:
            f.write(script_content)

        print("✅ Script de carregamento criado")

    def update_startup_scripts(self, env_vars: Dict[str, str]):
        """Atualiza scripts de inicialização existentes"""
        print("🔄 Atualizando scripts de inicialização...")

        scripts = [
            "start.sh",
            "start_dev.sh",
            "start_production.sh",
            "start_backend.sh",
            "start_render.sh",
        ]

        for script_name in scripts:
            script_path = self.root_path / script_name
            if script_path.exists():
                try:
                    with open(script_path, "r") as f:
                        content = f.read()

                    # Adicionar carregamento de .env se não existir
                    if "set -a" not in content and "source .env" not in content:
                        lines = content.split("\n")
                        # Encontrar local após shebang
                        insert_pos = 1 if lines[0].startswith("#!") else 0

                        lines.insert(insert_pos, "set -a  # Export all variables")
                        lines.insert(insert_pos + 1, "[ -f .env ] && source .env")
                        lines.insert(insert_pos + 2, "set +a  # Stop exporting")
                        lines.insert(insert_pos + 3, "")

                        with open(script_path, "w") as f:
                            f.write("\n".join(lines))

                    print(f"✅ {script_name} atualizado")

                except Exception as e:
                    print(f"❌ Erro ao atualizar {script_name}: {e}")

    def run_propagation(self):
        """Executa propagação completa"""
        print("🔄 PROPAGAÇÃO AUTOMÁTICA DE VARIÁVEIS")
        print("=" * 50)

        # Carregar variáveis
        env_vars = self.load_env_vars()
        if not env_vars:
            return False

        # Atualizar todos os arquivos
        self.update_alembic_env(env_vars)
        self.update_config_files(env_vars)
        self.update_docker_compose(env_vars)
        self.update_render_yaml(env_vars)
        self.create_env_loader_script(env_vars)
        self.update_startup_scripts(env_vars)

        print("\n✅ PROPAGAÇÃO COMPLETA!")
        print("=" * 50)
        print("📋 Arquivos atualizados automaticamente:")
        print("   - alembic/env.py")
        print("   - src/synapse/config.py")
        print("   - docker-compose.yml")
        print("   - render.yaml")
        print("   - Scripts de inicialização")
        print("   - env_loader.py (novo)")
        print("\n🎉 Tudo sincronizado com seu .env!")

        return True


if __name__ == "__main__":
    propagator = EnvPropagator()
    propagator.run_propagation()
