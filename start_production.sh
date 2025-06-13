#!/bin/bash
# Script de inicialização para produção - SynapScale Backend
# Resolve problemas de importação de módulos

echo "🚀 Iniciando SynapScale Backend em produção..."

# Definir o diretório base
BASE_DIR="/opt/render/project/src"
if [ ! -d "$BASE_DIR" ]; then
    BASE_DIR="$(pwd)/src"
fi

# Adicionar src ao PYTHONPATH
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"

# Verificar se o diretório src existe
if [ ! -d "$BASE_DIR" ]; then
    echo "❌ Erro: Diretório src não encontrado em $BASE_DIR"
    exit 1
fi

# Verificar se o arquivo main.py existe
if [ ! -f "$BASE_DIR/synapse/main.py" ]; then
    echo "❌ Erro: Arquivo main.py não encontrado em $BASE_DIR/synapse/"
    exit 1
fi

echo "✅ PYTHONPATH configurado: $PYTHONPATH"
echo "✅ Diretório base: $BASE_DIR"

# Mudar para o diretório correto
cd "$BASE_DIR"

# Executar o servidor
echo "🚀 Iniciando servidor FastAPI..."
exec python -m uvicorn synapse.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
