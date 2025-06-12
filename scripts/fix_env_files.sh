#!/bin/bash
# Script para padronizar arquivos .env no repositório
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🔄 PADRONIZAÇÃO DOS ARQUIVOS .env${NC}"
echo -e "${BLUE}===============================================${NC}"

# Criar diretório de backup
mkdir -p backup/env_files

# Verificar e padronizar o arquivo .env.example
if [ -f ".env.example" ]; then
    echo -e "${BLUE}📄 Arquivo .env.example encontrado...${NC}"
    cp .env.example backup/env_files/
else
    echo -e "${YELLOW}⚠️ Arquivo .env.example não encontrado...${NC}"
    # Se não existir .env.example, vamos verificar .env.template
    if [ -f ".env.template" ]; then
        echo -e "${BLUE}📄 Encontrado .env.template, copiando como .env.example...${NC}"
        cp .env.template .env.example
        cp .env.template backup/env_files/.env.example
    elif [ -f "setup/templates/.env.template" ]; then
        echo -e "${BLUE}📄 Encontrado setup/templates/.env.template, copiando como .env.example...${NC}"
        cp setup/templates/.env.template .env.example
        cp setup/templates/.env.template backup/env_files/.env.example
    else
        echo -e "${RED}❌ Nenhum arquivo template/exemplo encontrado!${NC}"
        echo -e "${YELLOW}Criando um arquivo .env.example básico...${NC}"
        cat > .env.example << 'END'
# ==============================================================================
# SYNAPSCALE BACKEND - ARQUIVO EXEMPLO DE VARIÁVEIS DE AMBIENTE
# COPIE ESTE ARQUIVO COMO .env E CONFIGURE AS VARIÁVEIS
# ==============================================================================

# ============================
# CONFIGURAÇÕES GERAIS
# ============================
ENVIRONMENT=development
DEBUG=true
PROJECT_NAME=SynapScale Backend API
VERSION=2.0.0
API_V1_STR=/api/v1
DESCRIPTION=Plataforma de Automação com IA
SERVER_HOST=http://localhost:8000
HOST=0.0.0.0
PORT=8000

# ============================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_32_CARACTERES
JWT_SECRET_KEY=GERE_UMA_CHAVE_JWT_FORTE_64_CARACTERES
ENCRYPTION_KEY=GERE_UMA_CHAVE_CRIPTOGRAFIA_BASE64_32_BYTES
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================
DATABASE_URL=postgresql://user:password@localhost:5432/synapscale_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=synapscale_db
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_SSLMODE=prefer

# ============================
# CONFIGURAÇÕES DE REDIS
# ============================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://localhost:6379/0

# ============================
# CONFIGURAÇÕES DE IA
# ============================
OPENAI_API_KEY=sua_chave_openai
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDINGS_MODEL=text-embedding-ada-002
ANTHROPIC_API_KEY=sua_chave_anthropic
GOOGLE_API_KEY=sua_chave_google
END
    fi
fi

# Padronizar os templates
if [ -f ".env.template" ]; then
    echo -e "${YELLOW}🗑️ Removendo .env.template redundante (mantido em backup)...${NC}"
    cp .env.template backup/env_files/
    rm -f .env.template
fi

# Criar o template em setup/templates se não existir
mkdir -p setup/templates
if [ ! -f "setup/templates/.env.template" ]; then
    echo -e "${BLUE}📄 Criando setup/templates/.env.template...${NC}"
    cp .env.example setup/templates/.env.template
else
    echo -e "${BLUE}📄 Atualizando setup/templates/.env.template...${NC}"
    cp backup/env_files/setup-templates-.env.template.bak backup/env_files/ 2>/dev/null || true
    cp .env.example setup/templates/.env.template
fi

# Atualizar scripts para apontar para os arquivos .env padrão
echo -e "${BLUE}📝 Atualizando referências nos scripts...${NC}"

# Ajustar setup.sh
if [ -f "setup.sh" ]; then
    echo -e "${BLUE}📄 Ajustando setup.sh...${NC}"
    cp setup.sh backup/setup.sh.bak
    sed -i 's|setup/templates/env.complete|.env.example|g' setup.sh
fi

# Ajustar setup_complete.py
if [ -f "setup_complete.py" ]; then
    echo -e "${BLUE}📄 Ajustando setup_complete.py...${NC}"
    cp setup_complete.py backup/setup_complete.py.bak
    sed -i 's|self.env_template = self.root_path / ".env.template"|self.env_template = self.root_path / ".env.example"|g' setup_complete.py
fi

# Verificar se .env existe, caso não, criar a partir do .env.example
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ Arquivo .env não encontrado...${NC}"
    echo -e "${BLUE}📄 Criando .env a partir de .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Arquivo .env criado! Configure-o com suas credenciais.${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe.${NC}"
fi

echo -e "${GREEN}${BOLD}🎉 Padronização dos arquivos .env concluída com sucesso!${NC}"
echo -e "${YELLOW}Agora o projeto utiliza apenas .env.example e .env${NC}"
