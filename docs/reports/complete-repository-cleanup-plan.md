# 🎯 PLANO COMPLETO DE LIMPEZA DO REPOSITÓRIO SYNAPSCALE BACKEND

## 📊 SITUAÇÃO ATUAL ANALISADA
**Total de arquivos na raiz:** ~65 arquivos (incluindo diretórios)

### **🚨 PROBLEMAS IDENTIFICADOS:**
- Múltiplos scripts SQL de migração na raiz
- Logs temporários e arquivos de debug
- Scripts de instalação e setup dispersos
- Documentos de análise/relatórios na raiz
- Backups de arquivos JSON
- Scripts de limpeza temporários

---

## 📋 CATEGORIZAÇÃO COMPLETA DOS ARQUIVOS

### ✅ **MANTER NA RAIZ (Obrigatórios/Permitidos)**

#### **Configuração Essencial do Projeto**
```bash
# Arquivos fundamentais que DEVEM permanecer na raiz
README.md                    # ✅ Documentação principal
LICENSE                      # ✅ Licença do projeto
.gitignore                   # ✅ Configuração Git
requirements.txt             # ✅ Dependências Python
pyproject.toml              # ✅ Configuração Python/Poetry
pytest.ini                  # ✅ Configuração de testes
alembic.ini                 # ✅ Configuração Alembic
tasks.json                  # ✅ Configuração Taskmaster
```

#### **Arquivos de Configuração/Ambiente**
```bash
.env                        # ✅ Variáveis de ambiente (desenvolvimento)
.env.example               # ✅ Template de variáveis
.blackboxrules             # ✅ Regras do Blackbox AI
.clinerules                # ✅ Regras do Cline AI
.roomodes                  # ✅ Configuração Roo AI
```

#### **Scripts Operacionais Principais**
```bash
dev.sh                     # ✅ Script de desenvolvimento
prod.sh                    # ✅ Script de produção
setup.sh                  # ✅ Setup inicial do projeto
run_with_memory_bank.py    # ✅ Script específico do projeto
```

#### **Dados e APIs**
```bash
current_openapi.json       # ✅ Schema OpenAPI atual
synapse.db                 # ✅ Banco de dados SQLite (dev)
```

#### **Documentação de Agentes (Temporariamente permitida)**
```bash
AGENTS.md                  # ⚠️ Permitido (configuração de agentes)
CLAUDE.md                  # ⚠️ Permitido (configuração Claude)
```

---

### 🔄 **REORGANIZAR (Mover para pastas adequadas)**

#### **Scripts de Database/Migration → `migrations/` ou `scripts/database/`**
```bash
rls_policies.sql                    → migrations/sql/rls_policies.sql
rls_policies_admin_fix.sql          → migrations/sql/rls_policies_admin_fix.sql
rls_policies_batch2.sql             → migrations/sql/rls_policies_batch2.sql
rls_policies_batch3.sql             → migrations/sql/rls_policies_batch3.sql
```

#### **Scripts de Instalação/Setup → `setup/scripts/`**
```bash
install-gemini-cli.sh               → setup/scripts/install-gemini-cli.sh
install_memory_bank.sh              → setup/scripts/install_memory_bank.sh
cleanup_tests.sh                   → setup/scripts/cleanup_tests.sh
organize_repository.sh              → setup/scripts/organize_repository.sh
```

#### **Documentação de API/Segurança → `docs/`**
```bash
AGENTS_API_DOCUMENTATION.md         → docs/api/agents-api.md
SECURITY_API_KEYS.md                → docs/security/api-keys.md
```

#### **Relatórios/Análises → `docs/reports/`**
```bash
CLEANUP_REPORT.md                   → docs/reports/cleanup-report.md
REPOSITORY_CLEANUP_ANALYSIS.md      → docs/reports/repository-analysis.md
performance_report.txt              → docs/reports/performance-report.txt
```

#### **Logs → `logs/`**
```bash
init-debug.log                      → logs/init-debug.log
organization.log                    → logs/organization.log
server.log                          → logs/server.log
```

#### **Arquivos de Build/Coverage → `build/` ou `.build/`**
```bash
coverage.xml                        → build/coverage.xml
```

---

### 🗑️ **REMOVER (Temporários/Redundantes/Obsoletos)**

#### **Backups Automáticos**
```bash
current_openapi.json.backup         # 🗑️ Backup automático - pode ser removido
```

#### **Diretórios de Backup Temporários**
```bash
organization_backup_*               # 🗑️ Backups do script de organização
..bfg-report/                       # 🗑️ Relatório do BFG (ferramenta de limpeza Git)
```

