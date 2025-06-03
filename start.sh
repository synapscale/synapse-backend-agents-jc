#!/bin/bash

# Script de inicialização do SynapScale Backend
# Execute com: ./start.sh

echo "🚀 Iniciando SynapScale Backend..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ para continuar."
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip para continuar."
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo .env a partir do exemplo..."
    cp .env.example .env
    echo "📝 Configure as variáveis em .env antes de continuar"
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p storage/uploads
mkdir -p storage/temp
mkdir -p logs
mkdir -p backups

# Executar migrações do banco
echo "🗄️ Executando migrações do banco de dados..."
python -c "
from src.synapse.database import engine, Base
from src.synapse.models import *
Base.metadata.create_all(bind=engine)
print('✅ Tabelas criadas com sucesso!')
"

# Verificar configurações
echo "🔍 Verificando configurações..."
python -c "
from src.synapse.config import settings, validate_settings
try:
    validate_settings()
    print('✅ Configurações válidas!')
except Exception as e:
    print(f'⚠️ Aviso de configuração: {e}')
"

# Iniciar servidor
echo "🌟 Iniciando servidor..."
echo "📍 Backend disponível em: http://localhost:8000"
echo "📚 Documentação em: http://localhost:8000/docs"
echo "🔌 WebSocket em: ws://localhost:8000/ws"
echo ""
echo "Para parar o servidor, pressione Ctrl+C"
echo ""

# Executar com reload em desenvolvimento
if [ "$1" = "dev" ]; then
    uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000
fi

