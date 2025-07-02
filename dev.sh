#!/bin/bash
# Script de desenvolvimento simplificado
set -euo pipefail
echo "🔧 SynapScale Backend - Modo Desenvolvimento"
echo "=========================================="

# Ativar ambiente virtual
VENV_DIR="${VENV_PATH:-venv}"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "❌ Ambiente virtual não encontrado. Crie com: python3.11 -m venv $VENV_DIR"
  exit 1
fi
source "$VENV_DIR/bin/activate"

# Checar versão do Python
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$PYTHON_VERSION" != "3.11"* ]]; then
  echo "❌ O ambiente virtual deve ser Python 3.11.x. Versão atual: $PYTHON_VERSION"
  echo "Remova o venv e crie novamente com: python3.11 -m venv $VENV_DIR"
  deactivate
  exit 1
fi

# Exportar PYTHONPATH para garantir que o pacote synapse seja encontrado
export PYTHONPATH=./src

# Instalar dependências (automatizado)
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Checar alinhamento de schema (não-fatal)
echo "🔍 Checando alinhamento de schema..."
chmod +x tests/analysis/check_schema_alignment.py
tests/analysis/check_schema_alignment.py || true

# Desativar geração automática de modelos Pydantic e spec OpenAPI
if false; then
  echo "⏳ Sincronizando Pydantic models com o banco..."
  chmod +x scripts/generate_pydantic_models.py
  scripts/generate_pydantic_models.py

  # Regenerar OpenAPI spec (desativado)
  # echo "🔄 Regenerando current_openapi.json a partir do app FastAPI"
  # python3 - << 'PYCODE'
  # import json, os
  # from dotenv import load_dotenv
  # os.environ['PYTHONPATH'] = './src'
  # load_dotenv('.env')
  # from synapse.main import app
  # spec = app.openapi()
  # with open('current_openapi.json', 'w', encoding='utf-8') as f:
  #     json.dump(spec, f, indent=2, ensure_ascii=False)
  # print('✅ current_openapi.json atualizado')
  # PYCODE
fi

# Verificar se aplicação existe
if [ ! -d "src" ]; then
    echo "❌ Diretório src/ não encontrado"
    exit 1
fi

# Iniciar servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "📌 Acesse: http://localhost:8000/docs"
uvicorn synapse.main:app --reload --host 0.0.0.0 --port 8000
