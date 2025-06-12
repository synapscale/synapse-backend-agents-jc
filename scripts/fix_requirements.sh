#!/bin/bash
# Script para resolver a confusão dos arquivos requirements
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🔄 REORGANIZAÇÃO DOS ARQUIVOS REQUIREMENTS${NC}"
echo -e "${BLUE}===============================================${NC}"

# Verificar se requirements.txt existe na raiz
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Erro: requirements.txt não encontrado na raiz do projeto${NC}"
    exit 1
fi

# Backup dos arquivos requirements na pasta config
echo -e "${YELLOW}📦 Criando backup dos arquivos requirements...${NC}"
mkdir -p backup/config
if [ -f "config/requirements.txt" ]; then
    cp config/requirements.txt backup/config/
fi
if [ -f "config/requirements.backend.txt" ]; then
    cp config/requirements.backend.txt backup/config/
fi
if [ -f "config/requirements.notorch.txt" ]; then
    cp config/requirements.notorch.txt backup/config/
fi

# Remover arquivos na pasta config
echo -e "${YELLOW}🗑️ Removendo arquivos requirements duplicados...${NC}"
rm -f config/requirements.txt config/requirements.backend.txt config/requirements.notorch.txt
echo -e "${GREEN}✅ Arquivos requirements duplicados removidos${NC}"

# Atualizar scripts que referenciam os arquivos requirements
echo -e "${YELLOW}📝 Atualizando scripts que referenciam arquivos requirements...${NC}"

# Corrigir referência no setup.sh
if [ -f "setup.sh" ]; then
    echo -e "${BLUE}📄 Atualizando setup.sh...${NC}"
    sed -i 's|config/requirements.txt|requirements.txt|g' setup.sh
    sed -i 's|Arquivo requirements.txt não encontrado em config/|Arquivo requirements.txt não encontrado|g' setup.sh
fi

# Corrigir referência no scripts/analyze_repository.sh
if [ -f "scripts/analyze_repository.sh" ]; then
    echo -e "${BLUE}📄 Atualizando scripts/analyze_repository.sh...${NC}"
    sed -i 's|main_req="config/requirements.txt"|main_req="requirements.txt"|g' scripts/analyze_repository.sh
fi

# Remover script organize_requirements.sh, pois não é mais necessário
if [ -f "scripts/organize_requirements.sh" ]; then
    echo -e "${BLUE}📄 Removendo scripts/organize_requirements.sh...${NC}"
    rm -f scripts/organize_requirements.sh
fi

# Atualizar o README.md para refletir a mudança
if grep -q "config/requirements.txt" README.md; then
    echo -e "${BLUE}📄 Atualizando README.md...${NC}"
    sed -i 's|config/requirements.txt|requirements.txt|g' README.md
fi

echo -e "${GREEN}✅ Scripts atualizados${NC}"
echo -e "${GREEN}${BOLD}🎉 Reorganização dos arquivos requirements concluída com sucesso!${NC}"
echo -e "${YELLOW}Agora o projeto utiliza apenas um único arquivo requirements.txt na raiz.${NC}"
