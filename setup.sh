#!/bin/bash
# Script de setup unificado para SynapScale Backend
# Data: 12/06/2025

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🚀 SYNAPSCALE BACKEND - SETUP${BOLD}${NC}"
echo -e "${BLUE}===============================================${NC}"

# Modo de setup
MODO="basic"  # basic ou complete

# Setup básico
if [ "$MODO" == "basic" ]; then
    # Verificar ambiente virtual
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Criando ambiente virtual Python...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
    fi

    # Ativar ambiente virtual
    source venv/bin/activate
    echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"

    # Instalar dependências
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}📥 Instalando dependências...${NC}"
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Dependências instaladas${NC}"
    else
        echo -e "${RED}❌ Arquivo requirements.txt não encontrado!${NC}"
        exit 1
    fi

    # Configurar .env se não existir
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}📝 Criando arquivo .env a partir do exemplo...${NC}"
            cp .env.example .env
            echo -e "${GREEN}✅ Arquivo .env criado${NC}"
            echo -e "${YELLOW}⚠️ Importante: Edite o arquivo .env e configure suas credenciais!${NC}"
        else
            echo -e "${RED}❌ Arquivo .env.example não encontrado!${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}${BOLD}🎉 Setup básico concluído!${NC}"
    echo -e ""
    echo -e "Para continuar:"
    echo -e "1. ${BLUE}Configure o DATABASE_URL e outras variáveis no arquivo .env${NC}"
    echo -e "2. ${BLUE}Execute ./dev.sh para iniciar o servidor em modo desenvolvimento${NC}"
    echo -e ""

# Setup completo e automatizado
else
    if [ -f "setup_complete.py" ]; then
        echo -e "${YELLOW}🔄 Executando setup completo automatizado...${NC}"
        # Ativar ambiente virtual temporário se necessário
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install python-dotenv pydantic
        else
            source venv/bin/activate
        fi
        
        # Executar setup completo
        python setup_complete.py
    else
        echo -e "${RED}❌ Script setup_complete.py não encontrado!${NC}"
        echo -e "${YELLOW}Executando setup básico ao invés...${NC}"
        
        # Usar o mesmo código do setup básico
        # Verificar ambiente virtual
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}📦 Criando ambiente virtual Python...${NC}"
            python3 -m venv venv
            echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
        fi

        # Ativar ambiente virtual
        source venv/bin/activate
        echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"

        # Instalar dependências
        if [ -f "requirements.txt" ]; then
            echo -e "${YELLOW}📥 Instalando dependências...${NC}"
            pip install --upgrade pip
            pip install -r requirements.txt
            echo -e "${GREEN}✅ Dependências instaladas${NC}"
        else
            echo -e "${RED}❌ Arquivo requirements.txt não encontrado!${NC}"
            exit 1
        fi

        # Configurar .env se não existir
        if [ ! -f ".env" ]; then
            if [ -f ".env.example" ]; then
                echo -e "${YELLOW}📝 Criando arquivo .env a partir do exemplo...${NC}"
                cp .env.example .env
                echo -e "${GREEN}✅ Arquivo .env criado${NC}"
                echo -e "${YELLOW}⚠️ Importante: Edite o arquivo .env e configure suas credenciais!${NC}"
            else
                echo -e "${RED}❌ Arquivo .env.example não encontrado!${NC}"
                exit 1
            fi
        fi
    fi
fi
