#!/bin/bash

# Script para instalar o Memory Bank no SynapScale Backend

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Instalando Memory Bank ===${NC}"

# Verificar se o diretório memory-bank existe
if [ ! -d "memory-bank" ]; then
    echo -e "${RED}Erro: Diretório memory-bank não encontrado${NC}"
    echo "Certifique-se de estar no diretório raiz do SynapScale Backend"
    exit 1
fi

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado${NC}"
    echo "Por favor, instale o Python 3 antes de continuar"
    exit 1
fi

# Verificar se o pip está instalado
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Erro: pip não encontrado${NC}"
    echo "Por favor, instale o pip antes de continuar"
    exit 1
fi

# Instalar o Memory Bank em modo de desenvolvimento
echo -e "${YELLOW}Instalando Memory Bank em modo de desenvolvimento...${NC}"
pip install -e memory-bank

# Verificar se a instalação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro: Falha ao instalar Memory Bank${NC}"
    exit 1
fi

# Executar as migrações para criar as tabelas no banco de dados
echo -e "${YELLOW}Executando migrações para criar tabelas no banco de dados...${NC}"
python memory-bank/run_migrations.py

# Verificar se as migrações foram bem-sucedidas
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro: Falha ao executar migrações${NC}"
    exit 1
fi

# Configurar variáveis de ambiente
echo -e "${YELLOW}Configurando variáveis de ambiente...${NC}"

# Verificar se o arquivo .env existe
if [ -f ".env" ]; then
    # Verificar se a variável ENABLE_MEMORY_BANK já existe no arquivo .env
    if grep -q "ENABLE_MEMORY_BANK" .env; then
        # Atualizar a variável
        sed -i '' 's/ENABLE_MEMORY_BANK=.*/ENABLE_MEMORY_BANK=true/' .env
    else
        # Adicionar a variável
        echo "ENABLE_MEMORY_BANK=true" >> .env
    fi
    
    # Verificar se a variável MEMORY_BANK_EMBEDDING_MODEL já existe no arquivo .env
    if ! grep -q "MEMORY_BANK_EMBEDDING_MODEL" .env; then
        echo "MEMORY_BANK_EMBEDDING_MODEL=all-MiniLM-L6-v2" >> .env
    fi
    
    # Verificar se a variável MEMORY_BANK_VECTOR_STORE já existe no arquivo .env
    if ! grep -q "MEMORY_BANK_VECTOR_STORE" .env; then
        echo "MEMORY_BANK_VECTOR_STORE=faiss" >> .env
    fi
    
    # Verificar se a variável MEMORY_BANK_MAX_MEMORIES já existe no arquivo .env
    if ! grep -q "MEMORY_BANK_MAX_MEMORIES" .env; then
        echo "MEMORY_BANK_MAX_MEMORIES=1000" >> .env
    fi
else
    # Criar o arquivo .env
    echo "ENABLE_MEMORY_BANK=true" > .env
    echo "MEMORY_BANK_EMBEDDING_MODEL=all-MiniLM-L6-v2" >> .env
    echo "MEMORY_BANK_VECTOR_STORE=faiss" >> .env
    echo "MEMORY_BANK_MAX_MEMORIES=1000" >> .env
fi

# Tornar o script run_with_memory_bank.py executável
chmod +x run_with_memory_bank.py

echo -e "${GREEN}Memory Bank instalado com sucesso!${NC}"
echo -e "${YELLOW}Para executar o SynapScale Backend com o Memory Bank, use:${NC}"
echo -e "${GREEN}./run_with_memory_bank.py${NC}"
echo -e "${YELLOW}Ou configure a variável de ambiente ENABLE_MEMORY_BANK=true antes de iniciar o SynapScale Backend normalmente.${NC}"

exit 0
