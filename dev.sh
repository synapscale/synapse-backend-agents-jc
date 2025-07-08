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

# Regenerar OpenAPI spec atualizado
echo "🔄 Regenerando openapi.json a partir do app FastAPI..."
python3 - << 'PYCODE'
import json, os, sys
from dotenv import load_dotenv
sys.path.insert(0, './src')
load_dotenv('.env')
try:
    from synapse.main import app
    spec = app.openapi()
    with open('openapi.json', 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print('✅ openapi.json atualizado com sucesso!')
    print(f'   - Endpoints: {len(spec.get("paths", {}))}')
    print(f'   - Schemas: {len(spec.get("components", {}).get("schemas", {}))}')
except Exception as e:
    print(f'❌ Erro ao gerar openapi.json: {e}')
PYCODE

# Verificar se aplicação existe
if [ ! -d "src" ]; then
    echo "❌ Diretório src/ não encontrado"
    exit 1
fi

# Iniciar servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "📌 Acesse: http://localhost:8000/docs"
uvicorn synapse.main:app --reload --host 0.0.0.0 --port 8000
