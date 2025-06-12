# 9. Scripts criados para manutenção do repositório

Foram criados os seguintes scripts para facilitar a manutenção contínua do repositório:

## 9.1. `scripts/fix_requirements.sh`

Script para padronizar os arquivos de dependências. Consolida múltiplos arquivos de requisitos em um único `requirements.txt` na raiz do projeto.

## 9.2. `scripts/fix_env_files.sh`

Script para padronizar os arquivos de ambiente. Organiza os arquivos `.env*` para manter apenas `.env.example` e `.env`, com um template na pasta de configuração.

## 9.3. `scripts/fix_setup_scripts.sh`

Script para unificar os scripts de setup. Consolida múltiplos scripts em um único `setup.sh` com modos básico e completo.

## 9.4. `scripts/final_cleanup.sh`

Script para limpar a raiz do repositório. Move scripts utilitários para diretórios apropriados e remove arquivos redundantes.

## 9.5. `scripts/validate_changes.sh`

Script para validar as alterações feitas. Verifica se todas as mudanças foram aplicadas corretamente.

## 9.6. `scripts/analyze_repository.sh`

Script para analisar o estado atual do repositório. Gera relatório sobre estrutura de diretórios, arquivos Python principais e documentação.

## 9.7. `scripts/reorganize_repository.sh`

Script principal de reorganização. Executa as etapas de reorganização e limpeza do repositório.

## 9.8. `scripts/clean_temp_files.sh`

Script para limpar arquivos temporários. Remove caches Python, logs e arquivos temporários de IDEs.
