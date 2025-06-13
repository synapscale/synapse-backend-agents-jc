#!/bin/bash
# start_render.sh - Script de inicialização para o Render (Versão Corrigida)

set -e

echo "🚀 Iniciando SynapScale Backend no Render..."

# Debug: verificar onde estamos
echo "📁 Diretório atual: $(pwd)"
echo "📂 Arquivos disponíveis:"
ls -la

# Configurar PYTHONPATH para incluir o diretório src
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
echo "✅ PYTHONPATH configurado: $PYTHONPATH"

# Verificar se a estrutura está correta
if [ ! -d "src" ]; then
    echo "❌ ERRO: Diretório 'src' não encontrado!"
    exit 1
fi

if [ ! -d "src/synapse" ]; then
    echo "❌ ERRO: Diretório 'src/synapse' não encontrado!"
    echo "📁 Conteúdo de src/:"
    ls -la src/
    exit 1
fi

if [ ! -f "src/synapse/main.py" ]; then
    echo "❌ ERRO: Arquivo 'src/synapse/main.py' não encontrado!"
    echo "📁 Conteúdo de src/synapse/:"
    ls -la src/synapse/
    exit 1
fi

echo "✅ Estrutura de arquivos verificada"

# Mudar para o diretório src para executar
cd src

# Testar importação
echo "🔍 Testando importação do módulo..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    import synapse
    print('✅ Módulo synapse importado')
    from synapse.main import app
    print('✅ FastAPI app importada')
except Exception as e:
    print(f'❌ Erro na importação: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Iniciar o servidor
echo "🚀 Inicializando servidor FastAPI..."
echo "🌐 Host: 0.0.0.0, Port: ${PORT:-8000}"
exec python -m uvicorn synapse.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
