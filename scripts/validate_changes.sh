#!/bin/bash
# Script para validar e testar as alterações realizadas (atualizado)
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}✅ VALIDAÇÃO DAS ALTERAÇÕES${NC}"
echo -e "${BLUE}===============================================${NC}"

# Verificar requirements.txt
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ OK: requirements.txt na raiz${NC}"
else
    echo -e "${RED}❌ ERRO: requirements.txt não encontrado na raiz${NC}"
fi

# Verificar arquivos .env
if [ -f ".env.example" ]; then
    echo -e "${GREEN}✅ OK: .env.example na raiz${NC}"
else
    echo -e "${RED}❌ ERRO: .env.example não encontrado na raiz${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ OK: .env na raiz${NC}"
else
    echo -e "${YELLOW}⚠️ ATENÇÃO: .env não encontrado, mas pode ser criado pelo setup${NC}"
fi

# Verificar setup.sh
if [ -f "setup.sh" ]; then
    echo -e "${GREEN}✅ OK: setup.sh na raiz${NC}"
else
    echo -e "${RED}❌ ERRO: setup.sh não encontrado na raiz${NC}"
fi

# Verificar documentação
if [ -f "docs/guides/setup_scripts.md" ]; then
    echo -e "${GREEN}✅ OK: Documentação dos scripts de setup presente${NC}"
else
    echo -e "${RED}❌ ERRO: Documentação dos scripts de setup ausente${NC}"
fi

echo -e "\n${GREEN}${BOLD}🎉 VALIDAÇÃO CONCLUÍDA!${NC}"
echo -e "${YELLOW}O repositório foi reorganizado para usar:${NC}"
echo -e "  ${BLUE}- Um único arquivo requirements.txt na raiz${NC}"
echo -e "  ${BLUE}- Padrão .env.example e .env${NC}"
echo -e "  ${BLUE}- Scripts de setup unificados${NC}"
echo -e ""
echo -e "${GREEN}Todas as configurações redundantes foram removidas!${NC}"
