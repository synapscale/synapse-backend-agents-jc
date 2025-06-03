#!/bin/bash
echo "🚀 Iniciando SynapScale Backend..."
source venv/bin/activate 2>/dev/null || echo "Ambiente virtual não encontrado - executando sem venv"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload

