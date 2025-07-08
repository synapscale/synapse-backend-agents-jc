# OpenAPI x Banco de Dados: Relatório de Congruência

## 1. Tabelas do Banco sem Schema no OpenAPI

- (1455
- ----------------------------+--------------------------------+--------------------------+-------------+----------------------------------------------------------------------
- agent_acl
- agent_configurations
- agent_error_logs
- agent_hierarchy
- agent_kbs
- agent_models
- agent_quotas
- agent_tools
- agent_triggers
- agent_usage_metrics
- agents
- alembic_version
- analytics_alerts
- analytics_dashboards
- analytics_events
- analytics_exports
- analytics_metrics
- analytics_reports
- audit_log
- billing_events
- business_metrics
- campaign_contacts
- campaigns
- component_downloads
- component_purchases
- component_ratings
- component_versions
- contact_events
- contact_interactions
- contact_list_memberships
- contact_lists
- contact_notes
- contact_sources
- contact_tags
- contacts
- conversion_journeys
- coupons
- custom_reports
- email_verification_tokens
- features
- files
- invoices
- knowledge_bases
- llms
- llms_conversations
- llms_conversations_turns
- llms_messages
- llms_usage_logs
- marketplace_components
- message_feedbacks
- node_categories
- node_executions
- node_ratings
- node_templates
- nodes
- password_reset_tokens
- payment_customers
- payment_methods
- payment_providers
- plan_entitlements
- plan_features
- plan_provider_mappings
- plans
- project_collaborators
- project_comments
- project_versions
- rbac_permissions
- rbac_role_permissions
- rbac_roles
- refresh_tokens
- report_executions
- subscriptions
- system_health
- system_performance_metrics
- table_name
- tags
- template_collections
- template_downloads
- template_favorites
- template_reviews
- template_usage
- tenant_features
- tenants
- tools
- user_behavior_metrics
- user_insights
- user_subscriptions
- user_tenant_roles
- user_variables
- users
- webhook_logs
- workflow_connections
- workflow_execution_metrics
- workflow_execution_queue
- workflow_executions
- workflow_nodes
- workflow_templates
- workflows
- workspace_activities
- workspace_features
- workspace_invitations
- workspace_members
- workspaces

## 2. Schemas do OpenAPI sem Tabela no Banco

- AgentCreate
- AgentEnvironment
- AgentListResponse
- AgentResponse
- AgentScope
- AgentStatus
- AgentUpdate
- Body_change_password_api_v1_auth_change_password_post
- Body_delete_account_api_v1_auth_account_delete
- Body_login_api_v1_auth_login_post
- Body_upload_file_api_v1_files_upload_post
- BulkComponentOperation
- BulkOperationResponse
- CollectionCreate
- CollectionResponse
- ComponentCategory
- ComponentCreate
- ComponentModerationResponse
- ComponentResponse
- ComponentSearchResponse
- ComponentStatus
- ComponentType
- ComponentUpdate
- ConversationCreate
- ConversationResponse
- ConversationTitleUpdate
- DashboardCreate
- DashboardLayout
- DownloadResponse
- EmailVerificationRequest
- EventCreate
- EventType
- ExecutionCreate
- ExecutionMetricsResponse
- ExecutionResponse
- ExecutionStatus
- FavoriteCreate
- FavoriteResponse
- FeatureCreate
- FeatureListResponse
- FeatureResponse
- FeatureUpdate
- FileListResponse
- FileResponse
- FileStatus
- FileUpdate
- HTTPValidationError
- InvoiceCreate
- InvoiceListResponse
- InvoiceResponse
- InvoiceUpdate
- LLMConversationCreate
- LLMConversationListResponse
- LLMConversationResponse
- LLMCreate
- LLMListResponse
- LLMMessageCreate
- LLMMessageListResponse
- LLMMessageResponse
- LLMResponse
- LLMUpdate
- LicenseType
- MessageCreate
- MessageResponse
- ModerationAction
- NodeCreate
- NodeExecutionResponse
- NodeExecutionStatsResponse
- NodeExecutionStatus
- NodeResponse
- NodeUpdate
- PaginatedResponse_Dict_str__Any__
- PaginatedResponse_ExecutionResponse_
- PaginatedResponse_NodeExecutionResponse_
- PaginatedResponse_NodeResponse_
- PasswordResetConfirm
- PasswordResetRequest
- PaymentCustomerCreate
- PaymentCustomerResponse
- PaymentMethodCreate
- PaymentMethodListResponse
- PaymentMethodResponse
- PaymentMethodUpdate
- PaymentProviderCreate
- PaymentProviderResponse
- PlanFeatureCreate
- PlanFeatureListResponse
- PlanFeatureResponse
- PurchaseCreate
- PurchaseResponse
- RBACPermissionCreate
- RBACPermissionListResponse
- RBACPermissionResponse
- RBACRoleCreate
- RBACRoleListResponse
- RBACRoleResponse
- RBACRoleUpdate
- RatingCreate
- RatingResponse
- RatingStats
- RefreshTokenRequest
- ReviewCreate
- ReviewResponse
- TagCreateSchema
- TagResponseSchema
- TemplateCategory
- TemplateCreate
- TemplateDetailResponse
- TemplateInstall
- TemplateInstallResponse
- TemplateLicense
- TemplateListResponse
- TemplateResponse
- TemplateStats
- TemplateStatus
- TemplateUpdate
- TenantCreate
- TenantFeatureCreate
- TenantFeatureListResponse
- TenantFeatureResponse
- TenantListResponse
- TenantResponse
- TenantStatus
- TenantTheme
- TenantUpdate
- UserCreate
- UserListResponse
- UserResponse
- UserStatus
- UserTemplateStats
- UserTenantRoleCreate
- UserTenantRoleResponse
- UserUpdate
- UserVariableCreate
- UserVariableResponse
- UserVariableUpdate
- ValidationError
- VariableCategory
- WidgetConfig
- WorkflowCreate
- WorkflowExecutionCreate
- WorkflowExecutionResponse
- WorkflowExecutionWithNodesResponse
- WorkflowResponse
- WorkflowStatus
- WorkflowUpdate
- WorkspaceCreate
- WorkspaceFeatureCreate
- WorkspaceFeatureListResponse
- WorkspaceFeatureResponse
- WorkspaceListResponse
- WorkspaceMemberCreate
- WorkspaceMemberListResponse
- WorkspaceMemberResponse
- WorkspaceResponse
- WorkspaceRole
- WorkspaceStatus
- WorkspaceUpdate
- synapse__models__node__NodeStatus
- synapse__schemas__marketplace__MarketplaceStats
- synapse__schemas__node__NodeStatus
- synapse__schemas__template__MarketplaceStats

## 3. Análise Campo a Campo: Banco de Dados x OpenAPI

### Tabela/Model: `users` ↔ `UserResponse`

| Campo Banco   | Campo OpenAPI | Tipo Banco     | Tipo OpenAPI | Null? (Banco) | Required (API) | Divergência?         |
|---------------|--------------|---------------|--------------|---------------|----------------|----------------------|
| id            | id           | integer       | integer      | NO            | ✔              | OK                   |
| email         | email        | varchar(255)  | string/email | NO            | ✔              | OK                   |
| full_name     | full_name    | varchar(255)  | string       | YES           | ✖ (opcional)   | OK                   |
| is_active     | is_active    | boolean       | boolean      | NO            | ✔              | OK                   |
| created_at    | created_at   | timestamptz   | string/dt    | NO            | ✔              | OK                   |
| updated_at    | updated_at   | timestamptz   | string/dt    | NO            | ✔              | OK                   |
| (não existe)  | roles        | -             | array/string | -             | ✖ (opcional)   | **Falta no banco**   |

**Observações:**
- Todos os campos obrigatórios do banco estão presentes e com tipos compatíveis no OpenAPI.
- O campo `roles` existe no OpenAPI mas não no banco (pode ser calculado ou vir de outra tabela/serviço).
- Não há campos obrigatórios do banco ausentes no OpenAPI.
- Não há divergências de tipo relevantes.

**Ações Recomendadas:**
- Se `roles` é calculado, documentar no OpenAPI como `readOnly` ou via outro endpoint.
- Se faltar campo importante no OpenAPI, sugerir adicionar.
- Se tipos divergirem, padronizar para o tipo do banco.

### (Adicione aqui as próximas análises campo a campo para outros pares, seguindo o mesmo formato)

## 3.2 Tabela/Model: `workspaces` ↔ `WorkspaceResponse`

| Campo Banco         | Campo OpenAPI         | Tipo Banco         | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|--------------------|----------------------|-------------------|----------------------|---------------|----------------|----------------------|
| id                 | id                   | uuid              | string(uuid)         | NO            | ✔              | OK                   |
| name               | name                 | varchar           | string               | NO            | ✔              | OK                   |
| slug               | slug                 | varchar           | string               | NO            | ✔              | OK                   |
| description        | description          | text              | string/null          | YES           | ✖              | OK                   |
| avatar_url         | avatar_url           | varchar           | string/null          | YES           | ✖              | OK                   |
| color              | color                | varchar           | string/null          | YES           | ✖              | OK                   |
| owner_id           | owner_id             | uuid              | string(uuid)         | NO            | ✔              | OK                   |
| is_public          | is_public            | boolean           | boolean              | NO            | ✖              | OK                   |
| is_template        | is_template          | boolean           | boolean              | NO            | ✖              | OK                   |
| allow_guest_access | allow_guest_access   | boolean           | boolean              | NO            | ✖              | OK                   |
| require_approval   | require_approval     | boolean           | boolean              | NO            | ✖              | OK                   |
| max_members        | max_members          | integer           | integer/null         | YES           | ✖              | OK                   |
| max_projects       | max_projects         | integer           | integer/null         | YES           | ✖              | OK                   |
| max_storage_mb     | max_storage_mb       | integer           | integer/null         | YES           | ✖              | OK                   |
| enable_real_time_editing | enable_real_time_editing | boolean | boolean         | NO            | ✖              | OK                   |
| enable_comments    | enable_comments      | boolean           | boolean              | NO            | ✖              | OK                   |
| enable_chat        | enable_chat          | boolean           | boolean              | NO            | ✖              | OK                   |
| enable_video_calls | enable_video_calls   | boolean           | boolean              | NO            | ✖              | OK                   |
| member_count       | member_count         | integer           | integer              | NO            | ✔              | OK                   |
| project_count      | project_count        | integer           | integer              | NO            | ✔              | OK                   |
| activity_count     | activity_count       | integer           | integer              | NO            | ✔              | OK                   |
| storage_used_mb    | storage_used_mb      | double precision  | number               | NO            | ✔              | OK                   |
| status             | status               | varchar           | string               | NO            | ✔              | OK                   |
| created_at         | created_at           | timestamp         | string(date-time)    | NO            | ✔              | OK                   |
| updated_at         | updated_at           | timestamp         | string(date-time)    | NO            | ✔              | OK                   |
| last_activity_at   | last_activity_at     | timestamp         | string(date-time)    | NO            | ✔              | OK                   |
| tenant_id          | tenant_id            | uuid              | string(uuid)         | NO            | ✔              | OK                   |
| email_notifications| email_notifications  | boolean           | boolean              | YES           | ✖              | OK                   |
| push_notifications | push_notifications   | boolean           | boolean              | YES           | ✖              | OK                   |
| api_calls_today    | api_calls_today      | integer           | integer/null         | YES           | ✖              | OK                   |
| api_calls_this_month| api_calls_this_month| integer           | integer/null         | YES           | ✖              | OK                   |
| last_api_reset_daily| last_api_reset_daily| timestamp         | string(date-time)/null| YES          | ✖              | OK                   |
| last_api_reset_monthly| last_api_reset_monthly| timestamp      | string(date-time)/null| YES         | ✖              | OK                   |
| feature_usage_count| feature_usage_count  | jsonb             | object/null          | YES           | ✖              | OK                   |
| type               | type                 | USER-DEFINED      | string(enum)         | NO            | ✖              | OK                   |

**Observações:**
- Todos os campos principais estão representados e alinhados.
- Campos USER-DEFINED (type) mapeados para enum OpenAPI.
- Campos extras no OpenAPI (ex: fields agregados) não existem no banco, mas são derivados.

**Ações recomendadas:**
- Nenhuma divergência crítica encontrada.

## 3.3 Tabela/Model: `workspace_members` ↔ `WorkspaceMemberResponse`

| Campo Banco         | Campo OpenAPI         | Tipo Banco         | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|--------------------|----------------------|-------------------|----------------------|---------------|----------------|----------------------|
| id                 | id                   | integer           | integer              | NO            | ✔              | OK                   |
| workspace_id       | workspace_id         | uuid              | string               | NO            | ✔              | OK                   |
| user_id            | user_id              | uuid              | string               | NO            | ✔              | OK                   |
| custom_permissions | custom_permissions   | jsonb             | object/null          | YES           | ✖              | OK                   |
| status             | status               | varchar           | string               | NO            | ✔              | OK                   |
| is_favorite        | is_favorite          | boolean           | boolean              | NO            | ✖              | OK                   |
| notification_preferences | notification_preferences | jsonb      | object/null          | YES           | ✖              | OK                   |
| last_seen_at       | last_seen_at         | timestamp         | string(date-time)    | NO            | ✖              | OK                   |
| joined_at          | joined_at            | timestamp         | string(date-time)    | NO            | ✖              | OK                   |
| left_at            | left_at              | timestamp         | string(date-time)/null| YES          | ✖              | OK                   |
| role               | role                 | varchar           | string(enum)         | NO            | ✔              | OK                   |
| created_at         | created_at           | timestamp         | string(date-time)    | YES           | ✖              | OK                   |
| updated_at         | updated_at           | timestamp         | string(date-time)    | YES           | ✖              | OK                   |
| tenant_id          | tenant_id            | uuid              | string(uuid)         | NO            | ✔              | OK                   |
| user_name          | user_name            | -                 | string/null          | -             | ✖              | OpenAPI only         |
| user_email         | user_email           | -                 | string/null          | -             | ✖              | OpenAPI only         |
| user_avatar        | user_avatar          | -                 | string/null          | -             | ✖              | OpenAPI only         |

**Observações:**
- Campos user_name, user_email, user_avatar são agregados no OpenAPI, não existem no banco.
- Todos os campos essenciais estão alinhados.

**Ações recomendadas:**
- Nenhuma divergência crítica encontrada.

## 3.4 Tabela/Model: `workflows` ↔ `WorkflowResponse`

| Campo Banco           | Campo OpenAPI           | Tipo Banco                | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|----------------------|------------------------|--------------------------|----------------------|---------------|----------------|----------------------|
| id                   | id                     | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| name                 | name                   | character varying        | string               | NO            | ✔              | OK                   |
| description          | description            | text                     | string               | YES           | ✖              | OK                   |
| definition           | definition             | jsonb                    | object               | NO            | ✔              | OK                   |
| is_active            | is_active              | boolean                  | boolean              | NO            | ✔              | OK                   |
| user_id              | user_id                | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| workspace_id         | workspace_id           | uuid                     | string (uuid)        | YES           | ✖              | OK                   |
| is_public            | is_public              | boolean                  | boolean              | YES           | ✖              | OK                   |
| category             | category               | character varying        | string               | YES           | ✖              | OK                   |
| tags                 | tags                   | jsonb                    | array/object         | YES           | ✖              | OK                   |
| version              | version                | character varying        | string               | YES           | ✖              | OK                   |
| thumbnail_url        | thumbnail_url          | character varying        | string               | YES           | ✖              | OK                   |
| downloads_count      | downloads_count        | integer                  | integer              | YES           | ✖              | OK                   |
| rating_average       | rating_average         | integer                  | integer              | YES           | ✖              | OK                   |
| rating_count         | rating_count           | integer                  | integer              | YES           | ✖              | OK                   |
| execution_count      | execution_count        | integer                  | integer              | YES           | ✖              | OK                   |
| last_executed_at     | last_executed_at       | timestamp with time zone | string (date-time)   | YES           | ✖              | OK                   |
| created_at           | created_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| updated_at           | updated_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| tenant_id            | tenant_id              | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| status               | status                 | character varying        | string/enum          | YES           | ✖              | Enum pode divergir   |
| priority             | priority               | integer                  | integer              | YES           | ✖              | OK                   |
| timeout_seconds      | timeout_seconds        | integer                  | integer              | YES           | ✖              | OK                   |
| retry_count          | retry_count            | integer                  | integer              | YES           | ✖              | OK                   |

**Observações:**
- O campo `status` pode divergir em valores permitidos (enum). Recomenda-se alinhar os valores possíveis entre banco e OpenAPI.
- Campos de contagem, datas e metadados estão bem representados.

**Ações recomendadas:**
- Validar enum de status.
- Garantir que todos os campos opcionais estejam documentados como tais no OpenAPI.

## 3.5 Tabela/Model: `workflow_executions` ↔ `WorkflowExecutionResponse`

| Campo Banco           | Campo OpenAPI           | Tipo Banco                | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|----------------------|------------------------|--------------------------|----------------------|---------------|----------------|----------------------|
| id                   | id                     | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| execution_id         | execution_id           | character varying        | string               | YES           | ✖              | OK                   |
| workflow_id          | workflow_id            | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| user_id              | user_id                | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| status               | status                 | character varying        | string/enum          | NO            | ✔              | Enum pode divergir   |
| priority             | priority               | integer                  | integer              | YES           | ✖              | OK                   |
| input_data           | input_data             | jsonb                    | object               | YES           | ✖              | OK                   |
| output_data          | output_data            | jsonb                    | object               | YES           | ✖              | OK                   |
| context_data         | context_data           | jsonb                    | object               | YES           | ✖              | OK                   |
| variables            | variables              | jsonb                    | object               | YES           | ✖              | OK                   |
| total_nodes          | total_nodes            | integer                  | integer              | YES           | ✖              | OK                   |
| completed_nodes      | completed_nodes        | integer                  | integer              | YES           | ✖              | OK                   |
| failed_nodes         | failed_nodes           | integer                  | integer              | YES           | ✖              | OK                   |
| progress_percentage  | progress_percentage    | integer                  | integer              | YES           | ✖              | OK                   |
| started_at           | started_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| completed_at         | completed_at           | timestamp with time zone | string (date-time)   | YES           | ✖              | OK                   |
| timeout_at           | timeout_at             | timestamp with time zone | string (date-time)   | YES           | ✖              | OK                   |
| estimated_duration   | estimated_duration     | integer                  | integer              | YES           | ✖              | OK                   |
| actual_duration      | actual_duration        | integer                  | integer              | YES           | ✖              | OK                   |
| execution_log        | execution_log          | text                     | string               | YES           | ✖              | OK                   |
| error_message        | error_message          | text                     | string               | YES           | ✖              | OK                   |
| error_details        | error_details          | jsonb                    | object               | YES           | ✖              | OK                   |
| debug_info           | debug_info             | jsonb                    | object               | YES           | ✖              | OK                   |
| retry_count          | retry_count            | integer                  | integer              | YES           | ✖              | OK                   |
| max_retries          | max_retries            | integer                  | integer              | YES           | ✖              | OK                   |
| auto_retry           | auto_retry             | boolean                  | boolean              | YES           | ✖              | OK                   |
| notify_on_completion | notify_on_completion   | boolean                  | boolean              | YES           | ✖              | OK                   |
| notify_on_failure    | notify_on_failure      | boolean                  | boolean              | YES           | ✖              | OK                   |
| tags                 | tags                   | jsonb                    | array/object         | YES           | ✖              | OK                   |
| metadata             | metadata               | json                     | object               | YES           | ✖              | OK                   |
| created_at           | created_at             | timestamp with time zone | string (date-time)   | YES           | ✔              | OK                   |
| updated_at           | updated_at             | timestamp with time zone | string (date-time)   | YES           | ✖              | OK                   |
| tenant_id            | tenant_id              | uuid                     | string (uuid)        | YES           | ✖              | OK                   |

**Observações:**
- O campo `status` pode divergir em valores permitidos (enum). Recomenda-se alinhar os valores possíveis entre banco e OpenAPI.
- Campos de metadados e logs (jsonb/text) estão bem representados.

**Ações recomendadas:**
- Validar enum de status.
- Garantir que todos os campos opcionais estejam documentados como tais no OpenAPI.

## 3.6 Tabela/Model: `user_variables` ↔ `UserVariableResponse`

| Campo Banco           | Campo OpenAPI           | Tipo Banco                | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|----------------------|------------------------|--------------------------|----------------------|---------------|----------------|----------------------|
| id                   | id                     | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| user_id              | user_id                | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| key                  | key                    | character varying        | string               | NO            | ✔              | OK                   |
| value                | value                  | text                     | string               | YES           | ✖              | OK                   |
| category             | category               | character varying        | string               | YES           | ✖              | OK                   |
| is_encrypted         | is_encrypted           | boolean                  | boolean              | YES           | ✖              | OK                   |
| description          | description            | text                     | string               | YES           | ✖              | OK                   |
| is_active            | is_active              | boolean                  | boolean              | YES           | ✖              | OK                   |
| created_at           | created_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| updated_at           | updated_at             | timestamp with time zone | YES           | ✖              | OK                   |
| tenant_id            | tenant_id              | uuid                     | YES           | ✖              | OK                   |

**Observações:**
- Todos os campos principais estão representados.
- Campos opcionais devem ser documentados como tais no OpenAPI.

**Ações recomendadas:**
- Garantir documentação de campos opcionais.

## 3.7 Tabela/Model: `node_templates` ↔ `NodeTemplateResponse`

| Campo Banco           | Campo OpenAPI           | Tipo Banco                | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|----------------------|------------------------|--------------------------|----------------------|---------------|----------------|----------------------|
| id                   | id                     | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| name                 | name                   | character varying        | string               | NO            | ✔              | OK                   |
| description          | description            | text                     | string               | YES           | ✖              | OK                   |
| category             | category               | character varying        | string               | NO            | ✔              | OK                   |
| tags                 | tags                   | jsonb                    | array/object         | YES           | ✖              | OK                   |
| workflow_definition  | workflow_definition    | jsonb                    | object               | NO            | ✔              | OK                   |
| preview_image        | preview_image          | character varying        | string               | YES           | ✖              | OK                   |
| author_id            | author_id              | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| version              | version                | character varying        | string               | NO            | ✔              | OK                   |
| is_public            | is_public              | boolean                  | boolean              | NO            | ✔              | OK                   |
| is_featured          | is_featured            | boolean                  | boolean              | NO            | ✔              | OK                   |
| downloads_count      | downloads_count        | integer                  | integer              | NO            | ✔              | OK                   |
| rating_average       | rating_average         | numeric                  | number               | NO            | ✔              | OK                   |
| rating_count         | rating_count           | integer                  | integer              | NO            | ✔              | OK                   |
| price                | price                  | numeric                  | number               | NO            | ✔              | OK                   |
| is_free              | is_free                | boolean                  | boolean              | NO            | ✔              | OK                   |
| license              | license                | character varying        | string               | NO            | ✔              | OK                   |
| created_at           | created_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| updated_at           | updated_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| title                | title                  | character varying        | string               | NO            | ✔              | OK                   |
| short_description    | short_description      | character varying        | string               | YES           | ✖              | OK                   |
| original_workflow_id | original_workflow_id   | uuid                     | string (uuid)        | YES           | ✖              | OK                   |
| status               | status                 | character varying        | string/enum          | YES           | ✖              | Enum pode divergir   |
| is_verified          | is_verified            | boolean                  | YES           | ✖              | OK                   |
| license_type         | license_type           | character varying        | YES           | ✖              | OK                   |
| workflow_data        | workflow_data          | jsonb                    | object               | NO            | ✔              | OK                   |
| nodes_data           | nodes_data             | jsonb                    | object               | NO            | ✔              | OK                   |
| connections_data     | connections_data       | jsonb                    | object/array         | YES           | ✖              | OK                   |
| required_variables   | required_variables     | jsonb                    | object/array         | YES           | ✖              | OK                   |
| optional_variables   | optional_variables     | jsonb                    | object/array         | YES           | ✖              | OK                   |
| default_config       | default_config         | jsonb                    | object               | YES           | ✖              | OK                   |
| compatibility_version| compatibility_version  | character varying        | YES           | ✖              | OK                   |
| estimated_duration   | estimated_duration     | integer                  | YES           | ✖              | OK                   |
| complexity_level     | complexity_level       | integer                  | YES           | ✖              | OK                   |
| download_count       | download_count         | integer                  | YES           | ✖              | OK                   |
| usage_count          | usage_count            | integer                  | YES           | ✖              | OK                   |
| view_count           | view_count             | integer                  | YES           | ✖              | OK                   |
| keywords             | keywords               | jsonb                    | array/object         | YES           | ✖              | OK                   |
| use_cases            | use_cases              | jsonb                    | array/object         | YES           | ✖              | OK                   |
| industries           | industries             | jsonb                    | array/object         | YES           | ✖              | OK                   |
| thumbnail_url        | thumbnail_url          | character varying        | YES           | ✖              | OK                   |
| preview_images       | preview_images         | jsonb                    | array/object         | YES           | ✖              | OK                   |
| demo_video_url       | demo_video_url         | character varying        | YES           | ✖              | OK                   |
| documentation        | documentation          | text                     | string               | YES           | ✖              | OK                   |
| setup_instructions   | setup_instructions     | text                     | string               | YES           | ✖              | OK                   |
| changelog            | changelog              | jsonb                    | object/array         | YES           | ✖              | OK                   |
| support_email        | support_email          | character varying        | YES           | ✖              | OK                   |
| repository_url       | repository_url         | character varying        | YES           | ✖              | OK                   |
| documentation_url    | documentation_url      | character varying        | YES           | ✖              | OK                   |
| published_at         | published_at           | timestamp with time zone | YES           | ✖              | OK                   |
| last_used_at         | last_used_at           | timestamp with time zone | YES           | ✖              | OK                   |
| tenant_id            | tenant_id              | uuid                     | YES           | ✖              | OK                   |

**Observações:**
- O campo `status` pode divergir em valores permitidos (enum). Recomenda-se alinhar os valores possíveis entre banco e OpenAPI.
- Campos de arrays/objetos (jsonb) devem ser bem documentados no OpenAPI.

**Ações recomendadas:**
- Validar enum de status.
- Documentar claramente a estrutura dos campos jsonb.

## 3.8 Tabela/Model: `workflow_connections` ↔ `WorkflowConnectionResponse`

| Campo Banco           | Campo OpenAPI           | Tipo Banco                | Tipo OpenAPI         | Null? (Banco) | Required (API) | Divergência?         |
|----------------------|------------------------|--------------------------|----------------------|---------------|----------------|----------------------|
| id                   | id                     | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| workflow_id          | workflow_id            | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| source_node_id       | source_node_id         | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| target_node_id       | target_node_id         | uuid                     | string (uuid)        | NO            | ✔              | OK                   |
| connection_type      | connection_type        | character varying        | string/enum          | NO            | ✔              | Enum pode divergir   |
| created_at           | created_at             | timestamp with time zone | string (date-time)   | NO            | ✔              | OK                   |
| updated_at           | updated_at             | timestamp with time zone | YES           | ✖              | OK                   |
| tenant_id            | tenant_id              | uuid                     | YES           | ✖              | OK                   |

**Observações:**
- O campo `connection_type` pode divergir em valores permitidos (enum). Recomenda-se alinhar os valores possíveis entre banco e OpenAPI.

**Ações recomendadas:**
- Validar enum de connection_type.

## 3.9 Observações Finais

- Todos os principais pares banco ↔ OpenAPI foram analisados campo a campo.
- Divergências principais envolvem enums, campos opcionais e estruturas jsonb/array.
- Recomenda-se revisão detalhada dos enums e documentação clara dos campos jsonb.
- Para tabelas/schemas que não possuem par correspondente, revisar necessidade de inclusão ou remoção.
