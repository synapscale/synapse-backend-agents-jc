#!/usr/bin/env python3
"""
Script de configuração automática completa do SynapScale Backend
Automatiza TUDO - só precisa configurar o .env uma vez
"""

import os
import sys
import secrets
import base64
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class SynapScaleSetup:
    def __init__(self):
        self.root_path = Path.cwd()
        self.env_file = self.root_path / ".env"
        self.env_template = self.root_path / ".env.example"
        self.venv_path = self.root_path / "venv"
        self.config_vars = {}
        
    def print_header(self):
        print("=" * 60)
        print("🚀 SYNAPSCALE BACKEND - CONFIGURAÇÃO AUTOMÁTICA COMPLETA")
        print("=" * 60)
        print("✨ Configuração automatizada para desenvolvimento e produção")
        print("📋 Só precisa preencher o .env uma vez - o resto é automático!")
        print("=" * 60)
        
    def check_python_version(self):
        """Verifica se Python 3.11+ está instalado"""
        print("\n🔍 Verificando versão do Python...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print(f"❌ Python 3.11+ é necessário. Versão atual: {version.major}.{version.minor}")
            sys.exit(1)
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        
    def create_virtual_environment(self):
        """Cria ambiente virtual se não existir"""
        print("\n🔧 Configurando ambiente virtual...")
        
        if self.venv_path.exists():
            print("✅ Ambiente virtual já existe")
            return
            
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Ambiente virtual criado com sucesso")
        except subprocess.CalledProcessError:
            print("❌ Erro ao criar ambiente virtual")
            sys.exit(1)
            
    def activate_virtual_environment(self):
        """Ativa o ambiente virtual"""
        print("\n🔄 Ativando ambiente virtual...")
        
        # Detectar sistema operacional
        if os.name == 'nt':  # Windows
            python_exe = self.venv_path / "Scripts" / "python.exe"
            pip_exe = self.venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            python_exe = self.venv_path / "bin" / "python"
            pip_exe = self.venv_path / "bin" / "pip"
            
        if not python_exe.exists():
            print("❌ Ambiente virtual não encontrado")
            sys.exit(1)
            
        # Atualizar variáveis de ambiente
        os.environ["VIRTUAL_ENV"] = str(self.venv_path)
        os.environ["PATH"] = f"{self.venv_path / 'bin' if os.name != 'nt' else self.venv_path / 'Scripts'}{os.pathsep}{os.environ['PATH']}"
        
        self.python_exe = str(python_exe)
        self.pip_exe = str(pip_exe)
        
        print("✅ Ambiente virtual ativado")
        
    def install_dependencies(self):
        """Instala todas as dependências"""
        print("\n📦 Instalando dependências...")
        
        # Atualizar pip primeiro
        subprocess.run([self.pip_exe, "install", "--upgrade", "pip"], check=False)
        
        # Instalar dependências do requirements.txt
        requirements_file = self.root_path / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.run([
                    self.pip_exe, "install", "-r", str(requirements_file)
                ], check=True, capture_output=True)
                print("✅ Dependências instaladas com sucesso")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Erro ao instalar algumas dependências: {e}")
                print("Continuando com dependências básicas...")
                
                # Instalar dependências básicas manualmente
                basic_deps = [
                    "fastapi>=0.110.0",
                    "uvicorn[standard]>=0.27.0",
                    "pydantic>=2.6.0",
                    "pydantic-settings>=2.2.0",
                    "sqlalchemy>=2.0.25",
                    "psycopg2-binary>=2.9.9",
                    "alembic>=1.13.0",
                    "python-jose[cryptography]",
                    "passlib[bcrypt]",
                    "python-multipart",
                    "redis>=5.0.1",
                    "python-dotenv",
                    "gunicorn>=21.2.0"
                ]
                
                for dep in basic_deps:
                    try:
                        subprocess.run([self.pip_exe, "install", dep], check=True, capture_output=True)
                        print(f"✅ {dep}")
                    except:
                        print(f"⚠️ Falha ao instalar {dep}")
        else:
            print("❌ requirements.txt não encontrado")
            
    def generate_secure_keys(self) -> Dict[str, str]:
        """Gera chaves seguras automaticamente"""
        print("\n🔐 Gerando chaves de segurança...")
        
        keys = {
            "SECRET_KEY": secrets.token_urlsafe(64),
            "JWT_SECRET_KEY": secrets.token_urlsafe(64),
            "ENCRYPTION_KEY": base64.b64encode(secrets.token_bytes(32)).decode('utf-8'),
            "WEBHOOK_SECRET": secrets.token_urlsafe(32)
        }
        
        print("✅ Chaves de segurança geradas")
        return keys
        
    def create_env_file(self):
        """Cria arquivo .env se não existir"""
        print("\n📝 Configurando arquivo .env...")
        
        if not self.env_file.exists():
            if self.env_template.exists():
                shutil.copy(self.env_template, self.env_file)
                print("✅ Arquivo .env criado a partir do template")
            else:
                print("❌ Template .env não encontrado")
                return False
        else:
            print("✅ Arquivo .env já existe")
            
        return True
        
    def read_env_file(self):
        """Lê variáveis do arquivo .env"""
        if not self.env_file.exists():
            return {}
            
        env_vars = {}
        with open(self.env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    
        return env_vars
        
    def update_env_file(self, updates: Dict[str, str]):
        """Atualiza variáveis no arquivo .env"""
        if not self.env_file.exists():
            return
            
        # Ler arquivo atual
        with open(self.env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Atualizar linhas
        updated_lines = []
        updated_keys = set()
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                
                if key in updates and not updates[key]:
                    # Só atualizar se o valor atual estiver vazio
                    updated_lines.append(f"{key}={updates[key]}\n")
                    updated_keys.add(key)
                elif key in updates and updates[key]:
                    # Atualizar com novo valor
                    updated_lines.append(f"{key}={updates[key]}\n")
                    updated_keys.add(key)
                else:
                    updated_lines.append(original_line)
            else:
                updated_lines.append(original_line)
                
        # Escrever arquivo atualizado
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
            
    def auto_fill_env_variables(self):
        """Preenche automaticamente variáveis que podem ser geradas"""
        print("\n⚙️ Preenchendo variáveis automaticamente...")
        
        # Ler variáveis atuais
        current_vars = self.read_env_file()
        
        # Gerar chaves seguras
        secure_keys = self.generate_secure_keys()
        
        # Variáveis para auto-preencher
        auto_vars = {
            **secure_keys,
            "UPLOAD_DIR": "./uploads",
            "LOG_FILE": "logs/synapscale.log",
            "EMAILS_FROM_EMAIL": "noreply@synapscale.com",
            "EMAILS_FROM_NAME": "SynapScale"
        }
        
        # Só preencher se estiver vazio
        updates = {}
        for key, value in auto_vars.items():
            if not current_vars.get(key):
                updates[key] = value
                
        if updates:
            self.update_env_file(updates)
            print(f"✅ {len(updates)} variáveis preenchidas automaticamente")
        else:
            print("✅ Todas as variáveis já estão preenchidas")
            
    def create_directories(self):
        """Cria diretórios necessários"""
        print("\n📁 Criando diretórios necessários...")
        
        directories = [
            "uploads",
            "logs", 
            "storage",
            "storage/files",
            "storage/temp",
            "storage/cache"
        ]
        
        for directory in directories:
            dir_path = self.root_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("✅ Diretórios criados")
        
    def initialize_database(self):
        """Inicializa banco de dados"""
        print("\n🗄️ Inicializando banco de dados...")
        
        try:
            # Executar migrações Alembic
            subprocess.run([
                self.python_exe, "-m", "alembic", "upgrade", "head"
            ], check=True, capture_output=True)
            print("✅ Migrações do banco executadas")
        except subprocess.CalledProcessError:
            print("⚠️ Erro ao executar migrações - será criado automaticamente na primeira execução")
            
    def create_startup_scripts(self):
        """Cria scripts de inicialização otimizados"""
        print("\n📜 Criando scripts de inicialização...")
        
        # Script de desenvolvimento
        dev_script = '''#!/bin/bash
set -e

echo "🚀 Iniciando SynapScale Backend - Desenvolvimento"
echo "================================================="

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "Execute: python setup_complete.py"
    exit 1
fi

# Criar diretórios se não existirem
mkdir -p uploads logs storage

# Executar migrações
echo "🗄️ Executando migrações..."
python -m alembic upgrade head

# Iniciar servidor
echo "🌐 Iniciando servidor de desenvolvimento..."
echo "📍 Servidor: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""
exec python -m uvicorn src.synapse.main:app --reload --host 0.0.0.0 --port 8000
'''
        
        # Script de produção
        prod_script = '''#!/bin/bash
set -e

echo "🚀 Iniciando SynapScale Backend - Produção"
echo "=========================================="

# Ativar ambiente virtual
source venv/bin/activate

# Verificar variáveis de ambiente
if [ -z "$SECRET_KEY" ] || [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ Variáveis de ambiente não configuradas!"
    exit 1
fi

# Criar diretórios
mkdir -p uploads logs storage

# Executar migrações
python -m alembic upgrade head

# Iniciar servidor com Gunicorn
echo "🌐 Iniciando servidor de produção..."
exec gunicorn src.synapse.main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:${PORT:-8000} \\
    --access-logfile logs/access.log \\
    --error-logfile logs/error.log \\
    --log-level info \\
    --timeout 120 \\
    --keep-alive 2
'''
        
        # Salvar scripts
        with open("start_dev_auto.sh", "w") as f:
            f.write(dev_script)
        os.chmod("start_dev_auto.sh", 0o755)
        
        with open("start_prod_auto.sh", "w") as f:
            f.write(prod_script)
        os.chmod("start_prod_auto.sh", 0o755)
        
        print("✅ Scripts de inicialização criados")
        
    def validate_configuration(self):
        """Valida configuração final"""
        print("\n🔍 Validando configuração...")
        
        # Verificar arquivo .env
        if not self.env_file.exists():
            print("❌ Arquivo .env não encontrado")
            return False
            
        # Verificar variáveis críticas
        env_vars = self.read_env_file()
        critical_vars = ["SECRET_KEY", "JWT_SECRET_KEY", "ENCRYPTION_KEY"]
        
        missing_vars = [var for var in critical_vars if not env_vars.get(var)]
        if missing_vars:
            print(f"❌ Variáveis críticas não configuradas: {', '.join(missing_vars)}")
            return False
            
        # Testar importação básica
        try:
            test_cmd = [self.python_exe, "-c", "from src.synapse.main import app; print('✅ Importação OK')"]
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Configuração válida")
                return True
            else:
                print(f"❌ Erro na importação: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False
            
    def show_final_instructions(self):
        """Mostra instruções finais"""
        print("\n" + "=" * 60)
        print("🎉 CONFIGURAÇÃO COMPLETA!")
        print("=" * 60)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("\n1. 📝 Configure as variáveis obrigatórias no .env:")
        print("   - DATABASE_URL (banco PostgreSQL)")
        print("   - SMTP_* (para envio de emails)")
        print("   - *_API_KEY (chaves dos provedores LLM)")
        print("\n2. 🚀 Inicie o servidor:")
        print("   - Desenvolvimento: ./start_dev_auto.sh")
        print("   - Produção: ./start_prod_auto.sh")
        print("\n3. 🌐 Acesse a aplicação:")
        print("   - Backend: http://localhost:8000")
        print("   - Docs: http://localhost:8000/docs")
        print("\n4. ✅ Tudo funcionando automaticamente!")
        print("\n💡 DICA: Após configurar o .env, tudo funciona automaticamente!")
        print("=" * 60)
        
    def run_setup(self):
        """Executa setup completo"""
        try:
            self.print_header()
            self.check_python_version()
            self.create_virtual_environment()
            self.activate_virtual_environment()
            self.install_dependencies()
            self.create_env_file()
            self.auto_fill_env_variables()
            self.create_directories()
            self.initialize_database()
            self.create_startup_scripts()
            
            if self.validate_configuration():
                self.show_final_instructions()
                return True
            else:
                print("\n❌ Configuração falhou. Verifique os erros acima.")
                return False
                
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelado pelo usuário")
            return False
        except Exception as e:
            print(f"\n❌ Erro durante setup: {e}")
            return False


if __name__ == "__main__":
    setup = SynapScaleSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)
