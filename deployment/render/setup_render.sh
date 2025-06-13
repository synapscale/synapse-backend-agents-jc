#!/bin/bash
# setup_render.sh - Script de configuração para deploy no Render

set -e

echo "🚀 Configurando ambiente para Render..."

# Criar diretórios necessários
mkdir -p logs storage/archive storage/audio storage/cache storage/csv storage/document uploads workflows

# Definir permissões
chmod -R 755 logs storage uploads workflows

# Verificar versão do Python
echo "🐍 Verificando Python..."
python --version
pip --version

echo "✅ Configuração inicial concluída"
chmod +x deployment/render/test_imports.py
python deployment/render/test_imports.py

echo "✅ Configuração inicial concluída"
