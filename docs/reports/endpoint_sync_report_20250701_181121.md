# SynapScale Endpoint-Database Synchronization Report

Generated on: 2025-07-01 18:11:21

## Executive Summary

- **Total Database Tables**: 103
- **Total API Resources**: 79
- **Mapped Tables**: 25
- **Unmapped Tables**: 78
- **Sync Coverage**: 24.3%

## Synchronization Metrics

| Metric | Value |
|--------|-------|
| Database Tables | 103 |
| API Resources | 79 |
| Mapped Tables | 25 |
| Unmapped Tables | 78 |
| Coverage Score | 24.3% |
| Full CRUD Coverage | 11 tables |

## Table Categories Analysis

### Core Entities
- Count: 36
- Tables: workflow_executions, workflow_templates, agent_quotas, user_subscriptions, user_variables, llms, user_insights, agent_kbs, workspace_projects, workflow_execution_metrics (and 26 more)

### Relationship Tables
- Count: 5
- Tables: contact_list_memberships, rbac_role_permissions, rbac_roles, rbac_permissions, plan_provider_mappings

### Audit Logs
- Count: 2
- Tables: webhook_logs, audit_log

### System Tables
- Count: 3
- Tables: system_health, alembic_version, system_performance_metrics

### Feature Specific
- Count: 37
- Tables: plan_entitlements, tags, project_versions, knowledge_bases, contact_tags, contact_lists, password_reset_tokens, refresh_tokens, component_versions, component_ratings (and 27 more)

### Analytics
- Count: 11
- Tables: billing_events, custom_reports, business_metrics, analytics_dashboards, report_executions, analytics_reports, analytics_exports, contact_events, analytics_events, analytics_metrics (and 1 more)

### Configuration
- Count: 9
- Tables: features, template_reviews, node_templates, template_favorites, template_downloads, template_usage, tenant_features, plan_features, template_collections

## Mapping Quality

### Well-Mapped Tables (Full CRUD)
- **workflow_templates** → `templates` (Score: 1.0)
- **analytics_dashboards** → `analytics_dashboards` (Score: 1.0)
- **marketplace_components** → `marketplace_components` (Score: 1.0)
- **analytics_reports** → `analytics_reports` (Score: 1.0)
- **workflow_nodes** → `nodes` (Score: 1.0)
- **node_templates** → `templates` (Score: 1.0)
- **agents** → `agents` (Score: 1.0)
- **workflows** → `workflows` (Score: 1.0)
- **workspaces** → `workspaces` (Score: 1.0)
- **nodes** → `nodes` (Score: 1.0)

... and 1 more

### Tables with Incomplete CRUD Coverage
- **workflow_executions** → `executions` (Missing: update, delete)
- **tags** → `marketplace_tags` (Missing: create, read, update, delete)
- **system_health** → `health` (Missing: create, read, update, delete)
- **llms** → `llm_providers` (Missing: create, read, update, delete)
- **report_executions** → `executions` (Missing: update, delete)
- **llms_conversations_turns** → `llm` (Missing: update, delete, list)
- **llms_messages** → `llm` (Missing: update, delete, list)
- **llms_usage_logs** → `llm` (Missing: update, delete, list)
- **analytics_exports** → `analytics_exports` (Missing: create, update, delete)
- **llms_conversations** → `llm` (Missing: update, delete, list)
- **node_executions** → `executions` (Missing: update, delete)
- **analytics_events** → `analytics_events` (Missing: read, update, delete)
- **files** → `files` (Missing: create, update)
- **analytics_metrics** → `analytics_metrics` (Missing: create, read, update, delete)

