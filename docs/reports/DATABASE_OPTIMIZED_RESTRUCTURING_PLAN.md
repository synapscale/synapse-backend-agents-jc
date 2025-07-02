# Plano de Reestruturação Otimizado do Banco de Dados (synapscale_db)

**Data:** 30 de junho de 2025
**Status:** ✅ **PLANO FINALIZADO E OTIMIZADO**

## 1. Introdução

Este documento consolida e finaliza o plano de reestruturação do banco de dados `synapscale_db`, incorporando as descobertas da auditoria inicial e as valiosas pontuações críticas do agente Cursor. O objetivo é garantir que a arquitetura do banco de dados seja robusta, performática, segura e alinhada com as melhores práticas para um sistema SaaS multi-tenant B2B, considerando a hierarquia de entidades como super admins, tenants, workspaces, usuários, planos e assinaturas.

## 2. Princípios Fundamentais Revisados para Design Multi-Tenant

A análise crítica destacou a importância de certas decisões arquiteturais no contexto de um SaaS multi-tenant. Os princípios a seguir guiaram a revisão das recomendações:

*   **`tenant_id` em Tabelas Filhas (Redundância Estratégica)**:
    *   A presença explícita de `tenant_id` em tabelas filhas é **altamente recomendada e será mantida** na maioria dos casos, mesmo que a informação possa ser derivada via `JOIN`.
    *   **Justificativa**: Essencial para performance em queries multi-tenant (filtros diretos, índices compostos), fundamental para implementação de Row-Level Security (RLS), facilita futuras estratégias de sharding e garante clareza e auditabilidade da propriedade do dado.
    *   **Exceção**: A coluna `users.tenant_id` será removida, pois a relação usuário-tenant será exclusivamente gerenciada pela tabela `user_tenant_roles` para permitir que um usuário pertença a múltiplos tenants.

*   **Colunas de Contagem (Denormalização Controlada para Performance)**:
    *   Colunas como `member_count`, `downloads_count`, `rating_average`, `rating_count` são denormalizações intencionais para otimizar a performance de leitura em dashboards e relatórios. Elas **serão mantidas**.
    *   **Justificativa**: Evitam `JOINs` e agregações complexas em tempo real para dados frequentemente acessados.
    *   **Ação Complementar**: É crucial que essas colunas sejam **sincronizadas** de forma consistente, preferencialmente via triggers de banco de dados ou lógica de aplicação robusta, para garantir a integridade dos dados.

*   **Ações `ON DELETE` para Chaves Estrangeiras**:
    *   A escolha da ação (`CASCADE`, `SET NULL`, `RESTRICT`) é vital para a integridade referencial e a lógica de negócios. As recomendações foram refinadas para garantir que o comportamento de exclusão esteja alinhado com as expectativas de um sistema SaaS multi-tenant, priorizando a preservação de dados históricos/de auditoria onde apropriado.

*   **JSON vs. JSONB**:
    *   A padronização para `JSONB` para otimização de armazenamento, performance de consulta e indexação é **mantida e reforçada**.

*   **Tipos de Timestamp**:
    *   O uso de `timestamp with time zone` para todas as colunas de data/hora é **mantido e reforçado** para evitar problemas de fuso horário em um ambiente global.

*   **Nomenclatura**:
    *   As recomendações de padronização de nomes (ex: `meta_data` para `metadata`) são **mantidas**.

## 3. Recomendações Detalhadas por Grupo de Tabelas (Otimizado)

### 3.1. Tabelas de Backup

*   **Observação:** Foram identificadas 16 tabelas com o prefixo `backup_`.
*   **Recomendação:** Estas tabelas devem ser exportadas para um local de arquivamento seguro (via `pg_dump`) e, em seguida, removidas do schema de produção para evitar confusão e poluição. Automatizar o processo de exportação e limpeza, mantendo logs de auditoria.

### 3.2. RBAC (Role-Based Access Control)

*   **Tabela Afetada:** `rbac_roles`
    *   **Inconsistência:** Coluna `permissions` (JSONB) cria "verdade dupla".
    *   **Recomendação:** Garantir que todos os dados de permissão sejam migrados do campo JSON para a tabela `rbac_role_permissions`. Remover a coluna `permissions` da tabela `rbac_roles`.

