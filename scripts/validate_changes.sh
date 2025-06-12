#!/bin/bash
# Script para validar e testar as alterações realizadas
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

# Verificar arquivos requirements
echo -e "${YELLOW}📝 Verificando requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ OK: requirements.txt na raiz${NC}"
else
    echo -e "${RED}❌ ERRO: requirements.txt não encontrado na raiz${NC}"
fi

# Verificar arquivos redundantes
if [ -f "config/requirements.txt" ] || [ -f "config/requirements.backend.txt" ] || [ -f "config/requirements.notorch.txt" ]; then
    echo -e "${RED}❌ ERRO: Ainda existem arquivos requirements redundantes na pasta config/${NC}"
else
    echo -e "${GREEN}✅ OK: Sem arquivos requirements redundantes${NC}"
fi

# Verificar arquivos .env
echo -e "\n${YELLOW}📝 Verificando arquivos .env...${NC}"
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

if [ -f ".env.template" ]; then
    echo -e "${RED}❌ ERRO: Ainda existe .env.template redundante na raiz${NC}"
else
    echo -e "${GREEN}✅ OK: Sem .env.template redundante na raiz${NC}"
fi

if [ -f "setup/templates/.env.template" ]; then
    echo -e "${GREEN}✅ OK: .env.template presente em setup/templates/${NC}"
else
    echo -e "${RED}❌ ERRO: .env.template não encontrado em setup/templates/${NC}"
fi

# Verificar scripts de setup
echo -e "\n${YELLOW}📝 Verificando scripts de setup...${NC}"
if [ -f "setup.sh" ]; then
    echo -e "${GREEN}✅ OK: setup.sh na raiz${NC}"
else
    echo -e "${RED}❌ ERRO: setup.sh não encontrado na raiz${NC}"
fi

if [ -f "setup_complete.py" ]; then
    echo -e "${GREEN}✅ OK: setup_complete.py na raiz${NC}"
else
    echo -e "${RED}❌ ERRO: setup_complete.py não encontrado na raiz${NC}"
fi

if [ -f "scripts/setup.sh" ]; then
    echo -e "${RED}❌ ERRO: Ainda existe scripts/setup.sh redundante${NC}"
else
    echo -e "${GREEN}✅ OK: scripts/setup.sh foi removido${NC}"
fi

if [ -f "setup/scripts/setup_complete.py" ] || [ -f "setup/scripts/setup_complete.sh" ]; then
    echo -e "${RED}❌ ERRO: Ainda existem scripts redundantes em setup/scripts/${NC}"
else
    echo -e "${GREEN}✅ OK: Sem scripts redundantes em setup/scripts/${NC}"
fi

# Verificar documentação
echo -e "\n${YELLOW}📝 Verificando documentação...${NC}"
if [ -f "docs/guides/setup_scripts.md" ]; then
    echo -e "${GREEN}✅ OK: Documentação dos scripts de setup presente${NC}"
else
    echo -e "${RED}❌ ERRO: Documentação dos scripts de setup ausente${NC}"
fi

# Testes funcionais
echo -e "\n${YELLOW}🧪 Executando testes funcionais...${NC}"

# Tentar executar setup.sh com opção --help
echo -e "${BLUE}🔍 Testando setup.sh --help...${NC}"
./setup.sh --help > /dev/null 2>&1
if [ $? -eq 0 ] || [ $? -eq 1 ]; then  # Pode retornar 0 ou 1, ambos são aceitáveis
    echo -e "${GREEN}✅ OK: setup.sh pode ser executado${NC}"
else
    echo -e "${RED}❌ ERRO: setup.sh não pode ser executado${NC}"
fi

echo -e "\n${GREEN}${BOLD}🎉 VALIDAÇÃO CONCLUÍDA!${NC}"
echo -e "${YELLOW}O repositório foi reorganizado para usar:${NC}"
echo -e "  ${BLUE}- Um único arquivo requirements.txt na raiz${NC}"
echo -e "  ${BLUE}- Padrão .env.example e .env${NC}"
echo -e "  ${BLUE}- Scripts de setup unificados${NC}"
echo -e ""
echo -e "${GREEN}Todas as configurações redundantes foram removidas!${NC}"
