#!/bin/bash
# Script para limpar arquivos adicionais na raiz do repositório
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🧹 LIMPEZA FINAL DO REPOSITÓRIO${NC}"
echo -e "${BLUE}===============================================${NC}"

# Criar diretório para os scripts Python de utilidade
mkdir -p tools/utils

# 1. Mover scripts Python de utilidade para o diretório apropriado
echo -e "${YELLOW}🔄 Movendo scripts Python de utilidade...${NC}"

# Backup dos scripts
mkdir -p backup/root_scripts

if [ -f "propagate_env.py" ]; then
    cp propagate_env.py backup/root_scripts/
    mv propagate_env.py tools/utils/
    echo -e "${GREEN}✅ Movido: propagate_env.py → tools/utils/${NC}"
fi

if [ -f "validate_setup.py" ]; then
    cp validate_setup.py backup/root_scripts/
    mv validate_setup.py tools/utils/
    echo -e "${GREEN}✅ Movido: validate_setup.py → tools/utils/${NC}"
fi

# 2. Remover quick_reorganize.sh (redundante)
if [ -f "quick_reorganize.sh" ]; then
    cp quick_reorganize.sh backup/root_scripts/
    rm quick_reorganize.sh
    echo -e "${RED}🗑️ Removido: quick_reorganize.sh (redundante)${NC}"
fi

# 3. Verificar qualquer outro arquivo que não deveria estar na raiz
echo -e "${YELLOW}🔍 Verificando outros arquivos na raiz...${NC}"

# Lista de arquivos permitidos na raiz
ALLOWED_FILES=(
    ".env"
    ".env.example"
    ".gitignore"
    "LICENSE"
    "README.md"
    "dev.sh"
    "prod.sh"
    "requirements.txt"
    "setup.sh"
    "setup_complete.py"
)

# Lista de diretórios permitidos na raiz
ALLOWED_DIRS=(
    "alembic"
    "backup"
    "config"
    "deployment"
    "docs"
    "migrations"
    "scripts"
    "setup"
    "src"
    "storage"
    "tests"
    "tools"
    "venv"
    "workflows"
    ".git"
)

# Buscar arquivos adicionais na raiz
for file in $(find . -maxdepth 1 -type f ! -path "./.*" | sed 's|^\./||'); do
    # Verificar se o arquivo está na lista de permitidos
    if [[ ! " ${ALLOWED_FILES[@]} " =~ " $file " ]]; then
        echo -e "${YELLOW}⚠️ Arquivo não reconhecido na raiz:${NC} $file"
        
        # Perguntar o que fazer com o arquivo
        echo -e "O que deseja fazer com este arquivo?"
        echo -e "  ${BLUE}1)${NC} Mover para tools/utils/"
        echo -e "  ${BLUE}2)${NC} Mover para scripts/"
        echo -e "  ${BLUE}3)${NC} Mover para backup/"
        echo -e "  ${BLUE}4)${NC} Ignorar (manter na raiz)"
        read -p "Escolha uma opção (1-4): " option
        
        case $option in
            1)
                cp "$file" "backup/root_scripts/"
                mv "$file" "tools/utils/"
                echo -e "${GREEN}✅ Movido: $file → tools/utils/${NC}"
                ;;
            2)
                cp "$file" "backup/root_scripts/"
                mv "$file" "scripts/"
                echo -e "${GREEN}✅ Movido: $file → scripts/${NC}"
                ;;
            3)
                mv "$file" "backup/root_scripts/"
                echo -e "${GREEN}✅ Movido: $file → backup/root_scripts/${NC}"
                ;;
            *)
                echo -e "${BLUE}ℹ️ Mantido na raiz: $file${NC}"
                ;;
        esac
    fi
done

# 4. Atualizar scripts que possam referenciar os arquivos movidos
echo -e "${YELLOW}🔄 Atualizando referências aos arquivos movidos...${NC}"

# Arquivo setup.sh
if [ -f "setup.sh" ]; then
    sed -i 's|python validate_setup.py|python tools/utils/validate_setup.py|g' setup.sh
    sed -i 's|python propagate_env.py|python tools/utils/propagate_env.py|g' setup.sh
fi

# Arquivo dev.sh
if [ -f "dev.sh" ]; then
    sed -i 's|python validate_setup.py|python tools/utils/validate_setup.py|g' dev.sh
    sed -i 's|python propagate_env.py|python tools/utils/propagate_env.py|g' dev.sh
fi

# Arquivo prod.sh
if [ -f "prod.sh" ]; then
    sed -i 's|python validate_setup.py|python tools/utils/validate_setup.py|g' prod.sh
    sed -i 's|python propagate_env.py|python tools/utils/propagate_env.py|g' prod.sh
fi

echo -e "${GREEN}${BOLD}🎉 LIMPEZA FINAL CONCLUÍDA!${NC}"
echo -e "${YELLOW}A raiz do repositório agora está organizada e limpa.${NC}"
echo -e "${BLUE}✨ Executado em: $(date)${NC}"