*   **Tabelas Afetadas:** `rbac_roles`, `rbac_permissions`, `rbac_role_permissions`
    *   **Inconsistência:** A coluna `tenant_id` é nulável.
    *   **Recomendação:** Clarificar a arquitetura. Se papéis e permissões customizadas devem sempre pertencer a um tenant, a coluna `tenant_id` deveria ser `NOT NULL`. Se a intenção é ter papéis globais, a nulidade está correta, mas isso deve ser documentado. Considerar adicionar uma coluna `scope` (e.g., 'global', 'tenant') para maior clareza e validação via constraints/checks.

### 3.3. Workflows e Execuções

*   **Tabela Afetada:** `workflows`
    *   **Inconsistência:** `workspace_id` é nulável; `workflows_workspace_id_fkey` sem `ON DELETE`; `tags` é `json`.
    *   **Recomendação:** Tornar `workspace_id` `NOT NULL` (assumindo que todos os workflows devem pertencer a um workspace). Se houver workflows de sistema não atrelados a workspaces, considerar uma tabela separada ou uma lógica de `tenant_id` nulo bem definida. Adicionar `ON DELETE CASCADE` à chave estrangeira `workflows_workspace_id_fkey`. Alterar o tipo da coluna `tags` para `jsonb` (ou `text[]` se for apenas uma lista simples de strings).

*   **Tabela Afetada:** `workflow_executions`
    *   **Inconsistência:** Uso misto de `json` e `jsonb`; `meta_data` em vez de `metadata`.
    *   **Recomendação:** Padronizar todas as colunas de dados semi-estruturados para `jsonb`. Renomear a coluna `meta_data` para `metadata`. Manter a coluna `tenant_id` para performance e RLS.

### 3.4. LLMs e Agentes

*   **Tabela Afetada:** `agents`
    *   **Inconsistência:** Redundância de `provider`/`model`/`model_provider`; `tools`, `knowledge_base`, `capabilities`, `configuration` são `json`; `workspace_id` é anulável; `agents_workspace_id_fkey` sem `ON DELETE`.
    *   **Recomendação:** Remover a coluna `model_provider`. Alterar as colunas `tools`, `knowledge_base`, `capabilities`, e `configuration` para `jsonb`. Tornar `workspace_id` `NOT NULL` se um agente deve sempre pertencer a um workspace. Caso contrário, documentar claramente a lógica de agentes globais. Adicionar `ON DELETE CASCADE` à chave estrangeira `agents_workspace_id_fkey`.

*   **Tabela Afetada:** `llms`
    *   **Inconsistência:** `llm_metadata` é `json`; `usage_logs_llm_id_fkey` tem `ON DELETE RESTRICT`.
    *   **Recomendação:** Alterar a coluna `llm_metadata` para `jsonb`. Considerar alterar a ação da chave estrangeira `usage_logs_llm_id_fkey` para `ON DELETE SET NULL` ou `ON DELETE SET DEFAULT` para permitir a remoção de LLMs sem bloquear a exclusão de logs de uso.

*   **Tabela Afetada:** `llms_conversations`
    *   **Inconsistência:** `context` e `settings` são `json`; `tenant_id` é anulável com `ON DELETE CASCADE`.
    *   **Recomendação:** Alterar as colunas `context` e `settings` para `jsonb`. Se uma conversa sempre pertence a um tenant, a coluna `tenant_id` deve ser `NOT NULL`. Caso contrário, documentar claramente a lógica de conversas globais.

*   **Tabela Afetada:** `llms_conversations_turns`
    *   **Inconsistência:** Nomenclatura longa.
    *   **Recomendação:** Renomear a tabela para `conversation_turns` para clareza. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `llms_messages`
    *   **Inconsistência:** `rating` e `feedback` são redundantes; `attachments` é `json`; nomenclatura longa.
    *   **Recomendação:** Remover as colunas `rating` e `feedback`. Alterar a coluna `attachments` para `jsonb`. Renomear a tabela para `messages` para clareza. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `llms_message_feedbacks`
    *   **Inconsistência:** `feedback_metadata` é `json`; nomenclatura longa.
    *   **Recomendação:** Alterar a coluna `feedback_metadata` para `jsonb`. Renomear a tabela para `message_feedbacks` para clareza. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `llms_usage_logs`
    *   **Inconsistência:** `api_request_payload`, `api_response_metadata`, `model_settings` são `json`.
    *   **Recomendação:** Alterar as colunas `api_request_payload`, `api_response_metadata`, e `model_settings` para `jsonb`. Manter as colunas `user_id`, `conversation_id`, `workspace_id`, e `tenant_id` para performance, RLS e rastreabilidade em logs de uso.

