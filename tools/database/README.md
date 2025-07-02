# Utilitários de Banco de Dados SynapScale

Este diretório agrupa scripts auxiliares para manutenção, verificação e migração do banco de dados SynapScale. Cada script foi desenvolvido para automatizar tarefas específicas de administração e diagnóstico do sistema.

## ⚠️ AVISO CRÍTICO DE SEGURANÇA

🚨 **ALGUNS SCRIPTS MANIPULAM DIRETAMENTE O BANCO DE DADOS** 🚨

- **`create_saas_user_fixed.py`** é **EXTREMAMENTE PERIGOSO**
- Conecta diretamente ao PostgreSQL **SEM validações**
- **BYPASSA completamente** a API da aplicação  
- **PODE CAUSAR** inconsistências graves de dados
- **RISCO MÁXIMO** em ambiente de produção
- **SÓ USAR EM EMERGÊNCIAS** com backup completo

**🛡️ REGRA DE OURO:** Sempre prefira scripts via API (`create_saas_user.py`) para operações normais.

---

## 🚀 Setup Rápido

**Para começar imediatamente com o sistema de automação:**

```bash
# 1. Execute o setup automático
bash tools/database/setup_automation.sh

# 2. Configure o .env com suas variáveis

# 3. Execute manutenção completa
./quick_maintenance.sh
```

**🎉 Pronto! Seu sistema agora tem manutenção automatizada completa.**

---

## 🤖 Sistema de Automação

### 🏥 Health Check Master

**Script:** [`health_check_master.py`](tools/database/health_check_master.py)

Sistema integrado que executa **todos os checks** em sequência e gera relatório completo de saúde:

**Funcionalidades:**
- ✅ Executa todos os scripts `check_*` automaticamente
- 🔌 Verifica conectividade com banco e API
- 📊 Gera score de saúde (0-100%)
- 📋 Relatório detalhado com sugestões
- 🎨 Interface colorida e intuitiva
- 💾 Salva relatórios em JSON/HTML

**Uso:**
```bash
# Verificação completa
python tools/database/health_check_master.py

# Com relatório JSON
python tools/database/health_check_master.py --json --report health_report.json

# Apenas verificar sem detalhes
python tools/database/health_check_master.py >/dev/null; echo "Status: $?"
```

**Saída típica:**
```
🏥 RELATÓRIO DE SAÚDE DO SISTEMA
================================
📊 STATUS GERAL: EXCELENTE (95.2%)
⏱️  Tempo de execução: 12.3s
📋 Verificações: 8/8 bem-sucedidas
```

### 🔄 Sync Validator

**Script:** [`sync_validator.py`](tools/database/sync_validator.py)

Valida sincronização entre **banco, models, API e schemas**:

**O que verifica:**
- 🏗️ **Banco vs Models**: Compara tabelas e colunas
- 🌐 **API vs Schema**: Endpoints refletem estrutura do banco
- 📋 **OpenAPI Sync**: Documentação está atualizada
- 🔗 **Relacionamentos**: FKs e constraints estão corretos

**Detecta:**
- Tabelas faltantes em models
- Colunas dessincronizadas
- Endpoints incompletos (CRUD)
- Models órfãos

**Uso:**
```bash
# Validação completa
python tools/database/sync_validator.py

# Com relatório detalhado
python tools/database/sync_validator.py --json --report sync_report.json
```

**Saída típica:**
```
🔄 RELATÓRIO DE SINCRONIZAÇÃO
=============================
📊 STATUS: SINCRONIZADO
📋 Tabelas no banco: 15
🏗️  Models SQLAlchemy: 14
⚠️  Total de problemas: 2

🔄 INCONSISTÊNCIAS BANCO vs MODELS:
   • Tabela 'user_sessions' existe no banco mas não tem model correspondente
     💡 Criar model SQLAlchemy para tabela 'user_sessions'
```

### 📚 Doc Generator

**Script:** [`doc_generator.py`](tools/database/doc_generator.py)

Gera documentação completa **automaticamente** baseada no banco real:

**Gera:**
- 📖 **Schema em Markdown**: Documentação completa de tabelas
- 🎨 **Diagrama ER**: Mermaid com relacionamentos
- 🌐 **Dashboard HTML**: Interface web de monitoramento
- 📊 **Dados JSON**: Estrutura completa para automação

