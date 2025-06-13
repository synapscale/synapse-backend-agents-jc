#!/bin/bash
# start_render.sh - Script de inicialização para o Render

set -e

echo "🚀 Iniciando SynapScale Backend no Render..."

# Configurar PYTHONPATH para o Render
export PYTHONPATH="/opt/render/project/src:$PYTHONPATH"

# Mudar para o diretório src
cd /opt/render/project/src

# Verificações de debug
echo "✅ Diretório atual: $(pwd)"
echo "✅ PYTHONPATH: $PYTHONPATH"

# Verificar se os arquivos essenciais existem
if [ ! -f "synapse/main.py" ]; then
    echo "❌ ERRO: synapse/main.py não encontrado!"
    echo "📁 Conteúdo do diretório atual:"
    ls -la
    exit 1
fi

# Verificar se o módulo pode ser importado
echo "🔍 Testando importação do módulo..."
python -c "
try:
    import synapse
    print('✅ Módulo synapse importado com sucesso')
except ImportError as e:
    print(f'❌ Erro na importação: {e}')
    exit(1)
"

# Iniciar o servidor
echo "🚀 Inicializando servidor FastAPI..."
exec python -m uvicorn synapse.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