### 3.5. Marketplace e Componentes

*   **Tabela Afetada:** `marketplace_components`
    *   **Inconsistência:** `author_name` é redundante; `configuration_schema`, `dependencies`, `compatibility`, `examples`, `screenshots`, `keywords` são `json`; `tags` é `text`; timestamps sem fuso horário.
    *   **Recomendação:** Remover a coluna `author_name`. Alterar as colunas JSON para `jsonb`. Alterar a coluna `tags` para `text[]` e as colunas de timestamp para `timestamp with time zone`. Manter as colunas `downloads_count`, `rating_average`, e `rating_count` como denormalizações para performance, garantindo que sejam sincronizadas via triggers ou lógica de aplicação.

*   **Tabela Afetada:** `component_versions`
    *   **Inconsistência:** `component_data` e `dependencies` são `json`; timestamps sem fuso horário.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `component_purchases`
    *   **Inconsistência:** Timestamps sem fuso horário.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `component_ratings`
    *   **Inconsistência:** Timestamps sem fuso horário.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `component_downloads`
    *   **Inconsistência:** Timestamps sem fuso horário.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

### 3.6. Analytics

*   **Tabela Afetada:** `analytics_alerts`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `analytics_dashboards`
    *   **Inconsistência:** `layout`, `widgets`, `filters`, `shared_with` são `json`; `last_viewed_at` sem fuso horário; `analytics_dashboards_workspace_id_fkey` sem `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar a coluna `last_viewed_at` para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada (e.g., `SET NULL` ou `CASCADE`) à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `analytics_events`
    *   **Inconsistência:** `analytics_events_workflow_id_fkey` e `analytics_events_workspace_id_fkey` sem `ON DELETE`.
    *   **Recomendação:** Adicionar ações `ON DELETE` apropriadas às chaves estrangeiras. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `analytics_exports`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `analytics_metrics`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `analytics_reports`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

### 3.7. Billing e Pagamentos

*   **Tabela Afetada:** `billing_events`
    *   **Inconsistência:** `billing_metadata` é `json`.
    *   **Recomendação:** Alterar a coluna `billing_metadata` para `jsonb`. Manter as colunas `tenant_id` e `workspace_id` para performance e RLS.

*   **Tabela Afetada:** `invoices`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `payment_customers`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `payment_methods`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `payment_providers`
    *   **Consistência:** A tabela parece bem estruturada.

### 3.8. Contatos e Campanhas

*   **Tabela Afetada:** `contacts`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `campaigns`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `campaign_contacts`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `contact_lists`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `contact_list_memberships`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

### 3.9. Gerenciamento de Usuários e Autenticação

*   **Tabela Afetada:** `users`
    *   **Inconsistência:** A coluna `tenant_id` aqui é redundante se a relação usuário-tenant for gerenciada pela tabela `user_tenant_roles` (que permite múltiplos tenants por usuário).
    *   **Recomendação:** Remover a coluna `tenant_id` da tabela `users`. A relação de um usuário com um ou mais tenants deve ser exclusivamente gerenciada pela tabela `user_tenant_roles`.

*   **Tabela Afetada:** `email_verification_tokens`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `password_reset_tokens`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `refresh_tokens`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `user_variables`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

### 3.10. Eventos e Interações de Contatos

*   **Tabela Afetada:** `contact_events`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `contact_interactions`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `contact_notes`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `contact_sources`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `contact_tags`
    *   **Consistência:** A tabela parece bem estruturada.

### 3.11. Entidades Core

*   **Tabela Afetada:** `tenants`
    *   **Consistência:** A tabela parece bem estruturada. A chave estrangeira para `plans` com `ON DELETE RESTRICT` é uma escolha de design que impede a exclusão de um plano se houver tenants associados a ele.

*   **Tabela Afetada:** `plans`
    *   **Consistência:** A tabela parece bem estruturada. A coluna `slug` é única, o que é bom. As chaves estrangeiras com `ON DELETE RESTRICT` são apropriadas para evitar a exclusão acidental de planos que estão em uso.

*   **Tabela Afetada:** `features`
    *   **Consistência:** A tabela parece bem estruturada. A coluna `key` é única, o que é bom.

*   **Tabela Afetada:** `plan_features`
    *   **Consistência:** A tabela parece bem estruturada. O uso de `jsonb` para `config` é apropriado. A restrição de unicidade em `(plan_id, feature_id)` garante a integridade dos dados.

*   **Tabela Afetada:** `plan_entitlements`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `plan_provider_mappings`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `subscriptions`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `user_subscriptions`
    *   **Inconsistência:** Uso de JSON: A coluna `subscription_metadata` é do tipo `json`.
    *   **Recomendação:** Alterar a coluna `subscription_metadata` para `jsonb`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `tenant_features`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `user_tenant_roles`
    *   **Consistência:** A tabela parece bem estruturada.

### 3.12. Workspaces e Projetos

*   **Tabela Afetada:** `workspaces`
    *   **Inconsistência:** Uso de JSON: A coluna `feature_usage_count` é do tipo `json`; Chaves Estrangeiras: Várias chaves estrangeiras referenciando `workspaces` não possuem ações `ON DELETE` definidas.
    *   **Recomendação:** Manter as colunas `member_count`, `project_count`, `activity_count`, e `storage_used_mb` como denormalizações para performance, garantindo que sejam sincronizadas via triggers ou lógica de aplicação. Alterar a coluna `feature_usage_count` para `jsonb`. Adicionar ações `ON DELETE` apropriadas (e.g., `SET NULL` ou `CASCADE`) às chaves estrangeiras.

*   **Tabela Afetada:** `workspace_projects`
    *   **Inconsistência:** Tipos de Dados: As colunas `created_at`, `updated_at`, e `last_edited_at` são `timestamp without time zone`; Chaves Estrangeiras: As chaves estrangeiras `workspace_projects_workflow_id_fkey` e `workspace_projects_workspace_id_fkey` não possuem ações `ON DELETE`.
    *   **Recomendação:** Manter as colunas `collaborator_count`, `edit_count`, e `comment_count` como denormalizações para performance, garantindo que sejam sincronizadas via triggers ou lógica de aplicação. Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar ações `ON DELETE` apropriadas às chaves estrangeiras. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workspace_members`
    *   **Inconsistência:** Uso de JSON: As colunas `custom_permissions` e `notification_preferences` são do tipo `json`; Tipos de Dados: As colunas `last_seen_at`, `joined_at`, e `left_at` são `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `workspace_members_workspace_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workspace_activities`
    *   **Inconsistência:** Uso de JSON: A coluna `meta_data` é do tipo `json`; Tipos de Dados: A coluna `created_at` é `timestamp without time zone`; Nomenclatura: A coluna `meta_data` deve ser renomeada para `metadata`; Chave Estrangeira: A chave estrangeira `workspace_activities_workspace_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar a coluna `meta_data` para `jsonb`. Alterar a coluna `created_at` para `timestamp with time zone`. Renomear a coluna `meta_data` para `metadata`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workspace_features`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workspace_invitations`
    *   **Inconsistência:** Tipos de Dados: As colunas `created_at`, `expires_at`, e `responded_at` são `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `workspace_invitations_workspace_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `project_collaborators`
    *   **Inconsistência:** Uso de JSON: A coluna `current_cursor_position` é do tipo `json`; Tipos de Dados: As colunas `last_edit_at`, `added_at`, e `last_seen_at` são `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `project_collaborators_project_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar a coluna `current_cursor_position` para `jsonb`. Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `project_comments`
    *   **Inconsistência:** Tipos de Dados: As colunas `created_at`, `updated_at`, e `resolved_at` são `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `project_comments_project_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `project_versions`
    *   **Inconsistência:** Uso de JSON: As colunas `workflow_data` e `changes_summary` são do tipo `json`; Tipos de Dados: A coluna `created_at` é `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `project_versions_project_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar a coluna `created_at` para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