**Uso:**
```bash
# Gerar toda documentação
python tools/database/doc_generator.py

# Apenas schema
python tools/database/doc_generator.py --schema-only

# Diretório customizado
python tools/database/doc_generator.py --output-dir custom_docs/
```

**Arquivos gerados:**
- `docs/database/schema.md` - Documentação do schema
- `docs/database/er_diagram.mmd` - Diagrama Mermaid
- `docs/database/health_dashboard.html` - Dashboard web
- `docs/database/database_info.json` - Dados estruturados

### 🤖 Maintenance Automation

**Script:** [`maintenance_automation.py`](tools/database/maintenance_automation.py)

**O NÚCLEO da automação** - executa manutenção completa em 5 fases:

**Fases de Execução:**
1. 🏥 **Health Check**: Verifica saúde geral do sistema
2. 🔄 **Sync Validation**: Valida sincronização completa
3. 📚 **Documentation**: Atualiza documentação automaticamente
4. 📋 **OpenAPI Sync**: Verifica e sugere atualizações
5. 📋 **Action Plan**: Gera plano de ação detalhado

**Recursos Avançados:**
- 🚨 **Detecção de problemas críticos**: Para execução se houver problemas graves
- 📊 **Relatórios detalhados**: Markdown + JSON com análise completa
- 💡 **Sugestões acionáveis**: Próximos passos específicos
- ⏱️ **Execução otimizada**: Apenas 30-60 segundos para verificação completa
- 🎯 **Exit codes**: Integração fácil com CI/CD

**Uso:**
```bash
# Manutenção completa (recomendado)
python tools/database/maintenance_automation.py

# Apenas uma fase específica
python tools/database/maintenance_automation.py --phase health
python tools/database/maintenance_automation.py --phase sync
python tools/database/maintenance_automation.py --phase docs

# Simulação (sem mudanças)
python tools/database/maintenance_automation.py --dry-run
```

**Saída típica:**
```
🏁 MANUTENÇÃO AUTOMATIZADA CONCLUÍDA
====================================
⏱️  Tempo de execução: 45.7 segundos
📁 Relatórios salvos em: reports/maintenance/
📋 Relatório principal: maintenance_report_20250107_143022.md
📊 Action plan: action_plan_20250107_143022.json

🎉 Sistema está funcionando corretamente!
```

**Integração com CI/CD:**
```yaml
# .github/workflows/maintenance.yml
- name: Database Maintenance
  run: python tools/database/maintenance_automation.py
  # Exit codes: 0=OK, 1=Critical, 2=Warnings
```

**Agendamento automático:**
```bash
# Cron job para manutenção diária às 2:00
0 2 * * * cd /path/to/project && ./quick_maintenance.sh >> logs/maintenance.log
```

---

## Sumário

