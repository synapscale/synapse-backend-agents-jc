-- =====================================================
-- SYNAPSCALE DATABASE - SCRIPT SQL POSTGRESQL DEFINITIVO
-- TODAS AS 46 TABELAS IDENTIFICADAS NO PROJETO
-- Criado por: Análise completa dos modelos Python
-- Data: 04/06/2025
-- =====================================================

-- Configurações iniciais do PostgreSQL
SET timezone = 'UTC';
SET client_encoding = 'UTF8';

-- Extensões necessárias (serão instaladas no schema público)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Cria o schema principal
CREATE SCHEMA IF NOT EXISTS synapscale_db;

-- Define o schema padrão para criação de todos os objetos
SET search_path TO synapscale_db, public;

-- =====================================================
-- FUNÇÕES GERAIS
-- =====================================================

-- Função para gerar CUID compatível com Prisma
CREATE OR REPLACE FUNCTION generate_cuid() RETURNS TEXT AS $$
BEGIN
    RETURN 'c' || encode(gen_random_bytes(12), 'base64')::text;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar timestamp automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TABELAS PRINCIPAIS
-- =====================================================

-- 1. users
CREATE TABLE IF NOT EXISTS users (
    id              VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do usuário (CUID)
    email           VARCHAR(255) UNIQUE NOT NULL, -- Endereço de e-mail do usuário (único)
    username        VARCHAR(100) UNIQUE NOT NULL, -- Nome de usuário do usuário (único)
    full_name       VARCHAR(255), -- Nome completo do usuário
    hashed_password VARCHAR(255) NOT NULL, -- Senha do usuário (hash)
    is_active       BOOLEAN DEFAULT TRUE, -- Indica se o usuário está ativo
    is_superuser    BOOLEAN DEFAULT FALSE, -- Indica se o usuário é um superusuário (admin)
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora da última atualização do registro
);

