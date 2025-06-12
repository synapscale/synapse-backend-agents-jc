#!/bin/bash
# =============================================================================
# SYNAPSCALE BACKEND - SCRIPT MASTER DE INICIALIZAÇÃO
# =============================================================================
# Este é o script principal que você deve executar
# Ele faz ABSOLUTAMENTE TUDO automaticamente
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funções
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "${PURPLE}$1${NC}"; }

# Header impressionante
clear
echo "============================================================================="
log_header "🚀 SYNAPSCALE BACKEND - CONFIGURAÇÃO AUTOMÁTICA COMPLETA"
echo "============================================================================="
log_info "✨ TUDO será configurado automaticamente"
log_info "📝 Você só precisa preencher o .env no final"
log_info "🎯 100% automático - Zero trabalho manual"
echo "============================================================================="

# Verificar se é a primeira execução
if [ ! -f ".env" ] && [ ! -d "venv" ]; then
    log_header "🔧 PRIMEIRA EXECUÇÃO - SETUP COMPLETO"
    log_info "Executando configuração inicial completa..."
    
    # Executar setup completo
    if ./auto_setup.sh; then
        log_success "Setup completo executado com sucesso!"
    else
        log_error "Falha no setup inicial"
        exit 1
    fi
else
    log_header "🔄 EXECUÇÃO SUBSEQUENTE - VERIFICAÇÃO E ATUALIZAÇÃO"
    
    # Verificar se precisa atualizar configurações
    log_info "Verificando se configurações precisam ser atualizadas..."
    
    # Ativar ambiente virtual
    if [ -d "venv" ]; then
        log_info "Ativando ambiente virtual..."
        source venv/bin/activate
        log_success "Ambiente virtual ativado"
    else
        log_error "Ambiente virtual não encontrado! Execute o setup inicial."
        exit 1
    fi
    
    # Verificar se .env existe
    if [ ! -f ".env" ]; then
        log_warning "Arquivo .env não encontrado. Criando..."
        python3 setup_complete.py
    fi
    
    # Re-propagar variáveis
    log_info "Atualizando configurações com base no .env..."
    if python3 propagate_env.py; then
        log_success "Configurações atualizadas"
    else
        log_warning "Erro na propagação, mas continuando..."
    fi
fi

# Validação final
log_info "Executando validação final..."
if python3 validate_setup.py; then
    log_success "Validação passou - sistema OK!"
else
    log_warning "Validação encontrou problemas, mas continuando..."
fi

# Verificar configuração do banco
log_info "Verificando configuração do banco de dados..."
if grep -q "DATABASE_URL=postgresql" .env; then
    log_success "DATABASE_URL configurada"
else
    log_warning "DATABASE_URL não configurada adequadamente"
    log_info "Por favor, configure DATABASE_URL no arquivo .env"
    
    # Perguntar se quer editar agora
    read -p "🔧 Quer configurar o DATABASE_URL agora? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Abrindo .env para edição..."
        ${EDITOR:-nano} .env
        
        # Re-propagar após edição
        log_info "Atualizando configurações..."
        python3 propagate_env.py
    fi
fi

# Menu de inicialização
echo ""
echo "============================================================================="
log_header "🎯 ESCOLHA O MODO DE INICIALIZAÇÃO"
echo "============================================================================="
echo "1) 🔧 Desenvolvimento (com reload automático)"
echo "2) 🏭 Produção (otimizado)"
echo "3) 🧪 Apenas validar (não iniciar)"
echo "4) ⚙️  Configurar apenas (sem iniciar)"
echo "5) 📊 Mostrar status atual"
echo "6) 🚪 Sair"
echo "============================================================================="

read -p "Escolha uma opção (1-6): " choice

case $choice in
    1)
        log_header "🔧 INICIANDO MODO DESENVOLVIMENTO"
        log_info "Servidor com reload automático em http://localhost:8000"
        log_info "Documentação em http://localhost:8000/docs"
        ./start_dev_auto.sh
        ;;
    2)
        log_header "🏭 INICIANDO MODO PRODUÇÃO"
        log_info "Servidor otimizado com Gunicorn"
        ./start_prod_auto.sh
        ;;
    3)
        log_header "🧪 EXECUTANDO VALIDAÇÃO COMPLETA"
        python3 validate_setup.py
        ;;
    4)
        log_header "⚙️ EXECUTANDO APENAS CONFIGURAÇÃO"
        python3 setup_complete.py
        python3 propagate_env.py
        log_success "Configuração concluída!"
        ;;
    5)
        log_header "📊 STATUS ATUAL DO SISTEMA"
        echo ""
        log_info "Verificando arquivos essenciais..."
        
        # Verificar arquivos
        files=(".env" "venv" "requirements.txt" "src/synapse/main.py")
        for file in "${files[@]}"; do
            if [ -e "$file" ]; then
                log_success "$file existe"
            else
                log_error "$file não encontrado"
            fi
        done
        
        echo ""
        log_info "Verificando variáveis críticas no .env..."
        if [ -f ".env" ]; then
            if grep -q "SECRET_KEY=.*[a-zA-Z0-9]" .env; then
                log_success "SECRET_KEY configurada"
            else
                log_warning "SECRET_KEY não configurada"
            fi
            
            if grep -q "DATABASE_URL=.*postgresql" .env; then
                log_success "DATABASE_URL configurada"
            else
                log_warning "DATABASE_URL não configurada"
            fi
        else
            log_error "Arquivo .env não encontrado"
        fi
        
        echo ""
        log_info "Para configuração completa, escolha opção 4"
        ;;
    6)
        log_info "Até logo!"
        exit 0
        ;;
    *)
        log_error "Opção inválida"
        exit 1
        ;;
esac
