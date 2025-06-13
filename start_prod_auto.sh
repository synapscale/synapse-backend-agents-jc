#!/bin/bash
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
exec gunicorn src.synapse.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --timeout 120 \
    --keep-alive 2
