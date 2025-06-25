#!/bin/bash
# Script de produção simplificado
echo "🏭 SynapScale Backend - Modo Produção"
echo "======================================"

# Ativar ambiente virtual
if [ ! -f venv/bin/activate ]; then
  echo "❌ Ambiente virtual não encontrado. Crie com: python3.11 -m venv venv"
  exit 1
fi
source venv/bin/activate

# Checar versão do Python
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$PYTHON_VERSION" != "3.11" ]; then
  echo "❌ O ambiente virtual deve ser Python 3.11. Versão atual: $PYTHON_VERSION"
  echo "Remova o venv e crie novamente com: python3.11 -m venv venv"
  deactivate
  exit 1
fi

# Exportar PYTHONPATH para garantir que o pacote synapse seja encontrado
export PYTHONPATH=./src

# Verificar se aplicação existe
if [ ! -d "src" ]; then
    echo "❌ Diretório src/ não encontrado"
    exit 1
fi

# Iniciar servidor de produção
echo "🚀 Iniciando servidor em modo produção..."
echo "📌 Servidor rodando em: http://0.0.0.0:8000"

# Verificar se gunicorn está instalado
if python3 -c "import gunicorn" &>/dev/null; then
    exec gunicorn -k uvicorn.workers.UvicornWorker src.synapse.main:app --bind 0.0.0.0:8000 --workers 4 --timeout 120
else
    echo "⚠️ Gunicorn não encontrado, usando Uvicorn..."
    uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000
fi
