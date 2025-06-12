#!/bin/bash
# Script de produção simplificado
echo "🏭 SynapScale Backend - Modo Produção"
echo "======================================"

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

# Iniciar servidor de produção
echo "🚀 Iniciando servidor em modo produção..."
echo "📌 Servidor rodando em: http://0.0.0.0:8000"

# Verificar se gunicorn está instalado
if python3 -c "import gunicorn" &>/dev/null; then
    gunicorn src.synapse.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
    echo "⚠️ Gunicorn não encontrado, usando Uvicorn..."
    uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000
fi