### Unmapped Tables
- **agent_acl**
- **agent_configurations**
- **agent_error_logs**
- **agent_hierarchy**
- **agent_kbs**
- **agent_models**
- **agent_quotas**
- **agent_tools**
- **agent_triggers**
- **agent_usage_metrics**
- **alembic_version**
- **audit_log**
- **billing_events**
- **business_metrics**
- **campaign_contacts**
- **campaigns**
- **component_downloads**
- **component_purchases**
- **component_ratings**
- **component_versions**
- **contact_events**
- **contact_interactions**
- **contact_list_memberships**
- **contact_lists**
- **contact_notes**
- **contact_sources**
- **contact_tags**
- **contacts**
- **conversion_journeys**
- **coupons**
- **custom_reports**
- **email_verification_tokens**
- **features**
- **invoices**
- **knowledge_bases**
- **message_feedbacks**
- **node_categories**
- **node_ratings**
- **password_reset_tokens**
- **payment_customers**
- **payment_methods**
- **payment_providers**
- **plan_entitlements**
- **plan_features**
- **plan_provider_mappings**
- **plans**
- **project_collaborators**
- **project_comments**
- **project_versions**
- **rbac_permissions**
- **rbac_role_permissions**
- **rbac_roles**
- **refresh_tokens**
- **subscriptions**
- **system_performance_metrics**
- **template_collections**
- **template_downloads**
- **template_favorites**
- **template_reviews**
- **template_usage**
- **tenant_features**
- **tenants**
- **tools**
- **user_behavior_metrics**
- **user_insights**
- **user_subscriptions**
- **user_tenant_roles**
- **user_variables**
- **users**
- **webhook_logs**
- **workflow_connections**
- **workflow_execution_metrics**
- **workflow_execution_queue**
- **workspace_activities**
- **workspace_features**
- **workspace_invitations**
- **workspace_members**
- **workspace_projects**


## Recommendations

1. 🚨 CRITICAL: Add API endpoints for core entities: agent_quotas, user_subscriptions, user_variables, user_insights, agent_kbs, workspace_projects, workflow_execution_metrics, agent_triggers, agent_tools, user_behavior_metrics, users, workspace_invitations, user_tenant_roles, agent_hierarchy, workspace_activities, agent_error_logs, workflow_execution_queue, agent_models, agent_acl, agent_configurations, agent_usage_metrics, workflow_connections, workspace_members, workspace_features
2. ⚠️  Add missing CRUD operations for: workflow_executions (missing: update, delete); llms (missing: create, read, update, delete); llms_conversations_turns (missing: update, delete, list); llms_messages (missing: update, delete, list); llms_usage_logs (missing: update, delete, list); llms_conversations (missing: update, delete, list); files (missing: create, update)
3. 📋 Consider adding endpoints for feature tables: plan_entitlements, project_versions, knowledge_bases, contact_tags, contact_lists
4. 🔍 Review endpoints without corresponding tables: analytics_admin, auth_logout, nodes_categories
5. 📊 Consider analytics endpoints for: billing_events, custom_reports, business_metrics


## API Resources Without Database Tables

- `analytics_admin`
- `analytics_analysis`
- `analytics_export`
- `analytics_insights`
- `analytics_overview`
- `analytics_queries`
- `auth_account`
- `auth_change-password`
- `auth_docs-login`
- `auth_forgot-password`
- `auth_login`
- `auth_logout`
- `auth_logout-all`
- `auth_me`
- `auth_refresh`
- `auth_register`
- `auth_resend-verification`
- `auth_reset-password`
- `auth_test-hybrid-auth`
- `auth_test-token`
- `auth_verify-email`
- `conversations`
- `executions_admin`
- `executions_batch`
- `executions_queue`
- `executions_stats`
- `executions_validate-workflow`
- `files_upload`
- `llm_chat`
- `llm_count-tokens`
- `llm_count-tokens-original`
- `llm_generate`
- `llm_models`
- `llm_test-tags`
- `marketplace_admin`
- `marketplace_categories`
- `marketplace_favorites`
- `marketplace_my-components`
- `marketplace_purchases`
- `marketplace_ratings`
- `marketplace_recommendations`
- `marketplace_stats`
- `nodes_categories`
- `nodes_types`
- `templates_collections`
- `templates_favorites`
- `templates_install`
- `templates_marketplace`
- `templates_my-stats`
- `templates_stats`
- `user-variables`
- `user-variables_api-keys`
- `user-variables_debug`
- `workspaces_creation-rules`
- `workspaces_integrations`
- `workspaces_invitations`
- `workspaces_projects`
- `workspaces_search`
- `workspaces_workspaces`
- `ws_stats`
- `ws_status`
