#!/bin/bash

# Script para usar credenciais locais de desenvolvimento
# Este script copia as credenciais reais do .env.local para .env

echo "🔄 Configurando credenciais locais para desenvolvimento..."

if [ -f ".env.local" ]; then
    cp .env.local .env
    echo "✅ Credenciais locais configuradas com sucesso!"
    echo "🚀 Agora você pode rodar o servidor com as credenciais reais."
    echo ""
    echo "Para iniciar o servidor:"
    echo "python -m uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload"
else
    echo "❌ Arquivo .env.local não encontrado!"
    echo "Este arquivo deve conter suas credenciais reais de desenvolvimento."
fi
