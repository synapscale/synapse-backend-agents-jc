#!/bin/bash
# Script de desenvolvimento simplificado
echo "🔧 SynapScale Backend - Modo Desenvolvimento"
echo "=========================================="

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se aplicação existe
if [ ! -d "src" ]; then
    echo "❌ Diretório src/ não encontrado"
    exit 1
fi

# Executar migrações se alembic.ini existir
if [ -f "config/alembic.ini" ]; then
    echo "🔄 Executando migrações de banco de dados..."
    cp config/alembic.ini .
    alembic upgrade head || echo "⚠️ Erro ao executar migrações, continuando..."
    rm alembic.ini
fi

# Iniciar servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "📌 Acesse: http://localhost:8000/docs"
uvicorn src.synapse.main:app --reload --host 0.0.0.0 --port 8000
