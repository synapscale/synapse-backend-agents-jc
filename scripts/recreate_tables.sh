#!/bin/bash
# Script para recriar as tabelas do banco de dados
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🔄 RECRIAÇÃO DAS TABELAS DO BANCO DE DADOS${NC}"
echo -e "${BLUE}===============================================${NC}"

# Ativar ambiente virtual
source venv/bin/activate

# 1. Verificar conexão com o banco de dados
echo -e "${YELLOW}🔍 Testando conexão com o banco de dados...${NC}"

# Extrair informações do banco de dados do arquivo .env
if [ -f ".env" ]; then
    # Tentar obter DATABASE_URL do arquivo .env
    DB_URL=$(grep DATABASE_URL .env | cut -d '=' -f2-)
    
    if [ -z "$DB_URL" ]; then
        echo -e "${RED}❌ DATABASE_URL não encontrada no arquivo .env${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}ℹ️ Usando configuração do banco de dados do arquivo .env${NC}"
else
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    exit 1
fi

# 2. Preparar ambiente Alembic
echo -e "${YELLOW}🔄 Preparando ambiente Alembic...${NC}"

# Copiar alembic.ini da pasta config para a raiz (necessário para o Alembic funcionar corretamente)
if [ -f "config/alembic.ini" ]; then
    cp config/alembic.ini .
    echo -e "${GREEN}✅ alembic.ini copiado para a raiz${NC}"
else
    echo -e "${RED}❌ config/alembic.ini não encontrado${NC}"
    exit 1
fi

# 3. Verificar e corrigir arquivos de migração
echo -e "${YELLOW}🔍 Verificando arquivos de migração...${NC}"

# Remover arquivos de migração vazios ou problemáticos
EMPTY_FILES=$(find alembic/versions -type f -size -2c)
if [ ! -z "$EMPTY_FILES" ]; then
    echo -e "${YELLOW}⚠️ Encontrados arquivos de migração vazios ou problemáticos:${NC}"
    for file in $EMPTY_FILES; do
        echo -e "${RED}🗑️ Removendo: $file${NC}"
        rm "$file"
    done
fi

# 4. Recriar as tabelas executando as migrações
echo -e "${YELLOW}🔄 Recriando tabelas no banco de dados...${NC}"

# Executar a migração Alembic
echo -e "${BLUE}ℹ️ Executando Alembic para criar tabelas...${NC}"
alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ Tabelas recriadas com sucesso!${NC}"
else
    echo -e "${RED}❌ Houve erros ao recriar as tabelas. Verifique as mensagens acima.${NC}"
fi

# 5. Limpar
echo -e "${YELLOW}🧹 Limpando arquivos temporários...${NC}"
rm -f alembic.ini

echo -e "${GREEN}${BOLD}🎉 PROCESSO DE RECRIAÇÃO DE TABELAS FINALIZADO!${NC}"
echo -e "${BLUE}Próximos passos:${NC}"
echo -e "1. ${YELLOW}Verifique se as tabelas foram criadas corretamente${NC}"
echo -e "2. ${YELLOW}Reinicie o servidor com ./dev.sh${NC}"
