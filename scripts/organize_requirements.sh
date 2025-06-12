#!/bin/bash
# Script para organizar os arquivos de requirements
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

# Criar pasta de backup
echo -e "${YELLOW}📦 Criando backup dos arquivos requirements existentes...${NC}"
mkdir -p backup/config
cp config/requirements*.txt backup/config/ 2>/dev/null

# Mover o arquivo principal requirements.txt para o local correto
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📄 Movendo requirements.txt unificado para config/requirements.txt...${NC}"
    cp requirements.txt config/requirements.txt
    echo -e "${GREEN}✅ Arquivo unificado copiado para config/requirements.txt${NC}"
fi

# Criar versões específicas a partir do arquivo principal
echo -e "${YELLOW}🔍 Criando versões específicas a partir do arquivo unificado...${NC}"

# Versão notorch - sem PyTorch
cat requirements.txt | grep -v "torch>=" > config/requirements.notorch.txt
echo -e "${GREEN}✅ Versão notorch criada em config/requirements.notorch.txt${NC}"

# Versão backend - somente dependências essenciais
cat requirements.txt | grep -v "torch>=" | grep -v "anthropic>=" | grep -v "google-generativeai>=" | grep -v "groq>=" | grep -v "cohere>=" | grep -v "together>=" | grep -v "replicate>=" > config/requirements.backend.txt
echo -e "${GREEN}✅ Versão backend criada em config/requirements.backend.txt${NC}"

echo -e "${YELLOW}📝 Atualizando comentário nos arquivos...${NC}"
sed -i '1i# Arquivo gerado automaticamente a partir do requirements.txt principal - 12/06/2025' config/requirements.notorch.txt
sed -i '1i# Arquivo gerado automaticamente a partir do requirements.txt principal - 12/06/2025' config/requirements.backend.txt

echo -e "\n${GREEN}${BOLD}✅ REORGANIZAÇÃO CONCLUÍDA!${NC}"
echo -e "${YELLOW}Os arquivos requirements foram reorganizados da seguinte forma:${NC}"
echo -e " - ${BLUE}requirements.txt${NC} - Arquivo principal na raiz (completo)"
echo -e " - ${BLUE}config/requirements.txt${NC} - Cópia do arquivo principal na pasta config"
echo -e " - ${BLUE}config/requirements.notorch.txt${NC} - Versão sem PyTorch"
echo -e " - ${BLUE}config/requirements.backend.txt${NC} - Versão com dependências essenciais"
echo -e "\n${YELLOW}Para instalar todas as dependências:${NC}"
echo -e "${BLUE}pip install -r requirements.txt${NC}"
echo -e "\n${YELLOW}Para instalar sem PyTorch:${NC}"
echo -e "${BLUE}pip install -r config/requirements.notorch.txt${NC}"
echo -e "\n${YELLOW}Para instalar apenas dependências essenciais do backend:${NC}"
echo -e "${BLUE}pip install -r config/requirements.backend.txt${NC}"
