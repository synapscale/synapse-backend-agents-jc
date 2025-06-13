#!/bin/bash
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
