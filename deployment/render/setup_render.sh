#!/bin/bash
# setup_render.sh - Script de configuração para deploy no Render
# Este script deve ser executado durante o build no Render

set -e

echo "🚀 Configurando ambiente para Render..."

# Criar diretórios necessários
mkdir -p logs
mkdir -p storage/archive
mkdir -p storage/audio
mkdir -p storage/cache
mkdir -p storage/csv
mkdir -p storage/document
mkdir -p uploads
mkdir -p workflows

# Definir permissões
chmod -R 755 logs
chmod -R 755 storage
chmod -R 755 uploads
chmod -R 755 workflows

# Verificar se as variáveis essenciais estão definidas
echo "🔍 Verificando variáveis de ambiente..."

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️ SECRET_KEY não está configurada"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️ JWT_SECRET_KEY não está configurada"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️ DATABASE_URL não está configurada"
fi

# Verificar versão do Python
echo "🐍 Verificando Python..."
python --version
pip --version

echo "✅ Configuração inicial concluída"