#### **Arquivos de Cache/Temporários**
```bash
.ruff_cache/                        # 🗑️ Cache do Ruff (pode ser regenerado)
.pytest_cache/                      # 🗑️ Cache do pytest (pode ser regenerado)  
htmlcov/                            # 🗑️ Relatório HTML de coverage (pode ser regenerado)
.benchmarks/                        # 🗑️ Cache de benchmarks (se temporário)
~/                                  # 🗑️ Diretório home acidental
```

---

## 🚀 **PLANO DE EXECUÇÃO DEFINITIVO**

### **Fase 1: Preparação**
```bash
# Criar estrutura de diretórios necessária
mkdir -p migrations/sql
mkdir -p setup/scripts  
mkdir -p docs/{api,security,reports}
mkdir -p logs
mkdir -p build
```

### **Fase 2: Reorganização de Scripts SQL**
```bash
# Mover arquivos SQL para migrations
mv rls_policies*.sql migrations/sql/
```

### **Fase 3: Reorganização de Scripts de Setup**
```bash
# Mover scripts de instalação e organização
mv install-*.sh setup/scripts/
mv install_*.sh setup/scripts/
mv cleanup_tests.sh setup/scripts/
mv organize_repository.sh setup/scripts/
```

### **Fase 4: Reorganização de Documentação**
```bash
# Mover documentações para docs/
mv AGENTS_API_DOCUMENTATION.md docs/api/agents-api.md
mv SECURITY_API_KEYS.md docs/security/api-keys.md
mv CLEANUP_REPORT.md docs/reports/cleanup-report.md
mv REPOSITORY_CLEANUP_ANALYSIS.md docs/reports/repository-analysis.md
mv performance_report.txt docs/reports/performance-report.txt
```

### **Fase 5: Reorganização de Logs**
```bash
# Mover logs para diretório apropriado
mv *.log logs/
```

### **Fase 6: Reorganização de Build Artifacts**
```bash
# Mover arquivos de build
mv coverage.xml build/
```

### **Fase 7: Limpeza de Temporários**
```bash
# Remover backups e temporários
rm -f current_openapi.json.backup
rm -rf organization_backup_*
rm -rf ..bfg-report/
rm -rf .ruff_cache/
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -rf .benchmarks/
rm -rf ~/  # Apenas se for um diretório acidental vazio
```

---

## 📊 **ESTRUTURA FINAL ESPERADA**

### **Raiz Limpa (21 arquivos essenciais)**
```
synapse-backend-agents-jc/
├── README.md                       # Documentação principal
├── LICENSE                         # Licença
├── .gitignore                      # Config Git
├── requirements.txt                # Dependências
├── pyproject.toml                  # Config Python
├── pytest.ini                     # Config testes
├── alembic.ini                     # Config Alembic
├── tasks.json                      # Config Taskmaster
├── .env                           # Vars ambiente (dev)
├── .env.example                   # Template vars
├── .blackboxrules                 # Regras Blackbox
├── .clinerules                    # Regras Cline
├── .roomodes                      # Config Roo
├── dev.sh                         # Script desenvolvimento
├── prod.sh                        # Script produção  
├── setup.sh                       # Setup inicial
├── run_with_memory_bank.py        # Script específico
├── current_openapi.json           # Schema OpenAPI
├── synapse.db                     # DB SQLite
├── AGENTS.md                      # Config agentes
└── CLAUDE.md                      # Config Claude
```

### **Estrutura Organizada**
```
├── migrations/sql/                 # Scripts SQL organizados
├── setup/scripts/                 # Scripts de instalação
├── docs/
│   ├── api/                       # Docs da API
│   ├── security/                  # Docs de segurança  
│   └── reports/                   # Relatórios e análises
├── logs/                          # Todos os logs
├── build/                         # Artifacts de build
└── [outros diretórios existentes mantidos]
```

---

## ⚡ **SCRIPT DE EXECUÇÃO AUTOMÁTICA**

