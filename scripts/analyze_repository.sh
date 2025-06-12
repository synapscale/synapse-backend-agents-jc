#!/bin/bash
# Script para analisar o estado do repositório e documentar os arquivos importantes
# Data: 12/06/2025

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}${BOLD}📊 ANÁLISE DO REPOSITÓRIO SYNAPSCALE${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "Data: $(date)"
echo ""

# Diretório atual
REPO_DIR=$(pwd)
TEMP_DIR="/tmp/repo_analysis"
mkdir -p "$TEMP_DIR"

# Função para analisar arquivos Python
analyze_python_files() {
    echo -e "${YELLOW}${BOLD}🐍 ANALISANDO ARQUIVOS PYTHON${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Quantidade de arquivos por diretório
    echo -e "${CYAN}Distribuição de arquivos Python:${NC}"
    find . -name "*.py" | grep -v "__pycache__" | awk -F"/" '{print $2}' | sort | uniq -c | sort -nr
    
    # Arquivos Python mais grandes
    echo -e "\n${CYAN}Arquivos Python mais grandes:${NC}"
    find . -name "*.py" | grep -v "__pycache__" | xargs wc -l 2>/dev/null | sort -nr | head -n 10
    
    echo ""
}

# Função para analisar scripts shell
analyze_shell_scripts() {
    echo -e "${YELLOW}${BOLD}🐚 ANALISANDO SCRIPTS SHELL${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Listar todos os scripts shell
    echo -e "${CYAN}Scripts shell encontrados:${NC}"
    find . -name "*.sh" -type f | sort
    
    # Scripts shell mais utilizados (baseado em data de acesso)
    echo -e "\n${CYAN}Scripts shell mais utilizados:${NC}"
    find . -name "*.sh" -type f -exec ls -la {} \; | sort -k6,8
    
    echo ""
}

# Função para analisar documentação
analyze_documentation() {
    echo -e "${YELLOW}${BOLD}📚 ANALISANDO DOCUMENTAÇÃO${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Quantidade de arquivos de documentação por diretório
    echo -e "${CYAN}Distribuição de arquivos de documentação:${NC}"
    find . -name "*.md" | awk -F"/" '{print $2}' | sort | uniq -c | sort -nr
    
    # Documentação mais completa (por tamanho)
    echo -e "\n${CYAN}Arquivos de documentação mais completos:${NC}"
    find . -name "*.md" | xargs wc -l 2>/dev/null | sort -nr | head -n 10
    
    echo ""
}

# Função para analisar estrutura do projeto
analyze_project_structure() {
    echo -e "${YELLOW}${BOLD}📁 ANALISANDO ESTRUTURA DO PROJETO${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Gerar e exibir estrutura de diretórios
    echo -e "${CYAN}Estrutura de diretórios principal:${NC}"
    tree -L 2 -I 'venv*|__pycache__|.git|.pytest_cache|*.egg-info' > "$TEMP_DIR/structure.txt"
    cat "$TEMP_DIR/structure.txt"
    
    # Analisar diretórios vazios ou possivelmente desnecessários
    echo -e "\n${CYAN}Diretórios vazios ou com poucos arquivos:${NC}"
    find . -type d -not -path "*/__pycache__*" -not -path "*/\.*" -not -path "*/venv*" | while read dir; do
        file_count=$(find "$dir" -type f | wc -l)
        if [ "$file_count" -lt 3 ] && [ "$dir" != "." ]; then
            echo "$dir ($file_count arquivos)"
        fi
    done
    
    echo ""
}

# Função para analisar dependências
analyze_dependencies() {
    echo -e "${YELLOW}${BOLD}📦 ANALISANDO DEPENDÊNCIAS${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    # Verificar arquivos de requisitos
    echo -e "${CYAN}Arquivos de requisitos encontrados:${NC}"
    find . -name "requirements*.txt" | sort
    
    # Se existir, mostrar conteúdo do requirements.txt principal
    main_req="requirements.txt"
    if [ -f "$main_req" ]; then
        echo -e "\n${CYAN}Dependências principais:${NC}"
        grep -v "^#" "$main_req" | sort
    fi
    
    echo ""
}

# Função para gerar relatório
generate_report() {
    echo -e "${YELLOW}${BOLD}📝 GERANDO RELATÓRIO DE ANÁLISE${NC}"
    echo -e "${BLUE}-----------------------------------------------${NC}"
    
    report_file="$REPO_DIR/docs/repository_analysis.md"
    
    cat > "$report_file" << EOL
# 📊 Análise do Repositório SynapScale Backend

**Data de análise:** $(date)

Este documento contém uma análise automatizada da estrutura atual do repositório SynapScale Backend.
Utilize-o como referência para decisões de reorganização e limpeza.

## 📁 Estrutura de Diretórios

\`\`\`
$(cat "$TEMP_DIR/structure.txt")
\`\`\`

## 🗂️ Mapeamento de Responsabilidades

| Diretório | Propósito | Status |
|-----------|-----------|--------|
| \`src/\` | Código-fonte principal | ✅ Manter |
| \`config/\` | Arquivos de configuração | ✅ Manter |
| \`tests/\` | Testes automatizados | ✅ Manter |
| \`docs/\` | Documentação | ⚠️ Consolidar |
| \`scripts/\` | Scripts de utilitários | ⚠️ Reorganizar |
| \`alembic/\` | Migrações de banco de dados | ✅ Manter |
| \`migrations/\` | Scripts de migração adicional | ⚠️ Verificar redundância |
| \`tools/\` | Ferramentas auxiliares | ⚠️ Avaliar utilidade |
| \`deployment/\` | Configuração de implantação | ✅ Manter |

## 🐍 Principais Arquivos Python

Lista dos arquivos Python mais importantes do repositório, organizados por funcionalidade.

### Arquivos Core

- \`src/synapse/__init__.py\`: Inicialização do pacote principal
- \`src/synapse/config.py\`: Configuração centralizada
- \`src/synapse/main.py\`: Ponto de entrada da aplicação FastAPI

### Scripts e Ferramentas

- \`setup_complete.py\`: Script de verificação da configuração
- \`validate_setup.py\`: Validação do ambiente
- \`propagate_env.py\`: Propagação de variáveis de ambiente

## 📚 Documentação

### Documentos a Manter

- \`README.md\`: Documentação principal
- \`docs/architecture/overview.md\`: Visão geral da arquitetura
- \`docs/api/quick_guide.md\`: Guia rápido da API
- \`docs/guides/development.md\`: Guia de desenvolvimento
- \`docs/SECURITY.md\`: Diretrizes de segurança

### Documentos a Remover ou Consolidar

- Documentos duplicados com "FINAL" ou "COMPLETO" no nome
- Múltiplas versões de guias de configuração
- Relatórios temporários ou desatualizados

## 📋 Próximos Passos

1. Executar o script de reorganização do repositório
2. Testar todas as funcionalidades após limpeza
3. Atualizar a documentação principal (README.md)
4. Simplificar scripts de inicialização
EOL
    
    echo -e "${GREEN}✅ Relatório gerado em:${NC} $report_file"
}

# Executar todas as análises
analyze_python_files
analyze_shell_scripts
analyze_documentation
analyze_project_structure
analyze_dependencies
generate_report

echo -e "\n${GREEN}${BOLD}✅ ANÁLISE CONCLUÍDA${NC}"
echo -e "${YELLOW}Um relatório detalhado foi gerado em:${NC} $REPO_DIR/docs/repository_analysis.md"
echo -e "${YELLOW}Use este relatório como guia para reorganizar o repositório.${NC}"
echo -e "${BLUE}Para executar a reorganização automatizada, execute:${NC}"
echo -e "${CYAN}$ bash scripts/reorganize_repository.sh${NC}"
echo -e ""
