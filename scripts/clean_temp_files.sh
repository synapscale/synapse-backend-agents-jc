#!/bin/bash
# Script para limpeza de arquivos temporários e cache do projeto
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🧹 LIMPEZA DE ARQUIVOS TEMPORÁRIOS${NC}"
echo -e "${BLUE}===============================================${NC}"

# Remover arquivos de cache Python
echo -e "${YELLOW}Removendo arquivos de cache Python...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type f -name ".coverage" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type d -name "*.egg" -exec rm -rf {} +
find . -type d -name ".eggs" -exec rm -rf {} +

# Remover logs e arquivos temporários
echo -e "${YELLOW}Removendo logs e arquivos temporários...${NC}"
find . -type f -name "*.log" -delete
find ./storage/temp -type f -delete 2>/dev/null
find ./storage/uploads -type f -mtime +7 -delete 2>/dev/null

# Limpar diretório .mypy_cache se existir
if [ -d ".mypy_cache" ]; then
    echo -e "${YELLOW}Removendo cache do mypy...${NC}"
    rm -rf .mypy_cache
fi

# Limpar arquivos temporários de IDE
echo -e "${YELLOW}Removendo arquivos temporários de IDE...${NC}"
find . -type d -name ".idea" -exec rm -rf {} +
find . -type d -name ".vscode" -exec rm -rf {} +
find . -type f -name ".DS_Store" -delete

echo -e "${GREEN}${BOLD}✅ Limpeza concluída!${NC}"
echo -e "${BLUE}O repositório agora está livre de arquivos temporários e caches.${NC}"