-- 2. agents
CREATE TABLE IF NOT EXISTS agents (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do agente (CUID)
    name         VARCHAR(255) NOT NULL, -- Nome do agente
    description  TEXT, -- Descrição do agente
    provider     VARCHAR(100) NOT NULL, -- Provedor do modelo de IA (ex: openai, anthropic)
    model        VARCHAR(100) NOT NULL, -- Modelo de IA (ex: gpt-4, claude-3)
    system_prompt TEXT, -- Prompt do sistema para o agente
    temperature  DECIMAL(3,2) DEFAULT 0.7, -- Temperatura do modelo de IA (0.0 - 1.0)
    max_tokens   INTEGER DEFAULT 1000, -- Número máximo de tokens para a resposta do agente
    is_active    BOOLEAN DEFAULT TRUE, -- Indica se o agente está ativo
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário que criou o agente (FK para users)
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. conversations
CREATE TABLE IF NOT EXISTS conversations (
    id             VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da conversa (CUID)
    title          VARCHAR(255), -- Título da conversa
    user_id        VARCHAR(30) NOT NULL, -- ID do usuário que iniciou a conversa (FK para users)
    agent_id       VARCHAR(30), -- ID do agente envolvido na conversa (FK para agents, pode ser NULL)
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id)  REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- 4. messages
CREATE TABLE IF NOT EXISTS messages (
    id              VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da mensagem (CUID)
    content         TEXT NOT NULL, -- Conteúdo da mensagem
    role            VARCHAR(20) NOT NULL, -- Papel do emissor da mensagem (user, assistant, system)
    conversation_id VARCHAR(30) NOT NULL, -- ID da conversa a que a mensagem pertence (FK para conversations)
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- 5. files
CREATE TABLE IF NOT EXISTS files (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do arquivo (CUID)
    filename      VARCHAR(255) NOT NULL, -- Nome do arquivo (com extensão)
    original_name VARCHAR(255) NOT NULL, -- Nome original do arquivo (antes do upload)
    file_path     VARCHAR(500) NOT NULL, -- Caminho do arquivo no sistema de arquivos
    file_size     INTEGER NOT NULL, -- Tamanho do arquivo em bytes
    mime_type     VARCHAR(100) NOT NULL, -- Tipo MIME do arquivo (ex: image/jpeg)
    category      VARCHAR(50) NOT NULL, -- Categoria do arquivo (image, video, audio, document, archive)
    is_public     BOOLEAN DEFAULT FALSE, -- Indica se o arquivo é público
    user_id       VARCHAR(30) NOT NULL, -- ID do usuário que enviou o arquivo (FK para users)
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. workflows
CREATE TABLE IF NOT EXISTS workflows (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do workflow (CUID)
    name         VARCHAR(255) NOT NULL, -- Nome do workflow
    description  TEXT, -- Descrição do workflow
    definition   JSONB NOT NULL, -- Definição do workflow em formato JSON
    is_active    BOOLEAN DEFAULT TRUE, -- Indica se o workflow está ativo
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário que criou o workflow (FK para users)
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. workflow_executions
CREATE TABLE IF NOT EXISTS workflow_executions (
    id               VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da execução do workflow (CUID)
    status           VARCHAR(20) NOT NULL DEFAULT 'pending', -- Status da execução (pending, running, completed, failed)
    input_data       JSONB, -- Dados de entrada para o workflow em formato JSON
    output_data      JSONB, -- Dados de saída do workflow em formato JSON
    error_message    TEXT, -- Mensagem de erro (se houver)
    workflow_id      VARCHAR(30) NOT NULL, -- ID do workflow executado (FK para workflows)
    started_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora do início da execução
    completed_at     TIMESTAMP WITH TIME ZONE, -- Data e hora da conclusão da execução (pode ser NULL se ainda estiver em execução)
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- 8. nodes
CREATE TABLE IF NOT EXISTS nodes (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do nó (CUID)
    name          VARCHAR(255) NOT NULL, -- Nome do nó
    category      VARCHAR(100) NOT NULL, -- Categoria do nó (ai, data, logic, io, etc.)
    description   TEXT, -- Descrição do nó
    version       VARCHAR(50) DEFAULT '1.0.0', -- Versão do nó
    definition    JSONB NOT NULL, -- Definição do nó em formato JSON
    is_public     BOOLEAN DEFAULT FALSE, -- Indica se o nó é público
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora da última atualização do registro
);

-- 9. user_variables
CREATE TABLE IF NOT EXISTS user_variables (
    id         VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da variável (CUID)
    key        VARCHAR(255) NOT NULL, -- Chave da variável
    value      TEXT NOT NULL, -- Valor da variável
    is_secret  BOOLEAN DEFAULT FALSE, -- Indica se a variável é secreta (ex: senha)
    user_id    VARCHAR(30) NOT NULL, -- ID do usuário a que a variável pertence (FK para users)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, key) -- Garante que cada usuário tenha apenas uma variável com determinada chave
);

-- =====================================================
-- TABELAS DE EXECUÇÃO (MIGRAÇÃO 002)
-- =====================================================

-- 10. node_executions
CREATE TABLE IF NOT EXISTS node_executions (
    id                      VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da execução do nó (CUID)
    workflow_execution_id   VARCHAR(30) NOT NULL, -- ID da execução do workflow a que o nó pertence (FK para workflow_executions)
    node_id                 VARCHAR(30) NOT NULL, -- ID do nó executado (FK para nodes)
    status                  VARCHAR(20) DEFAULT 'pending', -- Status da execução do nó (pending, running, completed, failed, skipped)
    input_data              JSONB, -- Dados de entrada para o nó em formato JSON
    output_data             JSONB, -- Dados de saída do nó em formato JSON
    error_message           TEXT, -- Mensagem de erro (se houver)
    execution_time_ms       INTEGER DEFAULT 0, -- Tempo de execução do nó em milissegundos
    started_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora do início da execução do nó
    completed_at            TIMESTAMP WITH TIME ZONE, -- Data e hora da conclusão da execução do nó (pode ser NULL se ainda estiver em execução)
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id)                REFERENCES nodes(id) ON DELETE CASCADE
);

-- 11. execution_queue
CREATE TABLE IF NOT EXISTS execution_queue (
    id                    VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da entrada na fila (CUID)
    workflow_execution_id VARCHAR(30) NOT NULL, -- ID da execução do workflow a que a entrada na fila pertence (FK para workflow_executions)
    node_id               VARCHAR(30) NOT NULL, -- ID do nó a ser executado (FK para nodes)
    priority              INTEGER DEFAULT 0, -- Prioridade da entrada na fila (0 = mais alta)
    scheduled_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora agendada para a execução
    status                VARCHAR(20) DEFAULT 'queued', -- Status da entrada na fila (queued, processing, completed, failed)
    attempts              INTEGER DEFAULT 0, -- Número de tentativas de execução
    max_attempts          INTEGER DEFAULT 3, -- Número máximo de tentativas de execução
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id)                REFERENCES nodes(id) ON DELETE CASCADE
);

-- 12. execution_metrics
CREATE TABLE IF NOT EXISTS execution_metrics (
    id                        VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único das métricas (CUID)
    workflow_execution_id     VARCHAR(30) NOT NULL, -- ID da execução do workflow a que as métricas pertencem (FK para workflow_executions)
    total_nodes               INTEGER DEFAULT 0, -- Número total de nós no workflow
    completed_nodes           INTEGER DEFAULT 0, -- Número de nós completados
    failed_nodes              INTEGER DEFAULT 0, -- Número de nós que falharam
    total_execution_time_ms   INTEGER DEFAULT 0, -- Tempo total de execução do workflow em milissegundos
    memory_usage_mb           DECIMAL(10,2) DEFAULT 0, -- Uso de memória em MB
    cpu_usage_percent         DECIMAL(5,2) DEFAULT 0, -- Uso da CPU em porcentagem
    created_at                TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at                TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE
);

-- =====================================================
-- TABELAS DE TEMPLATES (MIGRAÇÃO 003)
-- =====================================================

-- 13. workflow_templates
CREATE TABLE IF NOT EXISTS workflow_templates (
    id                VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do template (CUID)
    name              VARCHAR(255) NOT NULL, -- Nome do template
    description       TEXT, -- Descrição do template
    category          VARCHAR(100) NOT NULL, -- Categoria do template
    tags              TEXT, -- Tags do template (array JSON)
    workflow_definition JSONB NOT NULL, -- Definição do workflow em formato JSON
    preview_image     VARCHAR(500), -- URL da imagem de visualização do template
    author_id         VARCHAR(30) NOT NULL, -- ID do autor do template (FK para users)
    version           VARCHAR(50) DEFAULT '1.0.0', -- Versão do template
    is_public         BOOLEAN DEFAULT FALSE, -- Indica se o template é público
    is_featured       BOOLEAN DEFAULT FALSE, -- Indica se o template é destacado
    downloads_count   INTEGER DEFAULT 0, -- Número de downloads do template
    rating_average    DECIMAL(3,2) DEFAULT 0.00, -- Média das avaliações do template
    rating_count      INTEGER DEFAULT 0, -- Número de avaliações do template
    price             DECIMAL(10,2) DEFAULT 0.00, -- Preço do template
    is_free           BOOLEAN DEFAULT TRUE, -- Indica se o template é gratuito
    license           VARCHAR(50) DEFAULT 'MIT', -- Licença do template
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 14. template_reviews
CREATE TABLE IF NOT EXISTS template_reviews (
    id                   VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da avaliação (CUID)
    template_id          VARCHAR(30) NOT NULL, -- ID do template avaliado (FK para workflow_templates)
    user_id              VARCHAR(30) NOT NULL, -- ID do usuário que fez a avaliação (FK para users)
    rating               INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- Avaliação (1 a 5 estrelas)
    comment              TEXT, -- Comentário da avaliação
    is_verified_purchase BOOLEAN DEFAULT FALSE, -- Indica se a avaliação é de uma compra verificada
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(template_id, user_id) -- Garante que cada usuário só pode avaliar um template uma vez
);

-- 15. template_downloads
CREATE TABLE IF NOT EXISTS template_downloads (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do download (CUID)
    template_id   VARCHAR(30) NOT NULL, -- ID do template baixado (FK para workflow_templates)
    user_id       VARCHAR(30) NOT NULL, -- ID do usuário que fez o download (FK para users)
    download_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora do download
    ip_address    INET, -- Endereço IP do usuário que fez o download
    user_agent    TEXT, -- User agent do usuário que fez o download
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE
);

-- 16. template_favorites
CREATE TABLE IF NOT EXISTS template_favorites (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do favorito (CUID)
    template_id   VARCHAR(30) NOT NULL, -- ID do template favoritado (FK para workflow_templates)
    user_id       VARCHAR(30) NOT NULL, -- ID do usuário que favoritou (FK para users)
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(template_id, user_id) -- Garante que cada usuário só pode favoritar um template uma vez
);

-- 17. template_collections
CREATE TABLE IF NOT EXISTS template_collections (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da coleção (CUID)
    name         VARCHAR(255) NOT NULL, -- Nome da coleção
    description  TEXT, -- Descrição da coleção
    owner_id     VARCHAR(30) NOT NULL, -- ID do proprietário da coleção (FK para users)
    is_public    BOOLEAN DEFAULT FALSE, -- Indica se a coleção é pública
    template_ids TEXT, -- IDs dos templates na coleção (array JSON)
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 18. template_usage
CREATE TABLE IF NOT EXISTS template_usage (
    id             VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do uso do template (CUID)
    template_id    VARCHAR(30) NOT NULL, -- ID do template usado (FK para workflow_templates)
    user_id        VARCHAR(30) NOT NULL, -- ID do usuário que usou o template (FK para users)
    workflow_id    VARCHAR(30), -- ID do workflow criado a partir do template (FK para workflows, pode ser NULL)
    usage_date     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora do uso do template
    usage_context  VARCHAR(100), -- Contexto de uso (creation, modification, execution)
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE SET NULL
);

-- =====================================================
-- TABELAS DE CONFIGURAÇÃO DE EXECUTORES (MIGRAÇÃO 004)
-- =====================================================

-- 19. executor_configs
CREATE TABLE IF NOT EXISTS executor_configs (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da configuração do executor (CUID)
    name         VARCHAR(255) NOT NULL, -- Nome da configuração
    executor_type VARCHAR(100) NOT NULL, -- Tipo de executor (http, python, javascript, etc.)
    config       JSONB NOT NULL, -- Configuração do executor em formato JSON
    is_active    BOOLEAN DEFAULT TRUE, -- Indica se a configuração está ativa
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora da última atualização do registro
);

-- 20. http_cache
CREATE TABLE IF NOT EXISTS http_cache (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do cache HTTP (CUID)
    url_hash     VARCHAR(64) NOT NULL UNIQUE, -- Hash da URL (para identificação única)
    url          TEXT NOT NULL, -- URL da requisição HTTP
    method       VARCHAR(10) DEFAULT 'GET', -- Método HTTP (GET, POST, etc.)
    headers      JSONB, -- Headers da requisição HTTP em formato JSON
    response_data JSONB, -- Dados da resposta HTTP em formato JSON
    status_code  INTEGER, -- Código de status HTTP
    expires_at   TIMESTAMP WITH TIME ZONE, -- Data e hora de expiração do cache
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora da criação do registro
);

-- 21. executor_metrics
CREATE TABLE IF NOT EXISTS executor_metrics (
    id                      VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único das métricas do executor (CUID)
    executor_type           VARCHAR(100) NOT NULL, -- Tipo de executor (http, python, javascript, etc.)
    total_executions        INTEGER DEFAULT 0, -- Número total de execuções
    successful_executions   INTEGER DEFAULT 0, -- Número de execuções bem-sucedidas
    failed_executions       INTEGER DEFAULT 0, -- Número de execuções que falharam
    average_execution_time_ms DECIMAL(10,2) DEFAULT 0, -- Tempo médio de execução em milissegundos
    last_execution_at       TIMESTAMP WITH TIME ZONE, -- Data e hora da última execução
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora da última atualização do registro
);

-- =====================================================
-- TABELAS DO MARKETPLACE (MIGRAÇÃO 005)
-- =====================================================

-- 22. marketplace_components
CREATE TABLE IF NOT EXISTS marketplace_components (
    id               VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do componente (CUID)
    name             VARCHAR(255) NOT NULL, -- Nome do componente
    description      TEXT, -- Descrição do componente
    category         VARCHAR(100) NOT NULL, -- Categoria do componente
    component_type   VARCHAR(50) NOT NULL, -- Tipo de componente (ex: workflow, node)
    tags             TEXT, -- Tags do componente (array JSON)
    price            DECIMAL(10,2) DEFAULT 0.00, -- Preço do componente
    is_free          BOOLEAN DEFAULT TRUE, -- Indica se o componente é gratuito
    author_id        VARCHAR(30) NOT NULL, -- ID do autor do componente (FK para users)
    version          VARCHAR(50) NOT NULL DEFAULT '1.0.0', -- Versão do componente
    content          TEXT, -- Conteúdo do componente (JSON)
    metadata         TEXT, -- Metadados do componente (JSON)
    downloads_count  INTEGER DEFAULT 0, -- Número de downloads do componente
    rating_average   DECIMAL(3,2) DEFAULT 0.00, -- Média das avaliações do componente
    rating_count     INTEGER DEFAULT 0, -- Número de avaliações do componente
    is_featured      BOOLEAN DEFAULT FALSE, -- Indica se o componente é destacado
    is_approved      BOOLEAN DEFAULT FALSE, -- Indica se o componente foi aprovado
    status           VARCHAR(20) DEFAULT 'pending', -- Status do componente (pending, approved, rejected)
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 23. component_ratings
CREATE TABLE IF NOT EXISTS component_ratings (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da avaliação (CUID)
    component_id VARCHAR(30) NOT NULL, -- ID do componente avaliado (FK para marketplace_components)
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário que fez a avaliação (FK para users)
    rating       INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- Avaliação (1 a 5 estrelas)
    comment      TEXT, -- Comentário da avaliação
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(component_id, user_id) -- Garante que cada usuário só pode avaliar um componente uma vez
);

-- 24. component_downloads
CREATE TABLE IF NOT EXISTS component_downloads (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do download (CUID)
    component_id  VARCHAR(30) NOT NULL, -- ID do componente baixado (FK para marketplace_components)
    user_id       VARCHAR(30) NOT NULL, -- ID do usuário que fez o download (FK para users)
    download_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora do download
    ip_address    INET, -- Endereço IP do usuário que fez o download
    user_agent    TEXT, -- User agent do usuário que fez o download
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE
);

-- 25. component_purchases
CREATE TABLE IF NOT EXISTS component_purchases (
    id             VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da compra (CUID)
    component_id   VARCHAR(30) NOT NULL, -- ID do componente comprado (FK para marketplace_components)
    user_id        VARCHAR(30) NOT NULL, -- ID do usuário que fez a compra (FK para users)
    purchase_price DECIMAL(10,2) NOT NULL, -- Preço pago pelo componente
    payment_method VARCHAR(50), -- Método de pagamento usado
    transaction_id VARCHAR(255), -- ID da transação
    purchase_date  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da compra
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE
);

-- 26. component_favorites
CREATE TABLE IF NOT EXISTS component_favorites (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do favorito (CUID)
    component_id VARCHAR(30) NOT NULL, -- ID do componente favoritado (FK para marketplace_components)
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário que favoritou (FK para users)
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(component_id, user_id) -- Garante que cada usuário só pode favoritar um componente uma vez
);

-- 27. component_versions
CREATE TABLE IF NOT EXISTS component_versions (
    id          VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da versão (CUID)
    component_id VARCHAR(30) NOT NULL, -- ID do componente (FK para marketplace_components)
    version      VARCHAR(50) NOT NULL, -- Versão do componente (ex: 1.0.0)
    changelog    TEXT, -- Changelog da versão
    content      TEXT, -- Conteúdo da versão (JSON)
    is_active    BOOLEAN DEFAULT TRUE, -- Indica se a versão está ativa
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    UNIQUE(component_id, version) -- Garante que cada componente tenha apenas uma versão com determinado número
);

-- =====================================================
-- TABELAS DE WORKSPACES (MIGRAÇÃO 005)
-- =====================================================

-- 28. workspaces
CREATE TABLE IF NOT EXISTS workspaces (
    id          VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do workspace (CUID)
    name        VARCHAR(255) NOT NULL, -- Nome do workspace
    description TEXT, -- Descrição do workspace
    owner_id    VARCHAR(30) NOT NULL, -- ID do proprietário do workspace (FK para users)
    is_public   BOOLEAN DEFAULT FALSE, -- Indica se o workspace é público
    settings    JSONB DEFAULT '{}', -- Configurações do workspace em formato JSON
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 29. workspace_members
CREATE TABLE IF NOT EXISTS workspace_members (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do membro (CUID)
    workspace_id  VARCHAR(30) NOT NULL, -- ID do workspace a que o membro pertence (FK para workspaces)
    user_id       VARCHAR(30) NOT NULL, -- ID do usuário que é membro (FK para users)
    role          VARCHAR(20) DEFAULT 'member', -- Papel do membro (owner, admin, member, viewer)
    permissions   JSONB DEFAULT '{}', -- Permissões do membro em formato JSON
    joined_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora em que o membro se juntou ao workspace
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(workspace_id, user_id) -- Garante que um usuário só pode ser membro de um workspace uma vez
);

-- 30. workspace_invitations
CREATE TABLE IF NOT EXISTS workspace_invitations (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do convite (CUID)
    workspace_id VARCHAR(30) NOT NULL, -- ID do workspace para o qual o usuário foi convidado (FK para workspaces)
    email        VARCHAR(255) NOT NULL, -- E-mail do usuário convidado
    role         VARCHAR(20) DEFAULT 'member', -- Papel do usuário convidado (member, admin, etc.)
    invited_by   VARCHAR(30) NOT NULL, -- ID do usuário que convidou (FK para users)
    token        VARCHAR(255) UNIQUE NOT NULL, -- Token único para o convite
    expires_at   TIMESTAMP WITH TIME ZONE NOT NULL, -- Data e hora de expiração do convite
    accepted_at  TIMESTAMP WITH TIME ZONE, -- Data e hora em que o convite foi aceito (pode ser NULL se ainda não aceito)
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by)    REFERENCES users(id) ON DELETE CASCADE
);

-- 31. workspace_projects
CREATE TABLE IF NOT EXISTS workspace_projects (
    id          VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do projeto (CUID)
    workspace_id VARCHAR(30) NOT NULL, -- ID do workspace a que o projeto pertence (FK para workspaces)
    name        VARCHAR(255) NOT NULL, -- Nome do projeto
    description TEXT, -- Descrição do projeto
    status      VARCHAR(20) DEFAULT 'active', -- Status do projeto (active, archived, completed)
    created_by  VARCHAR(30) NOT NULL, -- ID do usuário que criou o projeto (FK para users)
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by)    REFERENCES users(id) ON DELETE CASCADE
);

-- 32. project_collaborators: Associa usuários aos projetos, especificando o papel de cada colaborador.
CREATE TABLE IF NOT EXISTS project_collaborators (
    id         VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do colaborador (CUID)
    project_id VARCHAR(30) NOT NULL, -- ID do projeto a que o colaborador pertence (FK para workspace_projects)
    user_id    VARCHAR(30) NOT NULL, -- ID do usuário que é colaborador (FK para users)
    role       VARCHAR(20) DEFAULT 'collaborator', -- Papel do colaborador (por exemplo: owner, collaborator, viewer)
    added_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora em que o colaborador foi adicionado
    FOREIGN KEY (project_id) REFERENCES workspace_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id) -- Garante que um usuário só pode ser associado a um mesmo projeto uma vez
);

-- =====================================================
-- TABELAS ADICIONAIS (33 a 46)
-- =====================================================

-- 33. activity_logs: Registra atividades importantes do sistema e dos usuários.
CREATE TABLE IF NOT EXISTS activity_logs (
    id              VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do log de atividade (CUID)
    user_id         VARCHAR(30), -- ID do usuário que realizou a atividade (FK para users; pode ser NULL para atividades do sistema)
    activity_type   VARCHAR(50) NOT NULL, -- Tipo de atividade (ex: login, update, delete, create)
    details         TEXT, -- Detalhes sobre a atividade realizada
    ip_address      INET, -- Endereço IP de onde a atividade foi realizada
    occurred_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora em que a atividade ocorreu
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 34. user_sessions: Armazena sessões de login dos usuários.
CREATE TABLE IF NOT EXISTS user_sessions (
    id                VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da sessão (CUID)
    user_id           VARCHAR(30) NOT NULL, -- ID do usuário associado à sessão (FK para users)
    session_token     VARCHAR(255) UNIQUE NOT NULL, -- Token único da sessão
    login_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora do login
    last_activity_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atividade na sessão
    expires_at        TIMESTAMP WITH TIME ZONE, -- Data e hora de expiração da sessão
    ip_address        INET, -- Endereço IP do usuário durante a sessão
    user_agent        TEXT, -- User agent do navegador ou dispositivo
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do registro
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 35. notifications: Gerencia notificações enviadas aos usuários.
CREATE TABLE IF NOT EXISTS notifications (
    id          VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da notificação (CUID)
    user_id     VARCHAR(30) NOT NULL, -- ID do usuário que receberá a notificação (FK para users)
    message     TEXT NOT NULL, -- Conteúdo da notificação
    type        VARCHAR(50) DEFAULT 'generic', -- Tipo da notificação (ex: alert, warning, info)
    is_read     BOOLEAN DEFAULT FALSE, -- Indica se a notificação foi lida
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação da notificação
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização da notificação
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 36. api_keys: Armazena as chaves API utilizadas para integrações.
CREATE TABLE IF NOT EXISTS api_keys (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da chave API (CUID)
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário associado à chave API (FK para users)
    api_key      VARCHAR(255) UNIQUE NOT NULL, -- Valor da chave API
    description  TEXT, -- Descrição ou finalidade da chave API
    is_active    BOOLEAN DEFAULT TRUE, -- Indica se a chave API está ativa
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do registro
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 37. integration_configs: Configurações para integrações com serviços externos.
CREATE TABLE IF NOT EXISTS integration_configs (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da configuração de integração (CUID)
    service_name VARCHAR(100) NOT NULL, -- Nome do serviço de integração (ex: Slack, GitHub, Stripe)
    config       JSONB NOT NULL, -- Configuração do serviço em formato JSON
    is_active    BOOLEAN DEFAULT TRUE, -- Indica se a integração está ativa
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da criação do registro
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP  -- Data e hora da última atualização do registro
);

-- 38. billing_transactions: Registra transações de pagamento e cobrança dos usuários.
CREATE TABLE IF NOT EXISTS billing_transactions (
    id                  VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da transação de cobrança (CUID)
    user_id             VARCHAR(30) NOT NULL, -- ID do usuário que realizou a transação (FK para users)
    amount              DECIMAL(10,2) NOT NULL, -- Valor da transação
    currency            VARCHAR(10) NOT NULL, -- Tipo de moeda utilizada (ex: USD, EUR)
    status              VARCHAR(20) NOT NULL, -- Status da transação (pending, completed, failed, refunded)
    payment_method      VARCHAR(50), -- Método de pagamento utilizado (ex: credit card, PayPal)
    transaction_details JSONB, -- Detalhes adicionais da transação em formato JSON
    transaction_date    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da transação
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 39. subscription_plans: Define os planos de assinatura disponíveis.
CREATE TABLE IF NOT EXISTS subscription_plans (
    id            VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do plano de assinatura (CUID)
    name          VARCHAR(255) NOT NULL, -- Nome do plano de assinatura
    description   TEXT, -- Descrição do plano e benefícios oferecidos
    price         DECIMAL(10,2) NOT NULL, -- Preço do plano
    billing_cycle VARCHAR(50) NOT NULL, -- Ciclo de faturamento (ex: monthly, yearly)
    features      JSONB, -- Funcionalidades incluídas no plano, em formato JSON
    is_active     BOOLEAN DEFAULT TRUE, -- Indica se o plano está ativo
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do registro
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP  -- Data e hora da última atualização do registro
);

-- 40. user_subscriptions: Liga os usuários aos seus respectivos planos de assinatura.
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id          VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da assinatura do usuário (CUID)
    user_id     VARCHAR(30) NOT NULL, -- ID do usuário que possui a assinatura (FK para users)
    plan_id     VARCHAR(30) NOT NULL, -- ID do plano de assinatura (FK para subscription_plans)
    start_date  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data de início da assinatura
    end_date    TIMESTAMP WITH TIME ZONE, -- Data de término da assinatura (pode ser NULL se ativa ou sem término definido)
    status      VARCHAR(20) DEFAULT 'active', -- Status da assinatura (active, canceled, expired)
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do registro
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do registro
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE CASCADE
);

-- 41. support_tickets: Registra os chamados de suporte abertos pelos usuários.
CREATE TABLE IF NOT EXISTS support_tickets (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do chamado de suporte (CUID)
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário que abriu o chamado (FK para users)
    subject      VARCHAR(255) NOT NULL, -- Assunto do chamado
    description  TEXT NOT NULL, -- Descrição detalhada do problema ou solicitação
    status       VARCHAR(20) DEFAULT 'open', -- Status do chamado (open, pending, closed)
    priority     VARCHAR(20) DEFAULT 'medium', -- Prioridade do chamado (low, medium, high)
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do chamado
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização do chamado
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 42. ticket_messages: Armazena as mensagens dos tickets de suporte.
CREATE TABLE IF NOT EXISTS ticket_messages (
    id         VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da mensagem do ticket (CUID)
    ticket_id  VARCHAR(30) NOT NULL, -- ID do ticket ao qual a mensagem pertence (FK para support_tickets)
    sender_id  VARCHAR(30) NOT NULL, -- ID do usuário que enviou a mensagem (FK para users)
    message    TEXT NOT NULL, -- Conteúdo da mensagem
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora em que a mensagem foi enviada
    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 43. referral_codes: Armazena os códigos de indicação para promoções e descontos.
CREATE TABLE IF NOT EXISTS referral_codes (
    id             VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do código de indicação (CUID)
    code           VARCHAR(50) UNIQUE NOT NULL, -- Código de indicação único
    discount_value DECIMAL(10,2) DEFAULT 0.00, -- Valor do desconto oferecido pelo código
    usage_limit    INTEGER DEFAULT 1, -- Número máximo de vezes que o código pode ser utilizado
    valid_until    TIMESTAMP WITH TIME ZONE, -- Data e hora de validade do código
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora de criação do código
);

-- 44. user_referrals: Registra as indicações realizadas pelos usuários.
CREATE TABLE IF NOT EXISTS user_referrals (
    id                VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único da indicação do usuário (CUID)
    user_id           VARCHAR(30) NOT NULL, -- ID do usuário que fez a indicação (FK para users)
    referred_user_id  VARCHAR(30), -- ID do usuário indicado (FK para users; pode ser NULL se ainda não se registrou)
    referral_code     VARCHAR(50) NOT NULL, -- Código de indicação utilizado
    referral_date     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da indicação
    reward_given      BOOLEAN DEFAULT FALSE, -- Indica se a recompensa pela indicação foi concedida
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (referred_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 45. data_exports: Gerencia os pedidos de exportação de dados dos usuários.
CREATE TABLE IF NOT EXISTS data_exports (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do registro de exportação (CUID)
    user_id      VARCHAR(30) NOT NULL, -- ID do usuário que solicitou a exportação (FK para users)
    export_type  VARCHAR(50) NOT NULL, -- Tipo de exportação (ex: csv, json, xml)
    status       VARCHAR(20) DEFAULT 'pending', -- Status da exportação (pending, completed, failed)
    file_path    VARCHAR(500), -- Caminho ou URL do arquivo exportado
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da solicitação de exportação
    completed_at TIMESTAMP WITH TIME ZONE, -- Data e hora da conclusão da exportação
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 46. server_status: Monitora o status e desempenho dos servidores do sistema.
CREATE TABLE IF NOT EXISTS server_status (
    id           VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(), -- ID único do registro de status do servidor (CUID)
    server_name  VARCHAR(255) NOT NULL, -- Nome ou identificador do servidor
    status       VARCHAR(20) NOT NULL, -- Status do servidor (online, offline, maintenance)
    load         DECIMAL(5,2) DEFAULT 0.00, -- Carga do servidor em porcentagem (ex: 75.50)
    memory_usage DECIMAL(10,2) DEFAULT 0.00, -- Uso de memória do servidor em MB
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última verificação do status
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Data e hora de criação do registro
);

-- =====================================================
-- VIEWS ADICIONAIS
-- =====================================================

-- 1. active_users_view: Exibe os usuários ativos com informações básicas.
CREATE OR REPLACE VIEW active_users_view AS
SELECT
    id,
    email,
    username,
    full_name,
    created_at
FROM users
WHERE is_active = TRUE;

-- 2. agent_details_view: Exibe os detalhes dos agentes juntamente com o usuário que os criou.
CREATE OR REPLACE VIEW agent_details_view AS
SELECT
    a.id AS agent_id,
    a.name AS agent_name,
    a.description,
    a.provider,
    a.model,
    a.system_prompt,
    a.temperature,
    a.max_tokens,
    a.is_active,
    a.user_id,
    u.username AS created_by,
    a.created_at
FROM agents a
JOIN users u ON a.user_id = u.id;

-- 3. conversation_summary_view: Resume informações de conversas, incluindo contagem de mensagens.
CREATE OR REPLACE VIEW conversation_summary_view AS
SELECT
    c.id AS conversation_id,
    c.title,
    c.user_id,
    u.username AS owner_username,
    c.agent_id,
    a.name AS agent_name,
    c.created_at,
    c.updated_at,
    (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) AS total_messages
FROM conversations c
LEFT JOIN users u ON c.user_id = u.id
LEFT JOIN agents a ON c.agent_id = a.id;

-- 4. workflow_execution_summary_view: Fornece um resumo das execuções de workflows, agregando dados dos nós.
CREATE OR REPLACE VIEW workflow_execution_summary_view AS
SELECT
    we.id AS workflow_execution_id,
    we.workflow_id,
    w.name AS workflow_name,
    we.status,
    we.started_at,
    we.completed_at,
    (SELECT COUNT(*) FROM node_executions ne WHERE ne.workflow_execution_id = we.id) AS total_nodes,
    (SELECT COUNT(*) FROM node_executions ne WHERE ne.workflow_execution_id = we.id AND ne.status = 'completed') AS completed_nodes
FROM workflow_executions we
LEFT JOIN workflows w ON we.workflow_id = w.id;

-- 5. workspace_overview_view: Apresenta uma visão geral dos workspaces, incluindo contagem de membros e projetos.
CREATE OR REPLACE VIEW workspace_overview_view AS
SELECT
    w.id AS workspace_id,
    w.name AS workspace_name,
    w.description,
    w.owner_id,
    u.username AS owner_username,
    w.created_at,
    (SELECT COUNT(*) FROM workspace_members wm WHERE wm.workspace_id = w.id) AS total_members,
    (SELECT COUNT(*) FROM workspace_projects wp WHERE wp.workspace_id = w.id) AS total_projects
FROM workspaces w
JOIN users u ON w.owner_id = u.id;

-- 6. template_overview_view: Fornece uma visão geral dos templates de workflows com informações relevantes.
CREATE OR REPLACE VIEW template_overview_view AS
SELECT
    wt.id AS template_id,
    wt.name,
    wt.description,
    wt.category,
    wt.tags,
    wt.version,
    wt.is_public,
    wt.is_featured,
    wt.downloads_count,
    wt.rating_average,
    wt.rating_count,
    wt.price,
    wt.is_free,
    wt.license,
    wt.created_at,
    u.username AS author_username
FROM workflow_templates wt
JOIN users u ON wt.author_id = u.id;

-- 7. component_overview_view: Exibe uma visão geral dos componentes disponíveis no marketplace.
CREATE OR REPLACE VIEW component_overview_view AS
SELECT
    mc.id AS component_id,
    mc.name AS component_name,
    mc.description,
    mc.category,
    mc.component_type,
    mc.tags,
    mc.price,
    mc.is_free,
    mc.author_id,
    u.username AS author_username,
    mc.version,
    mc.downloads_count,
    mc.rating_average,
    mc.rating_count,
    mc.is_featured,
    mc.is_approved,
    mc.status,
    mc.created_at
FROM marketplace_components mc
JOIN users u ON mc.author_id = u.id;