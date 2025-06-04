#!/bin/bash
echo "🚀 Iniciando SynapScale Backend..."
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload
