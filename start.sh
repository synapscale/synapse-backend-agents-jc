#!/bin/bash

# Script de inicialização do SynapScale Backend
# Versão corrigida com PostgreSQL/Prisma

echo "🚀 Iniciando SynapScale Backend..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "📋 Criando arquivo .env a partir do .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Configure suas variáveis de ambiente no arquivo .env"
    echo "⚠️  Especialmente: SECRET_KEY, DATABASE_URL e API keys"
fi

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale o Python 3.8+ primeiro."
    exit 1
fi

# Verificar se o Node.js está instalado (para Prisma)
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale o Node.js primeiro."
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar dependências Node.js (Prisma)
echo "📦 Instalando dependências Node.js..."
npm install

# Gerar cliente Prisma
echo "🔧 Gerando cliente Prisma..."
npx prisma generate

# Criar diretório de storage
echo "📁 Criando diretório de storage..."
mkdir -p storage

# Verificar configuração do banco de dados
echo "🗄️  Verificando configuração do banco de dados..."
if grep -q "postgresql://username:password@localhost:5432/synapscale_db" .env; then
    echo "⚠️  ATENÇÃO: Configure a URL do banco PostgreSQL no arquivo .env"
    echo "⚠️  Exemplo: DATABASE_URL=\"postgresql://user:password@localhost:5432/synapscale\""
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas variáveis de ambiente no arquivo .env"
echo "2. Configure seu banco PostgreSQL"
echo "3. Execute: npx prisma db push (para criar as tabelas)"
echo "4. Execute: python -m uvicorn src.synapse.main:app --reload"
echo ""
echo "🌐 A API estará disponível em: http://localhost:8000"
echo "📚 Documentação em: http://localhost:8000/docs"