### 🤖 Sistema de Automação (NOVO!)
- [🚀 Setup Rápido](#setup-rápido)
- [🏥 Health Check Master](#health-check-master)
- [🔄 Sync Validator](#sync-validator)  
- [📚 Doc Generator](#doc-generator)
- [🤖 Maintenance Automation](#maintenance-automation)

### 📋 Scripts Tradicionais
- [Requisitos](#requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Scripts de Verificação](#scripts-de-verificação)
  - [check_all_schemas.py](#check_all_schemaspy)
  - [check_relationships.py](#check_relationshipspy)
  - [check_schema.py](#check_schemapy)
  - [check_synapscale_schema.py](#check_synapscale_schemapy)
  - [check_users_table.py](#check_users_tablepy)
- [Scripts de Migração](#scripts-de-migração)
  - [apply_migrations.py](#apply_migrationspy)
- [Scripts de Criação de Usuários](#scripts-de-criação-de-usuários)
  - [create_custom_user.py](#create_custom_userpy)
  - [create_saas_user.py](#create_saas_userpy)
  - [create_saas_user_fixed.py](#create_saas_user_fixedpy)
- [Configurações do Banco](#configurações-do-banco)
- [Estrutura de Schemas](#estrutura-de-schemas)
- [Segurança e Boas Práticas](#segurança-e-boas-práticas)
- [Troubleshooting](#troubleshooting)

---

## Requisitos

### Software
- **Python 3.11 ou superior**
- **PostgreSQL** (versão 12+)
- **Conexão com banco configurada** (DigitalOcean Managed Database ou local)

### Dependências Python
```bash
pip install -r requirements.txt
```

**Principais bibliotecas utilizadas:**
- `psycopg2-binary` - Driver PostgreSQL
- `python-dotenv` - Gerenciamento de variáveis de ambiente
- `bcrypt` - Hash de senhas
- `requests` - Requisições HTTP (para scripts API)
- `alembic` - Migrações de banco

---

## Configuração do Ambiente

### Variáveis de Ambiente Obrigatórias

**IMPORTANTE**: Todas as configurações devem estar no arquivo `.env` na raiz do projeto. **Nenhum script deve ter variáveis hardcoded**.

**Arquivo `.env` completo:**
```bash
# === CONFIGURAÇÃO PRINCIPAL DO BANCO ===
# URL completa de conexão (usado pela maioria dos scripts)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database_name

# === CONFIGURAÇÕES DETALHADAS ===
# Usadas por scripts específicos (check_synapscale_schema.py, check_users_table.py)
DB_HOST=your_host_here
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_SSLMODE=require

# === CONFIGURAÇÕES DO SISTEMA ===
# Schema padrão do sistema
DATABASE_SCHEMA=synapscale_db

# === CONFIGURAÇÕES DE API ===
# Para scripts que usam API (create_saas_user.py)
API_BASE_URL=http://localhost:8000
```

**⚠️ REGRAS IMPORTANTES:**
- Todos os scripts **devem** usar `load_dotenv()` para carregar variáveis
- **Nunca** definir valores padrão hardcoded nos scripts
- **Sempre** verificar se a variável existe antes de usar
- Usar `os.getenv("VARIAVEL")` em todos os scripts

### Validação do .env

**Template completo do arquivo `.env`:**
```bash
# === CONFIGURAÇÃO PRINCIPAL (obrigatória) ===
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database_name

# === CONFIGURAÇÕES DETALHADAS (para scripts específicos) ===
DB_HOST=your_host_here
DB_PORT=5432
DB_NAME=your_database_name  
DB_USER=your_username
DB_PASSWORD=your_password
DB_SSLMODE=require

# === CONFIGURAÇÕES DO SISTEMA ===
DATABASE_SCHEMA=synapscale_db

# === API CONFIGURAÇÃO ===
API_BASE_URL=http://localhost:8000

# === CONFIGURAÇÕES DE USUÁRIOS (para scripts de criação) ===
ADMIN_EMAIL=admin@synapscale.com
ADMIN_PASSWORD=your_secure_password
DEFAULT_USER_PASSWORD=your_default_password
```

### Testando a Conexão
```bash
# Teste rápido de conexão
python tools/database/check_schema.py

# Verificar se todas as variáveis estão configuradas
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
required_vars = ['DATABASE_URL', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
missing = [var for var in required_vars if not os.getenv(var)]
print('✅ Todas as variáveis configuradas!' if not missing else f'❌ Faltam: {missing}')
"
```

---

## Scripts de Verificação

Os scripts de verificação (`check_*`) são fundamentais para diagnóstico e monitoramento do estado do banco de dados. Eles fornecem informações críticas sobre a estrutura, integridade e configuração do sistema.

### check_all_schemas.py

**Funcionalidade:** Escaneia todos os schemas no banco de dados e lista suas tabelas.

**O que ele revela:**
- 📊 **Estrutura Global**: Todos os schemas existentes no banco
- 📋 **Inventário de Tabelas**: Lista completa de tabelas por schema
- 🔍 **Schemas Órfãos**: Identifica schemas criados acidentalmente
- 📈 **Organização**: Verifica se a estrutura está organizada conforme esperado

**Informações Técnicas:**
- Usa `information_schema.schemata` para buscar schemas
- Filtra schemas do sistema (`pg_%`, `information_schema`)
- Consulta `information_schema.tables` para cada schema
- Ordena resultados por nome para facilitar análise

**Saída Típica:**
```
🔍 Verificando todos os schemas...
📊 Schemas disponíveis: ['public', 'synapscale_db']

🔸 Schema: public
   Total: 0 tabelas

🔸 Schema: synapscale_db
   Total: 15 tabelas
   ✓ agents
   ✓ alembic_version
   ✓ users
   ✓ workflow_executions
   ...
```

**Uso:**
```bash
python tools/database/check_all_schemas.py
```

### check_relationships.py

**Funcionalidade:** Verifica integridade referencial e relacionamentos entre tabelas.

**O que ele revela:**
- 🔗 **Chaves Estrangeiras**: Mapeamento completo de relacionamentos
- 📊 **Integridade Referencial**: Confirma se as FK estão bem configuradas
- 🏗️ **Arquitetura de Dados**: Mostra como as tabelas se conectam
- ⚠️ **Problemas de Design**: Identifica relacionamentos problemáticos

**Informações Técnicas:**
- Consulta `information_schema.table_constraints` para FK
- Une com `key_column_usage` e `constraint_column_usage`
- Foca no schema `synapscale_db`
- Mostra origem e destino de cada relacionamento

**Saída Típica:**
```
🔍 Verificando relacionamentos no schema synapscale_db...
📊 Total de relacionamentos encontrados: 8
  ✓ workflow_executions.agent_id -> agents.id
  ✓ workflow_executions.user_id -> users.id
  ✓ user_variables.user_id -> users.id
  ...
```

**Por que é importante:**
- Detecta tabelas isoladas (sem relacionamentos)
- Valida se migrações criaram FK corretamente
- Ajuda no planejamento de queries complexas
- Identifica problemas de performance por FK mal indexadas

**Uso:**
```bash
python tools/database/check_relationships.py
```

### check_schema.py

**Funcionalidade:** Verificação focada no schema principal `synapscale_db`.

**O que ele revela:**
- 📋 **Inventário Principal**: Lista das tabelas do sistema
- 🔖 **Status de Migração**: Versão atual do Alembic
- ✅ **Estado do Schema**: Confirma se o schema existe e está populado
- 🎯 **Diagnóstico Rápido**: Visão geral do estado do sistema

**Informações Técnicas:**
- Foca especificamente no schema `synapscale_db`
- Verifica existência da tabela `alembic_version`
- Mostra versão atual das migrações
- Ordena tabelas alfabeticamente

**Saída Típica:**
```
🔍 Verificando schema synapscale_db...
📊 Tabelas existentes no schema 'synapscale_db': 15 tabelas
  ✓ agents
  ✓ alembic_version
  ✓ executor_configs
  ✓ templates
  ✓ user_variables
  ✓ users
  ✓ workflow_executions

🔖 Versão atual do Alembic: abc123def456
```

**Casos de uso:**
- Verificação pós-migração
- Diagnóstico rápido de problemas
- Validação de deploy
- Monitoramento de integridade

**Uso:**
```bash
python tools/database/check_schema.py
```

### check_synapscale_schema.py

**Funcionalidade:** Análise detalhada do schema principal com foco na estrutura de dados.

**O que ele revela:**
- 🏗️ **Estrutura Detalhada**: Colunas, tipos de dados, constraints
- 👥 **Dados de Usuários**: Análise da tabela principal `users`
- 📊 **Estatísticas**: Contagem de registros e distribuição
- 🔍 **Metadados**: Informações completas sobre colunas

**Informações Técnicas:**
- Usa configuração por variáveis separadas (DB_HOST, DB_PORT, etc.)
- Consulta `information_schema.columns` para detalhes das colunas
- Faz análise específica da tabela `users`
- Mostra exemplos de dados (primeiros 5 registros)

**Saída Típica:**
```
🔗 Verificando schema synapscale_db no DigitalOcean...
✅ Conexão bem-sucedida!
✅ Schema 'synapscale_db' encontrado!
📋 Tabelas no schema synapscale_db (15): ['agents', 'users', ...]

👥 Tabela synapscale_db.users: 3 registros
📝 Estrutura da tabela synapscale_db.users:
  - id: uuid (NOT NULL)
  - email: character varying (NOT NULL)
  - username: character varying (NULL)
  - full_name: character varying (NULL)
  - hashed_password: character varying (NOT NULL)
  - is_active: boolean (NOT NULL)
  - is_superuser: boolean (NOT NULL)
  - created_at: timestamp without time zone (NOT NULL)
  - updated_at: timestamp without time zone (NOT NULL)

👤 Usuários existentes:
  - ID: 123e4567-e89b-12d3-a456-426614174000, Email: admin@synapscale.com, Username: admin, Nome: Administrador, Ativo: True
```

**Por que usar:**
- Análise detalhada da estrutura
- Verificação de tipos de dados
- Auditoria de usuários existentes
- Validação pós-migração detalhada

**Uso:**
```bash
python tools/database/check_synapscale_schema.py
```

### check_users_table.py

**Funcionalidade:** Auditoria específica da tabela de usuários.

**O que ele revela:**
- 👥 **Estrutura de Usuários**: Colunas e tipos da tabela users
- 🔐 **Campos de Segurança**: Identifica colunas de senha/hash
- 📊 **População da Tabela**: Quantos usuários existem
- 👤 **Exemplos de Dados**: Mostra registros reais (sem senhas)

**Informações Técnicas:**
- Busca especificamente por campos de senha (`%password%`, `%hash%`, `%senha%`)
- Consulta o schema `public` (versão antiga) ou `synapscale_db`
- Mostra defaults das colunas
- Limitado aos primeiros 3 usuários por segurança

**Saída Típica:**
```
🔍 Verificando estrutura da tabela users...
📋 Estrutura da tabela 'users' (9 colunas):
----------------------------------------------------------------------
  id                   | uuid            | Null: NO  | Default: gen_random_uuid()
  email                | character varying| Null: NO  | Default: None
  username             | character varying| Null: YES | Default: None
  full_name            | character varying| Null: YES | Default: None
  hashed_password      | character varying| Null: NO  | Default: None
  is_active            | boolean         | Null: NO  | Default: true
  is_superuser         | boolean         | Null: NO  | Default: false
  created_at           | timestamp       | Null: NO  | Default: now()
  updated_at           | timestamp       | Null: NO  | Default: now()

🔐 Colunas relacionadas a senha encontradas: ['hashed_password']
👥 Registros na tabela users: 3

📝 Exemplo de dados:
  ID: 123e4567-e89b-12d3-a456-426614174000, Email: admin@synapscale.com, Nome: Admin SynapScale
```

**Por que é crucial:**
- Auditoria de segurança
- Verificação de campos obrigatórios
- Análise de estrutura antes de migrações
- Troubleshooting de problemas de login

**Uso:**
```bash
python tools/database/check_users_table.py
```

---

## Scripts de Migração

### apply_migrations.py

**Funcionalidade:** Executor avançado de migrações Python personalizadas.

**O que ele faz:**
- 🚀 **Migrações Customizadas**: Executa arquivos Python na pasta `migrations/`
- 📋 **Sequência Controlada**: Aplica migrações em ordem específica
- 🔄 **Controle de Estado**: Rastreia sucessos e falhas
- 📊 **Relatório Final**: Mostra tabelas criadas após migrações

**Arquitetura Técnica:**
- Executa arquivos Python usando `exec()`
- Passa variáveis de ambiente para cada migração
- Sequência predefinida de arquivos:
  1. `001_create_user_variables.py`
  2. `002_create_workflow_executions.py`
  3. `003_create_templates.py`
  4. `004_create_executor_configs.py`
  5. `005_create_fase4_tables.py`

**Migrações Executadas:**
1. **User Variables**: Variáveis personalizadas por usuário
2. **Workflow Executions**: Histórico de execuções de workflows
3. **Templates**: Templates de workflows e configurações
4. **Executor Configs**: Configurações de executores
5. **Fase 4 Tables**: Tabelas avançadas do sistema

**Saída Típica:**
```
🚀 Iniciando execução das migrações adicionais...
📊 Schema de destino: synapscale_db

🔄 Executando migração: 001_create_user_variables.py
✅ Migração 001_create_user_variables.py executada com sucesso!

🔄 Executando migração: 002_create_workflow_executions.py
✅ Migração 002_create_workflow_executions.py executada com sucesso!

...

🏁 Concluído! 5/5 migrações executadas com sucesso.
📊 Total de tabelas no schema 'synapscale_db': 15
```

**Uso:**
```bash
python tools/database/apply_migrations.py
```

---

## Scripts de Criação de Usuários

### create_custom_user.py

**Funcionalidade:** Criação direta de usuário específico no banco de dados.

**Características:**
- 🎯 **Usuário Específico**: Cria usuário `joaovictor@liderimobiliaria.com.br`
- 🔐 **Hash Seguro**: Usa bcrypt para hash da senha
- 📁 **Arquivo de Credenciais**: Salva informações para referência
- 🧪 **Teste de Login**: Valida se a senha funciona

**Funcionalidades Técnicas:**
- Gera UUID único para o usuário
- Hash da senha com bcrypt e salt
- Validação de unicidade (email/username)
- Teste automático de verificação de senha
- Salvamento de credenciais em arquivo txt

**⚠️ CONFIGURAÇÃO NECESSÁRIA NO .env:**
```bash
# Todas as configurações de banco devem estar no .env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database_name
# OU as variáveis separadas (DB_HOST, DB_PORT, etc.)
```

**Dados do Usuário Criado:**
- Email: `joaovictor@liderimobiliaria.com.br`
- Username: `joaovictor` 
- Nome: `João Victor - Líder Imobiliária`
- Senha: `@Teste123` (configurada no script, deve vir do .env)
- Tipo: Usuário normal (não superuser)

**Saída Típica:**
```
🎯 Criador de Usuário Personalizado - SynapScale
===============================================
📧 Email: joaovictor@liderimobiliaria.com.br
🔐 Senha: @Teste123

🚀 Criando usuário personalizado no sistema SynapScale...
✅ Conectado ao banco DigitalOcean
✅ Usuário criado com sucesso!
📧 Email: joaovictor@liderimobiliaria.com.br
👤 Username: joaovictor
👥 Nome: João Victor - Líder Imobiliária
🆔 ID: 123e4567-e89b-12d3-a456-426614174000
🔐 Senha: @Teste123
📊 Total de usuários na base: 1
💾 Credenciais salvas em: usuario_joaovictor_credenciais.txt

🧪 Testando login...
✅ Teste de login bem-sucedido!
```

**Uso:**
```bash
python tools/database/create_custom_user.py
```

### create_saas_user.py

**Funcionalidade:** Criação de usuários via API do sistema SynapScale.

**Características:**
- 🌐 **Via API**: Usa endpoint de registro da aplicação
- 🎭 **Interativo**: Interface amigável para coleta de dados
- 📋 **Validação**: Valida dados antes de enviar
- 💾 **Arquivo de Saída**: Salva informações do usuário criado
- 🧪 **Teste de Conexão**: Verifica se API está acessível

**Funcionalidades:**
1. **Criação Interativa**: Coleta dados do usuário via prompt
2. **Usuário Demo**: Opção para criar usuário de demonstração
3. **Validação de API**: Testa conexão antes de criar usuário
4. **Gestão de Erros**: Tratamento detalhado de erros da API

**⚠️ CONFIGURAÇÃO NECESSÁRIA NO .env:**
```bash
# Configuração da API (obrigatória)
API_BASE_URL=http://localhost:8000

# Configurações automáticas baseadas na API_BASE_URL
# REGISTER_ENDPOINT = {API_BASE_URL}/api/v1/auth/register
# LOGIN_ENDPOINT = {API_BASE_URL}/api/v1/auth/login
```

**Menu Interativo:**
```
📋 Opções disponíveis:
1. Criar novo usuário (interativo)
2. Criar usuário de demonstração
3. Testar conexão com API
4. Sair
```

**Usuário Demo Criado:**
```
Email: demo@synapscale.com
Nome: Demo User
Senha: DemoPassword123!
```

**Uso:**
```bash
python tools/database/create_saas_user.py
```

### create_saas_user_fixed.py

🚨🚨🚨 **SCRIPT EXTREMAMENTE PERIGOSO** 🚨🚨🚨

**⚠️⚠️⚠️ ATENÇÃO CRÍTICA:**
- **MANIPULA DIRETAMENTE** o banco PostgreSQL
- **BYPASSA TODAS** as validações da aplicação
- **PODE CAUSAR** inconsistências graves de dados
- **RISCO EXTREMO** em ambiente de produção
- **SÓ PARA EMERGÊNCIAS** quando API está quebrada

**🔴 ESTE SCRIPT:**
- Conecta diretamente ao PostgreSQL
- Cria usuários SEM passar pela API
- BYPASSA toda lógica de negócio
- PODE quebrar integridade referencial
- É PERIGOSO em produção

**🛑 SÓ USE SE:**
- Você é DBA experiente
- API está quebrada (emergência)
- Você entende os riscos
- FEZ BACKUP do banco antes

**⚠️ CONFIGURAÇÃO OBRIGATÓRIA NO .env:**
```bash
# TODAS as variáveis são obrigatórias
DB_HOST=your_host_here
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_SSLMODE=require

# Configurações recomendadas para usuário
ADMIN_EMAIL=admin@synapscale.com
ADMIN_PASSWORD=your_secure_password
```

**Proteções Implementadas:**
- **Detecção de produção**: Avisa se está em ambiente de produção
- **Confirmações múltiplas**: Require 4 confirmações específicas
- **Avisos coloridos**: Interface com cores para chamar atenção
- **Verificação de .env**: Valida variáveis antes de executar
- **Última chance**: Confirmação final antes do INSERT

**Confirmações Necessárias:**
1. `SIM-FIZ-BACKUP` - Confirma que fez backup
2. `ENTENDO-OS-RISCOS` - Confirma entendimento dos riscos
3. `MODIFICAR-BANCO-DIRETO` - Confirma modificação direta
4. `INSERIR-DADOS-DIRETO-NO-BANCO` - Última confirmação

**Usuário Criado:**
- Email: Configurado via `ADMIN_EMAIL` (padrão: `admin@synapscale.com`)
- Username: `admin`
- Nome: `Administrador SynapScale`
- Senha: Configurada via `ADMIN_PASSWORD` (padrão hardcoded)
- Tipo: **SUPERUSER** (administrador com privilégios máximos)

**🚨 QUANDO NÃO USAR:**
- ✅ **USE create_saas_user.py** - Via API (seguro)
- ✅ **USE interface web** - Interface administrativa  
- ✅ **USE endpoints admin** - APIs de administração
- ❌ **NÃO use em produção** sem backup completo
- ❌ **NÃO use rotineiramente** - só emergências

**Riscos Conhecidos:**
- Inconsistência com cache da aplicação
- Problemas de sincronização
- Quebra de constraints não validadas
- Usuário pode ter comportamento anômalo
- Logs da aplicação podem não refletir a criação

**Uso (com extremo cuidado):**
```bash
# FAÇA BACKUP PRIMEIRO!
pg_dump $DATABASE_URL > backup_antes_do_risco.sql

# Execute o script perigoso
python tools/database/create_saas_user_fixed.py

# Monitore logs após criação
tail -f logs/application.log
```

**💡 ALTERNATIVAS SEGURAS:**
```bash
# Método recomendado (via API)
python tools/database/create_saas_user.py

# Verificar se API está funcionando
curl http://localhost:8000/health
```

---

## Configurações do Banco

### Schema Principal: synapscale_db

O sistema utiliza um schema dedicado `synapscale_db` para separar as tabelas da aplicação das tabelas do sistema PostgreSQL.

**Estrutura Esperada:**
```
synapscale_db/
├── alembic_version        # Controle de migrações
├── users                  # Usuários do sistema
├── agents                 # Agentes de IA
├── workflow_executions    # Histórico de execuções
├── user_variables         # Variáveis por usuário
├── templates              # Templates de workflows
├── executor_configs       # Configurações de executores
└── ... (outras tabelas)
```

### Configurações de Conexão

**DigitalOcean Managed Database:**
```bash
# SSL obrigatório
DB_SSLMODE=require

# Pool de conexões recomendado
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

**Local Development:**
```bash
# SSL opcional
DB_SSLMODE=prefer

# Pool menor para desenvolvimento
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

---

## Estrutura de Schemas

### Schema synapscale_db
- **Propósito**: Tabelas principais da aplicação
- **Migrações**: Controladas pelo Alembic
- **Segurança**: Acesso controlado por roles

### Schema public
- **Propósito**: Tabelas temporárias e extensões
- **Uso**: Desenvolvimento e testes
- **Manutenção**: Limpeza manual periódica

### Schemas do Sistema
- **pg_catalog**: Metadados do PostgreSQL
- **information_schema**: Padrão SQL para metadados
- **pg_toast**: Armazenamento de dados grandes

---

## Segurança e Boas Práticas

### Senhas e Hashes
- **Algoritmo**: bcrypt com salt
- **Força**: 12 rounds mínimo
- **Validação**: Sempre usar `bcrypt.checkpw()`

### Conexões
- **SSL**: Sempre obrigatório em produção
- **Timeouts**: Configurar timeouts apropriados
- **Pool**: Limitar conexões simultâneas

### Backup
```bash
# Backup completo
pg_dump -h host -U user -d database -f backup_$(date +%Y%m%d_%H%M%S).sql

# Backup apenas schema synapscale_db
pg_dump -h host -U user -d database -n synapscale_db -f synapscale_backup.sql
```

### Auditoria
- **Logs**: Sempre ativar log de conexões e queries lentas
- **Monitoramento**: Usar scripts de verificação periodicamente
- **Alertas**: Configurar alertas para falhas de conexão

---

## Troubleshooting

### Problemas Comuns

**1. Erro de conexão - DATABASE_URL**
```bash
❌ ERRO: DATABASE_URL não encontrada no arquivo .env
```
**Solução:** 
- Verificar se arquivo `.env` existe na raiz do projeto
- Verificar se variável `DATABASE_URL` está definida no `.env`
- Executar teste: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(bool(os.getenv('DATABASE_URL')))"`

**2. Erro de configuração - Variáveis separadas**
```bash
❌ Erro na conexão: psycopg2.OperationalError: could not connect to server
```
**Solução:**
- Verificar se todas as variáveis estão no `.env`: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Testar conexão: `python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); print('✅ Conexão OK')"`

**3. Schema não encontrado**
```bash
❌ Schema 'synapscale_db' não encontrado!
```
**Solução:** Executar migrações Alembic ou criar schema manualmente

**4. Usuário já existe**
```bash
⚠️ Usuário já existe com ID: 123e4567-e89b-12d3-a456-426614174000
```
**Solução:** Normal, indica que usuário já foi criado anteriormente

**5. API não acessível**
```bash
❌ API não está acessível
```
**Solução:** Verificar se servidor está rodando em `http://localhost:8000`

### Comandos de Diagnóstico

```bash
# Verificação completa do sistema
python tools/database/check_all_schemas.py
python tools/database/check_synapscale_schema.py
python tools/database/check_relationships.py

# Teste de conexão rápido
python -c "import psycopg2; print('✅ psycopg2 OK')"

# Verificar variáveis de ambiente
python -c "import os; print('DATABASE_URL:', bool(os.getenv('DATABASE_URL')))"
```

### Logs e Monitoramento

**Ativar logs detalhados no PostgreSQL:**
```sql
-- postgresql.conf
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000  -- queries > 1s
```

**Monitoramento de performance:**
```sql
-- Queries lentas
SELECT query, mean_time, calls FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Conexões ativas
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

---

## Scripts de Manutenção

### Limpeza Periódica
```bash
# Remover arquivos de credenciais antigos
find . -name "usuario_*_credenciais.txt" -mtime +30 -delete

# Limpar logs antigos
find logs/ -name "*.log" -mtime +7 -delete
```

### Verificação de Integridade
```bash
# Executar todos os checks
for script in tools/database/check_*.py; do
    echo "=== Executando $(basename $script) ==="
    python "$script"
    echo
done
```

### Backup Automatizado
```bash
#!/bin/bash
# backup_database.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > "backups/synapscale_$DATE.sql"
echo "Backup salvo em: backups/synapscale_$DATE.sql"
```

---

*Última atualização: 2025-01-07*
*Versão: 2.0*
*Documentação completa e análise detalhada dos utilitários de banco de dados SynapScale*