### 3.13. Nós e Workflows

*   **Tabela Afetada:** `nodes`
    *   **Inconsistência:** Redundância: As colunas `downloads_count`, `usage_count`, `rating_average`, e `rating_count` são redundantes; Uso de JSON: As colunas `input_schema`, `output_schema`, `parameters_schema`, e `examples` são do tipo `json`; Chave Estrangeira: A chave estrangeira `nodes_workspace_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Manter as colunas `downloads_count`, `usage_count`, `rating_average`, e `rating_count` como denormalizações para performance, garantindo que sejam sincronizadas via triggers ou lógica de aplicação. Alterar as colunas JSON para `jsonb`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira.

*   **Tabela Afetada:** `node_categories`
    *   **Consistência:** A tabela parece bem estruturada.

*   **Tabela Afetada:** `node_executions`
    *   **Inconsistência:** Uso de JSON: As colunas `input_data`, `output_data`, `config_data`, `error_details`, `debug_info`, `dependencies`, `dependents`, e `meta_data` são do tipo `json`; Nomenclatura: A coluna `meta_data` deve ser renomeada para `metadata`; Chaves Estrangeiras: As chaves estrangeiras `node_executions_node_id_fkey` e `node_executions_workflow_execution_id_fkey` não possuem ações `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Renomear a coluna `meta_data` para `metadata`. Adicionar ações `ON DELETE` apropriadas às chaves estrangeiras. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `node_ratings`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `node_templates`
    *   **Inconsistência:** Uso de JSON: As colunas `input_schema`, `output_schema`, `parameters_schema`, e `examples` são do tipo `json`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`.

*   **Tabela Afetada:** `workflow_connections`
    *   **Inconsistência:** Chaves Estrangeiras: As chaves estrangeiras `workflow_connections_source_node_id_fkey`, `workflow_connections_target_node_id_fkey`, e `workflow_connections_workflow_id_fkey` não possuem ações `ON DELETE`.
    *   **Recomendação:** Adicionar ações `ON DELETE` apropriadas às chaves estrangeiras. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workflow_execution_metrics`
    *   **Inconsistência:** Uso de JSON: A coluna `value_json` e `tags` são do tipo `json`; Chaves Estrangeiras: As chaves estrangeiras `execution_metrics_node_execution_id_fkey` e `execution_metrics_workflow_execution_id_fkey` não possuem ações `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Adicionar ações `ON DELETE` apropriadas às chaves estrangeiras. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workflow_execution_queue`
    *   **Inconsistência:** Uso de JSON: A coluna `meta_data` é do tipo `json`; Nomenclatura: A coluna `meta_data` deve ser renomeada para `metadata`; Chave Estrangeira: A chave estrangeira `execution_queue_workflow_execution_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar a coluna `meta_data` para `jsonb`. Renomear a coluna `meta_data` para `metadata`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workflow_nodes`
    *   **Inconsistência:** Uso de JSON: A coluna `configuration` é do tipo `json`; Chaves Estrangeiras: As chaves estrangeiras `workflow_nodes_node_id_fkey` e `workflow_nodes_workflow_id_fkey` não possuem ações `ON DELETE`.
    *   **Recomendação:** Alterar a coluna `configuration` para `jsonb`. Adicionar ações `ON DELETE` apropriadas às chaves estrangeiras. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `workflow_templates`
    *   **Inconsistência:** Redundância: As colunas `downloads_count`, `rating_average`, `rating_count`, `download_count`, `usage_count`, e `view_count` são redundantes; Uso de JSON: As colunas `tags`, `workflow_data`, `nodes_data`, `connections_data`, `required_variables`, `optional_variables`, `default_config`, `keywords`, `use_cases`, `industries`, `preview_images`, e `changelog` são do tipo `json`; Chave Estrangeira: A chave estrangeira `workflow_templates_original_workflow_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Manter as colunas `downloads_count`, `rating_average`, `rating_count`, `download_count`, `usage_count`, e `view_count` como denormalizações para performance, garantindo que sejam sincronizadas via triggers ou lógica de aplicação. Alterar as colunas JSON para `jsonb`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

### 3.14. Arquivos e Armazenamento

*   **Tabela Afetada:** `files`
    *   **Inconsistência:** Uso de JSON: A coluna `tags` é do tipo `json`.
    *   **Recomendação:** Alterar a coluna `tags` para `jsonb`. Manter a coluna `tenant_id` para performance e RLS.

### 3.15. Métricas e Relatórios

*   **Tabela Afetada:** `business_metrics`
    *   **Inconsistência:** Tipos de Dados: As colunas `date`, `created_at`, e `updated_at` são `timestamp without time zone`.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `custom_reports`
    *   **Inconsistência:** Uso de JSON: As colunas `query_config`, `visualization_config`, `filters`, `schedule_config`, `shared_with`, e `cached_data` são do tipo `json`; Tipos de Dados: As colunas `last_run_at`, `next_run_at`, `cache_expires_at`, `created_at`, e `updated_at` são `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `custom_reports_workspace_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `report_executions`
    *   **Inconsistência:** Uso de JSON: As colunas `parameters` e `result_data` são do tipo `json`; Tipos de Dados: As colunas `started_at` e `completed_at` são `timestamp without time zone`; Chave Estrangeira: A chave estrangeira `report_executions_report_id_fkey` não possui uma ação `ON DELETE`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar as colunas de timestamp para `timestamp with time zone`. Adicionar uma ação `ON DELETE` apropriada à chave estrangeira. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `system_performance_metrics`
    *   **Inconsistência:** Uso de JSON: A coluna `tags` é do tipo `json`; Tipos de Dados: A coluna `timestamp` é `timestamp without time zone`.
    *   **Recomendação:** Alterar a coluna `tags` para `jsonb`. Alterar a coluna `timestamp` para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `user_behavior_metrics`
    *   **Inconsistência:** Tipos de Dados: As colunas `date`, `created_at`, e `updated_at` são `timestamp without time zone`.
    *   **Recomendação:** Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `user_insights`
    *   **Inconsistência:** Uso de JSON: As colunas `supporting_data` e `action_data` são do tipo `json`; Tipos de Dados: As colunas `expires_at`, `created_at`, `read_at`, e `acted_at` são `timestamp without time zone`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Alterar as colunas de timestamp para `timestamp with time zone`. Manter a coluna `tenant_id` para performance e RLS.

### 3.16. Templates

*   **Tabela Afetada:** `template_collections`
    *   **Inconsistência:** Uso de JSON: As colunas `template_ids` e `tags` são do tipo `json`.
    *   **Recomendação:** Alterar as colunas JSON para `jsonb`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `template_downloads`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `template_favorites`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `template_reviews`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `template_usage`
    *   **Inconsistência:** Uso de JSON: A coluna `modifications_made` é do tipo `json`.
    *   **Recomendação:** Alterar a coluna `modifications_made` para `jsonb`. Manter a coluna `tenant_id` para performance e RLS.

### 3.17. Outras Tabelas

*   **Tabela Afetada:** `alembic_version`
    *   **Consistência:** A tabela parece consistente e bem estruturada. É uma tabela de controle de versão do Alembic e não requer alterações.

*   **Tabela Afetada:** `coupons`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `tags`
    *   **Inconsistência:** Uso de JSON: A coluna `tag_metadata` é do tipo `json`.
    *   **Recomendação:** Alterar a coluna `tag_metadata` para `jsonb`. Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `webhook_logs`
    *   **Recomendação:** Manter a coluna `tenant_id` para performance e RLS.

*   **Tabela Afetada:** `conversion_journeys`
    *   **Consistência:** A tabela parece bem estruturada.

## 4. Ideias e Melhorias Adicionais (Mantidas da Análise do Cursor)

*   **Documentação Abrangente:** Garantir que todas as mudanças estejam refletidas em diagramas ER e documentação técnica.
*   **Validação Automatizada de Schema:** Integrar ferramentas de lint/CI para checar uso de jsonb, tipos de timestamp e ações de foreign key.
*   **Auditorias de Performance:** Após grandes mudanças, rodar benchmarks de queries e monitorar triggers.
*   **Políticas de Retenção de Dados:** Definir e automatizar políticas para tabelas de alta rotatividade (logs, analytics).
*   **Planos de Rollback:** Documentar e testar estratégias de rollback para cada migração relevante.
*   **Sincronização com Código:** Garantir que modelos ORM e APIs estejam 100% alinhados ao novo schema.
*   **Revisão de Segurança:** Após reestruturação, revisar toda lógica de permissões e acessos.
*   **Monitoramento de Triggers:** Implementar métricas para identificar triggers que impactam performance.
*   **Testes de Stress:** Realizar testes de carga em operações críticas após alterações estruturais.
*   **Política de Versionamento de Schema:** Adotar versionamento semântico para evoluções do schema.

## 5. Conclusão e Próximos Passos Estratégicos

Este plano de reestruturação otimizado reflete uma compreensão aprofundada das necessidades de um sistema SaaS multi-tenant, equilibrando normalização, performance, segurança e manutenibilidade. A implementação dessas recomendações elevará significativamente a qualidade e a sustentabilidade do `synapscale_db`.

**Próximos Passos:**
1.  Revisão e aprovação final deste plano pela equipe.
2.  Criação de tarefas detalhadas para cada recomendação, incluindo scripts de migração Alembic, atualizações de código (modelos ORM, serviços, APIs) e testes.
3.  Execução das mudanças em ambiente de desenvolvimento/staging, com testes rigorosos de regressão e performance.
4.  Monitoramento contínuo após a implantação em produção.
