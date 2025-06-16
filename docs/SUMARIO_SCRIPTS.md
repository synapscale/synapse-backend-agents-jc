# Sumário Detalhado de Scripts e Utilitários

Este documento lista todos os scripts e utilitários do repositório SynapScale Backend, organizados por diretório, com nome, caminho e descrição do propósito de cada um.

---

## scripts/
- **fix_migration_types.py**  
  Corrige tipos de dados inconsistentes em migrations do Alembic.
- **fix_requirements.sh**  
  Ajusta e organiza o arquivo requirements.txt, removendo duplicatas e corrigindo versões.
- **fix_schema_references.py**  
  Corrige referências de schema em arquivos de migration.
- **fix_setup_scripts.sh**  
  Corrige e padroniza scripts de setup do projeto.
- **organize_requirements.sh**  
  Organiza e ordena requirements.txt.
- **prepare_tests.sh**  
  Prepara o ambiente para execução de testes automatizados.
- **recreate_tables.sh**  
  Recria tabelas do banco de dados a partir dos models.
- **reorganize_repository.sh**  
  Reorganiza a estrutura de diretórios e arquivos do repositório.
- **run_tests.sh**  
  Executa todos os testes automatizados do projeto.
- **start-production.sh**  
  Inicia o backend em modo produção.
- **start.sh**  
  Inicia o backend (modo padrão).
- **validate.sh**  
  Valida o setup e a configuração do ambiente.
- **validate_changes.sh**  
  Valida alterações recentes no repositório.
- **endpoint_analyzer.py**  
  Analisa endpoints da API para documentação e validação.
- **final_cleanup.sh**  
  Realiza limpeza final de arquivos e diretórios desnecessários.
- **fix_alembic_heads.py**  
  Corrige múltiplos heads em migrations do Alembic.
- **fix_create_index_syntax.py**  
  Corrige sintaxe de criação de índices em migrations.
- **fix_create_table_syntax.py**  
  Corrige sintaxe de criação de tabelas em migrations.
- **fix_duplicate_schema.py**  
  Remove schemas duplicados em migrations.
- **fix_env_files.sh**  
  Corrige e padroniza arquivos de ambiente (.env).
- **fix_migration_schemas.py**  
  Corrige schemas em migrations.
- **analyze_repository.sh**  
  Analisa a estrutura do repositório.
- **clean_temp_files.sh**  
  Limpa arquivos temporários do projeto.

---

## tools/testing/
- **demo_server.py**  
  Servidor de demonstração para testes locais.
- **diagnose_detailed.py**  
  Diagnóstico detalhado de endpoints e serviços.
- **diagnose_endpoints.py**  
  Diagnóstico rápido dos endpoints da API.
- **simple_auth_test.py**  
  Teste simples de autenticação.
- **test_auth_correct.py**  
  Teste de autenticação correta.
- **test_db_connection.py**  
  Teste de conexão com o banco de dados.
- **test_env.py**  
  Testa o carregamento das variáveis de ambiente.
- **test_final_corrections.py**  
  Teste de correções finais no ambiente.
- **test_imports.py**  
  Testa importação de módulos principais.
- **test_render_simulation.py**  
  Simula ambiente de deploy Render.
- **test_saas_user_login.py**  
  Teste de login de usuário SaaS.
- **test_simple_db.py**  
  Teste simples de operações no banco.
- **test_user_creation.py**  
  Teste de criação de usuário.

---

## tools/utilities/
- **clean_secrets.sh**  
  Remove segredos sensíveis de arquivos e logs.
- **disable_env_masking.sh**  
  Desativa mascaramento de variáveis de ambiente.
- **enable_env_masking.sh**  
  Ativa mascaramento de variáveis de ambiente.
- **env_aliases.sh**  
  Define aliases úteis para manipulação de ambiente.
- **force_disable_masking.sh**  
  Força desativação de mascaramento de variáveis.
- **generate_test_token.py**  
  Gera tokens de teste para autenticação.
- **index.ts**  
  (Utilitário para integração com TypeScript/Node.)
- **load_env.sh**  
  Carrega variáveis do .env no shell.
- **security_scan.sh**  
  Realiza scan de segurança no projeto.
- **view_env.py**  
  Visualiza variáveis do .env (com mascaramento).
- **view_env_clear.py**  
  Visualiza variáveis do .env (sem mascaramento).

---

## tools/utils/
- **propagate_env.py**  
  Propaga variáveis do .env para todos os arquivos e scripts necessários.
- **validate_setup.py**  
  Valida o setup final do backend, checando arquivos, venv, dependências, etc.

---

## tools/database/
- **create_saas_user_fixed.py**  
  Cria usuário SaaS no banco (versão corrigida).
- **create_user_direct.py**  
  Cria usuário diretamente no banco.
- **check_synapscale_schema.py**  
  Checa a existência e integridade do schema synapscale.
- **check_users_table.py**  
  Checa a existência e integridade da tabela de usuários.
- **create_saas_user.py**  
  Cria usuário SaaS no banco.

---

## setup/scripts/
- **generate_secure_keys.py**  
  Gera chaves seguras para o .env do projeto.

---

## docs/config-templates/
- **.env.template, env.complete, env.render.example**  
  Modelos de arquivos de ambiente para diferentes cenários.

---

## scripts utilitários na raiz
- **generate_secure_keys.py**  
  (Duplicado de setup/scripts/generate_secure_keys.py, pode ser removido ou centralizado.)
- **validate_no_hardcoded.py**  
  Valida se não há segredos hardcoded no código.
- **verify_env_usage.py**  
  Verifica o uso correto de variáveis de ambiente.
- **move_tables.py**  
  Move tabelas entre schemas no banco.
- **run_migrations.py**  
  Executa migrations manualmente.
- **create_custom_user.py**  
  Cria usuário customizado no banco.
- **create_schema.py**  
  Cria schema no banco.
- **apply_migrations.py**  
  Aplica migrations no banco.
- **check_all_schemas.py**  
  Checa todos os schemas do banco.
- **check_relationships.py**  
  Checa relacionamentos no banco.
- **check_schema.py**  
  Checa schema específico no banco.
- **test_import.py**  
  Teste de importação (vazio, pode ser removido). 