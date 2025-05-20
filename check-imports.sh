#!/bin/bash
# check-imports.sh - Script para verificar importações em todo o projeto

echo "Verificando importações..."

# Instalar ferramentas necessárias se ainda não estiverem instaladas
if ! command -v eslint &> /dev/null; then
  echo "Instalando eslint..."
  npm install -g eslint
fi

# Verificar importações em todos os arquivos JavaScript/TypeScript do projeto
echo "Executando eslint para verificar importações..."
eslint --ext .js,.jsx,.ts,.tsx . --fix

# Verificar caminhos em importações de componentes
echo "Verificando padrões de importação..."
find . -type f -name "*.ts" -o -name "*.tsx" | grep -v "node_modules" | xargs grep -l "import .* from" | xargs grep -l "@/" | while read file; do
  echo "AVISO: Possível problema de importação com @ em: $file"
done

echo "Verificação concluída!"
