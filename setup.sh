#!/bin/bash
# setup.sh - Script para configurar o ambiente de desenvolvimento

echo "Configurando ambiente de desenvolvimento..."

# Instalar pnpm se não estiver instalado
if ! command -v pnpm &> /dev/null; then
  echo "Instalando pnpm..."
  npm install -g pnpm
fi

# Instalar dependências
echo "Instalando dependências do projeto..."
pnpm install

# Criar arquivos .env se não existirem
echo "Verificando arquivos .env..."
if [ ! -f "./apps/ai-agents-sidebar/.env.local" ]; then
  echo "Criando .env.local para ai-agents-sidebar..."
  cat > ./apps/ai-agents-sidebar/.env.local << EOF
# Ambiente local
NEXT_PUBLIC_API_URL=http://localhost:3000/api
EOF
fi

# Executar verificação de importações
echo "Verificando importações..."
./check-imports.sh

echo "Configuração concluída! Para iniciar o servidor de desenvolvimento, execute:"
echo "pnpm dev"
