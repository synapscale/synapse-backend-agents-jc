#!/bin/bash

# ===================================================
# SCRIPT DE CORREÇÃO DOS PROBLEMAS DO PRISMA
# ===================================================

set -e  # Para se houver qualquer erro

echo "🔧 Iniciando correção dos problemas do Prisma..."

# 1. Backup do .env atual
echo "📋 Fazendo backup do .env atual..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 2. Corrigir .env
echo "🔧 Corrigindo configuração do .env..."
cp .env.fixed .env

# 3. Parar qualquer instância em execução
echo "🛑 Parando processos em execução..."
pkill -f "uvicorn" || true
docker-compose down || true

# 4. Limpar instalações anteriores
echo "🧹 Limpando instalações anteriores..."
rm -rf node_modules
rm -f package-lock.json
rm -rf app/generated/prisma/client

# 5. Instalar dependências
echo "📦 Instalando dependências Node.js..."
npm install

# 6. Gerar cliente Prisma
echo "🔄 Gerando cliente Prisma..."
npx prisma generate

# 7. Verificar se PostgreSQL está rodando
echo "🔍 Verificando PostgreSQL..."
if ! pg_isready -h localhost -p 5432 2>/dev/null; then
    echo "⚠️  PostgreSQL não está rodando localmente."
    echo "🐳 Iniciando PostgreSQL via Docker..."
    docker-compose up -d db
    
    echo "⏳ Aguardando PostgreSQL inicializar..."
    for i in {1..30}; do
        if pg_isready -h localhost -p 5432 2>/dev/null; then
            echo "✅ PostgreSQL está pronto!"
            break
        fi
        sleep 2
        echo "   Tentativa $i/30..."
    done
fi

# 8. Criar banco se não existir
echo "🗄️  Verificando/criando banco de dados..."
PGPASSWORD=postgres psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'synapse'" | grep -q 1 || \
PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE synapse;"

# 9. Aplicar schema
echo "🚀 Aplicando schema do banco de dados..."
npx prisma db push --force-reset

# 10. Verificar conexão
echo "🔍 Testando conexão com o banco..."
npx prisma db execute --stdin <<EOF
SELECT 'Conexão bem-sucedida!' as status;
EOF

echo ""
echo "✅ Correção concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Verifique se o .env está correto"
echo "2. Execute: python -m uvicorn src.synapse.main:app --reload"
echo "3. Acesse: http://localhost:8000/docs"
echo ""
echo "🔧 Se ainda houver problemas, execute:"
echo "   npx prisma studio  # Para verificar o banco"
echo "   docker-compose logs db  # Para logs do PostgreSQL"
