#!/bin/bash
# start_render.sh - Script de inicialização para o Render

set -e

echo "🚀 Iniciando SynapScale Backend no Render..."

# Mostrar onde estamos e o que temos
echo "✅ Diretório atual: $(pwd)"
echo "✅ PYTHONPATH inicial: $PYTHONPATH"

# Verificar se os arquivos essenciais existem
if [ ! -f "src/synapse/main.py" ]; then
    echo "❌ ERRO: src/synapse/main.py não encontrado!"
    echo "📁 Conteúdo do diretório atual:"
    ls -la
    exit 1
fi

echo "✅ Arquivo src/synapse/main.py encontrado!"

# Configurar PYTHONPATH para incluir o diretório src
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
echo "✅ PYTHONPATH configurado: $PYTHONPATH"

# Definir valores padrão para variáveis de ambiente
export BACKEND_CORS_ORIGINS='["http://localhost:3000", "http://127.0.0.1:3000"]'
export ALLOWED_EXTENSIONS='[".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".xml"]'
echo "✅ Variáveis de ambiente configuradas"

# Navegar para o diretório src onde está o código
cd src
echo "✅ Diretório de trabalho atual: $(pwd)"

# Verificar se o módulo pode ser importado
echo "🔍 Testando importação do módulo..."
python -c "
import sys
import os

# Garantir que o diretório atual está no path
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print('Python path:', sys.path[:3])  # Mostrar apenas os primeiros 3 para não lotar o log
try:
    import synapse
    print('✅ Módulo synapse importado com sucesso')
    from synapse.main import app
    print('✅ Aplicação FastAPI importada com sucesso')
except ImportError as e:
    print(f'❌ Erro na importação: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Iniciar o servidor
echo "🚀 Inicializando servidor FastAPI..."
exec python -m uvicorn synapse.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
