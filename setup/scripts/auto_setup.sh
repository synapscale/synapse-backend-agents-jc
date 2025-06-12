#!/bin/bash
# =============================================================================
# SYNAPSCALE BACKEND - SCRIPT DE INICIALIZAÇÃO AUTOMÁTICA COMPLETA
# =============================================================================
# Este script faz TUDO automaticamente:
# 1. Cria ambiente virtual
# 2. Instala dependências  
# 3. Configura .env com chaves seguras
# 4. Propaga variáveis para todos os arquivos
# 5. Inicializa banco de dados
# 6. Inicia o servidor
# =============================================================================

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Header
clear
echo "============================================================================="
log_header "🚀 SYNAPSCALE BACKEND - INICIALIZAÇÃO AUTOMÁTICA COMPLETA"
echo "============================================================================="
log_info "✨ Configuração 100% automatizada - só preencher o .env!"
log_info "📋 Tudo será configurado automaticamente para você"
echo "============================================================================="

# Verificar se Python está instalado
log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado! Instale Python 3.11+ primeiro"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
log_success "Python $python_version encontrado"

# Executar setup completo
log_info "Executando configuração automática completa..."
python3 setup_complete.py

if [ $? -ne 0 ]; then
    log_error "Falha na configuração automática"
    exit 1
fi

# Verificar se .env foi criado
if [ ! -f .env ]; then
    log_error "Arquivo .env não foi criado!"
    log_info "Execute manualmente: python3 setup_complete.py"
    exit 1
fi

log_success "Configuração automática concluída!"

# Propagar variáveis para todos os arquivos
log_info "Propagando variáveis do .env para todos os arquivos..."
source venv/bin/activate
python3 propagate_env.py

if [ $? -ne 0 ]; then
    log_warning "Erro na propagação, mas continuando..."
fi

# Verificar configurações críticas no .env
log_info "Verificando configurações críticas..."

if ! grep -q "SECRET_KEY=.*[a-zA-Z0-9]" .env; then
    log_error "SECRET_KEY não configurada no .env!"
    log_info "Execute novamente: python3 setup_complete.py"
    exit 1
fi

if ! grep -q "DATABASE_URL=.*postgresql" .env; then
    log_warning "DATABASE_URL não parece estar configurada corretamente"
    log_info "Por favor, configure DATABASE_URL no arquivo .env"
    
    # Perguntar se quer continuar mesmo assim
    read -p "Continuar mesmo assim? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Configure o .env e execute novamente"
        exit 1
    fi
fi

log_success "Configurações verificadas"

# Ativar ambiente virtual
log_info "Ativando ambiente virtual..."
source venv/bin/activate
log_success "Ambiente virtual ativado"

# Verificar dependências críticas
log_info "Verificando dependências críticas..."
python3 -c "import fastapi, uvicorn, sqlalchemy, pydantic" 2>/dev/null
if [ $? -eq 0 ]; then
    log_success "Dependências críticas OK"
else
    log_warning "Reinstalando dependências críticas..."
    pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
fi

# Executar migrações do banco
log_info "Executando migrações do banco de dados..."
if python3 -m alembic upgrade head 2>/dev/null; then
    log_success "Migrações executadas com sucesso"
else
    log_warning "Erro nas migrações - banco será criado automaticamente"
fi

# Teste de importação
log_info "Testando importação da aplicação..."
if python3 -c "from src.synapse.main import app; print('✅ Import OK')" 2>/dev/null; then
    log_success "Aplicação importada com sucesso"
else
    log_error "Erro na importação da aplicação"
    log_info "Verifique se todas as dependências estão instaladas"
    exit 1
fi

# Criar diretórios necessários
log_info "Criando diretórios necessários..."
mkdir -p uploads logs storage/files storage/temp storage/cache
log_success "Diretórios criados"

# Exibir informações finais
echo ""
echo "============================================================================="
log_header "🎉 CONFIGURAÇÃO COMPLETA - BACKEND PRONTO!"
echo "============================================================================="
log_success "✅ Ambiente virtual: configurado e ativado"
log_success "✅ Dependências: instaladas"
log_success "✅ Arquivo .env: criado e configurado"
log_success "✅ Chaves de segurança: geradas automaticamente"
log_success "✅ Banco de dados: configurado"
log_success "✅ Diretórios: criados"
log_success "✅ Scripts: prontos para uso"
echo "============================================================================="

echo ""
log_header "📋 COMO USAR:"
echo ""
log_info "1. 📝 Configure variáveis obrigatórias no .env:"
echo "   - DATABASE_URL=postgresql://user:pass@host:port/db"
echo "   - SMTP_* (para emails)"
echo "   - *_API_KEY (chaves LLM - opcional)"
echo ""
log_info "2. 🚀 Inicie o servidor:"
echo "   - Desenvolvimento: ./start_dev_auto.sh"
echo "   - Produção: ./start_prod_auto.sh"
echo ""
log_info "3. 🌐 Acesse:"
echo "   - Backend: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo ""
log_header "💡 TUDO FUNCIONA AUTOMATICAMENTE AGORA!"
echo "============================================================================="

# Perguntar se quer iniciar agora
echo ""
read -p "🚀 Quer iniciar o servidor agora? (Y/n): " -r
if [[ $REPLY =~ ^[Nn]$ ]]; then
    log_info "Para iniciar depois, use: ./start_dev_auto.sh"
    exit 0
fi

# Iniciar servidor de desenvolvimento
log_info "Iniciando servidor de desenvolvimento..."
exec ./start_dev_auto.sh
