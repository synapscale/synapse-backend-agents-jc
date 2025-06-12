#!/bin/bash
# Script para reorganização e limpeza completa do repositório SynapScale Backend
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}🔄 REORGANIZAÇÃO DO REPOSITÓRIO SYNAPSCALE${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "Data de execução: $(date)"
echo ""

# Função para confirmação
confirm() {
    read -p "❓ $1 (s/n): " response
    case "$response" in
        [sS]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Função para criar backup antes de iniciar
create_backup() {
    echo -e "${YELLOW}📦 Criando backup do repositório antes das alterações...${NC}"
    backup_dir="../synapscale_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Exclusões para o backup
    rsync -av --exclude ".git" --exclude "venv*" --exclude "__pycache__" \
          --exclude "*.pyc" --exclude "node_modules" --exclude ".pytest_cache" \
          ./ "$backup_dir"
    
    echo -e "${GREEN}✅ Backup criado em: $backup_dir${NC}"
    echo ""
}

# 1. LIMPEZA DE SCRIPTS DUPLICADOS/OBSOLETOS
cleanup_scripts() {
    echo -e "${YELLOW}${BOLD}🧹 FASE 1: LIMPEZA DE SCRIPTS OBSOLETOS${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Lista de scripts redundantes a serem removidos
    scripts_to_remove=(
        "clean_repo.sh"             # Será substituído por este script
        "finalize_reorganization.sh" # Será consolidado aqui
        "verify_organization.sh"
        "reorganize.sh"
        "auto_setup.sh"
        "show_summary.sh"
    )
    
    for script in "${scripts_to_remove[@]}"; do
        if [ -f "$script" ]; then
            echo -e "${RED}🗑️ Removendo script obsoleto:${NC} $script"
            rm -f "$script"
        fi
    done
    
    echo -e "${GREEN}✅ Limpeza de scripts concluída${NC}"
    echo ""
}

# 2. LIMPEZA DE DOCUMENTAÇÃO REDUNDANTE
cleanup_docs() {
    echo -e "${YELLOW}${BOLD}📚 FASE 2: LIMPEZA DE DOCUMENTAÇÃO REDUNDANTE${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Lista de documentos redundantes ou desatualizados
    docs_to_remove=(
        "docs/FINAL_VALIDATION.md"
        "docs/ENV_SETUP_COMPLETE.md"
        "docs/GUIA_CONFIGURACAO_ENV.md"
        "docs/GUIA_MASCARAMENTO_ENV.md"
        "docs/MASCARAMENTO_DESATIVADO.md"
        "docs/PROGRESSO_OTIMIZACAO.md"
        "docs/CORREÇÕES_E_USO_BACKEND.md"
        "docs/🎉 SynapScale Backend - RELATÓRIO FINAL 100% COMPLETO.md"
        "docs/GUIA-PRODUCAO-COMPLETO.md"
        "docs/GUIA_COMPLETO_SYNAPSCALE.md"
    )
    
    for doc in "${docs_to_remove[@]}"; do
        if [ -f "$doc" ]; then
            echo -e "${RED}🗑️ Removendo documentação redundante:${NC} $doc"
            rm -f "$doc"
        fi
    done
    
    echo -e "${GREEN}✅ Limpeza de documentação concluída${NC}"
    echo ""
}

# 3. CONSOLIDAÇÃO DA DOCUMENTAÇÃO ESSENCIAL
consolidate_docs() {
    echo -e "${YELLOW}${BOLD}📝 FASE 3: CONSOLIDAÇÃO DA DOCUMENTAÇÃO ESSENCIAL${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Garantir que diretórios principais de documentação existam
    mkdir -p docs/api
    mkdir -p docs/guides
    mkdir -p docs/architecture
    
    # Documentos a serem movidos para locais apropriados
    if [ -f "docs/development_guide.md" ] && [ ! -f "docs/guides/development.md" ]; then
        echo -e "${BLUE}📋 Movendo:${NC} docs/development_guide.md → docs/guides/development.md"
        mv "docs/development_guide.md" "docs/guides/development.md"
    fi
    
    if [ -f "docs/architecture.md" ] && [ ! -f "docs/architecture/overview.md" ]; then
        echo -e "${BLUE}📋 Movendo:${NC} docs/architecture.md → docs/architecture/overview.md"
        mv "docs/architecture.md" "docs/architecture/overview.md"
    fi
    
    if [ -f "docs/guia_rapido_api.md" ] && [ ! -f "docs/api/quick_guide.md" ]; then
        echo -e "${BLUE}📋 Movendo:${NC} docs/guia_rapido_api.md → docs/api/quick_guide.md"
        mv "docs/guia_rapido_api.md" "docs/api/quick_guide.md"
    fi
    
    echo -e "${GREEN}✅ Consolidação de documentação concluída${NC}"
    echo ""
}

# 4. REORGANIZAR ESTRUTURA DE ARQUIVOS
reorganize_files() {
    echo -e "${YELLOW}${BOLD}📁 FASE 4: REORGANIZAÇÃO DE ESTRUTURA${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Garantir que todas as pastas principais existam
    main_dirs=("config" "src" "tests" "tools" "scripts" "docs" "alembic" "deployment")
    for dir in "${main_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            echo -e "${BLUE}📁 Criando diretório:${NC} $dir"
            mkdir -p "$dir"
        fi
    done
    
    # Mover arquivos de configuração espalhados
    if [ -f "pyproject.toml" ] && [ ! -f "config/pyproject.toml" ]; then
        echo -e "${BLUE}🔧 Movendo:${NC} pyproject.toml → config/pyproject.toml"
        mv "pyproject.toml" "config/pyproject.toml"
    fi
    
    # Reorganizar scripts espalhados
    script_files=$(find . -maxdepth 1 -name "*.sh" ! -name "setup.sh" ! -name "dev.sh" ! -name "prod.sh")
    for script in $script_files; do
        script_name=$(basename "$script")
        if [ ! -f "scripts/$script_name" ]; then
            echo -e "${BLUE}🔧 Movendo:${NC} $script_name → scripts/$script_name"
            mv "$script" "scripts/$script_name"
        fi
    done
    
    echo -e "${GREEN}✅ Reorganização de estrutura concluída${NC}"
    echo ""
}

# 5. ATUALIZAR README COM A NOVA ESTRUTURA
update_readme() {
    echo -e "${YELLOW}${BOLD}📝 FASE 5: ATUALIZANDO README.md${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Gerar estrutura atual do projeto
    echo -e "${BLUE}📊 Gerando estrutura de diretórios atual...${NC}"
    tree -L 2 -I 'venv*|__pycache__|.git|.pytest_cache|*.egg-info' > /tmp/project_structure.txt
    
    echo -e "${GREEN}✅ README.md será atualizado manualmente após revisão${NC}"
    echo ""
}

# 6. FINALIZAÇÃO E VERIFICAÇÃO
verify_organization() {
    echo -e "${YELLOW}${BOLD}🔍 FASE 6: VERIFICAÇÃO FINAL${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Verificar pastas principais
    main_dirs=("src" "config" "tests" "docs" "scripts")
    all_ok=true
    
    for dir in "${main_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✓ Diretório ${dir}/ existe${NC}"
        else
            echo -e "${RED}✗ Diretório ${dir}/ está faltando${NC}"
            all_ok=false
        fi
    done
    
    # Verificar scripts essenciais
    essential_files=("setup.sh" "dev.sh" "prod.sh")
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓ Arquivo ${file} existe${NC}"
        else
            echo -e "${RED}✗ Arquivo essencial ${file} está faltando${NC}"
            all_ok=false
        fi
    done
    
    if [ "$all_ok" = true ]; then
        echo -e "\n${GREEN}${BOLD}✅ VERIFICAÇÃO FINAL: SUCESSO${NC}"
        echo -e "${GREEN}O repositório foi reorganizado com sucesso!${NC}"
    else
        echo -e "\n${YELLOW}${BOLD}⚠️ VERIFICAÇÃO FINAL: ATENÇÃO${NC}"
        echo -e "${YELLOW}A reorganização foi concluída, mas alguns itens essenciais estão faltando.${NC}"
        echo -e "${YELLOW}Verifique os itens marcados acima e corrija conforme necessário.${NC}"
    fi
}

# Exibir instruções após reorganização
show_next_steps() {
    echo -e "\n${BLUE}===============================================${NC}"
    echo -e "${GREEN}${BOLD}🚀 PRÓXIMOS PASSOS${NC}"
    echo -e "${BLUE}===============================================${NC}"
    echo -e ""
    echo -e "${YELLOW}1. Revise a lista de documentos e scripts removidos${NC}"
    echo -e "${YELLOW}2. Confira a estrutura de diretórios atualizada${NC}"
    echo -e "${YELLOW}3. Atualize o README.md com a nova estrutura, se necessário${NC}"
    echo -e "${YELLOW}4. Execute os testes para garantir que tudo continua funcionando:${NC}"
    echo -e "   ${BLUE}$ ./scripts/run_tests.sh${NC}"
    echo -e ""
    echo -e "${GREEN}Para iniciar o servidor:${NC}"
    echo -e "  ${BLUE}$ ./dev.sh${NC}  ${GREEN}# Ambiente de desenvolvimento${NC}"
    echo -e "  ${BLUE}$ ./prod.sh${NC} ${GREEN}# Ambiente de produção${NC}"
    echo -e ""
}

# EXECUÇÃO PRINCIPAL
main() {
    # Mostrar plano de execução
    echo -e "${YELLOW}Este script executará as seguintes ações:${NC}"
    echo -e "  ${BLUE}1. Criar backup do repositório${NC}"
    echo -e "  ${BLUE}2. Remover scripts obsoletos e duplicados${NC}"
    echo -e "  ${BLUE}3. Limpar documentação redundante ou desatualizada${NC}"
    echo -e "  ${BLUE}4. Consolidar e organizar documentação essencial${NC}"
    echo -e "  ${BLUE}5. Reorganizar estrutura de arquivos${NC}"
    echo -e "  ${BLUE}6. Verificar estrutura final${NC}"
    echo ""
    
    if confirm "Deseja continuar com a reorganização?"; then
        create_backup
        cleanup_scripts
        cleanup_docs
        consolidate_docs
        reorganize_files
        update_readme
        verify_organization
        show_next_steps
    else
        echo -e "${YELLOW}⚠️ Reorganização cancelada pelo usuário${NC}"
    fi
}

# Iniciar execução
main
