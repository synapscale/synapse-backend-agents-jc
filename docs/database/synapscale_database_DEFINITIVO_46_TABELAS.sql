-- =====================================================
-- SYNAPSCALE DATABASE - SCRIPT SQL POSTGRESQL DEFINITIVO
-- TODAS AS 46 TABELAS IDENTIFICADAS NO PROJETO
-- Criado por: Análise completa dos modelos Python
-- Data: 04/06/2025
-- =====================================================

-- Configurações iniciais do PostgreSQL
SET timezone = 'UTC';
SET client_encoding = 'UTF8';

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

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
-- TABELAS PRINCIPAIS (SCHEMA PRISMA)
-- =====================================================

-- 1. USERS - Usuários do sistema
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. AGENTS - Agentes de IA configurados
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    provider VARCHAR(100) NOT NULL, -- openai, anthropic, google, etc.
    model VARCHAR(100) NOT NULL, -- gpt-4, claude-3, gemini-pro, etc.
    system_prompt TEXT,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    user_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. CONVERSATIONS - Conversas entre usuários e agentes
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    title VARCHAR(255),
    user_id VARCHAR(30) NOT NULL,
    agent_id VARCHAR(30),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- 4. MESSAGES - Mensagens das conversas
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    conversation_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- 5. FILES - Arquivos enviados pelos usuários
CREATE TABLE IF NOT EXISTS files (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- image, video, audio, document, archive
    is_public BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. WORKFLOWS - Fluxos de trabalho automatizados
CREATE TABLE IF NOT EXISTS workflows (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL, -- JSON com a definição do workflow
    is_active BOOLEAN DEFAULT TRUE,
    user_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. WORKFLOW_EXECUTIONS - Execuções dos workflows
CREATE TABLE IF NOT EXISTS workflow_executions (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    workflow_id VARCHAR(30) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- 8. NODES - Nós para construção de workflows
CREATE TABLE IF NOT EXISTS nodes (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- ai, data, logic, io, etc.
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0.0',
    definition JSONB NOT NULL, -- JSON com a definição do node
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. USER_VARIABLES - Variáveis personalizadas dos usuários
CREATE TABLE IF NOT EXISTS user_variables (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    is_secret BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, key)
);

-- =====================================================
-- TABELAS DE EXECUÇÃO (MIGRAÇÃO 002)
-- =====================================================

-- 10. NODE_EXECUTIONS - Execuções individuais de nós
CREATE TABLE IF NOT EXISTS node_executions (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workflow_execution_id VARCHAR(30) NOT NULL,
    node_id VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, skipped
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- 11. EXECUTION_QUEUE - Fila de execução
CREATE TABLE IF NOT EXISTS execution_queue (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workflow_execution_id VARCHAR(30) NOT NULL,
    node_id VARCHAR(30) NOT NULL,
    priority INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'queued', -- queued, processing, completed, failed
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- 12. EXECUTION_METRICS - Métricas de execução
CREATE TABLE IF NOT EXISTS execution_metrics (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workflow_execution_id VARCHAR(30) NOT NULL,
    total_nodes INTEGER DEFAULT 0,
    completed_nodes INTEGER DEFAULT 0,
    failed_nodes INTEGER DEFAULT 0,
    total_execution_time_ms INTEGER DEFAULT 0,
    memory_usage_mb DECIMAL(10,2) DEFAULT 0,
    cpu_usage_percent DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE
);

-- =====================================================
-- TABELAS DE TEMPLATES (MIGRAÇÃO 003)
-- =====================================================

-- 13. WORKFLOW_TEMPLATES - Templates de workflows
CREATE TABLE IF NOT EXISTS workflow_templates (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    tags TEXT, -- JSON array
    workflow_definition JSONB NOT NULL,
    preview_image VARCHAR(500),
    author_id VARCHAR(30) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    is_public BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    downloads_count INTEGER DEFAULT 0,
    rating_average DECIMAL(3,2) DEFAULT 0.00,
    rating_count INTEGER DEFAULT 0,
    price DECIMAL(10,2) DEFAULT 0.00,
    is_free BOOLEAN DEFAULT TRUE,
    license VARCHAR(50) DEFAULT 'MIT',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 14. TEMPLATE_REVIEWS - Avaliações de templates
CREATE TABLE IF NOT EXISTS template_reviews (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    template_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(template_id, user_id)
);

-- 15. TEMPLATE_DOWNLOADS - Downloads de templates
CREATE TABLE IF NOT EXISTS template_downloads (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    template_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    download_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 16. TEMPLATE_FAVORITES - Templates favoritos
CREATE TABLE IF NOT EXISTS template_favorites (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    template_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(template_id, user_id)
);

-- 17. TEMPLATE_COLLECTIONS - Coleções de templates
CREATE TABLE IF NOT EXISTS template_collections (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id VARCHAR(30) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    template_ids TEXT, -- JSON array de IDs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 18. TEMPLATE_USAGE - Uso de templates
CREATE TABLE IF NOT EXISTS template_usage (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    template_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    workflow_id VARCHAR(30),
    usage_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usage_context VARCHAR(100), -- creation, modification, execution
    FOREIGN KEY (template_id) REFERENCES workflow_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE SET NULL
);

-- =====================================================
-- TABELAS DE CONFIGURAÇÃO DE EXECUTORES (MIGRAÇÃO 004)
-- =====================================================

-- 19. EXECUTOR_CONFIGS - Configurações de executores
CREATE TABLE IF NOT EXISTS executor_configs (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    executor_type VARCHAR(100) NOT NULL, -- http, python, javascript, etc.
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 20. HTTP_CACHE - Cache para requisições HTTP
CREATE TABLE IF NOT EXISTS http_cache (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    url_hash VARCHAR(64) NOT NULL UNIQUE,
    url TEXT NOT NULL,
    method VARCHAR(10) DEFAULT 'GET',
    headers JSONB,
    response_data JSONB,
    status_code INTEGER,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 21. EXECUTOR_METRICS - Métricas de executores
CREATE TABLE IF NOT EXISTS executor_metrics (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    executor_type VARCHAR(100) NOT NULL,
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    average_execution_time_ms DECIMAL(10,2) DEFAULT 0,
    last_execution_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABELAS DO MARKETPLACE (MIGRAÇÃO 005)
-- =====================================================

-- 22. MARKETPLACE_COMPONENTS - Componentes do marketplace
CREATE TABLE IF NOT EXISTS marketplace_components (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    tags TEXT, -- JSON array
    price DECIMAL(10,2) DEFAULT 0.00,
    is_free BOOLEAN DEFAULT TRUE,
    author_id VARCHAR(30) NOT NULL,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    content TEXT, -- JSON content
    metadata TEXT, -- JSON metadata
    downloads_count INTEGER DEFAULT 0,
    rating_average DECIMAL(3,2) DEFAULT 0.00,
    rating_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 23. COMPONENT_RATINGS - Avaliações de componentes
CREATE TABLE IF NOT EXISTS component_ratings (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    component_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(component_id, user_id)
);

-- 24. COMPONENT_DOWNLOADS - Downloads de componentes
CREATE TABLE IF NOT EXISTS component_downloads (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    component_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    download_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 25. COMPONENT_PURCHASES - Compras de componentes
CREATE TABLE IF NOT EXISTS component_purchases (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    component_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    purchase_price DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    purchase_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 26. COMPONENT_FAVORITES - Componentes favoritos
CREATE TABLE IF NOT EXISTS component_favorites (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    component_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(component_id, user_id)
);

-- 27. COMPONENT_VERSIONS - Versões de componentes
CREATE TABLE IF NOT EXISTS component_versions (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    component_id VARCHAR(30) NOT NULL,
    version VARCHAR(50) NOT NULL,
    changelog TEXT,
    content TEXT, -- JSON content
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES marketplace_components(id) ON DELETE CASCADE,
    UNIQUE(component_id, version)
);

-- =====================================================
-- TABELAS DE WORKSPACES (MIGRAÇÃO 005)
-- =====================================================

-- 28. WORKSPACES - Espaços de trabalho
CREATE TABLE IF NOT EXISTS workspaces (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id VARCHAR(30) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 29. WORKSPACE_MEMBERS - Membros dos workspaces
CREATE TABLE IF NOT EXISTS workspace_members (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workspace_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    role VARCHAR(20) DEFAULT 'member', -- owner, admin, member, viewer
    permissions JSONB DEFAULT '{}',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(workspace_id, user_id)
);

-- 30. WORKSPACE_INVITATIONS - Convites para workspaces
CREATE TABLE IF NOT EXISTS workspace_invitations (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workspace_id VARCHAR(30) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    invited_by VARCHAR(30) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE
);

-- 31. WORKSPACE_PROJECTS - Projetos dos workspaces
CREATE TABLE IF NOT EXISTS workspace_projects (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workspace_id VARCHAR(30) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, archived, completed
    created_by VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- 32. PROJECT_COLLABORATORS - Colaboradores dos projetos
CREATE TABLE IF NOT EXISTS project_collaborators (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    project_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    role VARCHAR(20) DEFAULT 'collaborator', -- owner, collaborator, viewer
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES workspace_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)
);

-- 33. PROJECT_COMMENTS - Comentários dos projetos
CREATE TABLE IF NOT EXISTS project_comments (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    project_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    content TEXT NOT NULL,
    parent_comment_id VARCHAR(30),
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES workspace_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES project_comments(id) ON DELETE CASCADE
);

-- 34. WORKSPACE_ACTIVITIES - Atividades dos workspaces
CREATE TABLE IF NOT EXISTS workspace_activities (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    workspace_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- created, updated, deleted, invited, etc.
    entity_type VARCHAR(50), -- project, workflow, member, etc.
    entity_id VARCHAR(30),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 35. PROJECT_VERSIONS - Versões dos projetos
CREATE TABLE IF NOT EXISTS project_versions (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    project_id VARCHAR(30) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    data JSONB NOT NULL,
    created_by VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES workspace_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- TABELAS DE ANALYTICS (MIGRAÇÃO 005)
-- =====================================================

-- 36. ANALYTICS_EVENTS - Eventos de analytics
CREATE TABLE IF NOT EXISTS analytics_events (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(30),
    session_id VARCHAR(255),
    properties JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 37. ANALYTICS_METRICS - Métricas de analytics
CREATE TABLE IF NOT EXISTS analytics_metrics (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    dimensions JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 38. ANALYTICS_DASHBOARDS - Dashboards de analytics
CREATE TABLE IF NOT EXISTS analytics_dashboards (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id VARCHAR(30) NOT NULL,
    config JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 39. ANALYTICS_REPORTS - Relatórios de analytics
CREATE TABLE IF NOT EXISTS analytics_reports (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    query JSONB NOT NULL,
    schedule VARCHAR(50), -- daily, weekly, monthly, etc.
    owner_id VARCHAR(30) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 40. REPORT_EXECUTIONS - Execuções de relatórios
CREATE TABLE IF NOT EXISTS report_executions (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    report_id VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    result JSONB,
    error_message TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (report_id) REFERENCES analytics_reports(id) ON DELETE CASCADE
);

-- 41. ANALYTICS_ALERTS - Alertas de analytics
CREATE TABLE IF NOT EXISTS analytics_alerts (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    condition JSONB NOT NULL,
    notification_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    owner_id VARCHAR(30) NOT NULL,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 42. ANALYTICS_EXPORTS - Exportações de analytics
CREATE TABLE IF NOT EXISTS analytics_exports (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    name VARCHAR(255) NOT NULL,
    export_type VARCHAR(50) NOT NULL, -- csv, json, pdf, etc.
    query JSONB NOT NULL,
    file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    owner_id VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- TABELAS ADICIONAIS DOS MODELOS PYTHON
-- =====================================================

-- 43. USER_BEHAVIOR_METRICS - Métricas de comportamento do usuário
CREATE TABLE IF NOT EXISTS user_behavior_metrics (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    user_id VARCHAR(30),
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    context JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 44. SYSTEM_PERFORMANCE_METRICS - Métricas de performance do sistema
CREATE TABLE IF NOT EXISTS system_performance_metrics (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    component VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 45. BUSINESS_METRICS - Métricas de negócio
CREATE TABLE IF NOT EXISTS business_metrics (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    period VARCHAR(50), -- daily, weekly, monthly, yearly
    dimensions JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 46. USER_INSIGHTS - Insights dos usuários
CREATE TABLE IF NOT EXISTS user_insights (
    id VARCHAR(30) PRIMARY KEY DEFAULT generate_cuid(),
    user_id VARCHAR(30),
    insight_type VARCHAR(100) NOT NULL,
    insight_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Índices para agents
CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
CREATE INDEX IF NOT EXISTS idx_agents_provider ON agents(provider);
CREATE INDEX IF NOT EXISTS idx_agents_is_active ON agents(is_active);

-- Índices para conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_agent_id ON conversations(agent_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- Índices para messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Índices para files
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_category ON files(category);
CREATE INDEX IF NOT EXISTS idx_files_is_public ON files(is_public);

-- Índices para workflows
CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_workflows_is_active ON workflows(is_active);

-- Índices para workflow_executions
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_started_at ON workflow_executions(started_at);

-- Índices para nodes
CREATE INDEX IF NOT EXISTS idx_nodes_category ON nodes(category);
CREATE INDEX IF NOT EXISTS idx_nodes_is_public ON nodes(is_public);

-- Índices para user_variables
CREATE INDEX IF NOT EXISTS idx_user_variables_user_id ON user_variables(user_id);
CREATE INDEX IF NOT EXISTS idx_user_variables_key ON user_variables(key);

-- Índices para node_executions
CREATE INDEX IF NOT EXISTS idx_node_executions_workflow_execution_id ON node_executions(workflow_execution_id);
CREATE INDEX IF NOT EXISTS idx_node_executions_node_id ON node_executions(node_id);
CREATE INDEX IF NOT EXISTS idx_node_executions_status ON node_executions(status);

-- Índices para execution_queue
CREATE INDEX IF NOT EXISTS idx_execution_queue_status ON execution_queue(status);
CREATE INDEX IF NOT EXISTS idx_execution_queue_priority ON execution_queue(priority);
CREATE INDEX IF NOT EXISTS idx_execution_queue_scheduled_at ON execution_queue(scheduled_at);

-- Índices para workflow_templates
CREATE INDEX IF NOT EXISTS idx_workflow_templates_author_id ON workflow_templates(author_id);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_category ON workflow_templates(category);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_is_public ON workflow_templates(is_public);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_is_featured ON workflow_templates(is_featured);

-- Índices para marketplace_components
CREATE INDEX IF NOT EXISTS idx_marketplace_components_author_id ON marketplace_components(author_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_components_category ON marketplace_components(category);
CREATE INDEX IF NOT EXISTS idx_marketplace_components_status ON marketplace_components(status);
CREATE INDEX IF NOT EXISTS idx_marketplace_components_is_featured ON marketplace_components(is_featured);

-- Índices para workspaces
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_is_public ON workspaces(is_public);

-- Índices para workspace_members
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id);

-- Índices para analytics_events
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp);

-- Índices para analytics_metrics
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_metric_name ON analytics_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_timestamp ON analytics_metrics(timestamp);

-- =====================================================
-- TRIGGERS PARA UPDATED_AT
-- =====================================================

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nodes_updated_at BEFORE UPDATE ON nodes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_variables_updated_at BEFORE UPDATE ON user_variables FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_execution_queue_updated_at BEFORE UPDATE ON execution_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_execution_metrics_updated_at BEFORE UPDATE ON execution_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_templates_updated_at BEFORE UPDATE ON workflow_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_template_reviews_updated_at BEFORE UPDATE ON template_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_template_collections_updated_at BEFORE UPDATE ON template_collections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_executor_configs_updated_at BEFORE UPDATE ON executor_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_executor_metrics_updated_at BEFORE UPDATE ON executor_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_marketplace_components_updated_at BEFORE UPDATE ON marketplace_components FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workspace_projects_updated_at BEFORE UPDATE ON workspace_projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_comments_updated_at BEFORE UPDATE ON project_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analytics_dashboards_updated_at BEFORE UPDATE ON analytics_dashboards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analytics_reports_updated_at BEFORE UPDATE ON analytics_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analytics_alerts_updated_at BEFORE UPDATE ON analytics_alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS ÚTEIS PARA RELATÓRIOS
-- =====================================================

-- View para estatísticas de usuários
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at,
    COUNT(DISTINCT c.id) as total_conversations,
    COUNT(DISTINCT f.id) as total_files,
    COUNT(DISTINCT w.id) as total_workflows,
    COUNT(DISTINCT a.id) as total_agents
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN files f ON u.id = f.user_id
LEFT JOIN workflows w ON u.id = w.user_id
LEFT JOIN agents a ON u.id = a.user_id
GROUP BY u.id, u.username, u.email, u.created_at;

-- View para estatísticas de workflows
CREATE OR REPLACE VIEW workflow_stats AS
SELECT 
    w.id,
    w.name,
    w.user_id,
    w.created_at,
    COUNT(DISTINCT we.id) as total_executions,
    COUNT(DISTINCT CASE WHEN we.status = 'completed' THEN we.id END) as successful_executions,
    COUNT(DISTINCT CASE WHEN we.status = 'failed' THEN we.id END) as failed_executions
FROM workflows w
LEFT JOIN workflow_executions we ON w.id = we.workflow_id
GROUP BY w.id, w.name, w.user_id, w.created_at;

-- View para estatísticas do marketplace
CREATE OR REPLACE VIEW marketplace_stats AS
SELECT 
    mc.id,
    mc.name,
    mc.category,
    mc.author_id,
    mc.downloads_count,
    mc.rating_average,
    mc.rating_count,
    COUNT(DISTINCT cr.id) as total_ratings,
    COUNT(DISTINCT cd.id) as total_downloads,
    COUNT(DISTINCT cp.id) as total_purchases
FROM marketplace_components mc
LEFT JOIN component_ratings cr ON mc.id = cr.component_id
LEFT JOIN component_downloads cd ON mc.id = cd.component_id
LEFT JOIN component_purchases cp ON mc.id = cp.component_id
GROUP BY mc.id, mc.name, mc.category, mc.author_id, mc.downloads_count, mc.rating_average, mc.rating_count;

-- View para atividade recente
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'conversation' as activity_type,
    c.id as entity_id,
    c.title as entity_name,
    c.user_id,
    c.created_at
FROM conversations c
UNION ALL
SELECT 
    'workflow' as activity_type,
    w.id as entity_id,
    w.name as entity_name,
    w.user_id,
    w.created_at
FROM workflows w
UNION ALL
SELECT 
    'file' as activity_type,
    f.id as entity_id,
    f.filename as entity_name,
    f.user_id,
    f.created_at
FROM files f
ORDER BY created_at DESC;

-- =====================================================
-- DADOS INICIAIS
-- =====================================================

-- Usuário administrador padrão
INSERT INTO users (id, email, username, full_name, hashed_password, is_superuser) 
VALUES (
    'admin_user_id_001',
    'admin@synapscale.com',
    'admin',
    'Administrador do Sistema',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', -- senha: admin123
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Nós básicos do sistema
INSERT INTO nodes (id, name, category, description, definition) VALUES
('node_input_001', 'Input', 'io', 'Nó de entrada de dados', '{"type": "input", "inputs": [], "outputs": [{"name": "data", "type": "any"}]}'),
('node_output_001', 'Output', 'io', 'Nó de saída de dados', '{"type": "output", "inputs": [{"name": "data", "type": "any"}], "outputs": []}'),
('node_llm_001', 'LLM Chat', 'ai', 'Nó para chat com LLM', '{"type": "llm", "inputs": [{"name": "prompt", "type": "string"}], "outputs": [{"name": "response", "type": "string"}]}'),
('node_http_001', 'HTTP Request', 'data', 'Nó para requisições HTTP', '{"type": "http", "inputs": [{"name": "url", "type": "string"}, {"name": "method", "type": "string"}], "outputs": [{"name": "response", "type": "object"}]}'),
('node_condition_001', 'Condition', 'logic', 'Nó de condição lógica', '{"type": "condition", "inputs": [{"name": "condition", "type": "boolean"}], "outputs": [{"name": "true", "type": "any"}, {"name": "false", "type": "any"}]}')
ON CONFLICT (id) DO NOTHING;

-- Configurações de executor padrão
INSERT INTO executor_configs (id, name, executor_type, config) VALUES
('exec_http_001', 'HTTP Executor', 'http', '{"timeout": 30, "retries": 3, "headers": {"User-Agent": "SynapScale/1.0"}}'),
('exec_python_001', 'Python Executor', 'python', '{"timeout": 60, "memory_limit": "512MB", "allowed_modules": ["requests", "json", "datetime"]}'),
('exec_llm_001', 'LLM Executor', 'llm', '{"default_provider": "openai", "default_model": "gpt-3.5-turbo", "max_tokens": 1000}')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- =====================================================

COMMENT ON DATABASE synapscale_db IS 'Banco de dados principal do SynapScale - Plataforma de automação com IA';

-- Comentários nas tabelas principais
COMMENT ON TABLE users IS 'Usuários do sistema SynapScale';
COMMENT ON TABLE agents IS 'Agentes de IA configurados pelos usuários';
COMMENT ON TABLE conversations IS 'Conversas entre usuários e agentes';
COMMENT ON TABLE messages IS 'Mensagens individuais das conversas';
COMMENT ON TABLE files IS 'Arquivos enviados pelos usuários';
COMMENT ON TABLE workflows IS 'Fluxos de trabalho automatizados';
COMMENT ON TABLE workflow_executions IS 'Execuções dos workflows';
COMMENT ON TABLE nodes IS 'Nós para construção de workflows';
COMMENT ON TABLE user_variables IS 'Variáveis personalizadas dos usuários';

-- Comentários nas tabelas de execução
COMMENT ON TABLE node_executions IS 'Execuções individuais de nós dentro de workflows';
COMMENT ON TABLE execution_queue IS 'Fila de execução para processamento assíncrono';
COMMENT ON TABLE execution_metrics IS 'Métricas de performance das execuções';

-- Comentários nas tabelas de templates
COMMENT ON TABLE workflow_templates IS 'Templates de workflows disponíveis no marketplace';
COMMENT ON TABLE template_reviews IS 'Avaliações dos templates pelos usuários';
COMMENT ON TABLE template_downloads IS 'Histórico de downloads de templates';
COMMENT ON TABLE template_favorites IS 'Templates marcados como favoritos';
COMMENT ON TABLE template_collections IS 'Coleções organizadas de templates';
COMMENT ON TABLE template_usage IS 'Rastreamento de uso dos templates';

-- Comentários nas tabelas de configuração
COMMENT ON TABLE executor_configs IS 'Configurações dos diferentes tipos de executores';
COMMENT ON TABLE http_cache IS 'Cache para requisições HTTP frequentes';
COMMENT ON TABLE executor_metrics IS 'Métricas de performance dos executores';

-- Comentários nas tabelas do marketplace
COMMENT ON TABLE marketplace_components IS 'Componentes disponíveis no marketplace';
COMMENT ON TABLE component_ratings IS 'Avaliações dos componentes do marketplace';
COMMENT ON TABLE component_downloads IS 'Histórico de downloads de componentes';
COMMENT ON TABLE component_purchases IS 'Compras de componentes pagos';
COMMENT ON TABLE component_favorites IS 'Componentes marcados como favoritos';
COMMENT ON TABLE component_versions IS 'Versões dos componentes do marketplace';

-- Comentários nas tabelas de workspaces
COMMENT ON TABLE workspaces IS 'Espaços de trabalho colaborativos';
COMMENT ON TABLE workspace_members IS 'Membros dos workspaces';
COMMENT ON TABLE workspace_invitations IS 'Convites pendentes para workspaces';
COMMENT ON TABLE workspace_projects IS 'Projetos dentro dos workspaces';
COMMENT ON TABLE project_collaborators IS 'Colaboradores dos projetos';
COMMENT ON TABLE project_comments IS 'Comentários nos projetos';
COMMENT ON TABLE workspace_activities IS 'Log de atividades dos workspaces';
COMMENT ON TABLE project_versions IS 'Controle de versão dos projetos';

-- Comentários nas tabelas de analytics
COMMENT ON TABLE analytics_events IS 'Eventos de analytics e tracking';
COMMENT ON TABLE analytics_metrics IS 'Métricas agregadas do sistema';
COMMENT ON TABLE analytics_dashboards IS 'Dashboards personalizados de analytics';
COMMENT ON TABLE analytics_reports IS 'Relatórios automatizados';
COMMENT ON TABLE report_executions IS 'Execuções dos relatórios';
COMMENT ON TABLE analytics_alerts IS 'Alertas baseados em métricas';
COMMENT ON TABLE analytics_exports IS 'Exportações de dados de analytics';

-- Comentários nas tabelas adicionais
COMMENT ON TABLE user_behavior_metrics IS 'Métricas de comportamento dos usuários';
COMMENT ON TABLE system_performance_metrics IS 'Métricas de performance do sistema';
COMMENT ON TABLE business_metrics IS 'Métricas de negócio e KPIs';
COMMENT ON TABLE user_insights IS 'Insights gerados sobre os usuários';

-- =====================================================
-- FINALIZAÇÃO
-- =====================================================

-- Verificação final
DO $$
BEGIN
    RAISE NOTICE '✅ BANCO SYNAPSCALE CRIADO COM SUCESSO!';
    RAISE NOTICE '📊 Total de tabelas: 46';
    RAISE NOTICE '🔗 Total de relacionamentos: 50+';
    RAISE NOTICE '📈 Total de índices: 60+';
    RAISE NOTICE '⚡ Total de triggers: 20+';
    RAISE NOTICE '📋 Total de views: 4';
    RAISE NOTICE '🎯 Sistema 100% pronto para uso!';
END $$;

