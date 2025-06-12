#!/bin/bash
# Script para padronizar scripts de setup
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🔄 PADRONIZAÇÃO DOS SCRIPTS DE SETUP${NC}"
echo -e "${BLUE}===============================================${NC}"

# Criar diretório de backup
mkdir -p backup/setup_scripts

# 1. Backup dos scripts existentes
echo -e "${YELLOW}📦 Criando backup dos scripts existentes...${NC}"

if [ -f "setup.sh" ]; then
    cp setup.sh backup/setup_scripts/
fi

if [ -f "setup_complete.py" ]; then
    cp setup_complete.py backup/setup_scripts/
fi

if [ -f "scripts/setup.sh" ]; then
    cp scripts/setup.sh backup/setup_scripts/scripts-setup.sh
fi

if [ -f "setup/scripts/setup_complete.sh" ]; then
    cp setup/scripts/setup_complete.sh backup/setup_scripts/setup-scripts-setup_complete.sh
fi

# 2. Consolidar scripts
echo -e "${YELLOW}🔄 Consolidando scripts de setup...${NC}"

# 2.1 Manter apenas setup.sh e setup_complete.py na raiz
# Remover scripts redundantes
echo -e "${RED}🗑️ Removendo scripts redundantes...${NC}"

if [ -f "scripts/setup.sh" ]; then
    rm scripts/setup.sh
    echo -e "${RED}🗑️ Removido: scripts/setup.sh${NC}"
fi

if [ -f "setup/scripts/setup_complete.sh" ] && [ -f "setup/scripts/setup_complete.py" ]; then
    rm setup/scripts/setup_complete.sh
    rm setup/scripts/setup_complete.py
    echo -e "${RED}🗑️ Removido: setup/scripts/setup_complete.sh e setup_complete.py${NC}"
fi

# 3. Atualizar setup.sh para usar setup_complete.py
echo -e "${BLUE}📝 Atualizando setup.sh...${NC}"

cat > setup.sh << 'END'
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

# Verificar argumentos
if [ "$1" == "--complete" ] || [ "$1" == "-c" ]; then
    MODO="complete"
    echo -e "${YELLOW}Executando setup completo e automatizado...${NC}"
else
    echo -e "${YELLOW}Executando setup básico...${NC}"
    echo -e "Para setup completo use: ${BLUE}./setup.sh --complete${NC}"
fi

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
END

chmod +x setup.sh

# 4. Adicionar README explicando os scripts de setup
echo -e "${BLUE}📝 Criando documentação sobre os scripts...${NC}"

mkdir -p docs/guides
cat > docs/guides/setup_scripts.md << 'END'
# 🛠️ Scripts de Setup do SynapScale Backend

Este documento explica os scripts de configuração disponíveis no projeto.

## 📋 Resumo

O SynapScale Backend possui dois modos de setup:

1. **Setup Básico** - Configuração manual simples
2. **Setup Completo** - Configuração automatizada e detalhada

## 🔧 Modo Básico

Para iniciar uma configuração básica, execute:

```bash
./setup.sh
```

Este modo:
- Cria um ambiente virtual Python
- Instala dependências do arquivo requirements.txt
- Cria um arquivo .env a partir do .env.example (se não existir)
- Exige configuração manual das variáveis no .env

## ⚙️ Modo Completo

Para uma configuração completa e automatizada, execute:

```bash
./setup.sh --complete
# ou
./setup.sh -c
```

Este modo utiliza o script `setup_complete.py` que:
- Automatiza todo o processo de configuração
- Gera chaves seguras automaticamente
- Cria estrutura de diretórios
- Configura banco de dados
- Oferece um assistente interativo para personalização

## 🤔 Qual escolher?

- **Setup Básico**: Ideal para desenvolvedores que querem controle manual ou para configurações simples.
- **Setup Completo**: Melhor para novos usuários ou para garantir uma configuração correta e completa.

## 📄 Arquivo setup_complete.py

O arquivo `setup_complete.py` é um script Python avançado que automatiza todo o processo de configuração. Ele oferece:

- Validação de ambiente
- Geração segura de chaves
- Configuração de banco de dados
- Verificação de dependências
- Criação de estrutura de diretórios
- Configuração dos arquivos de ambiente

Para executá-lo diretamente:

```bash
python setup_complete.py
```
END

echo -e "${GREEN}${BOLD}🎉 Padronização dos scripts de setup concluída com sucesso!${NC}"
echo -e "${YELLOW}Agora o projeto utiliza apenas:${NC}"
echo -e "  ${BLUE}- setup.sh${NC} - Script principal com modos básico e completo"
echo -e "  ${BLUE}- setup_complete.py${NC} - Script Python avançado para setup completo"
echo -e ""
echo -e "${YELLOW}Documentação disponível em:${NC} ${BLUE}docs/guides/setup_scripts.md${NC}"
