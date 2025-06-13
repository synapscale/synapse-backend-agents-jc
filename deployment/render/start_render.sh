#!/bin/bash
# start_render.sh - Script de inicialização para o Render

set -e

echo "🚀 Iniciando SynapScale Backend no Render..."

# Mostrar onde estamos e o que temos
echo "✅ Diretório atual: $(pwd)"
echo "✅ PYTHONPATH: $PYTHONPATH"

# Verificar se os arquivos essenciais existem
# No Render, o projeto é copiado e estamos no diretório raiz
if [ ! -f "src/synapse/main.py" ]; then
    echo "❌ ERRO: src/synapse/main.py não encontrado!"
    echo "📁 Conteúdo do diretório atual:"
    ls -la
    exit 1
fi

echo "✅ Arquivo src/synapse/main.py encontrado!"

# Navegar para o diretório src onde está o código
cd src

# Configurar PYTHONPATH para incluir o diretório src
export PYTHONPATH="$(pwd):$PYTHONPATH"
echo "✅ PYTHONPATH configurado: $PYTHONPATH"
echo "✅ Diretório de trabalho atual: $(pwd)"

# Definir valor padrão para BACKEND_CORS_ORIGINS
export BACKEND_CORS_ORIGINS='["http://localhost:3000", "http://127.0.0.1:3000"]'
echo "✅ BACKEND_CORS_ORIGINS configurado: $BACKEND_CORS_ORIGINS"

# Definir valor padrão para ALLOWED_EXTENSIONS
export ALLOWED_EXTENSIONS='[".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".xml"]'
echo "✅ ALLOWED_EXTENSIONS configurado: $ALLOWED_EXTENSIONS"

# Verificar se o módulo pode ser importado
echo "🔍 Testando importação do módulo..."
python -c "
import sys
print('Python path:', sys.path)
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
