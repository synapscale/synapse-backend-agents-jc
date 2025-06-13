#!/bin/bash
# setup_render.sh - Script de configuração para deploy no Render

set -e

echo "🚀 Configurando ambiente para Render..."

# Criar diretórios necessários
mkdir -p logs storage/archive storage/audio storage/cache storage/csv storage/document uploads workflows

# Definir permissões
chmod -R 755 logs storage uploads workflows

# Verificar versão do Python
echo "🐍 Verificando Python..."
python --version
pip --version

echo "✅ Configuração inicial concluída"

# Testar importações com o PYTHONPATH correto
echo "🧪 Testando importações..."
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
cd src
python -c "
import sys
print('PYTHONPATH durante teste:', sys.path)
try:
    import synapse
    from synapse.main import app
    from synapse.core.config_new import settings
    from synapse.database import init_db, get_db
    from synapse.api.v1.router import api_router
    print('✅ Todas as importações funcionaram!')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"
cd ..

echo "✅ Configuração inicial concluída"
