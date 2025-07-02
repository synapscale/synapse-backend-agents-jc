#!/bin/bash
# 🚀 Setup de Automação - Configuração completa do sistema

set -e  # Parar em caso de erro

echo "🚀 SETUP DE AUTOMAÇÃO - Sistema de Manutenção SynapScale"
echo "============================================================"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Verificar se estamos na raiz do projeto
if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
    error "Execute este script na raiz do projeto SynapScale"
fi

log "Verificando estrutura do projeto..."

# Criar diretórios necessários
mkdir -p docs/database
mkdir -p reports/maintenance
mkdir -p logs
mkdir -p scripts/automation

success "Diretórios criados"

# Verificar se .env existe
if [ ! -f ".env" ]; then
    warning "Arquivo .env não encontrado - criando template"
    
    cat > .env << EOF
# === CONFIGURAÇÃO PRINCIPAL DO BANCO ===
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database_name

# === CONFIGURAÇÕES DETALHADAS ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=synapscale
DB_USER=postgres
DB_PASSWORD=password
DB_SSLMODE=require

# === CONFIGURAÇÕES DO SISTEMA ===
DATABASE_SCHEMA=synapscale_db

# === API CONFIGURAÇÃO ===
API_BASE_URL=http://localhost:8000

# === CONFIGURAÇÕES DE USUÁRIOS ===
ADMIN_EMAIL=admin@synapscale.com
ADMIN_PASSWORD=SynapScale2024!
DEFAULT_USER_PASSWORD=DefaultPassword123!
EOF
    
    warning "Configure as variáveis no arquivo .env antes de continuar"
fi

# Verificar dependências Python
log "Verificando dependências Python..."

if ! command -v python3 &> /dev/null; then
    error "Python 3 não encontrado"
fi

if ! python3 -c "import psycopg2" 2>/dev/null; then
    warning "psycopg2 não encontrado - instalando..."
    pip install psycopg2-binary
fi

if ! python3 -c "import requests" 2>/dev/null; then
    warning "requests não encontrado - instalando..."
    pip install requests
fi

success "Dependências Python OK"

# Tornar scripts executáveis
log "Configurando permissões dos scripts..."

chmod +x tools/database/*.py
chmod +x tools/database/setup_automation.sh

success "Permissões configuradas"

# Criar script de execução diária
log "Criando script de automação diária..."

cat > scripts/automation/daily_maintenance.sh << 'EOF'
#!/bin/bash
# 🤖 Manutenção Diária Automatizada

cd "$(dirname "$0")/../.."

echo "🤖 Executando manutenção diária automatizada..."
echo "Iniciado em: $(date)"

# Executar manutenção completa
python tools/database/maintenance_automation.py

# Verificar se há problemas críticos
EXIT_CODE=$?

if [ $EXIT_CODE -eq 1 ]; then
    echo "🚨 PROBLEMAS CRÍTICOS DETECTADOS!"
    echo "Consulte os relatórios em reports/maintenance/"
    
    # Aqui você pode adicionar notificações (email, Slack, etc.)
    # curl -X POST -H 'Content-type: application/json' \
    #   --data '{"text":"🚨 SynapScale: Problemas críticos detectados na manutenção automática!"}' \
    #   YOUR_SLACK_WEBHOOK_URL
    
elif [ $EXIT_CODE -eq 2 ]; then
    echo "⚠️ Avisos detectados - verificação recomendada"
else
    echo "✅ Sistema funcionando perfeitamente!"
fi

echo "Concluído em: $(date)"
EOF

chmod +x scripts/automation/daily_maintenance.sh

success "Script de automação diária criado"

# Criar comando rápido
log "Criando comando rápido de manutenção..."

cat > quick_maintenance.sh << 'EOF'
#!/bin/bash
# 🚀 Manutenção Rápida SynapScale

echo "🚀 Executando manutenção rápida..."
python tools/database/maintenance_automation.py
EOF

chmod +x quick_maintenance.sh

success "Comando rápido criado: ./quick_maintenance.sh"

# Sugerir configuração de cron
log "Configuração de agendamento (cron)..."

echo ""
echo "📅 Para agendar manutenção automática, adicione ao cron:"
echo ""
echo "# Manutenção diária às 02:00"
echo "0 2 * * * cd $(pwd) && ./scripts/automation/daily_maintenance.sh >> logs/maintenance.log 2>&1"
echo ""
echo "Para configurar:"
echo "  crontab -e"
echo "  # Cole a linha acima"
echo ""

# Teste básico
log "Executando teste básico..."

if python3 tools/database/health_check_master.py --help >/dev/null 2>&1; then
    success "Health Check Master funcionando"
else
    error "Erro no Health Check Master"
fi

if python3 tools/database/sync_validator.py --help >/dev/null 2>&1; then
    success "Sync Validator funcionando"
else
    error "Erro no Sync Validator"
fi

if python3 tools/database/doc_generator.py --help >/dev/null 2>&1; then
    success "Doc Generator funcionando"
else
    error "Erro no Doc Generator"
fi

if python3 tools/database/maintenance_automation.py --help >/dev/null 2>&1; then
    success "Maintenance Automation funcionando"
else
    error "Erro no Maintenance Automation"
fi

# Resumo final
echo ""
echo "🎉 SETUP CONCLUÍDO COM SUCESSO!"
echo "================================="
echo ""
echo "📋 Próximos passos:"
echo "1. Configure as variáveis no .env"
echo "2. Execute: ./quick_maintenance.sh"
echo "3. Configure agendamento com cron (opcional)"
echo "4. Monitore relatórios em reports/maintenance/"
echo ""
echo "🛠️ Comandos disponíveis:"
echo "  ./quick_maintenance.sh                           # Manutenção completa"
echo "  python tools/database/health_check_master.py    # Apenas health check"
echo "  python tools/database/sync_validator.py         # Apenas validação de sync"
echo "  python tools/database/doc_generator.py          # Apenas documentação"
echo ""
echo "📊 Dashboards:"
echo "  docs/database/health_dashboard.html             # Dashboard de saúde"
echo "  docs/database/schema.md                         # Documentação do schema"
echo "  reports/maintenance/                            # Relatórios de manutenção"
echo ""
echo "✅ Sistema de manutenção automatizada configurado!"
EOF

chmod +x tools/database/setup_automation.sh

success "Script setup_automation.sh criado com sucesso"
