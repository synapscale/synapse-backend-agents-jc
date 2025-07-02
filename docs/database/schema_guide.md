# 🗄️ Guia do Schema PostgreSQL - SynapScale Backend

Este guia fornece instruções completas para configurar e gerenciar o banco de dados PostgreSQL do SynapScale Backend, incluindo a configuração inicial, migrações e estrutura do schema.

## 📋 Pré-requisitos

- PostgreSQL 13+ instalado e rodando (recomendado: 15+)
- Python 3.11+ para executar migrações Alembic
- Acesso ao terminal com cliente `psql`
- Variáveis de ambiente configuradas no `.env`

## 🔧 Passo 1: Criação do Banco de Dados e Usuário

1.  **Conecte-se ao PostgreSQL** como superusuário (geralmente `postgres`):
    ```bash
    sudo -u postgres psql
    ```

2.  **Crie um novo banco de dados** dedicado para o SynapScale:
    ```sql
    CREATE DATABASE synapscale_db OWNER postgres ENCODING 'UTF8' LC_COLLATE='en_US.utf8' LC_CTYPE='en_US.utf8' TEMPLATE template0;
    ```
    *   **Nota:** Ajuste `LC_COLLATE` e `LC_CTYPE` conforme a configuração do seu sistema, se necessário. `en_US.utf8` é um padrão comum.

3.  **Crie um usuário dedicado** para a aplicação SynapScale com uma senha segura:
    ```sql
    CREATE USER synapscale_user WITH PASSWORD 'coloque_uma_senha_forte_aqui';
    ```
    *   **⚠️ IMPORTANTE:** Substitua `'coloque_uma_senha_forte_aqui'` por uma senha realmente segura.

4.  **Conceda todos os privilégios** ao novo usuário no banco de dados criado:
    ```sql
    GRANT ALL PRIVILEGES ON DATABASE synapscale_db TO synapscale_user;
    ```

5.  **(Opcional, mas recomendado) Conecte-se ao novo banco** para garantir que as próximas operações ocorram nele:
    ```sql
    \c synapscale_db
    ```

6.  **Conceda permissões adicionais** ao usuário dentro do banco (necessário para criar tabelas, etc.):
    ```sql
    GRANT ALL ON SCHEMA public TO synapscale_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO synapscale_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO synapscale_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO synapscale_user;
    ```

7.  **Saia do `psql`**:
    ```sql
    \q
    ```

## ⚙️ Passo 2: Execução das Migrações Alembic

1. **Configure a DATABASE_URL** no arquivo `.env`:
   ```env
   DATABASE_URL=postgresql://synapscale_user:sua_senha_forte@localhost:5432/synapscale_db
   ```

2. **Execute as migrações** para criar todas as tabelas:
   ```bash
   # Ativar ambiente virtual
   source venv/bin/activate
   
   # Executar migrações
   alembic upgrade head
   ```

3. **Verificar se as tabelas foram criadas**:
   ```bash
   psql -U synapscale_user -d synapscale_db -c "\dt"
   ```

4. **Verificar estrutura principal**:
   ```sql
   -- Deve mostrar as tabelas principais
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;
   ```

## 🔗 Passo 3: Configuração do Backend SynapScale (.env)

1.  **Navegue até o diretório raiz** do projeto SynapScale Backend.
2.  **Copie o arquivo de exemplo `.env.example`** para `.env` (se ainda não o fez):
    ```bash
    cp .env.example .env
    ```
3.  **Edite o arquivo `.env`** e configure a variável `DATABASE_URL` com os dados do banco que você criou:
    ```env
    # ---------------------------------------------------------------------------
    # DATABASE CONFIGURATION
    # ---------------------------------------------------------------------------
    # Use o formato: postgresql://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL="postgresql://synapscale_user:coloque_sua_senha_forte_aqui@localhost:5432/synapscale_db"
    ```
    *   **⚠️ IMPORTANTE:** Substitua `coloque_sua_senha_forte_aqui` pela senha que você definiu para `synapscale_user`.
    *   Ajuste `localhost` e `5432` se o seu servidor PostgreSQL estiver em um host ou porta diferente.

4.  **Configure as outras variáveis** no arquivo `.env` conforme necessário (SECRET_KEY, chaves de API LLM, etc.). Consulte o arquivo `GUIA_CONFIGURACAO_ENV.md` para mais detalhes sobre as outras variáveis.

## ✅ Passo 4: Verificação e Inicialização

1. **Verificar se o aplicativo conecta ao banco:**
   ```bash
   # Testar conexão
   python -c "from src.synapse.database import get_db; print('✅ Conexão OK')"
   ```

2. **Executar testes de validação:**
   ```bash
   # Testar estrutura do banco
   python tests/validation/comprehensive_validation.py
   ```

## 🗄️ Estrutura Principal das Tabelas

### **👥 Core Entities**
- `users` - Usuários do sistema
- `workspaces` - Espaços de trabalho
- `workspace_members` - Membros dos workspaces
- `user_variables` - Variáveis de usuário e API keys

### **🤖 AI & LLM**
- `agents` - Agentes de IA
- `conversations` - Conversas
- `messages` - Mensagens das conversas
- `llms` - Modelos de linguagem disponíveis
- `usage_logs` - Logs de uso dos LLMs
- `billing_events` - Eventos de cobrança

### **⚙️ Workflows & Automation**
- `workflows` - Definições de workflows
- `workflow_executions` - Execuções de workflows
- `nodes` - Nós dos workflows
- `templates` - Templates de workflows

### **📁 Files & Data**
- `files` - Arquivos do sistema
- `file_uploads` - Uploads de arquivos

### **📊 Analytics & Monitoring**
- `analytics_events` - Eventos de analytics
- `system_alerts` - Alertas do sistema

### **🏷️ Support Tables**
- `tags` - Sistema de tags
- `message_feedbacks` - Feedbacks de mensagens

## 🔗 Relacionamentos Principais

```mermaid
graph TD
    Users --> Workspaces
    Users --> Conversations
    Users --> UserVariables
    Workspaces --> WorkspaceMembers
    Conversations --> Messages
    Messages --> UsageLogs
    Agents --> Conversations
    LLMs --> UsageLogs
    Workflows --> WorkflowExecutions
```

## 📊 Migrações e Versionamento

### **Comandos Úteis Alembic**

```bash
# Ver histórico de migrações
alembic history

# Ver migração atual
alembic current

# Criar nova migração
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migração específica
alembic upgrade <revision_id>

# Reverter uma migração
alembic downgrade <revision_id>
```

### **Backup Antes de Migrações**

```bash
# Fazer backup do banco
pg_dump -U synapscale_user -d synapscale_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup se necessário
psql -U synapscale_user -d synapscale_db < backup_20250107_120000.sql
```

## 🔍 Troubleshooting

### **Problemas Comuns**

**Erro de conexão:**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar configuração
psql -U synapscale_user -d synapscale_db -c "SELECT version();"
```

**Erro de migração:**
```bash
# Ver logs detalhados
alembic upgrade head --verbose

# Forçar revisão se necessário
alembic stamp head
```

**Verificar tabelas criadas:**
```sql
-- Contar tabelas
SELECT count(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- Verificar relacionamentos
SELECT count(*) FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY';
```

## 📚 Referências

- **[Alembic Guide](./alembic_guide.md)** - Guia detalhado de migrações
- **[Configuration Guide](../configuration/README.md)** - Configuração de variáveis
- **[Setup Guide](../SETUP_GUIDE.md)** - Guia de instalação completo