```bash
#!/bin/bash
# cleanup_repository_definitive.sh

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎯 INICIANDO LIMPEZA DEFINITIVA DO REPOSITÓRIO${NC}"

# Backup de segurança
BACKUP_DIR="final_cleanup_backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}📦 Criando backup em $BACKUP_DIR${NC}"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null || true

# Fase 1: Criar estrutura
echo -e "${BLUE}📁 Criando estrutura de diretórios${NC}"
mkdir -p migrations/sql
mkdir -p setup/scripts  
mkdir -p docs/{api,security,reports}
mkdir -p logs
mkdir -p build

# Fase 2: Mover SQLs
echo -e "${BLUE}🗄️ Movendo scripts SQL${NC}"
[ -f "rls_policies.sql" ] && mv rls_policies.sql migrations/sql/
[ -f "rls_policies_admin_fix.sql" ] && mv rls_policies_admin_fix.sql migrations/sql/
[ -f "rls_policies_batch2.sql" ] && mv rls_policies_batch2.sql migrations/sql/
[ -f "rls_policies_batch3.sql" ] && mv rls_policies_batch3.sql migrations/sql/

# Fase 3: Mover scripts de setup
echo -e "${BLUE}⚙️ Movendo scripts de setup${NC}"
[ -f "install-gemini-cli.sh" ] && mv install-gemini-cli.sh setup/scripts/
[ -f "install_memory_bank.sh" ] && mv install_memory_bank.sh setup/scripts/
[ -f "cleanup_tests.sh" ] && mv cleanup_tests.sh setup/scripts/
[ -f "organize_repository.sh" ] && mv organize_repository.sh setup/scripts/

# Fase 4: Mover documentação
echo -e "${BLUE}📚 Movendo documentação${NC}"
[ -f "AGENTS_API_DOCUMENTATION.md" ] && mv AGENTS_API_DOCUMENTATION.md docs/api/agents-api.md
[ -f "SECURITY_API_KEYS.md" ] && mv SECURITY_API_KEYS.md docs/security/api-keys.md
[ -f "CLEANUP_REPORT.md" ] && mv CLEANUP_REPORT.md docs/reports/cleanup-report.md
[ -f "REPOSITORY_CLEANUP_ANALYSIS.md" ] && mv REPOSITORY_CLEANUP_ANALYSIS.md docs/reports/repository-analysis.md
[ -f "performance_report.txt" ] && mv performance_report.txt docs/reports/performance-report.txt

# Fase 5: Mover logs
echo -e "${BLUE}📋 Movendo logs${NC}"
find . -maxdepth 1 -name "*.log" -exec mv {} logs/ \; 2>/dev/null || true

# Fase 6: Mover build artifacts
echo -e "${BLUE}🔨 Movendo artifacts de build${NC}"
[ -f "coverage.xml" ] && mv coverage.xml build/

# Fase 7: Limpeza de temporários
echo -e "${BLUE}🗑️ Removendo arquivos temporários${NC}"
[ -f "current_openapi.json.backup" ] && rm -f current_openapi.json.backup
rm -rf organization_backup_* 2>/dev/null || true
rm -rf ..bfg-report/ 2>/dev/null || true
rm -rf .ruff_cache/ 2>/dev/null || true
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true
rm -rf .benchmarks/ 2>/dev/null || true

# Verificação final
echo -e "${GREEN}✅ LIMPEZA CONCLUÍDA!${NC}"
echo -e "${BLUE}📊 Arquivos na raiz após limpeza:${NC}"
ls -la | grep "^-" | wc -l
echo -e "${BLUE}📦 Backup disponível em: $BACKUP_DIR${NC}"
```

---

## 🎯 **BENEFÍCIOS ESPERADOS**

### **Antes da Limpeza:**
- ❌ ~65 arquivos/diretórios na raiz
- ❌ Scripts SQL dispersos
- ❌ Logs e temporários misturados
- ❌ Documentação desorganizada
- ❌ Backups acumulados

### **Após a Limpeza:**
- ✅ ~21 arquivos essenciais na raiz
- ✅ Scripts SQL organizados em `migrations/sql/`
- ✅ Scripts de setup em `setup/scripts/`
- ✅ Documentação estruturada em `docs/`
- ✅ Logs centralizados em `logs/`
- ✅ Build artifacts em `build/`
- ✅ Conformidade com regras estabelecidas

### **Impacto na Produtividade:**
- 🚀 **Navegação mais rápida:** Localização intuitiva de recursos
- 🔍 **Busca eficiente:** Arquivos categorizados por função
- 🛠️ **Manutenção facilitada:** Estrutura padronizada
- 📋 **Onboarding acelerado:** Organização clara para novos devs
- 🔄 **CI/CD otimizado:** Caminhos previsíveis para automação

---

## ⚠️ **IMPORTANTE: VALIDAÇÃO PÓS-LIMPEZA**

```bash
# Verificar que não há arquivos órfãos críticos na raiz
find . -maxdepth 1 -type f -name "*.py" | grep -v "run_with_memory_bank.py" | wc -l
# Resultado esperado: 0

# Verificar que todos os scripts SQL foram movidos
find . -maxdepth 1 -name "*.sql" | wc -l  
# Resultado esperado: 0

# Verificar que logs foram movidos
find . -maxdepth 1 -name "*.log" | wc -l
# Resultado esperado: 0

# Testar que aplicação ainda funciona
python -m pytest tests/ --maxfail=1
```

---

> **🎯 Meta:** Transformar repositório caótico em estrutura organizada e produtiva, seguindo as melhores práticas estabelecidas nas regras do projeto. 