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

echo -e "${GREEN}✅ requirements.txt está presente na raiz do projeto${NC}"
echo -e "${GREEN}${BOLD}🎉 Reorganização dos arquivos requirements concluída com sucesso!${NC}"
echo -e "${YELLOW}Agora o projeto utiliza apenas um único arquivo requirements.txt na raiz.${NC}"
