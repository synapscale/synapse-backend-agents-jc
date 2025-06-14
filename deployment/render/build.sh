#!/bin/bash
# build.sh - Script de build otimizado para Render

set -e

echo "🚀 Iniciando build para Render..."

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs storage/archive storage/audio storage/cache storage/csv storage/document uploads workflows

# Definir permissões
chmod -R 755 logs storage uploads workflows

# Definir o PYTHONPATH corretamente
export PYTHONPATH="/opt/render/project/src/src:$PYTHONPATH"
echo "✅ PYTHONPATH configurado: $PYTHONPATH"

# Testar importações
echo "🧪 Testando importações..."
cd src
python -c "
import sys
import os
# Adicionar diretório src ao path
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
print('Python path:', sys.path)

try:
    import synapse
    print('✅ Módulo synapse importado com sucesso')
    
    from synapse.core.config_new import settings
    print('✅ Configurações carregadas')
    
    from synapse.main import app
    print('✅ Aplicação FastAPI importada com sucesso')
    
    print('✅ Build concluído com sucesso!')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

cd ..
echo "✅ Build concluído!"
