#!/bin/bash
# Script de desenvolvimento simplificado
echo "🔧 SynapScale Backend - Modo Desenvolvimento"
echo "=========================================="

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

# Iniciar servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "📌 Acesse: http://localhost:8000/docs"
uvicorn src.synapse.main:app --reload --host 0.0.0.0 --port 8000
