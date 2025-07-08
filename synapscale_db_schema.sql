--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP POLICY IF EXISTS tenant_isolation_workspaces_update ON synapscale_db.workspaces;
DROP POLICY IF EXISTS tenant_isolation_workspaces_select ON synapscale_db.workspaces;
DROP POLICY IF EXISTS tenant_isolation_workspaces_insert ON synapscale_db.workspaces;
DROP POLICY IF EXISTS tenant_isolation_workspaces_delete ON synapscale_db.workspaces;
DROP POLICY IF EXISTS tenant_isolation_workspace_projects_insert ON synapscale_db.workspace_projects;
DROP POLICY IF EXISTS tenant_isolation_workspace_projects ON synapscale_db.workspace_projects;
DROP POLICY IF EXISTS tenant_isolation_workspace_members_update ON synapscale_db.workspace_members;
DROP POLICY IF EXISTS tenant_isolation_workspace_members_select ON synapscale_db.workspace_members;
DROP POLICY IF EXISTS tenant_isolation_workspace_members_insert ON synapscale_db.workspace_members;
DROP POLICY IF EXISTS tenant_isolation_workspace_members_delete ON synapscale_db.workspace_members;
DROP POLICY IF EXISTS tenant_isolation_workflows_update ON synapscale_db.workflows;
DROP POLICY IF EXISTS tenant_isolation_workflows_select ON synapscale_db.workflows;
DROP POLICY IF EXISTS tenant_isolation_workflows_insert ON synapscale_db.workflows;
DROP POLICY IF EXISTS tenant_isolation_workflows_delete ON synapscale_db.workflows;
DROP POLICY IF EXISTS tenant_isolation_workflow_nodes_insert ON synapscale_db.workflow_nodes;
DROP POLICY IF EXISTS tenant_isolation_workflow_nodes ON synapscale_db.workflow_nodes;
DROP POLICY IF EXISTS tenant_isolation_workflow_executions_update ON synapscale_db.workflow_executions;
DROP POLICY IF EXISTS tenant_isolation_workflow_executions_select ON synapscale_db.workflow_executions;
DROP POLICY IF EXISTS tenant_isolation_workflow_executions_insert ON synapscale_db.workflow_executions;
DROP POLICY IF EXISTS tenant_isolation_workflow_executions_delete ON synapscale_db.workflow_executions;
DROP POLICY IF EXISTS tenant_isolation_workflow_connections_insert ON synapscale_db.workflow_connections;
DROP POLICY IF EXISTS tenant_isolation_workflow_connections ON synapscale_db.workflow_connections;
DROP POLICY IF EXISTS tenant_isolation_user_tenant_roles_update ON synapscale_db.user_tenant_roles;
DROP POLICY IF EXISTS tenant_isolation_user_tenant_roles_select ON synapscale_db.user_tenant_roles;
DROP POLICY IF EXISTS tenant_isolation_user_tenant_roles_insert ON synapscale_db.user_tenant_roles;
DROP POLICY IF EXISTS tenant_isolation_user_tenant_roles_delete ON synapscale_db.user_tenant_roles;
DROP POLICY IF EXISTS tenant_isolation_tools_insert ON synapscale_db.tools;
DROP POLICY IF EXISTS tenant_isolation_tools ON synapscale_db.tools;
DROP POLICY IF EXISTS tenant_isolation_tags_update ON synapscale_db.tags;
DROP POLICY IF EXISTS tenant_isolation_tags_select ON synapscale_db.tags;
DROP POLICY IF EXISTS tenant_isolation_tags_insert ON synapscale_db.tags;
DROP POLICY IF EXISTS tenant_isolation_tags_delete ON synapscale_db.tags;
DROP POLICY IF EXISTS tenant_isolation_subscriptions_insert ON synapscale_db.subscriptions;
DROP POLICY IF EXISTS tenant_isolation_subscriptions ON synapscale_db.subscriptions;
DROP POLICY IF EXISTS tenant_isolation_rbac_roles_insert ON synapscale_db.rbac_roles;
DROP POLICY IF EXISTS tenant_isolation_rbac_roles ON synapscale_db.rbac_roles;
DROP POLICY IF EXISTS tenant_isolation_rbac_permissions_insert ON synapscale_db.rbac_permissions;
DROP POLICY IF EXISTS tenant_isolation_rbac_permissions ON synapscale_db.rbac_permissions;
DROP POLICY IF EXISTS tenant_isolation_nodes_update ON synapscale_db.nodes;
DROP POLICY IF EXISTS tenant_isolation_nodes_select ON synapscale_db.nodes;
DROP POLICY IF EXISTS tenant_isolation_nodes_insert ON synapscale_db.nodes;
DROP POLICY IF EXISTS tenant_isolation_nodes_delete ON synapscale_db.nodes;
DROP POLICY IF EXISTS tenant_isolation_node_templates_insert ON synapscale_db.node_templates;
DROP POLICY IF EXISTS tenant_isolation_node_templates ON synapscale_db.node_templates;
DROP POLICY IF EXISTS tenant_isolation_marketplace_components_insert ON synapscale_db.marketplace_components;
DROP POLICY IF EXISTS tenant_isolation_marketplace_components ON synapscale_db.marketplace_components;
DROP POLICY IF EXISTS tenant_isolation_llms_insert ON synapscale_db.llms;
DROP POLICY IF EXISTS tenant_isolation_llms ON synapscale_db.llms;
DROP POLICY IF EXISTS tenant_isolation_knowledge_bases_insert ON synapscale_db.knowledge_bases;
DROP POLICY IF EXISTS tenant_isolation_knowledge_bases ON synapscale_db.knowledge_bases;
DROP POLICY IF EXISTS tenant_isolation_invoices_insert ON synapscale_db.invoices;
DROP POLICY IF EXISTS tenant_isolation_invoices ON synapscale_db.invoices;
DROP POLICY IF EXISTS tenant_isolation_files_update ON synapscale_db.files;
DROP POLICY IF EXISTS tenant_isolation_files_select ON synapscale_db.files;
DROP POLICY IF EXISTS tenant_isolation_files_insert ON synapscale_db.files;
DROP POLICY IF EXISTS tenant_isolation_files_delete ON synapscale_db.files;
DROP POLICY IF EXISTS tenant_isolation_contacts_update ON synapscale_db.contacts;
DROP POLICY IF EXISTS tenant_isolation_contacts_select ON synapscale_db.contacts;
DROP POLICY IF EXISTS tenant_isolation_contacts_insert ON synapscale_db.contacts;
DROP POLICY IF EXISTS tenant_isolation_contacts_delete ON synapscale_db.contacts;
DROP POLICY IF EXISTS tenant_isolation_contact_lists_insert ON synapscale_db.contact_lists;
DROP POLICY IF EXISTS tenant_isolation_contact_lists ON synapscale_db.contact_lists;
DROP POLICY IF EXISTS tenant_isolation_campaigns_update ON synapscale_db.campaigns;
DROP POLICY IF EXISTS tenant_isolation_campaigns_select ON synapscale_db.campaigns;
DROP POLICY IF EXISTS tenant_isolation_campaigns_insert ON synapscale_db.campaigns;
DROP POLICY IF EXISTS tenant_isolation_campaigns_delete ON synapscale_db.campaigns;
DROP POLICY IF EXISTS tenant_isolation_billing_events_insert ON synapscale_db.billing_events;
DROP POLICY IF EXISTS tenant_isolation_billing_events ON synapscale_db.billing_events;
DROP POLICY IF EXISTS tenant_isolation_analytics_events_insert ON synapscale_db.analytics_events;
DROP POLICY IF EXISTS tenant_isolation_analytics_events ON synapscale_db.analytics_events;
DROP POLICY IF EXISTS tenant_isolation_agents_insert ON synapscale_db.agents;
DROP POLICY IF EXISTS tenant_isolation_agents ON synapscale_db.agents;
DROP POLICY IF EXISTS tenant_isolation ON synapscale_db.agents;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspaces DROP CONSTRAINT IF EXISTS workspaces_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspaces DROP CONSTRAINT IF EXISTS workspaces_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_projects DROP CONSTRAINT IF EXISTS workspace_projects_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_projects DROP CONSTRAINT IF EXISTS workspace_projects_workflow_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_projects DROP CONSTRAINT IF EXISTS workspace_projects_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_members DROP CONSTRAINT IF EXISTS workspace_members_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_members DROP CONSTRAINT IF EXISTS workspace_members_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_members DROP CONSTRAINT IF EXISTS workspace_members_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_invitations DROP CONSTRAINT IF EXISTS workspace_invitations_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_invitations DROP CONSTRAINT IF EXISTS workspace_invitations_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_invitations DROP CONSTRAINT IF EXISTS workspace_invitations_inviter_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_invitations DROP CONSTRAINT IF EXISTS workspace_invitations_invited_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_features DROP CONSTRAINT IF EXISTS workspace_features_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_features DROP CONSTRAINT IF EXISTS workspace_features_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_features DROP CONSTRAINT IF EXISTS workspace_features_feature_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_activities DROP CONSTRAINT IF EXISTS workspace_activities_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_activities DROP CONSTRAINT IF EXISTS workspace_activities_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_activities DROP CONSTRAINT IF EXISTS workspace_activities_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflows DROP CONSTRAINT IF EXISTS workflows_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflows DROP CONSTRAINT IF EXISTS workflows_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflows DROP CONSTRAINT IF EXISTS workflows_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_templates DROP CONSTRAINT IF EXISTS workflow_templates_original_workflow_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_templates DROP CONSTRAINT IF EXISTS workflow_templates_author_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_workflow_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_executions DROP CONSTRAINT IF EXISTS workflow_executions_workflow_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_executions DROP CONSTRAINT IF EXISTS workflow_executions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_executions DROP CONSTRAINT IF EXISTS workflow_executions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_execution_queue DROP CONSTRAINT IF EXISTS workflow_execution_queue_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_execution_metrics DROP CONSTRAINT IF EXISTS workflow_execution_metrics_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_connections DROP CONSTRAINT IF EXISTS workflow_connections_workflow_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_connections DROP CONSTRAINT IF EXISTS workflow_connections_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_connections DROP CONSTRAINT IF EXISTS workflow_connections_target_node_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_connections DROP CONSTRAINT IF EXISTS workflow_connections_source_node_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.webhook_logs DROP CONSTRAINT IF EXISTS webhook_logs_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.webhook_logs DROP CONSTRAINT IF EXISTS webhook_logs_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.users DROP CONSTRAINT IF EXISTS users_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_variables DROP CONSTRAINT IF EXISTS user_variables_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_variables DROP CONSTRAINT IF EXISTS user_variables_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_tenant_roles DROP CONSTRAINT IF EXISTS user_tenant_roles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_tenant_roles DROP CONSTRAINT IF EXISTS user_tenant_roles_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_tenant_roles DROP CONSTRAINT IF EXISTS user_tenant_roles_role_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_tenant_roles DROP CONSTRAINT IF EXISTS user_tenant_roles_granted_by_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_subscriptions DROP CONSTRAINT IF EXISTS user_subscriptions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_subscriptions DROP CONSTRAINT IF EXISTS user_subscriptions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_subscriptions DROP CONSTRAINT IF EXISTS user_subscriptions_plan_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_insights DROP CONSTRAINT IF EXISTS user_insights_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_insights DROP CONSTRAINT IF EXISTS user_insights_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_behavior_metrics DROP CONSTRAINT IF EXISTS user_behavior_metrics_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_behavior_metrics DROP CONSTRAINT IF EXISTS user_behavior_metrics_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS usage_logs_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS usage_logs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS usage_logs_message_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS usage_logs_llm_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS usage_logs_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenant_features DROP CONSTRAINT IF EXISTS tenant_features_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenant_features DROP CONSTRAINT IF EXISTS tenant_features_feature_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_usage DROP CONSTRAINT IF EXISTS template_usage_workflow_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_usage DROP CONSTRAINT IF EXISTS template_usage_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_usage DROP CONSTRAINT IF EXISTS template_usage_template_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_reviews DROP CONSTRAINT IF EXISTS template_reviews_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_reviews DROP CONSTRAINT IF EXISTS template_reviews_template_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_favorites DROP CONSTRAINT IF EXISTS template_favorites_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_favorites DROP CONSTRAINT IF EXISTS template_favorites_template_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_downloads DROP CONSTRAINT IF EXISTS template_downloads_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_downloads DROP CONSTRAINT IF EXISTS template_downloads_template_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_collections DROP CONSTRAINT IF EXISTS template_collections_creator_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tags DROP CONSTRAINT IF EXISTS tags_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tags DROP CONSTRAINT IF EXISTS tags_created_by_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.system_performance_metrics DROP CONSTRAINT IF EXISTS system_performance_metrics_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_plan_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_payment_method_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_coupon_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.report_executions DROP CONSTRAINT IF EXISTS report_executions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.report_executions DROP CONSTRAINT IF EXISTS report_executions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.report_executions DROP CONSTRAINT IF EXISTS report_executions_report_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_roles DROP CONSTRAINT IF EXISTS rbac_roles_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_role_permissions DROP CONSTRAINT IF EXISTS rbac_role_permissions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_role_permissions DROP CONSTRAINT IF EXISTS rbac_role_permissions_role_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_role_permissions DROP CONSTRAINT IF EXISTS rbac_role_permissions_permission_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_permissions DROP CONSTRAINT IF EXISTS rbac_permissions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_versions DROP CONSTRAINT IF EXISTS project_versions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_versions DROP CONSTRAINT IF EXISTS project_versions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_versions DROP CONSTRAINT IF EXISTS project_versions_project_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_comments DROP CONSTRAINT IF EXISTS project_comments_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_comments DROP CONSTRAINT IF EXISTS project_comments_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_comments DROP CONSTRAINT IF EXISTS project_comments_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_collaborators DROP CONSTRAINT IF EXISTS project_collaborators_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_collaborators DROP CONSTRAINT IF EXISTS project_collaborators_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_provider_mappings DROP CONSTRAINT IF EXISTS plan_provider_mappings_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_provider_mappings DROP CONSTRAINT IF EXISTS plan_provider_mappings_plan_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_features DROP CONSTRAINT IF EXISTS plan_features_plan_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_features DROP CONSTRAINT IF EXISTS plan_features_feature_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_entitlements DROP CONSTRAINT IF EXISTS plan_entitlements_plan_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_entitlements DROP CONSTRAINT IF EXISTS plan_entitlements_feature_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_methods DROP CONSTRAINT IF EXISTS payment_methods_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_methods DROP CONSTRAINT IF EXISTS payment_methods_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_customers DROP CONSTRAINT IF EXISTS payment_customers_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_customers DROP CONSTRAINT IF EXISTS payment_customers_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.nodes DROP CONSTRAINT IF EXISTS nodes_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.nodes DROP CONSTRAINT IF EXISTS nodes_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.nodes DROP CONSTRAINT IF EXISTS nodes_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_ratings DROP CONSTRAINT IF EXISTS node_ratings_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_ratings DROP CONSTRAINT IF EXISTS node_ratings_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_ratings DROP CONSTRAINT IF EXISTS node_ratings_node_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_executions DROP CONSTRAINT IF EXISTS node_executions_workflow_execution_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_executions DROP CONSTRAINT IF EXISTS node_executions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_categories DROP CONSTRAINT IF EXISTS node_categories_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_categories DROP CONSTRAINT IF EXISTS node_categories_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_messages DROP CONSTRAINT IF EXISTS messages_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.message_feedbacks DROP CONSTRAINT IF EXISTS message_feedbacks_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.message_feedbacks DROP CONSTRAINT IF EXISTS message_feedbacks_message_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.marketplace_components DROP CONSTRAINT IF EXISTS marketplace_components_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.marketplace_components DROP CONSTRAINT IF EXISTS marketplace_components_author_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms DROP CONSTRAINT IF EXISTS llms_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations DROP CONSTRAINT IF EXISTS llms_conversations_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.invoices DROP CONSTRAINT IF EXISTS invoices_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.invoices DROP CONSTRAINT IF EXISTS invoices_subscription_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_templates DROP CONSTRAINT IF EXISTS fk_workflow_templates_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS fk_usage_msg;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS fk_usage_llm;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS fk_usage_conv;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenants DROP CONSTRAINT IF EXISTS fk_tenants_plan_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_usage DROP CONSTRAINT IF EXISTS fk_template_usage_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_reviews DROP CONSTRAINT IF EXISTS fk_template_reviews_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_favorites DROP CONSTRAINT IF EXISTS fk_template_favorites_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_downloads DROP CONSTRAINT IF EXISTS fk_template_downloads_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_collections DROP CONSTRAINT IF EXISTS fk_template_collections_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_templates DROP CONSTRAINT IF EXISTS fk_node_templates_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_messages DROP CONSTRAINT IF EXISTS fk_messages_conv;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS fk_llms_usage_logs_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_messages DROP CONSTRAINT IF EXISTS fk_llms_messages_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.message_feedbacks DROP CONSTRAINT IF EXISTS fk_llms_message_feedbacks_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations_turns DROP CONSTRAINT IF EXISTS fk_llms_conversations_turns_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations DROP CONSTRAINT IF EXISTS fk_llms_conversations_tenant_id;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations DROP CONSTRAINT IF EXISTS fk_llms_conversations_agent;
ALTER TABLE IF EXISTS ONLY synapscale_db.message_feedbacks DROP CONSTRAINT IF EXISTS fk_feedback_user;
ALTER TABLE IF EXISTS ONLY synapscale_db.message_feedbacks DROP CONSTRAINT IF EXISTS fk_feedback_msg;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations_turns DROP CONSTRAINT IF EXISTS fk_conv_turns_llm;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations_turns DROP CONSTRAINT IF EXISTS fk_conv_turns_conv;
ALTER TABLE IF EXISTS ONLY synapscale_db.files DROP CONSTRAINT IF EXISTS files_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.files DROP CONSTRAINT IF EXISTS files_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_execution_queue DROP CONSTRAINT IF EXISTS execution_queue_workflow_execution_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_execution_queue DROP CONSTRAINT IF EXISTS execution_queue_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.email_verification_tokens DROP CONSTRAINT IF EXISTS email_verification_tokens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.custom_reports DROP CONSTRAINT IF EXISTS custom_reports_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.custom_reports DROP CONSTRAINT IF EXISTS custom_reports_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.custom_reports DROP CONSTRAINT IF EXISTS custom_reports_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.coupons DROP CONSTRAINT IF EXISTS coupons_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.coupons DROP CONSTRAINT IF EXISTS coupons_created_by_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.conversion_journeys DROP CONSTRAINT IF EXISTS conversion_journeys_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.conversion_journeys DROP CONSTRAINT IF EXISTS conversion_journeys_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations DROP CONSTRAINT IF EXISTS conversations_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations_turns DROP CONSTRAINT IF EXISTS conversation_llms_llm_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations_turns DROP CONSTRAINT IF EXISTS conversation_llms_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contacts DROP CONSTRAINT IF EXISTS contacts_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contacts DROP CONSTRAINT IF EXISTS contacts_source_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_tags DROP CONSTRAINT IF EXISTS contact_tags_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_sources DROP CONSTRAINT IF EXISTS contact_sources_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_notes DROP CONSTRAINT IF EXISTS contact_notes_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_notes DROP CONSTRAINT IF EXISTS contact_notes_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_notes DROP CONSTRAINT IF EXISTS contact_notes_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_lists DROP CONSTRAINT IF EXISTS contact_lists_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_list_memberships DROP CONSTRAINT IF EXISTS contact_list_memberships_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_list_memberships DROP CONSTRAINT IF EXISTS contact_list_memberships_list_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_list_memberships DROP CONSTRAINT IF EXISTS contact_list_memberships_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_list_memberships DROP CONSTRAINT IF EXISTS contact_list_memberships_added_by_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_interactions DROP CONSTRAINT IF EXISTS contact_interactions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_interactions DROP CONSTRAINT IF EXISTS contact_interactions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_interactions DROP CONSTRAINT IF EXISTS contact_interactions_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_events DROP CONSTRAINT IF EXISTS contact_events_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_events DROP CONSTRAINT IF EXISTS contact_events_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_versions DROP CONSTRAINT IF EXISTS component_versions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_versions DROP CONSTRAINT IF EXISTS component_versions_component_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_ratings DROP CONSTRAINT IF EXISTS component_ratings_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_ratings DROP CONSTRAINT IF EXISTS component_ratings_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_ratings DROP CONSTRAINT IF EXISTS component_ratings_component_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_purchases DROP CONSTRAINT IF EXISTS component_purchases_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_purchases DROP CONSTRAINT IF EXISTS component_purchases_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_purchases DROP CONSTRAINT IF EXISTS component_purchases_component_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_downloads DROP CONSTRAINT IF EXISTS component_downloads_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_downloads DROP CONSTRAINT IF EXISTS component_downloads_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_downloads DROP CONSTRAINT IF EXISTS component_downloads_component_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaigns DROP CONSTRAINT IF EXISTS campaigns_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaigns DROP CONSTRAINT IF EXISTS campaigns_created_by_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaign_contacts DROP CONSTRAINT IF EXISTS campaign_contacts_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaign_contacts DROP CONSTRAINT IF EXISTS campaign_contacts_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaign_contacts DROP CONSTRAINT IF EXISTS campaign_contacts_campaign_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.business_metrics DROP CONSTRAINT IF EXISTS business_metrics_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.billing_events DROP CONSTRAINT IF EXISTS billing_events_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.billing_events DROP CONSTRAINT IF EXISTS billing_events_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.billing_events DROP CONSTRAINT IF EXISTS billing_events_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.billing_events DROP CONSTRAINT IF EXISTS billing_events_related_usage_log_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.billing_events DROP CONSTRAINT IF EXISTS billing_events_related_message_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.audit_log DROP CONSTRAINT IF EXISTS audit_log_changed_by_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_reports DROP CONSTRAINT IF EXISTS analytics_reports_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_reports DROP CONSTRAINT IF EXISTS analytics_reports_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_metrics DROP CONSTRAINT IF EXISTS analytics_metrics_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_exports DROP CONSTRAINT IF EXISTS analytics_exports_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_exports DROP CONSTRAINT IF EXISTS analytics_exports_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_events DROP CONSTRAINT IF EXISTS analytics_events_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_events DROP CONSTRAINT IF EXISTS analytics_events_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_events DROP CONSTRAINT IF EXISTS analytics_events_project_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_dashboards DROP CONSTRAINT IF EXISTS analytics_dashboards_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_dashboards DROP CONSTRAINT IF EXISTS analytics_dashboards_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_alerts DROP CONSTRAINT IF EXISTS analytics_alerts_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_alerts DROP CONSTRAINT IF EXISTS analytics_alerts_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agents DROP CONSTRAINT IF EXISTS agents_workspace_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agents DROP CONSTRAINT IF EXISTS agents_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agents DROP CONSTRAINT IF EXISTS agents_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agents DROP CONSTRAINT IF EXISTS agents_current_config_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_usage_metrics DROP CONSTRAINT IF EXISTS agent_usage_metrics_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_triggers DROP CONSTRAINT IF EXISTS agent_triggers_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_tools DROP CONSTRAINT IF EXISTS agent_tools_tool_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_tools DROP CONSTRAINT IF EXISTS agent_tools_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_quotas DROP CONSTRAINT IF EXISTS agent_quotas_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_quotas DROP CONSTRAINT IF EXISTS agent_quotas_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_models DROP CONSTRAINT IF EXISTS agent_models_llm_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_models DROP CONSTRAINT IF EXISTS agent_models_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_kbs DROP CONSTRAINT IF EXISTS agent_kbs_kb_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_kbs DROP CONSTRAINT IF EXISTS agent_kbs_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_hierarchy DROP CONSTRAINT IF EXISTS agent_hierarchy_descendant_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_hierarchy DROP CONSTRAINT IF EXISTS agent_hierarchy_ancestor_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_error_logs DROP CONSTRAINT IF EXISTS agent_error_logs_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_configurations DROP CONSTRAINT IF EXISTS agent_configurations_created_by_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_configurations DROP CONSTRAINT IF EXISTS agent_configurations_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_acl DROP CONSTRAINT IF EXISTS agent_acl_user_id_fkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_acl DROP CONSTRAINT IF EXISTS agent_acl_agent_id_fkey;
DROP TRIGGER IF EXISTS trigger_validate_workspace_limits ON synapscale_db.workspaces;
DROP TRIGGER IF EXISTS trigger_validate_project_limits ON synapscale_db.workspace_projects;
DROP TRIGGER IF EXISTS trigger_validate_member_limits ON synapscale_db.workspace_members;
DROP TRIGGER IF EXISTS trigger_sync_storage_usage ON synapscale_db.files;
DROP TRIGGER IF EXISTS trigger_sync_on_subscription_change ON synapscale_db.subscriptions;
DROP TRIGGER IF EXISTS trigger_subscriptions_sync ON synapscale_db.subscriptions;
DROP TRIGGER IF EXISTS trigger_plans_sync ON synapscale_db.plans;
DROP TRIGGER IF EXISTS trigger_check_workspace_limits ON synapscale_db.workspaces;
DROP TRIGGER IF EXISTS trg_updated_at_tools ON synapscale_db.tools;
DROP TRIGGER IF EXISTS trg_updated_at_knowledge_bases ON synapscale_db.knowledge_bases;
DROP TRIGGER IF EXISTS trg_updated_at_agent_configurations ON synapscale_db.agent_configurations;
DROP TRIGGER IF EXISTS trg_audit_tools ON synapscale_db.tools;
DROP TRIGGER IF EXISTS trg_audit_knowledge_bases ON synapscale_db.knowledge_bases;
DROP TRIGGER IF EXISTS trg_audit_agent_triggers ON synapscale_db.agent_triggers;
DROP TRIGGER IF EXISTS trg_audit_agent_tools ON synapscale_db.agent_tools;
DROP TRIGGER IF EXISTS trg_audit_agent_models ON synapscale_db.agent_models;
DROP TRIGGER IF EXISTS trg_audit_agent_kbs ON synapscale_db.agent_kbs;
DROP TRIGGER IF EXISTS trg_audit_agent_configurations ON synapscale_db.agent_configurations;
DROP INDEX IF EXISTS synapscale_db.ix_usage_logs_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_usage_logs_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_usage_logs_llm_id;
DROP INDEX IF EXISTS synapscale_db.ix_usage_logs_created_at;
DROP INDEX IF EXISTS synapscale_db.ix_usage_logs_conversation_id;
DROP INDEX IF EXISTS synapscale_db.ix_tags_target_type;
DROP INDEX IF EXISTS synapscale_db.ix_tags_target_id;
DROP INDEX IF EXISTS synapscale_db.ix_tags_tag_name;
DROP INDEX IF EXISTS synapscale_db.ix_tags_tag_category;
DROP INDEX IF EXISTS synapscale_db.ix_tags_is_system_tag;
DROP INDEX IF EXISTS synapscale_db.ix_tags_created_by_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_users_username;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_users_email;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_refresh_tokens_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_refresh_tokens_token;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_password_reset_tokens_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_password_reset_tokens_token;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_node_ratings_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_node_ratings_node_id;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_email_verification_tokens_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_synapscale_db_email_verification_tokens_token;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspaces_slug;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_projects_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_projects_workflow_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_members_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_members_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_members_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_invitations_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_invitations_token;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_invitations_inviter_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_invitations_invited_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_invitations_email;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_activities_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_activities_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workspace_activities_action;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflows_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_templates_status;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_templates_published_at;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_templates_original_workflow_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_templates_license_type;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_templates_is_verified;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_templates_download_count;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_nodes_workflow_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_nodes_node_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_executions_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_executions_priority;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_executions_execution_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_workflow_connections_workflow_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_user_insights_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_user_insights_insight_type;
DROP INDEX IF EXISTS synapscale_db.ix_public_user_insights_category;
DROP INDEX IF EXISTS synapscale_db.ix_public_user_behavior_metrics_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_user_behavior_metrics_date;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_usage_workflow_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_usage_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_usage_used_at;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_usage_template_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_usage_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_reviews_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_reviews_template_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_reviews_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_favorites_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_favorites_template_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_favorites_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_downloads_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_downloads_template_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_downloads_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_downloads_downloaded_at;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_collections_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_collections_creator_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_template_collections_collection_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_system_performance_metrics_timestamp;
DROP INDEX IF EXISTS synapscale_db.ix_public_system_performance_metrics_service;
DROP INDEX IF EXISTS synapscale_db.ix_public_system_performance_metrics_metric_name;
DROP INDEX IF EXISTS synapscale_db.ix_public_system_performance_metrics_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_report_executions_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_report_executions_report_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_versions_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_versions_project_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_comments_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_comments_project_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_comments_parent_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_collaborators_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_project_collaborators_project_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_nodes_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_nodes_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_workflow_execution_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_node_type;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_node_key;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_node_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_execution_order;
DROP INDEX IF EXISTS synapscale_db.ix_public_node_executions_execution_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_marketplace_components_subcategory;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_workflow_execution_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_worker_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_status;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_scheduled_at;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_queue_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_priority;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_queue_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_workflow_execution_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_node_execution_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_metric_type;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_metric_name;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_measured_at;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_execution_metrics_context;
DROP INDEX IF EXISTS synapscale_db.ix_public_custom_reports_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_custom_reports_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_custom_reports_category;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_versions_component_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_ratings_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_ratings_component_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_purchases_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_purchases_component_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_downloads_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_component_downloads_component_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_business_metrics_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_business_metrics_date;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_workflow_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_project_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_label;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_event_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_category;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_anonymous_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_events_action;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_dashboards_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_analytics_dashboards_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_public_agents_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_message_feedbacks_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_message_feedbacks_rating_type;
DROP INDEX IF EXISTS synapscale_db.ix_message_feedbacks_message_id;
DROP INDEX IF EXISTS synapscale_db.ix_llms_provider;
DROP INDEX IF EXISTS synapscale_db.ix_llms_name;
DROP INDEX IF EXISTS synapscale_db.ix_llms_is_active;
DROP INDEX IF EXISTS synapscale_db.ix_conversation_llms_llm_id;
DROP INDEX IF EXISTS synapscale_db.ix_conversation_llms_conversation_id;
DROP INDEX IF EXISTS synapscale_db.ix_billing_events_workspace_id;
DROP INDEX IF EXISTS synapscale_db.ix_billing_events_user_id;
DROP INDEX IF EXISTS synapscale_db.ix_billing_events_status;
DROP INDEX IF EXISTS synapscale_db.ix_billing_events_event_type;
DROP INDEX IF EXISTS synapscale_db.ix_billing_events_created_at;
DROP INDEX IF EXISTS synapscale_db.idx_workspaces_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspaces_status;
DROP INDEX IF EXISTS synapscale_db.idx_workspaces_last_api_reset_daily;
DROP INDEX IF EXISTS synapscale_db.idx_workspaces_email_notifications;
DROP INDEX IF EXISTS synapscale_db.idx_workspaces_api_calls_today;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_projects_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_projects_status;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_members_workspace_status;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_members_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_members_status;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_invitations_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_invitations_status;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_features_workspace_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_features_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_features_is_enabled;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_features_feature_id;
DROP INDEX IF EXISTS synapscale_db.idx_workspace_activities_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_tenant_workspace;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_tenant_user;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_status;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_priority;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_name;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_definition_nodes;
DROP INDEX IF EXISTS synapscale_db.idx_workflows_definition_connections;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_templates_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_nodes_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_executions_tenant_workflow;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_executions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_executions_status;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_executions_created_at;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_execution_queue_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_execution_metrics_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_workflow_connections_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_webhook_logs_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_webhook_logs_status;
DROP INDEX IF EXISTS synapscale_db.idx_webhook_logs_provider_id;
DROP INDEX IF EXISTS synapscale_db.idx_webhook_logs_event_type;
DROP INDEX IF EXISTS synapscale_db.idx_users_status;
DROP INDEX IF EXISTS synapscale_db.idx_users_last_login;
DROP INDEX IF EXISTS synapscale_db.idx_users_failed_attempts;
DROP INDEX IF EXISTS synapscale_db.idx_user_variables_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_variables_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_tenant_roles_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_tenant_roles_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_tenant_roles_role_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_subscriptions_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_subscriptions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_insights_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_user_behavior_metrics_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_tools_base_config;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_theme;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_status;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_slug;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_plan_id;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_mfa_required;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_max_workspaces;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_max_storage_mb;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_max_api_calls_per_day;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_language;
DROP INDEX IF EXISTS synapscale_db.idx_tenants_enabled_features;
DROP INDEX IF EXISTS synapscale_db.idx_tenant_features_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_tenant_features_feature_id;
DROP INDEX IF EXISTS synapscale_db.idx_template_usage_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_template_reviews_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_template_favorites_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_template_downloads_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_template_collections_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_tags_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_system_performance_metrics_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_subscriptions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_subscriptions_status;
DROP INDEX IF EXISTS synapscale_db.idx_subscriptions_plan_id;
DROP INDEX IF EXISTS synapscale_db.idx_subscriptions_current_period_end;
DROP INDEX IF EXISTS synapscale_db.idx_report_executions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_report_executions_status;
DROP INDEX IF EXISTS synapscale_db.idx_rbac_role_permissions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_rbac_permissions_key;
DROP INDEX IF EXISTS synapscale_db.idx_rbac_permissions_category;
DROP INDEX IF EXISTS synapscale_db.idx_project_versions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_project_comments_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_project_comments_node_id;
DROP INDEX IF EXISTS synapscale_db.idx_project_collaborators_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_plans_is_active;
DROP INDEX IF EXISTS synapscale_db.idx_plan_entitlements_plan_id;
DROP INDEX IF EXISTS synapscale_db.idx_plan_entitlements_feature_id;
DROP INDEX IF EXISTS synapscale_db.idx_payment_methods_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_payment_customers_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_payment_customers_provider_id;
DROP INDEX IF EXISTS synapscale_db.idx_password_reset_tokens_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_nodes_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_nodes_status;
DROP INDEX IF EXISTS synapscale_db.idx_node_templates_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_node_ratings_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_node_executions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_node_categories_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_messages_conversation_created;
DROP INDEX IF EXISTS synapscale_db.idx_marketplace_components_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_marketplace_components_status;
DROP INDEX IF EXISTS synapscale_db.idx_marketplace_components_name;
DROP INDEX IF EXISTS synapscale_db.idx_llms_usage_logs_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_usage_logs_status;
DROP INDEX IF EXISTS synapscale_db.idx_llms_usage_conv_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_status;
DROP INDEX IF EXISTS synapscale_db.idx_llms_messages_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_messages_status;
DROP INDEX IF EXISTS synapscale_db.idx_llms_messages_created_at;
DROP INDEX IF EXISTS synapscale_db.idx_llms_messages_conv_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_message_feedbacks_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_workspace_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_user_status;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_turns_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_status;
DROP INDEX IF EXISTS synapscale_db.idx_llms_conversations_agent_id;
DROP INDEX IF EXISTS synapscale_db.idx_kbs_content;
DROP INDEX IF EXISTS synapscale_db.idx_invoices_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_invoices_status;
DROP INDEX IF EXISTS synapscale_db.idx_invoices_due_date;
DROP INDEX IF EXISTS synapscale_db.idx_files_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_files_tenant_user;
DROP INDEX IF EXISTS synapscale_db.idx_files_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_files_status;
DROP INDEX IF EXISTS synapscale_db.idx_files_scan_status;
DROP INDEX IF EXISTS synapscale_db.idx_file_filename;
DROP INDEX IF EXISTS synapscale_db.idx_file_created_at;
DROP INDEX IF EXISTS synapscale_db.idx_feedback_message_id;
DROP INDEX IF EXISTS synapscale_db.idx_features_key;
DROP INDEX IF EXISTS synapscale_db.idx_features_category;
DROP INDEX IF EXISTS synapscale_db.idx_email_verification_tokens_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_custom_reports_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_custom_reports_status;
DROP INDEX IF EXISTS synapscale_db.idx_coupons_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_conversion_journeys_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_conversations_tenant_user;
DROP INDEX IF EXISTS synapscale_db.idx_conv_turns_conversation_id;
DROP INDEX IF EXISTS synapscale_db.idx_contacts_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_contacts_status;
DROP INDEX IF EXISTS synapscale_db.idx_contacts_email;
DROP INDEX IF EXISTS synapscale_db.idx_contact_notes_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_notes_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_lists_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_list_memberships_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_list_memberships_status;
DROP INDEX IF EXISTS synapscale_db.idx_contact_interactions_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_interactions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_interactions_status;
DROP INDEX IF EXISTS synapscale_db.idx_contact_interactions_created_at;
DROP INDEX IF EXISTS synapscale_db.idx_contact_interactions_contact_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_events_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_contact_events_contact_id;
DROP INDEX IF EXISTS synapscale_db.idx_component_versions_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_component_versions_status;
DROP INDEX IF EXISTS synapscale_db.idx_component_ratings_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_component_ratings_status;
DROP INDEX IF EXISTS synapscale_db.idx_component_purchases_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_component_purchases_status;
DROP INDEX IF EXISTS synapscale_db.idx_component_downloads_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_component_downloads_status;
DROP INDEX IF EXISTS synapscale_db.idx_campaigns_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_campaigns_status;
DROP INDEX IF EXISTS synapscale_db.idx_campaign_contacts_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_campaign_contacts_status;
DROP INDEX IF EXISTS synapscale_db.idx_business_metrics_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_billing_events_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_reports_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_metrics_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_exports_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_exports_status;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_events_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_events_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_dashboards_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_dashboards_status;
DROP INDEX IF EXISTS synapscale_db.idx_analytics_alerts_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_agents_user_id;
DROP INDEX IF EXISTS synapscale_db.idx_agents_tenant_workspace;
DROP INDEX IF EXISTS synapscale_db.idx_agents_tenant_user;
DROP INDEX IF EXISTS synapscale_db.idx_agents_tenant_id;
DROP INDEX IF EXISTS synapscale_db.idx_agents_status;
DROP INDEX IF EXISTS synapscale_db.idx_agents_priority;
DROP INDEX IF EXISTS synapscale_db.idx_agents_name;
DROP INDEX IF EXISTS synapscale_db.idx_agent_tools_config;
DROP INDEX IF EXISTS synapscale_db.idx_agent_kbs_config;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspaces DROP CONSTRAINT IF EXISTS workspaces_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_projects DROP CONSTRAINT IF EXISTS workspace_projects_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_members DROP CONSTRAINT IF EXISTS workspace_members_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_invitations DROP CONSTRAINT IF EXISTS workspace_invitations_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_features DROP CONSTRAINT IF EXISTS workspace_features_workspace_id_feature_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_features DROP CONSTRAINT IF EXISTS workspace_features_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workspace_activities DROP CONSTRAINT IF EXISTS workspace_activities_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflows DROP CONSTRAINT IF EXISTS workflows_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_templates DROP CONSTRAINT IF EXISTS workflow_templates_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_executions DROP CONSTRAINT IF EXISTS workflow_executions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_connections DROP CONSTRAINT IF EXISTS workflow_connections_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.webhook_logs DROP CONSTRAINT IF EXISTS webhook_logs_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_variables DROP CONSTRAINT IF EXISTS user_variables_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_tenant_roles DROP CONSTRAINT IF EXISTS user_tenant_roles_user_id_tenant_id_role_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_tenant_roles DROP CONSTRAINT IF EXISTS user_tenant_roles_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_subscriptions DROP CONSTRAINT IF EXISTS user_subscriptions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_insights DROP CONSTRAINT IF EXISTS user_insights_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.user_behavior_metrics DROP CONSTRAINT IF EXISTS user_behavior_metrics_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_usage_logs DROP CONSTRAINT IF EXISTS usage_logs_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tools DROP CONSTRAINT IF EXISTS tools_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenants DROP CONSTRAINT IF EXISTS tenants_slug_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenants DROP CONSTRAINT IF EXISTS tenants_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenant_features DROP CONSTRAINT IF EXISTS tenant_features_tenant_id_feature_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.tenant_features DROP CONSTRAINT IF EXISTS tenant_features_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_usage DROP CONSTRAINT IF EXISTS template_usage_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_reviews DROP CONSTRAINT IF EXISTS template_reviews_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_favorites DROP CONSTRAINT IF EXISTS template_favorites_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_downloads DROP CONSTRAINT IF EXISTS template_downloads_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.template_collections DROP CONSTRAINT IF EXISTS template_collections_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.tags DROP CONSTRAINT IF EXISTS tags_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.system_performance_metrics DROP CONSTRAINT IF EXISTS system_performance_metrics_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.report_executions DROP CONSTRAINT IF EXISTS report_executions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_roles DROP CONSTRAINT IF EXISTS rbac_roles_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_roles DROP CONSTRAINT IF EXISTS rbac_roles_name_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_role_permissions DROP CONSTRAINT IF EXISTS rbac_role_permissions_role_id_permission_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_role_permissions DROP CONSTRAINT IF EXISTS rbac_role_permissions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_permissions DROP CONSTRAINT IF EXISTS rbac_permissions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.rbac_permissions DROP CONSTRAINT IF EXISTS rbac_permissions_key_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_versions DROP CONSTRAINT IF EXISTS project_versions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_comments DROP CONSTRAINT IF EXISTS project_comments_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.project_collaborators DROP CONSTRAINT IF EXISTS project_collaborators_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plans DROP CONSTRAINT IF EXISTS plans_slug_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.plans DROP CONSTRAINT IF EXISTS plans_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_provider_mappings DROP CONSTRAINT IF EXISTS plan_provider_mappings_provider_id_external_plan_id_external_pr;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_provider_mappings DROP CONSTRAINT IF EXISTS plan_provider_mappings_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_features DROP CONSTRAINT IF EXISTS plan_features_plan_id_feature_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_features DROP CONSTRAINT IF EXISTS plan_features_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_entitlements DROP CONSTRAINT IF EXISTS plan_entitlements_plan_id_feature_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.plan_entitlements DROP CONSTRAINT IF EXISTS plan_entitlements_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_providers DROP CONSTRAINT IF EXISTS payment_providers_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_providers DROP CONSTRAINT IF EXISTS payment_providers_name_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_methods DROP CONSTRAINT IF EXISTS payment_methods_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_customers DROP CONSTRAINT IF EXISTS payment_customers_tenant_id_provider_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_customers DROP CONSTRAINT IF EXISTS payment_customers_provider_id_external_customer_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.payment_customers DROP CONSTRAINT IF EXISTS payment_customers_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.nodes DROP CONSTRAINT IF EXISTS nodes_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_templates DROP CONSTRAINT IF EXISTS node_templates_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_ratings DROP CONSTRAINT IF EXISTS node_ratings_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_executions DROP CONSTRAINT IF EXISTS node_executions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_categories DROP CONSTRAINT IF EXISTS node_categories_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.node_categories DROP CONSTRAINT IF EXISTS node_categories_name_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.message_feedbacks DROP CONSTRAINT IF EXISTS message_feedbacks_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.marketplace_components DROP CONSTRAINT IF EXISTS marketplace_components_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms DROP CONSTRAINT IF EXISTS llms_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.knowledge_bases DROP CONSTRAINT IF EXISTS knowledge_bases_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.invoices DROP CONSTRAINT IF EXISTS invoices_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.invoices DROP CONSTRAINT IF EXISTS invoices_invoice_number_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.files DROP CONSTRAINT IF EXISTS files_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.features DROP CONSTRAINT IF EXISTS features_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.features DROP CONSTRAINT IF EXISTS features_key_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_execution_queue DROP CONSTRAINT IF EXISTS execution_queue_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.workflow_execution_metrics DROP CONSTRAINT IF EXISTS execution_metrics_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.email_verification_tokens DROP CONSTRAINT IF EXISTS email_verification_tokens_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.custom_reports DROP CONSTRAINT IF EXISTS custom_reports_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.coupons DROP CONSTRAINT IF EXISTS coupons_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.coupons DROP CONSTRAINT IF EXISTS coupons_code_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.conversion_journeys DROP CONSTRAINT IF EXISTS conversion_journeys_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations DROP CONSTRAINT IF EXISTS conversations_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.llms_conversations_turns DROP CONSTRAINT IF EXISTS conversation_llms_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contacts DROP CONSTRAINT IF EXISTS contacts_tenant_id_email_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.contacts DROP CONSTRAINT IF EXISTS contacts_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_tags DROP CONSTRAINT IF EXISTS contact_tags_tenant_id_name_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_tags DROP CONSTRAINT IF EXISTS contact_tags_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_sources DROP CONSTRAINT IF EXISTS contact_sources_tenant_id_name_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_sources DROP CONSTRAINT IF EXISTS contact_sources_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_notes DROP CONSTRAINT IF EXISTS contact_notes_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_lists DROP CONSTRAINT IF EXISTS contact_lists_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_list_memberships DROP CONSTRAINT IF EXISTS contact_list_memberships_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_list_memberships DROP CONSTRAINT IF EXISTS contact_list_memberships_list_id_contact_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_interactions DROP CONSTRAINT IF EXISTS contact_interactions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.contact_events DROP CONSTRAINT IF EXISTS contact_events_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_versions DROP CONSTRAINT IF EXISTS component_versions_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_ratings DROP CONSTRAINT IF EXISTS component_ratings_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_purchases DROP CONSTRAINT IF EXISTS component_purchases_transaction_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_purchases DROP CONSTRAINT IF EXISTS component_purchases_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_purchases DROP CONSTRAINT IF EXISTS component_purchases_license_key_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.component_downloads DROP CONSTRAINT IF EXISTS component_downloads_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaigns DROP CONSTRAINT IF EXISTS campaigns_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaign_contacts DROP CONSTRAINT IF EXISTS campaign_contacts_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.campaign_contacts DROP CONSTRAINT IF EXISTS campaign_contacts_campaign_id_contact_id_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.business_metrics DROP CONSTRAINT IF EXISTS business_metrics_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.billing_events DROP CONSTRAINT IF EXISTS billing_events_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.audit_log DROP CONSTRAINT IF EXISTS audit_log_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_reports DROP CONSTRAINT IF EXISTS analytics_reports_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_metrics DROP CONSTRAINT IF EXISTS analytics_metrics_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_exports DROP CONSTRAINT IF EXISTS analytics_exports_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_events DROP CONSTRAINT IF EXISTS analytics_events_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_dashboards DROP CONSTRAINT IF EXISTS analytics_dashboards_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.analytics_alerts DROP CONSTRAINT IF EXISTS analytics_alerts_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY synapscale_db.agents DROP CONSTRAINT IF EXISTS agents_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_usage_metrics DROP CONSTRAINT IF EXISTS agent_usage_metrics_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_usage_metrics DROP CONSTRAINT IF EXISTS agent_usage_metrics_agent_id_period_start_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_triggers DROP CONSTRAINT IF EXISTS agent_triggers_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_tools DROP CONSTRAINT IF EXISTS agent_tools_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_quotas DROP CONSTRAINT IF EXISTS agent_quotas_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_models DROP CONSTRAINT IF EXISTS agent_models_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_kbs DROP CONSTRAINT IF EXISTS agent_kbs_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_hierarchy DROP CONSTRAINT IF EXISTS agent_hierarchy_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_error_logs DROP CONSTRAINT IF EXISTS agent_error_logs_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_configurations DROP CONSTRAINT IF EXISTS agent_configurations_pkey;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_configurations DROP CONSTRAINT IF EXISTS agent_configurations_agent_id_version_num_key;
ALTER TABLE IF EXISTS ONLY synapscale_db.agent_acl DROP CONSTRAINT IF EXISTS agent_acl_pkey;
ALTER TABLE IF EXISTS synapscale_db.workspace_members ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.workflow_execution_queue ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.workflow_execution_metrics ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.template_usage ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.template_reviews ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.template_favorites ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.template_downloads ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.template_collections ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.system_performance_metrics ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.node_executions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS synapscale_db.business_metrics ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS synapscale_db.workspaces;
DROP TABLE IF EXISTS synapscale_db.workspace_projects;
DROP SEQUENCE IF EXISTS synapscale_db.workspace_members_id_seq;
DROP TABLE IF EXISTS synapscale_db.workspace_members;
DROP TABLE IF EXISTS synapscale_db.workspace_invitations;
DROP TABLE IF EXISTS synapscale_db.workspace_features;
DROP TABLE IF EXISTS synapscale_db.workspace_activities;
DROP TABLE IF EXISTS synapscale_db.workflow_templates;
DROP TABLE IF EXISTS synapscale_db.workflow_nodes;
DROP TABLE IF EXISTS synapscale_db.workflow_executions;
DROP TABLE IF EXISTS synapscale_db.workflow_connections;
DROP TABLE IF EXISTS synapscale_db.webhook_logs;
DROP TABLE IF EXISTS synapscale_db.user_variables;
DROP TABLE IF EXISTS synapscale_db.user_tenant_roles;
DROP TABLE IF EXISTS synapscale_db.user_subscriptions;
DROP TABLE IF EXISTS synapscale_db.user_insights;
DROP TABLE IF EXISTS synapscale_db.user_behavior_metrics;
DROP TABLE IF EXISTS synapscale_db.tools;
DROP TABLE IF EXISTS synapscale_db.tenant_features;
DROP SEQUENCE IF EXISTS synapscale_db.template_usage_id_seq;
DROP TABLE IF EXISTS synapscale_db.template_usage;
DROP SEQUENCE IF EXISTS synapscale_db.template_reviews_id_seq;
DROP TABLE IF EXISTS synapscale_db.template_reviews;
DROP SEQUENCE IF EXISTS synapscale_db.template_favorites_id_seq;
DROP TABLE IF EXISTS synapscale_db.template_favorites;
DROP SEQUENCE IF EXISTS synapscale_db.template_downloads_id_seq;
DROP TABLE IF EXISTS synapscale_db.template_downloads;
DROP SEQUENCE IF EXISTS synapscale_db.template_collections_id_seq;
DROP TABLE IF EXISTS synapscale_db.template_collections;
DROP TABLE IF EXISTS synapscale_db.tags;
DROP SEQUENCE IF EXISTS synapscale_db.system_performance_metrics_id_seq;
DROP TABLE IF EXISTS synapscale_db.system_performance_metrics;
DROP VIEW IF EXISTS synapscale_db.system_health;
DROP TABLE IF EXISTS synapscale_db.workflows;
DROP TABLE IF EXISTS synapscale_db.users;
DROP TABLE IF EXISTS synapscale_db.tenants;
DROP TABLE IF EXISTS synapscale_db.subscriptions;
DROP TABLE IF EXISTS synapscale_db.report_executions;
DROP TABLE IF EXISTS synapscale_db.refresh_tokens;
DROP TABLE IF EXISTS synapscale_db.rbac_roles;
DROP TABLE IF EXISTS synapscale_db.rbac_role_permissions;
DROP TABLE IF EXISTS synapscale_db.rbac_permissions;
DROP TABLE IF EXISTS synapscale_db.project_versions;
DROP TABLE IF EXISTS synapscale_db.project_comments;
DROP TABLE IF EXISTS synapscale_db.project_collaborators;
DROP TABLE IF EXISTS synapscale_db.plans;
DROP TABLE IF EXISTS synapscale_db.plan_provider_mappings;
DROP TABLE IF EXISTS synapscale_db.plan_features;
DROP TABLE IF EXISTS synapscale_db.plan_entitlements;
DROP TABLE IF EXISTS synapscale_db.payment_providers;
DROP TABLE IF EXISTS synapscale_db.payment_methods;
DROP TABLE IF EXISTS synapscale_db.payment_customers;
DROP TABLE IF EXISTS synapscale_db.password_reset_tokens;
DROP TABLE IF EXISTS synapscale_db.nodes;
DROP TABLE IF EXISTS synapscale_db.node_templates;
DROP TABLE IF EXISTS synapscale_db.node_ratings;
DROP SEQUENCE IF EXISTS synapscale_db.node_executions_id_seq;
DROP TABLE IF EXISTS synapscale_db.node_executions;
DROP TABLE IF EXISTS synapscale_db.node_categories;
DROP TABLE IF EXISTS synapscale_db.message_feedbacks;
DROP TABLE IF EXISTS synapscale_db.marketplace_components;
DROP TABLE IF EXISTS synapscale_db.llms_usage_logs;
DROP TABLE IF EXISTS synapscale_db.llms_messages;
DROP TABLE IF EXISTS synapscale_db.llms_conversations_turns;
DROP TABLE IF EXISTS synapscale_db.llms_conversations;
DROP TABLE IF EXISTS synapscale_db.llms;
DROP TABLE IF EXISTS synapscale_db.knowledge_bases;
DROP TABLE IF EXISTS synapscale_db.invoices;
DROP TABLE IF EXISTS synapscale_db.files;
DROP TABLE IF EXISTS synapscale_db.features;
DROP SEQUENCE IF EXISTS synapscale_db.execution_queue_id_seq;
DROP TABLE IF EXISTS synapscale_db.workflow_execution_queue;
DROP SEQUENCE IF EXISTS synapscale_db.execution_metrics_id_seq;
DROP TABLE IF EXISTS synapscale_db.workflow_execution_metrics;
DROP TABLE IF EXISTS synapscale_db.email_verification_tokens;
DROP TABLE IF EXISTS synapscale_db.custom_reports;
DROP TABLE IF EXISTS synapscale_db.coupons;
DROP TABLE IF EXISTS synapscale_db.conversion_journeys;
DROP TABLE IF EXISTS synapscale_db.contacts;
DROP TABLE IF EXISTS synapscale_db.contact_tags;
DROP TABLE IF EXISTS synapscale_db.contact_sources;
DROP TABLE IF EXISTS synapscale_db.contact_notes;
DROP TABLE IF EXISTS synapscale_db.contact_lists;
DROP TABLE IF EXISTS synapscale_db.contact_list_memberships;
DROP TABLE IF EXISTS synapscale_db.contact_interactions;
DROP TABLE IF EXISTS synapscale_db.contact_events;
DROP TABLE IF EXISTS synapscale_db.component_versions;
DROP TABLE IF EXISTS synapscale_db.component_ratings;
DROP TABLE IF EXISTS synapscale_db.component_purchases;
DROP TABLE IF EXISTS synapscale_db.component_downloads;
DROP TABLE IF EXISTS synapscale_db.campaigns;
DROP TABLE IF EXISTS synapscale_db.campaign_contacts;
DROP SEQUENCE IF EXISTS synapscale_db.business_metrics_id_seq;
DROP TABLE IF EXISTS synapscale_db.business_metrics;
DROP TABLE IF EXISTS synapscale_db.billing_events;
DROP TABLE IF EXISTS synapscale_db.audit_log;
DROP TABLE IF EXISTS synapscale_db.analytics_reports;
DROP TABLE IF EXISTS synapscale_db.analytics_metrics;
DROP TABLE IF EXISTS synapscale_db.analytics_exports;
DROP TABLE IF EXISTS synapscale_db.analytics_events;
DROP TABLE IF EXISTS synapscale_db.analytics_dashboards;
DROP TABLE IF EXISTS synapscale_db.analytics_alerts;
DROP TABLE IF EXISTS synapscale_db.alembic_version;
DROP TABLE IF EXISTS synapscale_db.agents;
DROP TABLE IF EXISTS synapscale_db.agent_usage_metrics;
DROP TABLE IF EXISTS synapscale_db.agent_triggers;
DROP TABLE IF EXISTS synapscale_db.agent_tools;
DROP TABLE IF EXISTS synapscale_db.agent_quotas;
DROP TABLE IF EXISTS synapscale_db.agent_models;
DROP TABLE IF EXISTS synapscale_db.agent_kbs;
DROP TABLE IF EXISTS synapscale_db.agent_hierarchy;
DROP TABLE IF EXISTS synapscale_db.agent_error_logs;
DROP TABLE IF EXISTS synapscale_db.agent_configurations;
DROP TABLE IF EXISTS synapscale_db.agent_acl;
DROP FUNCTION IF EXISTS synapscale_db.validate_workspace_project_limits();
DROP FUNCTION IF EXISTS synapscale_db.validate_workspace_member_limits();
DROP FUNCTION IF EXISTS synapscale_db.validate_workspace_limits();
DROP FUNCTION IF EXISTS synapscale_db.validate_json_references();
DROP FUNCTION IF EXISTS synapscale_db.update_timestamp();
DROP FUNCTION IF EXISTS synapscale_db.sync_tenant_from_plan();
DROP FUNCTION IF EXISTS synapscale_db.sync_storage_usage();
DROP FUNCTION IF EXISTS synapscale_db.rollback_task8();
DROP FUNCTION IF EXISTS synapscale_db.rollback_task10_json_migration();
DROP FUNCTION IF EXISTS synapscale_db.refresh_tenant_plan_sync();
DROP FUNCTION IF EXISTS synapscale_db.fn_audit();
DROP FUNCTION IF EXISTS synapscale_db.check_workspace_limits();
DROP TYPE IF EXISTS synapscale_db.workspacetype;
DROP TYPE IF EXISTS synapscale_db.trigger_type_en;
DROP TYPE IF EXISTS synapscale_db.agent_scope;
DROP SCHEMA IF EXISTS synapscale_db;
--
-- Name: synapscale_db; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA synapscale_db;


--
-- Name: agent_scope; Type: TYPE; Schema: synapscale_db; Owner: -
--

CREATE TYPE synapscale_db.agent_scope AS ENUM (
    'global',
    'tenant'
);


--
-- Name: trigger_type_en; Type: TYPE; Schema: synapscale_db; Owner: -
--

CREATE TYPE synapscale_db.trigger_type_en AS ENUM (
    'schedule',
    'event'
);


--
-- Name: workspacetype; Type: TYPE; Schema: synapscale_db; Owner: -
--

CREATE TYPE synapscale_db.workspacetype AS ENUM (
    'individual',
    'collaborative'
);


--
-- Name: check_workspace_limits(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.check_workspace_limits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    workspace_count INTEGER;
    max_workspaces_allowed INTEGER;
BEGIN
    -- Conta os workspaces existentes para o tenant
    SELECT count(*) INTO workspace_count
    FROM synapscale_db.workspaces
    WHERE tenant_id = NEW.tenant_id;

    -- Obtém o limite da tabela tenants
    SELECT max_workspaces INTO max_workspaces_allowed
    FROM synapscale_db.tenants
    WHERE id = NEW.tenant_id;

    -- Verifica se o limite foi excedido
    IF workspace_count >= max_workspaces_allowed THEN
        RAISE EXCEPTION 'Workspace limit exceeded for this tenant. Max allowed: %', max_workspaces_allowed;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: fn_audit(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.fn_audit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  INSERT INTO synapscale_db.audit_log(table_name,record_id,changed_by,operation,diffs)
    VALUES (
      TG_TABLE_NAME,
      COALESCE(NEW.id,OLD.id),
      current_setting('app.current_user',true)::UUID,
      TG_OP,
      row_to_json(COALESCE(NEW,OLD)) #- '{audit_id}'
    );
  RETURN COALESCE(NEW,OLD);
END;
$$;


--
-- Name: refresh_tenant_plan_sync(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.refresh_tenant_plan_sync() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Refresh da view materializada
    REFRESH MATERIALIZED VIEW synapscale_db.tenant_plan_sync;
    
    -- Aplicar sincronização nos tenants afetados
    UPDATE synapscale_db.tenants 
    SET 
        settings = sync.synchronized_settings,
        updated_at = NOW()
    FROM synapscale_db.tenant_plan_sync sync
    WHERE tenants.id = sync.tenant_id;
    
    RETURN NULL;
END;
$$;


--
-- Name: rollback_task10_json_migration(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.rollback_task10_json_migration() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Remover colunas adicionadas aos tenants
    ALTER TABLE synapscale_db.tenants 
    DROP COLUMN IF EXISTS theme,
    DROP COLUMN IF EXISTS default_language,
    DROP COLUMN IF EXISTS timezone,
    DROP COLUMN IF EXISTS mfa_required,
    DROP COLUMN IF EXISTS session_timeout,
    DROP COLUMN IF EXISTS ip_whitelist;
    
    -- Remover colunas adicionadas aos workspaces
    ALTER TABLE synapscale_db.workspaces 
    DROP COLUMN IF EXISTS email_notifications,
    DROP COLUMN IF EXISTS push_notifications,
    DROP COLUMN IF EXISTS api_calls_today,
    DROP COLUMN IF EXISTS api_calls_this_month,
    DROP COLUMN IF EXISTS last_api_reset_daily,
    DROP COLUMN IF EXISTS last_api_reset_monthly,
    DROP COLUMN IF EXISTS feature_usage_count;
    
    -- Restaurar dados do backup
    DELETE FROM synapscale_db.tenants;
    INSERT INTO synapscale_db.tenants SELECT * FROM synapscale_db.backup_tenants_task10;
    
    DELETE FROM synapscale_db.workspaces;
    INSERT INTO synapscale_db.workspaces SELECT * FROM synapscale_db.backup_workspaces_task10;
    
    RETURN 'Rollback realizado com sucesso - dados restaurados do backup';
END;
$$;


--
-- Name: rollback_task8(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.rollback_task8() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE NOTICE 'Iniciando rollback da Task 8...';
    
    -- Restore workspaces
    DROP TABLE IF EXISTS synapscale_db.workspaces_temp;
    ALTER TABLE synapscale_db.workspaces RENAME TO workspaces_temp;
    ALTER TABLE synapscale_db.backup_workspaces_task8 RENAME TO workspaces;
    DROP TABLE IF EXISTS synapscale_db.workspaces_temp;
    
    -- Restore tenants
    DROP TABLE IF EXISTS synapscale_db.tenants_temp;
    ALTER TABLE synapscale_db.tenants RENAME TO tenants_temp;
    ALTER TABLE synapscale_db.backup_tenants_task8 RENAME TO tenants;
    DROP TABLE IF EXISTS synapscale_db.tenants_temp;
    
    RAISE NOTICE 'Rollback concluído com sucesso';
END;
$$;


--
-- Name: sync_storage_usage(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.sync_storage_usage() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    workspace_storage_limit NUMERIC;
    total_storage_used NUMERIC;
BEGIN
    -- Calcular storage total usado por files deste workspace
    SELECT COALESCE(SUM(file_size_bytes), 0) / (1024 * 1024) -- Converter para MB
    INTO total_storage_used
    FROM synapscale_db.files
    WHERE workspace_id = COALESCE(NEW.workspace_id, OLD.workspace_id);

    -- Buscar limite do workspace
    SELECT max_storage_mb INTO workspace_storage_limit
    FROM synapscale_db.workspaces
    WHERE id = COALESCE(NEW.workspace_id, OLD.workspace_id);

    -- Verificar se excede limite
    IF workspace_storage_limit IS NOT NULL AND total_storage_used > workspace_storage_limit THEN
        RAISE EXCEPTION 'STORAGE LIMIT EXCEEDED: Uso total de storage (%.2f MB) excede limite do workspace (% MB).',
            total_storage_used, workspace_storage_limit;
    END IF;

    -- Atualizar storage_used_mb na tabela workspaces
    UPDATE synapscale_db.workspaces 
    SET storage_used_mb = total_storage_used,
        updated_at = NOW()
    WHERE id = COALESCE(NEW.workspace_id, OLD.workspace_id);

    RETURN COALESCE(NEW, OLD);
END;
$$;


--
-- Name: sync_tenant_from_plan(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.sync_tenant_from_plan() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Atualiza as colunas do tenant com base no novo plan_id
    UPDATE synapscale_db.tenants t
    SET
        max_workspaces = p.max_workspaces,
        max_members_per_workspace = p.max_members_per_workspace,
        max_storage_mb = p.max_storage_mb,
        enabled_features = (
            SELECT array_agg(f.key)
            FROM synapscale_db.plan_features pf
            JOIN synapscale_db.features f ON pf.feature_id = f.id
            WHERE pf.plan_id = NEW.plan_id AND pf.is_enabled = true
        )
    FROM
        synapscale_db.plans p
    WHERE
        t.id = NEW.tenant_id AND p.id = NEW.plan_id;

    RETURN NEW;
END;
$$;


--
-- Name: update_timestamp(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;


--
-- Name: validate_json_references(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.validate_json_references() RETURNS TABLE(table_name text, issue_type text, issue_description text, affected_records bigint)
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Verificar permissions em rbac_roles que não existem em rbac_permissions
    RETURN QUERY
    WITH role_permissions AS (
        SELECT 
            r.id as role_id,
            r.name as role_name,
            jsonb_array_elements_text(r.permissions) as permission_action
        FROM synapscale_db.rbac_roles r
        WHERE r.permissions IS NOT NULL AND r.permissions != '[]'::jsonb
    )
    SELECT 
        'rbac_roles'::text as table_name,
        'missing_permission_reference'::text as issue_type,
        'Permission "' || rp.permission_action || '" in role "' || rp.role_name || '" does not exist in rbac_permissions table'::text as issue_description,
        COUNT(*)::bigint as affected_records
    FROM role_permissions rp
    LEFT JOIN synapscale_db.rbac_permissions p ON p.action = rp.permission_action
    WHERE p.action IS NULL
    GROUP BY rp.permission_action, rp.role_name;

    -- Verificar features em plans que não existem em features (usando 'key' em vez de 'code')
    RETURN QUERY
    WITH plan_features AS (
        SELECT 
            p.id as plan_id,
            p.name as plan_name,
            jsonb_array_elements_text(p.features::jsonb) as feature_key
        FROM synapscale_db.plans p
        WHERE p.features IS NOT NULL AND p.features::jsonb != '[]'::jsonb
    )
    SELECT 
        'plans'::text as table_name,
        'missing_feature_reference'::text as issue_type,
        'Feature "' || pf.feature_key || '" in plan "' || pf.plan_name || '" does not exist in features table'::text as issue_description,
        COUNT(*)::bigint as affected_records
    FROM plan_features pf
    LEFT JOIN synapscale_db.features f ON f.key = pf.feature_key
    WHERE f.key IS NULL
    GROUP BY pf.feature_key, pf.plan_name;
END;
$$;


--
-- Name: validate_workspace_limits(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.validate_workspace_limits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    tenant_plan_data RECORD;
    workspace_count INTEGER;
    violation_message TEXT;
BEGIN
    -- Buscar dados do plano do tenant
    SELECT 
        p.name as plan_name,
        p.max_workspaces,
        p.max_storage_mb as plan_max_storage,
        p.max_members_per_workspace as plan_max_members,
        p.max_projects_per_workspace as plan_max_projects
    INTO tenant_plan_data
    FROM synapscale_db.tenants t
    JOIN synapscale_db.subscriptions s ON s.tenant_id = t.id
    JOIN synapscale_db.plans p ON p.id = s.plan_id
    WHERE t.id = COALESCE(NEW.tenant_id, OLD.tenant_id);

    -- Se não encontrar plano, permitir (evitar quebrar o sistema)
    IF NOT FOUND THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    -- ========== VALIDAÇÃO 1: LIMITE DE WORKSPACES POR TENANT ==========
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NEW.tenant_id != OLD.tenant_id) THEN
        -- Contar workspaces existentes do tenant
        SELECT COUNT(*) INTO workspace_count
        FROM synapscale_db.workspaces 
        WHERE tenant_id = NEW.tenant_id
        AND (TG_OP = 'INSERT' OR id != NEW.id);

        -- Verificar limite de workspaces (-1 = unlimited)
        IF tenant_plan_data.max_workspaces != -1 AND workspace_count >= tenant_plan_data.max_workspaces THEN
            violation_message := format(
                'LIMITE EXCEEDED: Tenant já possui %s workspaces. Limite do plano %s: %s workspaces.',
                workspace_count, tenant_plan_data.plan_name, tenant_plan_data.max_workspaces
            );
            RAISE EXCEPTION '%', violation_message;
        END IF;
    END IF;

    -- ========== VALIDAÇÃO 2: STORAGE LIMITS ==========
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Verificar storage máximo do workspace
        IF tenant_plan_data.plan_max_storage != -1 AND 
           NEW.max_storage_mb IS NOT NULL AND 
           NEW.max_storage_mb > tenant_plan_data.plan_max_storage THEN
            violation_message := format(
                'STORAGE LIMIT EXCEEDED: Workspace max_storage_mb=%s excede limite do plano %s: %s MB.',
                NEW.max_storage_mb, tenant_plan_data.plan_name, tenant_plan_data.plan_max_storage
            );
            RAISE EXCEPTION '%', violation_message;
        END IF;
    END IF;

    -- ========== VALIDAÇÃO 3: MEMBER LIMITS ==========
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Verificar membros máximos do workspace
        IF tenant_plan_data.plan_max_members != -1 AND 
           NEW.max_members IS NOT NULL AND 
           NEW.max_members > tenant_plan_data.plan_max_members THEN
            violation_message := format(
                'MEMBER LIMIT EXCEEDED: Workspace max_members=%s excede limite do plano %s: %s membros.',
                NEW.max_members, tenant_plan_data.plan_name, tenant_plan_data.plan_max_members
            );
            RAISE EXCEPTION '%', violation_message;
        END IF;
    END IF;

    -- ========== VALIDAÇÃO 4: PROJECT LIMITS ==========
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Verificar projetos máximos do workspace
        IF tenant_plan_data.plan_max_projects != -1 AND 
           NEW.max_projects IS NOT NULL AND 
           NEW.max_projects > tenant_plan_data.plan_max_projects THEN
            violation_message := format(
                'PROJECT LIMIT EXCEEDED: Workspace max_projects=%s excede limite do plano %s: %s projetos.',
                NEW.max_projects, tenant_plan_data.plan_name, tenant_plan_data.plan_max_projects
            );
            RAISE EXCEPTION '%', violation_message;
        END IF;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;


--
-- Name: validate_workspace_member_limits(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.validate_workspace_member_limits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    current_member_count INTEGER;
    workspace_max_members INTEGER;
    workspace_name VARCHAR;
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Buscar informações do workspace
        SELECT w.max_members, w.name INTO workspace_max_members, workspace_name
        FROM synapscale_db.workspaces w
        WHERE w.id = NEW.workspace_id;

        -- Contar membros atuais
        SELECT COUNT(*) INTO current_member_count
        FROM synapscale_db.workspace_members
        WHERE workspace_id = NEW.workspace_id;

        -- Verificar limite
        IF workspace_max_members IS NOT NULL AND current_member_count >= workspace_max_members THEN
            RAISE EXCEPTION 'MEMBER LIMIT EXCEEDED: Workspace "%" já possui % membros. Limite: % membros.',
                workspace_name, current_member_count, workspace_max_members;
        END IF;

        -- Atualizar contador na tabela workspaces
        UPDATE synapscale_db.workspaces 
        SET member_count = current_member_count + 1,
            updated_at = NOW()
        WHERE id = NEW.workspace_id;

    ELSIF TG_OP = 'DELETE' THEN
        -- Decrementar contador na tabela workspaces
        UPDATE synapscale_db.workspaces 
        SET member_count = GREATEST(0, member_count - 1),
            updated_at = NOW()
        WHERE id = OLD.workspace_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;


--
-- Name: validate_workspace_project_limits(); Type: FUNCTION; Schema: synapscale_db; Owner: -
--

CREATE FUNCTION synapscale_db.validate_workspace_project_limits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    current_project_count INTEGER;
    workspace_max_projects INTEGER;
    workspace_name VARCHAR;
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Buscar informações do workspace
        SELECT w.max_projects, w.name INTO workspace_max_projects, workspace_name
        FROM synapscale_db.workspaces w
        WHERE w.id = NEW.workspace_id;

        -- Contar projetos atuais
        SELECT COUNT(*) INTO current_project_count
        FROM synapscale_db.workspace_projects
        WHERE workspace_id = NEW.workspace_id;

        -- Verificar limite
        IF workspace_max_projects IS NOT NULL AND current_project_count >= workspace_max_projects THEN
            RAISE EXCEPTION 'PROJECT LIMIT EXCEEDED: Workspace "%" já possui % projetos. Limite: % projetos.',
                workspace_name, current_project_count, workspace_max_projects;
        END IF;

        -- Atualizar contador na tabela workspaces
        UPDATE synapscale_db.workspaces 
        SET project_count = current_project_count + 1,
            updated_at = NOW()
        WHERE id = NEW.workspace_id;

    ELSIF TG_OP = 'DELETE' THEN
        -- Decrementar contador na tabela workspaces
        UPDATE synapscale_db.workspaces 
        SET project_count = GREATEST(0, project_count - 1),
            updated_at = NOW()
        WHERE id = OLD.workspace_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_acl; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_acl (
    agent_id uuid NOT NULL,
    user_id uuid NOT NULL,
    can_read boolean DEFAULT true NOT NULL,
    can_write boolean DEFAULT false NOT NULL
);


--
-- Name: TABLE agent_acl; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_acl IS 'Controle de acesso: permissões de leitura/escrita por usuário.';


--
-- Name: COLUMN agent_acl.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_acl.agent_id IS 'UUID do agente.';


--
-- Name: COLUMN agent_acl.user_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_acl.user_id IS 'UUID do usuário.';


--
-- Name: COLUMN agent_acl.can_read; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_acl.can_read IS 'Permissão de leitura/interação (TRUE = permite).';


--
-- Name: COLUMN agent_acl.can_write; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_acl.can_write IS 'Permissão de modificação (TRUE = permite).';


--
-- Name: agent_configurations; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_configurations (
    config_id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid NOT NULL,
    version_num integer NOT NULL,
    params jsonb NOT NULL,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE agent_configurations; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_configurations IS 'Armazena cada versão imutável das configurações de um agente.';


--
-- Name: COLUMN agent_configurations.config_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_configurations.config_id IS 'UUID desta versão de configuração (ex: gen_random_uuid() → ''3f1e5f2a-...'' ).';


--
-- Name: COLUMN agent_configurations.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_configurations.agent_id IS 'UUID do agente ao qual esta configuração pertence.';


--
-- Name: COLUMN agent_configurations.version_num; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_configurations.version_num IS 'Número sequencial desta versão (1 = primeira, 2 = segunda, etc.).';


--
-- Name: COLUMN agent_configurations.params; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_configurations.params IS 'JSONB com todos os parâmetros dessa versão (ex: { "system_prompt": "Olá", "temperature": 0.7 }).';


--
-- Name: COLUMN agent_configurations.created_by; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_configurations.created_by IS 'UUID do usuário que criou esta versão.';


--
-- Name: COLUMN agent_configurations.created_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_configurations.created_at IS 'Timestamp de quando esta versão foi registrada.';


--
-- Name: agent_error_logs; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_error_logs (
    error_id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid NOT NULL,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    error_code text,
    payload jsonb
);


--
-- Name: TABLE agent_error_logs; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_error_logs IS 'Registros de erros ocorridos durante execução de agentes.';


--
-- Name: COLUMN agent_error_logs.error_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_error_logs.error_id IS 'UUID do log de erro.';


--
-- Name: COLUMN agent_error_logs.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_error_logs.agent_id IS 'UUID do agente que gerou o erro.';


--
-- Name: COLUMN agent_error_logs.occurred_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_error_logs.occurred_at IS 'Timestamp de quando o erro ocorreu.';


--
-- Name: COLUMN agent_error_logs.error_code; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_error_logs.error_code IS 'Código ou categoria do erro (ex: ''TIMEOUT'').';


--
-- Name: COLUMN agent_error_logs.payload; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_error_logs.payload IS 'JSONB com detalhes do erro ou stack trace.';


--
-- Name: agent_hierarchy; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_hierarchy (
    ancestor uuid NOT NULL,
    descendant uuid NOT NULL,
    depth integer NOT NULL
);


--
-- Name: TABLE agent_hierarchy; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_hierarchy IS 'Árvore de hierarquia: relações pai-filho entre agentes.';


--
-- Name: COLUMN agent_hierarchy.ancestor; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_hierarchy.ancestor IS 'UUID do agente ancestral (pai).';


--
-- Name: COLUMN agent_hierarchy.descendant; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_hierarchy.descendant IS 'UUID do agente descendente (filho).';


--
-- Name: COLUMN agent_hierarchy.depth; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_hierarchy.depth IS 'Profundidade entre ancestral e descendente (1 = filho direto).';


--
-- Name: agent_kbs; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_kbs (
    agent_id uuid NOT NULL,
    kb_id uuid NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: TABLE agent_kbs; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_kbs IS 'Associação de agentes a bases de conhecimento com parâmetros próprios.';


--
-- Name: COLUMN agent_kbs.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_kbs.agent_id IS 'UUID do agente.';


--
-- Name: COLUMN agent_kbs.kb_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_kbs.kb_id IS 'UUID da base de conhecimento.';


--
-- Name: COLUMN agent_kbs.config; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_kbs.config IS 'JSONB de parâmetros do agente para esta KB (ex: { "max_chunks": 10 }).';


--
-- Name: agent_models; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_models (
    agent_id uuid NOT NULL,
    llm_id uuid NOT NULL,
    override jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: TABLE agent_models; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_models IS 'Relaciona agentes a modelos LLM, permitindo ajustes específicos.';


--
-- Name: COLUMN agent_models.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_models.agent_id IS 'UUID do agente.';


--
-- Name: COLUMN agent_models.llm_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_models.llm_id IS 'UUID do modelo LLM associado.';


--
-- Name: COLUMN agent_models.override; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_models.override IS 'JSONB de parâmetros que sobrescrevem o padrão para este LLM (ex: { "temperature": 0.5 }).';


--
-- Name: agent_quotas; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_quotas (
    quota_id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    max_calls bigint NOT NULL,
    max_tokens bigint NOT NULL,
    period interval NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE agent_quotas; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_quotas IS 'Cotas de uso (chamadas, tokens) definidas por agente e tenant.';


--
-- Name: COLUMN agent_quotas.quota_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.quota_id IS 'UUID do registro de cota.';


--
-- Name: COLUMN agent_quotas.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.agent_id IS 'UUID do agente.';


--
-- Name: COLUMN agent_quotas.tenant_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.tenant_id IS 'UUID do tenant proprietário.';


--
-- Name: COLUMN agent_quotas.max_calls; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.max_calls IS 'Máximo de chamadas permitido no período.';


--
-- Name: COLUMN agent_quotas.max_tokens; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.max_tokens IS 'Máximo de tokens permitido no período.';


--
-- Name: COLUMN agent_quotas.period; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.period IS 'Intervalo de reset da cota (ex: INTERVAL ''1 day'').';


--
-- Name: COLUMN agent_quotas.created_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_quotas.created_at IS 'Timestamp de criação da cota.';


--
-- Name: agent_tools; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_tools (
    agent_id uuid NOT NULL,
    tool_id uuid NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: TABLE agent_tools; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_tools IS 'Define quais ferramentas cada agente pode usar e seus parâmetros específicos.';


--
-- Name: COLUMN agent_tools.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_tools.agent_id IS 'UUID do agente.';


--
-- Name: COLUMN agent_tools.tool_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_tools.tool_id IS 'UUID da ferramenta associada.';


--
-- Name: COLUMN agent_tools.config; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_tools.config IS 'JSONB de overrides do agente para esta ferramenta (ex: { "max_results": 5 }).';


--
-- Name: agent_triggers; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_triggers (
    trigger_id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid NOT NULL,
    trigger_type synapscale_db.trigger_type_en NOT NULL,
    cron_expr text,
    event_name text,
    active boolean DEFAULT true NOT NULL,
    last_run_at timestamp with time zone,
    CONSTRAINT agent_triggers_check CHECK (((trigger_type <> 'schedule'::synapscale_db.trigger_type_en) OR (cron_expr ~ '^([0-5]?\d\s+){4}[0-5]?\d$'::text)))
);


--
-- Name: TABLE agent_triggers; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_triggers IS 'Gatilhos (cron ou eventos) para execução automática de agentes.';


--
-- Name: COLUMN agent_triggers.trigger_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.trigger_id IS 'UUID do gatilho (ex: gen_random_uuid() → ''ffff1111-...'' ).';


--
-- Name: COLUMN agent_triggers.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.agent_id IS 'UUID do agente que será acionado.';


--
-- Name: COLUMN agent_triggers.trigger_type; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.trigger_type IS 'Tipo do gatilho: ''schedule'' (cron) ou ''event'' (evento customizado).';


--
-- Name: COLUMN agent_triggers.cron_expr; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.cron_expr IS 'Expressão cron para agendamentos (ex: ''0 9 * * *'' para 9h diárias).';


--
-- Name: COLUMN agent_triggers.event_name; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.event_name IS 'Nome do evento que dispara o agente (ex: ''on_new_user_signup'').';


--
-- Name: COLUMN agent_triggers.active; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.active IS 'Flag se o gatilho está habilitado (TRUE = ativo).';


--
-- Name: COLUMN agent_triggers.last_run_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_triggers.last_run_at IS 'Timestamp da última execução gerada por este gatilho.';


--
-- Name: agent_usage_metrics; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agent_usage_metrics (
    metric_id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid NOT NULL,
    period_start timestamp with time zone NOT NULL,
    period_end timestamp with time zone NOT NULL,
    calls_count bigint NOT NULL,
    tokens_used bigint NOT NULL,
    cost_est numeric(12,4) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE agent_usage_metrics; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.agent_usage_metrics IS 'Métricas agregadas de uso (chamadas, tokens, custo) por agente.';


--
-- Name: COLUMN agent_usage_metrics.metric_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.metric_id IS 'UUID deste registro de métricas.';


--
-- Name: COLUMN agent_usage_metrics.agent_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.agent_id IS 'UUID do agente monitorado.';


--
-- Name: COLUMN agent_usage_metrics.period_start; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.period_start IS 'Início do intervalo de métricas (ex: ''2025-07-01T00:00:00Z'').';


--
-- Name: COLUMN agent_usage_metrics.period_end; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.period_end IS 'Fim do intervalo de métricas (ex: ''2025-07-02T00:00:00Z'').';


--
-- Name: COLUMN agent_usage_metrics.calls_count; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.calls_count IS 'Quantidade total de chamadas ao LLM neste período.';


--
-- Name: COLUMN agent_usage_metrics.tokens_used; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.tokens_used IS 'Total de tokens consumidos neste período.';


--
-- Name: COLUMN agent_usage_metrics.cost_est; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.cost_est IS 'Custo estimado em USD (ex: 0.0234).';


--
-- Name: COLUMN agent_usage_metrics.created_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agent_usage_metrics.created_at IS 'Timestamp de quando a métrica foi registrada.';


--
-- Name: agents; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.agents (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    workspace_id uuid,
    tenant_id uuid NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    priority integer DEFAULT 1,
    version character varying(20) DEFAULT '1.0.0'::character varying,
    environment character varying(20) DEFAULT 'development'::character varying,
    current_config uuid,
    CONSTRAINT agents_environment_check CHECK (((environment)::text = ANY ((ARRAY['development'::character varying, 'staging'::character varying, 'production'::character varying])::text[]))),
    CONSTRAINT agents_priority_check CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT agents_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'draft'::character varying, 'archived'::character varying, 'error'::character varying])::text[])))
);


--
-- Name: COLUMN agents.current_config; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.agents.current_config IS 'UUID da configuração ativa do agente, referenciando agent_configurations.config_id (ex: ''3f1e5f2a-...'' ).';


--
-- Name: alembic_version; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: analytics_alerts; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.analytics_alerts (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    condition jsonb NOT NULL,
    notification_config jsonb NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    owner_id uuid NOT NULL,
    last_triggered_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid
);


--
-- Name: analytics_dashboards; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.analytics_dashboards (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    icon character varying(50),
    color character varying(7),
    user_id uuid NOT NULL,
    layout jsonb NOT NULL,
    widgets jsonb NOT NULL,
    filters jsonb,
    auto_refresh boolean NOT NULL,
    refresh_interval integer,
    is_public boolean DEFAULT false NOT NULL,
    shared_with jsonb,
    is_default boolean NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    last_viewed_at timestamp with time zone,
    workspace_id uuid,
    tenant_id uuid
);


--
-- Name: analytics_events; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.analytics_events (
    id uuid NOT NULL,
    event_id character varying(36) NOT NULL,
    event_type character varying(100) NOT NULL,
    category character varying(50) NOT NULL,
    action character varying(100) NOT NULL,
    label character varying(200),
    user_id uuid,
    session_id character varying(255),
    anonymous_id character varying(100),
    ip_address text,
    user_agent text,
    referrer character varying(1000),
    page_url character varying(1000),
    properties jsonb DEFAULT '{}'::jsonb NOT NULL,
    value double precision,
    workspace_id uuid,
    project_id uuid NOT NULL,
    workflow_id uuid,
    country character varying(2),
    region character varying(100),
    city character varying(100),
    timezone character varying(50),
    device_type character varying(20),
    os character varying(50),
    browser character varying(50),
    screen_resolution character varying(20),
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: analytics_exports; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.analytics_exports (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    export_type character varying(50) NOT NULL,
    query jsonb NOT NULL,
    file_path character varying(500),
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    owner_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: analytics_metrics; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.analytics_metrics (
    id uuid NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_value numeric(15,4) NOT NULL,
    dimensions jsonb DEFAULT '{}'::jsonb NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: analytics_reports; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.analytics_reports (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    query jsonb NOT NULL,
    schedule character varying(50),
    owner_id uuid NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid
);


--
-- Name: audit_log; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.audit_log (
    audit_id uuid DEFAULT gen_random_uuid() NOT NULL,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    changed_by uuid,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    operation text NOT NULL,
    diffs jsonb,
    CONSTRAINT audit_log_operation_check CHECK ((operation = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text])))
);


--
-- Name: TABLE audit_log; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.audit_log IS 'Trilha de auditoria de INSERT/UPDATE/DELETE em tabelas críticas.';


--
-- Name: COLUMN audit_log.audit_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.audit_id IS 'UUID do registro de auditoria.';


--
-- Name: COLUMN audit_log.table_name; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.table_name IS 'Nome da tabela modificada.';


--
-- Name: COLUMN audit_log.record_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.record_id IS 'UUID do registro afetado.';


--
-- Name: COLUMN audit_log.changed_by; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.changed_by IS 'UUID do usuário que realizou a mudança.';


--
-- Name: COLUMN audit_log.changed_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.changed_at IS 'Timestamp de quando a mudança ocorreu.';


--
-- Name: COLUMN audit_log.operation; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.operation IS 'Tipo de operação aplicada: INSERT, UPDATE ou DELETE.';


--
-- Name: COLUMN audit_log.diffs; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.audit_log.diffs IS 'JSONB com diferenças antes/depois do registro, sem incluir audit_id.';


--
-- Name: billing_events; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.billing_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    workspace_id uuid,
    event_type character varying(50) NOT NULL,
    amount_usd double precision NOT NULL,
    description text,
    related_usage_log_id uuid,
    related_message_id uuid,
    invoice_id character varying(100),
    payment_provider character varying(50),
    payment_transaction_id character varying(100),
    billing_metadata jsonb,
    status character varying(20) DEFAULT 'pending'::character varying,
    processed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: business_metrics; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.business_metrics (
    id integer NOT NULL,
    date timestamp with time zone NOT NULL,
    period_type character varying(20) NOT NULL,
    total_users integer NOT NULL,
    new_users integer NOT NULL,
    active_users integer NOT NULL,
    churned_users integer NOT NULL,
    total_sessions integer NOT NULL,
    avg_session_duration double precision NOT NULL,
    total_page_views integer NOT NULL,
    bounce_rate double precision NOT NULL,
    workflows_created integer NOT NULL,
    workflows_executed integer NOT NULL,
    components_published integer NOT NULL,
    components_downloaded integer NOT NULL,
    workspaces_created integer NOT NULL,
    teams_formed integer NOT NULL,
    collaborative_sessions integer NOT NULL,
    total_revenue double precision NOT NULL,
    recurring_revenue double precision NOT NULL,
    marketplace_revenue double precision NOT NULL,
    avg_revenue_per_user double precision NOT NULL,
    error_rate double precision NOT NULL,
    avg_response_time double precision NOT NULL,
    uptime_percentage double precision NOT NULL,
    customer_satisfaction double precision NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    tenant_id uuid
);


--
-- Name: business_metrics_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.business_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: business_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.business_metrics_id_seq OWNED BY synapscale_db.business_metrics.id;


--
-- Name: campaign_contacts; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.campaign_contacts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    campaign_id uuid NOT NULL,
    contact_id uuid NOT NULL,
    status character varying(50) DEFAULT 'pending'::character varying,
    sent_at timestamp with time zone,
    opened_at timestamp with time zone,
    clicked_at timestamp with time zone,
    bounced_at timestamp with time zone,
    unsubscribed_at timestamp with time zone,
    error_message text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: campaigns; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.campaigns (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    type character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'draft'::character varying,
    subject character varying(255),
    content text,
    template_id uuid,
    scheduled_at timestamp with time zone,
    sent_at timestamp with time zone,
    stats jsonb DEFAULT '{}'::jsonb,
    settings jsonb DEFAULT '{}'::jsonb,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: component_downloads; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.component_downloads (
    id uuid NOT NULL,
    component_id uuid NOT NULL,
    user_id uuid NOT NULL,
    version character varying(20) NOT NULL,
    download_type character varying(20) NOT NULL,
    ip_address character varying(45),
    user_agent character varying(500),
    referrer character varying(500),
    status character varying(20) NOT NULL,
    file_size integer,
    created_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: component_purchases; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.component_purchases (
    id uuid NOT NULL,
    component_id uuid NOT NULL,
    user_id uuid NOT NULL,
    amount double precision NOT NULL,
    currency character varying(3) NOT NULL,
    payment_method character varying(50),
    transaction_id character varying(100) NOT NULL,
    payment_provider character varying(50),
    provider_transaction_id character varying(100),
    status character varying(20) NOT NULL,
    license_key character varying(100),
    license_expires_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    refunded_at timestamp with time zone,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: component_ratings; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.component_ratings (
    id uuid NOT NULL,
    component_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rating integer NOT NULL,
    title character varying(200),
    review text,
    ease_of_use integer,
    documentation_quality integer,
    performance integer,
    reliability integer,
    support_quality integer,
    version_used character varying(20),
    use_case character varying(100),
    experience_level character varying(20),
    helpful_count integer NOT NULL,
    reported_count integer NOT NULL,
    is_verified_purchase boolean NOT NULL,
    is_featured boolean NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    tenant_id uuid
);


--
-- Name: component_versions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.component_versions (
    id uuid NOT NULL,
    component_id uuid NOT NULL,
    version character varying(20) NOT NULL,
    is_latest boolean NOT NULL,
    is_stable boolean NOT NULL,
    changelog text,
    breaking_changes text,
    migration_guide text,
    component_data jsonb NOT NULL,
    file_size integer,
    min_platform_version character varying(20),
    max_platform_version character varying(20),
    dependencies jsonb,
    download_count integer NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deprecated_at timestamp with time zone,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: contact_events; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    contact_id uuid NOT NULL,
    event_type character varying(100) NOT NULL,
    event_data jsonb DEFAULT '{}'::jsonb,
    occurred_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: contact_interactions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_interactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    contact_id uuid NOT NULL,
    user_id uuid,
    type character varying(50) NOT NULL,
    channel character varying(50),
    subject character varying(255),
    content text,
    direction character varying(20) DEFAULT 'outbound'::character varying,
    status character varying(50) DEFAULT 'completed'::character varying,
    scheduled_at timestamp with time zone,
    completed_at timestamp with time zone,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: contact_list_memberships; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_list_memberships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    list_id uuid NOT NULL,
    contact_id uuid NOT NULL,
    added_by uuid,
    added_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(50) DEFAULT 'active'::character varying,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: contact_lists; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_lists (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    type character varying(50) DEFAULT 'static'::character varying,
    filters jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: contact_notes; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_notes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    contact_id uuid NOT NULL,
    user_id uuid NOT NULL,
    content text NOT NULL,
    type character varying(50) DEFAULT 'note'::character varying,
    is_private boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: contact_sources; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_sources (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    integration_type character varying(50),
    config jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: contact_tags; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contact_tags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    color character varying(7) DEFAULT '#6B7280'::character varying,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: contacts; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.contacts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    phone character varying(50),
    company character varying(255),
    job_title character varying(255),
    status character varying(50) DEFAULT 'active'::character varying,
    lead_score integer DEFAULT 0,
    source_id uuid,
    custom_fields jsonb DEFAULT '{}'::jsonb,
    tags text[],
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: conversion_journeys; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.conversion_journeys (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    contact_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    journey_name character varying(255),
    current_stage character varying(100),
    stages_completed jsonb DEFAULT '[]'::jsonb,
    conversion_probability numeric(5,2),
    last_interaction_at timestamp with time zone,
    converted_at timestamp with time zone,
    conversion_value numeric(12,2),
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: coupons; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.coupons (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(100) NOT NULL,
    name character varying(255),
    description text,
    type character varying(50) DEFAULT 'percentage'::character varying NOT NULL,
    value numeric(10,2) NOT NULL,
    currency character varying(3) DEFAULT 'USD'::character varying,
    max_uses integer,
    used_count integer DEFAULT 0,
    min_amount numeric(10,2),
    max_discount numeric(10,2),
    valid_from timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    valid_until timestamp with time zone,
    is_active boolean DEFAULT true,
    is_stackable boolean DEFAULT false,
    applicable_plans jsonb DEFAULT '[]'::jsonb,
    restrictions jsonb DEFAULT '{}'::jsonb,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: custom_reports; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.custom_reports (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    workspace_id uuid,
    name character varying(200) NOT NULL,
    description text,
    category character varying(50),
    query_config jsonb NOT NULL,
    visualization_config jsonb,
    filters jsonb,
    is_scheduled boolean NOT NULL,
    schedule_config jsonb,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    is_public boolean NOT NULL,
    shared_with jsonb,
    cached_data jsonb,
    cache_expires_at timestamp with time zone,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    tenant_id uuid
);


--
-- Name: email_verification_tokens; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.email_verification_tokens (
    id uuid NOT NULL,
    token character varying(500) NOT NULL,
    user_id uuid NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_used boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: workflow_execution_metrics; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflow_execution_metrics (
    id integer NOT NULL,
    workflow_execution_id uuid NOT NULL,
    node_execution_id integer,
    metric_type character varying(100) NOT NULL,
    metric_name character varying(255) NOT NULL,
    value_numeric integer,
    value_float character varying(50),
    value_text text,
    value_json jsonb,
    context character varying(255),
    tags jsonb,
    measured_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: execution_metrics_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.execution_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: execution_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.execution_metrics_id_seq OWNED BY synapscale_db.workflow_execution_metrics.id;


--
-- Name: workflow_execution_queue; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflow_execution_queue (
    id integer NOT NULL,
    queue_id character varying(36),
    workflow_execution_id uuid NOT NULL,
    user_id uuid NOT NULL,
    priority integer,
    scheduled_at timestamp with time zone,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    status character varying(50),
    worker_id character varying(100),
    max_execution_time integer,
    retry_count integer,
    max_retries integer,
    meta_data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: execution_queue_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.execution_queue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: execution_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.execution_queue_id_seq OWNED BY synapscale_db.workflow_execution_queue.id;


--
-- Name: features; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.features (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    key character varying(100) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    category character varying(100),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: files; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.files (
    id uuid NOT NULL,
    filename character varying(255) NOT NULL,
    original_name character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_size integer NOT NULL,
    mime_type character varying(100) NOT NULL,
    category character varying(50) NOT NULL,
    is_public boolean DEFAULT false NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tags jsonb,
    description text,
    tenant_id uuid,
    status character varying(20) DEFAULT 'active'::character varying,
    scan_status character varying(20) DEFAULT 'pending'::character varying,
    access_count integer DEFAULT 0,
    last_accessed_at timestamp with time zone,
    CONSTRAINT files_scan_status_check CHECK (((scan_status)::text = ANY ((ARRAY['pending'::character varying, 'scanning'::character varying, 'clean'::character varying, 'infected'::character varying, 'quarantined'::character varying])::text[]))),
    CONSTRAINT files_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying, 'archived'::character varying, 'deleted'::character varying])::text[])))
);


--
-- Name: invoices; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.invoices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    subscription_id uuid,
    invoice_number character varying(100) NOT NULL,
    status character varying(50) DEFAULT 'draft'::character varying NOT NULL,
    currency character varying(3) DEFAULT 'USD'::character varying NOT NULL,
    subtotal numeric(12,2) DEFAULT 0 NOT NULL,
    tax_amount numeric(12,2) DEFAULT 0 NOT NULL,
    discount_amount numeric(12,2) DEFAULT 0 NOT NULL,
    total_amount numeric(12,2) DEFAULT 0 NOT NULL,
    due_date date,
    paid_at timestamp with time zone,
    items jsonb DEFAULT '[]'::jsonb,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: knowledge_bases; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.knowledge_bases (
    kb_id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    content jsonb NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE knowledge_bases; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.knowledge_bases IS 'Cadastro de bases de conhecimento para consulta pelos agentes.';


--
-- Name: COLUMN knowledge_bases.kb_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.knowledge_bases.kb_id IS 'UUID da base de conhecimento (ex: gen_random_uuid() → ''1a2b3c4d-...'' ).';


--
-- Name: COLUMN knowledge_bases.title; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.knowledge_bases.title IS 'Título descritivo da base (ex: ''Documentação de Produto'').';


--
-- Name: COLUMN knowledge_bases.content; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.knowledge_bases.content IS 'JSONB ou ponteiro para o conteúdo (ex: { "source": "s3://bucket/doc.pdf" }).';


--
-- Name: COLUMN knowledge_bases.tenant_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.knowledge_bases.tenant_id IS 'UUID do tenant se a KB for exclusiva (NULL = global).';


--
-- Name: COLUMN knowledge_bases.updated_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.knowledge_bases.updated_at IS 'Timestamp da última atualização da base.';


--
-- Name: llms; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.llms (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    provider character varying(50) NOT NULL,
    model_version character varying(50),
    max_tokens_supported integer,
    supports_function_calling boolean DEFAULT false,
    supports_vision boolean DEFAULT false,
    supports_streaming boolean DEFAULT true,
    context_window integer,
    is_active boolean DEFAULT true,
    llm_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    status character varying(20) DEFAULT 'active'::character varying,
    health_status character varying(20) DEFAULT 'unknown'::character varying,
    response_time_avg_ms integer DEFAULT 0,
    availability_percentage numeric(5,2) DEFAULT 99.9,
    cost_per_token_input double precision,
    cost_per_token_output double precision,
    CONSTRAINT llms_health_status_check CHECK (((health_status)::text = ANY ((ARRAY['healthy'::character varying, 'degraded'::character varying, 'unhealthy'::character varying, 'unknown'::character varying])::text[]))),
    CONSTRAINT llms_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'maintenance'::character varying, 'deprecated'::character varying])::text[])))
);


--
-- Name: llms_conversations; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.llms_conversations (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    agent_id uuid,
    workspace_id uuid,
    title character varying(255),
    status character varying(50),
    message_count integer,
    total_tokens_used integer,
    context jsonb,
    settings jsonb,
    last_message_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: llms_conversations_turns; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.llms_conversations_turns (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    conversation_id uuid NOT NULL,
    llm_id uuid NOT NULL,
    first_used_at timestamp with time zone DEFAULT now() NOT NULL,
    last_used_at timestamp with time zone DEFAULT now() NOT NULL,
    message_count integer DEFAULT 0,
    total_input_tokens integer DEFAULT 0,
    total_output_tokens integer DEFAULT 0,
    total_cost_usd double precision DEFAULT 0.0,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: llms_messages; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.llms_messages (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    attachments jsonb,
    model_used character varying(100),
    model_provider character varying(50),
    tokens_used integer,
    processing_time_ms integer,
    temperature double precision,
    max_tokens integer,
    status character varying(50),
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: llms_usage_logs; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.llms_usage_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    message_id uuid NOT NULL,
    user_id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    llm_id uuid NOT NULL,
    workspace_id uuid,
    input_tokens integer DEFAULT 0 NOT NULL,
    output_tokens integer DEFAULT 0 NOT NULL,
    total_tokens integer DEFAULT 0 NOT NULL,
    cost_usd double precision DEFAULT 0.0 NOT NULL,
    latency_ms integer,
    api_status_code integer,
    api_request_payload jsonb,
    api_response_metadata jsonb,
    user_api_key_used boolean DEFAULT false,
    model_settings jsonb,
    error_message text,
    status character varying(20) DEFAULT 'success'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: marketplace_components; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.marketplace_components (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    category character varying(100) NOT NULL,
    component_type character varying(50) NOT NULL,
    tags text[],
    price numeric(10,2) DEFAULT 0.00 NOT NULL,
    is_free boolean DEFAULT true NOT NULL,
    author_id uuid NOT NULL,
    version character varying(50) DEFAULT '1.0.0'::character varying NOT NULL,
    content text,
    component_metadata text,
    downloads_count integer DEFAULT 0 NOT NULL,
    rating_average double precision NOT NULL,
    rating_count integer NOT NULL,
    is_featured boolean DEFAULT false NOT NULL,
    is_approved boolean DEFAULT false NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    title character varying(200) NOT NULL,
    short_description character varying(500),
    subcategory character varying(50),
    organization character varying(100),
    configuration_schema jsonb,
    dependencies jsonb,
    compatibility jsonb,
    documentation text,
    readme text,
    changelog text,
    examples jsonb,
    icon_url character varying(500),
    screenshots jsonb,
    demo_url character varying(500),
    video_url character varying(500),
    currency character varying(3),
    license_type character varying(50),
    install_count integer NOT NULL,
    view_count integer NOT NULL,
    like_count integer NOT NULL,
    is_verified boolean NOT NULL,
    moderation_notes text,
    keywords jsonb,
    search_vector text,
    popularity_score double precision NOT NULL,
    published_at timestamp with time zone,
    last_download_at timestamp with time zone,
    tenant_id uuid
);


--
-- Name: message_feedbacks; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.message_feedbacks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    message_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rating_type character varying(20) NOT NULL,
    rating_value integer,
    feedback_text text,
    feedback_category character varying(50),
    improvement_suggestions text,
    is_public boolean DEFAULT false,
    feedback_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid
);


--
-- Name: node_categories; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.node_categories (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    icon character varying(10),
    color character varying(7),
    parent_id uuid,
    sort_order integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: node_executions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.node_executions (
    id integer NOT NULL,
    execution_id character varying(36),
    workflow_execution_id uuid NOT NULL,
    node_id uuid NOT NULL,
    node_key character varying(255) NOT NULL,
    node_type character varying(100) NOT NULL,
    node_name character varying(255),
    execution_order integer NOT NULL,
    input_data jsonb,
    output_data jsonb,
    config_data jsonb,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    timeout_at timestamp with time zone,
    duration_ms integer,
    execution_log text,
    error_message text,
    error_details jsonb,
    debug_info jsonb,
    retry_count integer,
    max_retries integer,
    retry_delay integer,
    dependencies jsonb,
    dependents jsonb,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: node_executions_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.node_executions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: node_executions_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.node_executions_id_seq OWNED BY synapscale_db.node_executions.id;


--
-- Name: node_ratings; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.node_ratings (
    id uuid NOT NULL,
    node_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rating integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: node_templates; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.node_templates (
    id uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    category character varying(100),
    code_template text NOT NULL,
    input_schema jsonb NOT NULL,
    output_schema jsonb NOT NULL,
    parameters_schema jsonb,
    icon character varying(10),
    color character varying(7),
    documentation text,
    examples jsonb,
    is_system boolean,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: nodes; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.nodes (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    category character varying(100) NOT NULL,
    description text,
    version character varying(50) DEFAULT '1.0.0'::character varying NOT NULL,
    definition jsonb NOT NULL,
    is_public boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    code_template text NOT NULL,
    input_schema jsonb NOT NULL,
    output_schema jsonb NOT NULL,
    parameters_schema jsonb,
    icon character varying(10),
    color character varying(7),
    documentation text,
    examples jsonb,
    downloads_count integer,
    usage_count integer,
    rating_average integer,
    rating_count integer,
    user_id uuid NOT NULL,
    workspace_id uuid,
    tenant_id uuid,
    status character varying(20) DEFAULT 'active'::character varying,
    timeout_seconds integer DEFAULT 300,
    retry_count integer DEFAULT 3
);


--
-- Name: password_reset_tokens; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.password_reset_tokens (
    id uuid NOT NULL,
    token character varying(500) NOT NULL,
    user_id uuid NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_used boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: payment_customers; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.payment_customers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    external_customer_id character varying(255) NOT NULL,
    customer_data jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: payment_methods; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.payment_methods (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    customer_id uuid NOT NULL,
    external_method_id character varying(255) NOT NULL,
    type character varying(50) NOT NULL,
    last4 character varying(4),
    brand character varying(50),
    exp_month integer,
    exp_year integer,
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: payment_providers; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.payment_providers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(255) NOT NULL,
    is_active boolean DEFAULT true,
    config jsonb DEFAULT '{}'::jsonb,
    webhook_secret character varying(255),
    api_version character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: plan_entitlements; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.plan_entitlements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_id uuid NOT NULL,
    feature_id uuid NOT NULL,
    limit_value integer,
    is_unlimited boolean DEFAULT false,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: plan_features; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.plan_features (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_id uuid NOT NULL,
    feature_id uuid NOT NULL,
    is_enabled boolean DEFAULT true,
    config jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: plan_provider_mappings; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.plan_provider_mappings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    external_plan_id character varying(255) NOT NULL,
    external_price_id character varying(255),
    is_active boolean DEFAULT true,
    config jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: plans; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.plans (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(50) NOT NULL,
    description text,
    price_monthly double precision DEFAULT 0.0 NOT NULL,
    price_yearly double precision DEFAULT 0.0 NOT NULL,
    max_workspaces integer DEFAULT 1 NOT NULL,
    max_members_per_workspace integer DEFAULT 1 NOT NULL,
    max_projects_per_workspace integer DEFAULT 10 NOT NULL,
    max_storage_mb integer DEFAULT 100 NOT NULL,
    max_executions_per_month integer DEFAULT 100 NOT NULL,
    allow_collaborative_workspaces boolean DEFAULT false NOT NULL,
    allow_custom_domains boolean DEFAULT false NOT NULL,
    allow_api_access boolean DEFAULT false NOT NULL,
    allow_advanced_analytics boolean DEFAULT false NOT NULL,
    allow_priority_support boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_public boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    version character varying(20) DEFAULT '1.0.0'::character varying,
    sort_order integer DEFAULT 0,
    CONSTRAINT plans_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'deprecated'::character varying, 'coming_soon'::character varying])::text[])))
);


--
-- Name: project_collaborators; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.project_collaborators (
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    user_id uuid NOT NULL,
    can_edit boolean NOT NULL,
    can_comment boolean NOT NULL,
    can_share boolean NOT NULL,
    can_delete boolean NOT NULL,
    is_online boolean NOT NULL,
    current_cursor_position jsonb,
    last_edit_at timestamp with time zone,
    added_at timestamp with time zone NOT NULL,
    last_seen_at timestamp with time zone NOT NULL,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: project_comments; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.project_comments (
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    user_id uuid NOT NULL,
    parent_id uuid,
    content text NOT NULL,
    content_type character varying(20) NOT NULL,
    node_id character varying(36),
    position_x double precision,
    position_y double precision,
    is_resolved boolean NOT NULL,
    is_edited boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    resolved_at timestamp with time zone,
    tenant_id uuid
);


--
-- Name: project_versions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.project_versions (
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    user_id uuid NOT NULL,
    version_number integer NOT NULL,
    version_name character varying(100),
    description text,
    workflow_data jsonb NOT NULL,
    changes_summary jsonb,
    file_size integer,
    checksum character varying(64),
    is_major boolean NOT NULL,
    is_auto_save boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: rbac_permissions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.rbac_permissions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    key character varying(100) NOT NULL,
    description text,
    category character varying(100),
    resource character varying(100),
    action character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: rbac_role_permissions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.rbac_role_permissions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    role_id uuid NOT NULL,
    permission_id uuid NOT NULL,
    granted boolean DEFAULT true,
    conditions jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: rbac_roles; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.rbac_roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_system boolean DEFAULT false,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: refresh_tokens; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.refresh_tokens (
    id uuid NOT NULL,
    token character varying(500) NOT NULL,
    user_id uuid NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_revoked boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: report_executions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.report_executions (
    id uuid NOT NULL,
    report_id uuid NOT NULL,
    user_id uuid,
    execution_type character varying(20) NOT NULL,
    parameters json,
    status character varying(20) NOT NULL,
    result_data json,
    error_message text,
    execution_time_ms integer,
    rows_processed integer,
    data_size_bytes integer,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: subscriptions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.subscriptions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    plan_id uuid NOT NULL,
    provider_id uuid,
    external_subscription_id character varying(255),
    status character varying(50) DEFAULT 'active'::character varying NOT NULL,
    current_period_start timestamp with time zone,
    current_period_end timestamp with time zone,
    trial_start timestamp with time zone,
    trial_end timestamp with time zone,
    cancel_at_period_end boolean DEFAULT false,
    canceled_at timestamp with time zone,
    ended_at timestamp with time zone,
    payment_method_id uuid,
    coupon_id uuid,
    quantity integer DEFAULT 1,
    discount_amount numeric(10,2) DEFAULT 0,
    tax_percent numeric(5,2) DEFAULT 0,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tenants; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.tenants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    domain character varying(255),
    status character varying(50) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    plan_id uuid NOT NULL,
    theme character varying(20) DEFAULT 'light'::character varying,
    default_language character varying(10) DEFAULT 'en'::character varying,
    timezone character varying(50) DEFAULT 'UTC'::character varying,
    mfa_required boolean DEFAULT false,
    session_timeout integer DEFAULT 3600,
    ip_whitelist jsonb DEFAULT '[]'::jsonb,
    max_storage_mb integer,
    max_workspaces integer,
    max_api_calls_per_day integer,
    max_members_per_workspace integer,
    enabled_features text[]
);


--
-- Name: users; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(200) NOT NULL,
    is_active boolean DEFAULT true,
    is_verified boolean DEFAULT false,
    is_superuser boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    status character varying(20) DEFAULT 'active'::character varying,
    metadata jsonb DEFAULT '{}'::jsonb,
    last_login_at timestamp with time zone,
    login_count integer DEFAULT 0,
    failed_login_attempts integer DEFAULT 0,
    account_locked_until timestamp with time zone,
    tenant_id uuid,
    profile_image_url character varying(500),
    bio character varying(1000),
    CONSTRAINT users_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'suspended'::character varying, 'pending_verification'::character varying, 'deleted'::character varying])::text[])))
);


--
-- Name: workflows; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflows (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    definition jsonb NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    user_id uuid NOT NULL,
    workspace_id uuid,
    is_public boolean DEFAULT false,
    category character varying(100),
    tags jsonb,
    version character varying(20),
    thumbnail_url character varying(500),
    downloads_count integer,
    rating_average integer,
    rating_count integer,
    execution_count integer,
    last_executed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid NOT NULL,
    status character varying(20) DEFAULT 'draft'::character varying,
    priority integer DEFAULT 1,
    timeout_seconds integer DEFAULT 3600,
    retry_count integer DEFAULT 3,
    CONSTRAINT check_workflow_definition_structure CHECK (((definition ? 'nodes'::text) AND (definition ? 'connections'::text) AND (jsonb_typeof((definition -> 'nodes'::text)) = 'array'::text) AND (jsonb_typeof((definition -> 'connections'::text)) = 'array'::text))),
    CONSTRAINT workflows_priority_check CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT workflows_status_check CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'active'::character varying, 'paused'::character varying, 'completed'::character varying, 'failed'::character varying, 'archived'::character varying])::text[])))
);


--
-- Name: system_health; Type: VIEW; Schema: synapscale_db; Owner: -
--

CREATE VIEW synapscale_db.system_health AS
 SELECT 'database'::text AS component,
    'healthy'::text AS status,
    now() AS last_check,
    json_build_object('total_tenants', ( SELECT count(*) AS count
           FROM synapscale_db.tenants), 'active_tenants', ( SELECT count(*) AS count
           FROM synapscale_db.tenants
          WHERE ((tenants.status)::text = 'active'::text)), 'total_users', ( SELECT count(*) AS count
           FROM synapscale_db.users), 'active_users', ( SELECT count(*) AS count
           FROM synapscale_db.users
          WHERE (users.is_active = true)), 'total_workflows', ( SELECT count(*) AS count
           FROM synapscale_db.workflows), 'active_workflows', ( SELECT count(*) AS count
           FROM synapscale_db.workflows
          WHERE (workflows.is_active = true)), 'total_conversations', ( SELECT count(*) AS count
           FROM synapscale_db.llms_conversations), 'total_messages', ( SELECT count(*) AS count
           FROM synapscale_db.llms_messages)) AS metrics;


--
-- Name: system_performance_metrics; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.system_performance_metrics (
    id integer NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_type character varying(20) NOT NULL,
    service character varying(50) NOT NULL,
    environment character varying(20) NOT NULL,
    value double precision NOT NULL,
    unit character varying(20),
    tags jsonb,
    "timestamp" timestamp with time zone NOT NULL,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: system_performance_metrics_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.system_performance_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: system_performance_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.system_performance_metrics_id_seq OWNED BY synapscale_db.system_performance_metrics.id;


--
-- Name: tags; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.tags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    target_type character varying(50) NOT NULL,
    target_id uuid NOT NULL,
    tag_name character varying(100) NOT NULL,
    tag_value text,
    tag_category character varying(50),
    is_system_tag boolean DEFAULT false,
    created_by_user_id uuid,
    auto_generated boolean DEFAULT false,
    confidence_score double precision,
    tag_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: template_collections; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.template_collections (
    id integer NOT NULL,
    collection_id character varying(36),
    name character varying(255) NOT NULL,
    description text,
    creator_id uuid NOT NULL,
    is_public boolean,
    is_featured boolean,
    template_ids jsonb NOT NULL,
    tags jsonb,
    thumbnail_url character varying(500),
    view_count integer,
    follow_count integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: template_collections_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.template_collections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: template_collections_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.template_collections_id_seq OWNED BY synapscale_db.template_collections.id;


--
-- Name: template_downloads; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.template_downloads (
    id integer NOT NULL,
    template_id uuid NOT NULL,
    user_id uuid NOT NULL,
    download_type character varying(20),
    ip_address character varying(45),
    user_agent character varying(500),
    template_version character varying(20),
    downloaded_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: template_downloads_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.template_downloads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: template_downloads_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.template_downloads_id_seq OWNED BY synapscale_db.template_downloads.id;


--
-- Name: template_favorites; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.template_favorites (
    id integer NOT NULL,
    template_id uuid NOT NULL,
    user_id uuid NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: template_favorites_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.template_favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: template_favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.template_favorites_id_seq OWNED BY synapscale_db.template_favorites.id;


--
-- Name: template_reviews; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.template_reviews (
    id integer NOT NULL,
    template_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rating integer NOT NULL,
    title character varying(255),
    comment text,
    ease_of_use integer,
    documentation_quality integer,
    performance integer,
    value_for_money integer,
    is_verified_purchase boolean,
    is_helpful_count integer,
    is_reported boolean,
    version_reviewed character varying(20),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: template_reviews_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.template_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: template_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.template_reviews_id_seq OWNED BY synapscale_db.template_reviews.id;


--
-- Name: template_usage; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.template_usage (
    id integer NOT NULL,
    template_id uuid NOT NULL,
    user_id uuid NOT NULL,
    workflow_id uuid,
    usage_type character varying(20) NOT NULL,
    success boolean,
    template_version character varying(20),
    modifications_made jsonb,
    execution_time integer,
    ip_address character varying(45),
    user_agent character varying(500),
    used_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: template_usage_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.template_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: template_usage_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.template_usage_id_seq OWNED BY synapscale_db.template_usage.id;


--
-- Name: tenant_features; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.tenant_features (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    feature_id uuid NOT NULL,
    is_enabled boolean DEFAULT true,
    usage_count integer DEFAULT 0,
    limit_value integer,
    config jsonb DEFAULT '{}'::jsonb,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tools; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.tools (
    tool_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    category text,
    base_config jsonb DEFAULT '{}'::jsonb NOT NULL,
    tenant_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE tools; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON TABLE synapscale_db.tools IS 'Catálogo de ferramentas que agentes podem chamar.';


--
-- Name: COLUMN tools.tool_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.tool_id IS 'UUID da ferramenta (ex: gen_random_uuid() → ''9abc0def-...'' ).';


--
-- Name: COLUMN tools.name; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.name IS 'Nome amigável da ferramenta (ex: ''busca_web'').';


--
-- Name: COLUMN tools.category; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.category IS 'Categoria da ferramenta (ex: ''recuperação'').';


--
-- Name: COLUMN tools.base_config; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.base_config IS 'JSONB com configurações padrão da ferramenta (ex: { "timeout": 30 }).';


--
-- Name: COLUMN tools.tenant_id; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.tenant_id IS 'UUID do tenant se a ferramenta for customizada (NULL = global).';


--
-- Name: COLUMN tools.created_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.created_at IS 'Timestamp de criação da ferramenta.';


--
-- Name: COLUMN tools.updated_at; Type: COMMENT; Schema: synapscale_db; Owner: -
--

COMMENT ON COLUMN synapscale_db.tools.updated_at IS 'Timestamp da última atualização da ferramenta.';


--
-- Name: user_behavior_metrics; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.user_behavior_metrics (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    date timestamp with time zone NOT NULL,
    period_type character varying(20) NOT NULL,
    session_count integer NOT NULL,
    total_session_duration integer NOT NULL,
    avg_session_duration double precision NOT NULL,
    page_views integer NOT NULL,
    unique_pages_visited integer NOT NULL,
    workflows_created integer NOT NULL,
    workflows_executed integer NOT NULL,
    components_used integer NOT NULL,
    collaborations_initiated integer NOT NULL,
    marketplace_purchases integer NOT NULL,
    revenue_generated double precision NOT NULL,
    components_published integer NOT NULL,
    error_count integer NOT NULL,
    support_tickets integer NOT NULL,
    feature_requests integer NOT NULL,
    engagement_score double precision NOT NULL,
    satisfaction_score double precision NOT NULL,
    value_score double precision NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    tenant_id uuid
);


--
-- Name: user_insights; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.user_insights (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    insight_type character varying(50) NOT NULL,
    category character varying(50) NOT NULL,
    priority character varying(20) NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    recommendation text,
    supporting_data jsonb,
    confidence_score double precision NOT NULL,
    suggested_action character varying(100),
    action_url character varying(500),
    action_data jsonb,
    is_read boolean NOT NULL,
    is_dismissed boolean NOT NULL,
    is_acted_upon boolean NOT NULL,
    user_feedback character varying(20),
    expires_at timestamp with time zone,
    is_evergreen boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    read_at timestamp with time zone,
    acted_at timestamp with time zone,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_subscriptions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.user_subscriptions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    plan_id uuid NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    payment_method character varying(50),
    payment_provider character varying(50),
    external_subscription_id character varying(255),
    billing_cycle character varying(20) DEFAULT 'monthly'::character varying,
    current_period_start timestamp with time zone,
    current_period_end timestamp with time zone,
    current_workspaces integer DEFAULT 0 NOT NULL,
    current_storage_mb double precision DEFAULT 0.0 NOT NULL,
    current_executions_this_month integer DEFAULT 0 NOT NULL,
    subscription_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    status character varying(50) DEFAULT 'active'::character varying
);


--
-- Name: user_tenant_roles; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.user_tenant_roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    role_id uuid NOT NULL,
    granted_by uuid,
    granted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp with time zone,
    is_active boolean DEFAULT true,
    conditions jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_variables; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.user_variables (
    id uuid NOT NULL,
    key character varying(255) NOT NULL,
    value text NOT NULL,
    is_secret boolean DEFAULT false NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    category character varying(100),
    description text,
    is_encrypted boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    tenant_id uuid
);


--
-- Name: webhook_logs; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.webhook_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_id uuid NOT NULL,
    event_type character varying(100) NOT NULL,
    event_id character varying(255),
    payload jsonb NOT NULL,
    headers jsonb DEFAULT '{}'::jsonb,
    status character varying(50) DEFAULT 'pending'::character varying,
    processed_at timestamp with time zone,
    error_message text,
    retry_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: workflow_connections; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflow_connections (
    id uuid NOT NULL,
    workflow_id uuid NOT NULL,
    source_node_id uuid NOT NULL,
    target_node_id uuid NOT NULL,
    source_port character varying(100),
    target_port character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: workflow_executions; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflow_executions (
    id uuid NOT NULL,
    execution_id character varying(36),
    workflow_id uuid NOT NULL,
    user_id uuid NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    priority integer,
    input_data jsonb,
    output_data jsonb,
    context_data jsonb,
    variables jsonb,
    total_nodes integer,
    completed_nodes integer,
    failed_nodes integer,
    progress_percentage integer,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    timeout_at timestamp with time zone,
    estimated_duration integer,
    actual_duration integer,
    execution_log text,
    error_message text,
    error_details jsonb,
    debug_info jsonb,
    retry_count integer,
    max_retries integer,
    auto_retry boolean,
    notify_on_completion boolean,
    notify_on_failure boolean,
    tags jsonb,
    metadata json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tenant_id uuid
);


--
-- Name: workflow_nodes; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflow_nodes (
    id uuid NOT NULL,
    workflow_id uuid NOT NULL,
    node_id uuid NOT NULL,
    instance_name character varying(200),
    position_x integer NOT NULL,
    position_y integer NOT NULL,
    configuration jsonb,
    created_at timestamp with time zone DEFAULT now(),
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: workflow_templates; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workflow_templates (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    category character varying(100) NOT NULL,
    tags jsonb,
    workflow_definition jsonb NOT NULL,
    preview_image character varying(500),
    author_id uuid NOT NULL,
    version character varying(50) DEFAULT '1.0.0'::character varying NOT NULL,
    is_public boolean DEFAULT false NOT NULL,
    is_featured boolean DEFAULT false NOT NULL,
    downloads_count integer DEFAULT 0 NOT NULL,
    rating_average numeric(3,2) DEFAULT 0.00 NOT NULL,
    rating_count integer DEFAULT 0 NOT NULL,
    price numeric(10,2) DEFAULT 0.00 NOT NULL,
    is_free boolean DEFAULT true NOT NULL,
    license character varying(50) DEFAULT 'MIT'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    title character varying(255) NOT NULL,
    short_description character varying(500),
    original_workflow_id uuid,
    status character varying(20),
    is_verified boolean,
    license_type character varying(20),
    workflow_data jsonb NOT NULL,
    nodes_data jsonb NOT NULL,
    connections_data jsonb,
    required_variables jsonb,
    optional_variables jsonb,
    default_config jsonb,
    compatibility_version character varying(20),
    estimated_duration integer,
    complexity_level integer,
    download_count integer,
    usage_count integer,
    view_count integer,
    keywords jsonb,
    use_cases jsonb,
    industries jsonb,
    thumbnail_url character varying(500),
    preview_images jsonb,
    demo_video_url character varying(500),
    documentation text,
    setup_instructions text,
    changelog jsonb,
    support_email character varying(255),
    repository_url character varying(500),
    documentation_url character varying(500),
    published_at timestamp with time zone,
    last_used_at timestamp with time zone,
    tenant_id uuid
);


--
-- Name: workspace_activities; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workspace_activities (
    id uuid NOT NULL,
    workspace_id uuid NOT NULL,
    user_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_id character varying(255),
    description character varying(500) NOT NULL,
    metadata jsonb,
    ip_address character varying(45),
    user_agent character varying(500),
    created_at timestamp with time zone NOT NULL,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    meta_data jsonb DEFAULT '{}'::jsonb
);


--
-- Name: workspace_features; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workspace_features (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    feature_id uuid NOT NULL,
    is_enabled boolean DEFAULT true,
    config jsonb DEFAULT '{}'::jsonb,
    usage_count integer DEFAULT 0,
    limit_value integer,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid
);


--
-- Name: workspace_invitations; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workspace_invitations (
    id uuid NOT NULL,
    workspace_id uuid NOT NULL,
    inviter_id uuid NOT NULL,
    invited_user_id uuid,
    email character varying(255) NOT NULL,
    message text,
    token character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    responded_at timestamp with time zone,
    tenant_id uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: workspace_members; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workspace_members (
    id integer NOT NULL,
    workspace_id uuid NOT NULL,
    user_id uuid NOT NULL,
    custom_permissions jsonb,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    is_favorite boolean DEFAULT false NOT NULL,
    notification_preferences jsonb,
    last_seen_at timestamp with time zone NOT NULL,
    joined_at timestamp with time zone NOT NULL,
    left_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    tenant_id uuid NOT NULL,
    role character varying(50) DEFAULT 'member'::character varying NOT NULL
);


--
-- Name: workspace_members_id_seq; Type: SEQUENCE; Schema: synapscale_db; Owner: -
--

CREATE SEQUENCE synapscale_db.workspace_members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: workspace_members_id_seq; Type: SEQUENCE OWNED BY; Schema: synapscale_db; Owner: -
--

ALTER SEQUENCE synapscale_db.workspace_members_id_seq OWNED BY synapscale_db.workspace_members.id;


--
-- Name: workspace_projects; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workspace_projects (
    id uuid NOT NULL,
    workspace_id uuid NOT NULL,
    workflow_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(7),
    allow_concurrent_editing boolean NOT NULL,
    auto_save_interval integer,
    version_control_enabled boolean NOT NULL,
    status character varying(20) NOT NULL,
    is_template boolean NOT NULL,
    is_public boolean NOT NULL,
    collaborator_count integer NOT NULL,
    edit_count integer NOT NULL,
    comment_count integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    last_edited_at timestamp with time zone NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: workspaces; Type: TABLE; Schema: synapscale_db; Owner: -
--

CREATE TABLE synapscale_db.workspaces (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(120) NOT NULL,
    description text,
    avatar_url character varying(500),
    color character varying(7),
    owner_id uuid NOT NULL,
    is_public boolean DEFAULT false NOT NULL,
    is_template boolean DEFAULT false NOT NULL,
    allow_guest_access boolean DEFAULT false NOT NULL,
    require_approval boolean NOT NULL,
    max_members integer,
    max_projects integer,
    max_storage_mb integer,
    enable_real_time_editing boolean NOT NULL,
    enable_comments boolean NOT NULL,
    enable_chat boolean NOT NULL,
    enable_video_calls boolean NOT NULL,
    member_count integer NOT NULL,
    project_count integer NOT NULL,
    activity_count integer NOT NULL,
    storage_used_mb double precision NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    last_activity_at timestamp with time zone NOT NULL,
    tenant_id uuid NOT NULL,
    email_notifications boolean DEFAULT true,
    push_notifications boolean DEFAULT false,
    api_calls_today integer DEFAULT 0,
    api_calls_this_month integer DEFAULT 0,
    last_api_reset_daily timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_api_reset_monthly timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    feature_usage_count jsonb DEFAULT '{}'::jsonb,
    type synapscale_db.workspacetype DEFAULT 'individual'::synapscale_db.workspacetype NOT NULL
);


--
-- Name: business_metrics id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.business_metrics ALTER COLUMN id SET DEFAULT nextval('synapscale_db.business_metrics_id_seq'::regclass);


--
-- Name: node_executions id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_executions ALTER COLUMN id SET DEFAULT nextval('synapscale_db.node_executions_id_seq'::regclass);


--
-- Name: system_performance_metrics id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.system_performance_metrics ALTER COLUMN id SET DEFAULT nextval('synapscale_db.system_performance_metrics_id_seq'::regclass);


--
-- Name: template_collections id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_collections ALTER COLUMN id SET DEFAULT nextval('synapscale_db.template_collections_id_seq'::regclass);


--
-- Name: template_downloads id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_downloads ALTER COLUMN id SET DEFAULT nextval('synapscale_db.template_downloads_id_seq'::regclass);


--
-- Name: template_favorites id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_favorites ALTER COLUMN id SET DEFAULT nextval('synapscale_db.template_favorites_id_seq'::regclass);


--
-- Name: template_reviews id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_reviews ALTER COLUMN id SET DEFAULT nextval('synapscale_db.template_reviews_id_seq'::regclass);


--
-- Name: template_usage id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_usage ALTER COLUMN id SET DEFAULT nextval('synapscale_db.template_usage_id_seq'::regclass);


--
-- Name: workflow_execution_metrics id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_metrics ALTER COLUMN id SET DEFAULT nextval('synapscale_db.execution_metrics_id_seq'::regclass);


--
-- Name: workflow_execution_queue id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_queue ALTER COLUMN id SET DEFAULT nextval('synapscale_db.execution_queue_id_seq'::regclass);


--
-- Name: workspace_members id; Type: DEFAULT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_members ALTER COLUMN id SET DEFAULT nextval('synapscale_db.workspace_members_id_seq'::regclass);


--
-- Name: agent_acl agent_acl_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_acl
    ADD CONSTRAINT agent_acl_pkey PRIMARY KEY (agent_id, user_id);


--
-- Name: agent_configurations agent_configurations_agent_id_version_num_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_configurations
    ADD CONSTRAINT agent_configurations_agent_id_version_num_key UNIQUE (agent_id, version_num);


--
-- Name: agent_configurations agent_configurations_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_configurations
    ADD CONSTRAINT agent_configurations_pkey PRIMARY KEY (config_id);


--
-- Name: agent_error_logs agent_error_logs_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_error_logs
    ADD CONSTRAINT agent_error_logs_pkey PRIMARY KEY (error_id);


--
-- Name: agent_hierarchy agent_hierarchy_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_hierarchy
    ADD CONSTRAINT agent_hierarchy_pkey PRIMARY KEY (ancestor, descendant);


--
-- Name: agent_kbs agent_kbs_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_kbs
    ADD CONSTRAINT agent_kbs_pkey PRIMARY KEY (agent_id, kb_id);


--
-- Name: agent_models agent_models_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_models
    ADD CONSTRAINT agent_models_pkey PRIMARY KEY (agent_id, llm_id);


--
-- Name: agent_quotas agent_quotas_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_quotas
    ADD CONSTRAINT agent_quotas_pkey PRIMARY KEY (quota_id);


--
-- Name: agent_tools agent_tools_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_tools
    ADD CONSTRAINT agent_tools_pkey PRIMARY KEY (agent_id, tool_id);


--
-- Name: agent_triggers agent_triggers_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_triggers
    ADD CONSTRAINT agent_triggers_pkey PRIMARY KEY (trigger_id);


--
-- Name: agent_usage_metrics agent_usage_metrics_agent_id_period_start_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_usage_metrics
    ADD CONSTRAINT agent_usage_metrics_agent_id_period_start_key UNIQUE (agent_id, period_start);


--
-- Name: agent_usage_metrics agent_usage_metrics_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_usage_metrics
    ADD CONSTRAINT agent_usage_metrics_pkey PRIMARY KEY (metric_id);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: analytics_alerts analytics_alerts_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_alerts
    ADD CONSTRAINT analytics_alerts_pkey PRIMARY KEY (id);


--
-- Name: analytics_dashboards analytics_dashboards_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_dashboards
    ADD CONSTRAINT analytics_dashboards_pkey PRIMARY KEY (id);


--
-- Name: analytics_events analytics_events_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_events
    ADD CONSTRAINT analytics_events_pkey PRIMARY KEY (id);


--
-- Name: analytics_exports analytics_exports_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_exports
    ADD CONSTRAINT analytics_exports_pkey PRIMARY KEY (id);


--
-- Name: analytics_metrics analytics_metrics_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_metrics
    ADD CONSTRAINT analytics_metrics_pkey PRIMARY KEY (id);


--
-- Name: analytics_reports analytics_reports_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_reports
    ADD CONSTRAINT analytics_reports_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (audit_id);


--
-- Name: billing_events billing_events_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.billing_events
    ADD CONSTRAINT billing_events_pkey PRIMARY KEY (id);


--
-- Name: business_metrics business_metrics_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.business_metrics
    ADD CONSTRAINT business_metrics_pkey PRIMARY KEY (id);


--
-- Name: campaign_contacts campaign_contacts_campaign_id_contact_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaign_contacts
    ADD CONSTRAINT campaign_contacts_campaign_id_contact_id_key UNIQUE (campaign_id, contact_id);


--
-- Name: campaign_contacts campaign_contacts_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaign_contacts
    ADD CONSTRAINT campaign_contacts_pkey PRIMARY KEY (id);


--
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (id);


--
-- Name: component_downloads component_downloads_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_downloads
    ADD CONSTRAINT component_downloads_pkey PRIMARY KEY (id);


--
-- Name: component_purchases component_purchases_license_key_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_purchases
    ADD CONSTRAINT component_purchases_license_key_key UNIQUE (license_key);


--
-- Name: component_purchases component_purchases_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_purchases
    ADD CONSTRAINT component_purchases_pkey PRIMARY KEY (id);


--
-- Name: component_purchases component_purchases_transaction_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_purchases
    ADD CONSTRAINT component_purchases_transaction_id_key UNIQUE (transaction_id);


--
-- Name: component_ratings component_ratings_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_ratings
    ADD CONSTRAINT component_ratings_pkey PRIMARY KEY (id);


--
-- Name: component_versions component_versions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_versions
    ADD CONSTRAINT component_versions_pkey PRIMARY KEY (id);


--
-- Name: contact_events contact_events_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_events
    ADD CONSTRAINT contact_events_pkey PRIMARY KEY (id);


--
-- Name: contact_interactions contact_interactions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_interactions
    ADD CONSTRAINT contact_interactions_pkey PRIMARY KEY (id);


--
-- Name: contact_list_memberships contact_list_memberships_list_id_contact_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_list_memberships
    ADD CONSTRAINT contact_list_memberships_list_id_contact_id_key UNIQUE (list_id, contact_id);


--
-- Name: contact_list_memberships contact_list_memberships_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_list_memberships
    ADD CONSTRAINT contact_list_memberships_pkey PRIMARY KEY (id);


--
-- Name: contact_lists contact_lists_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_lists
    ADD CONSTRAINT contact_lists_pkey PRIMARY KEY (id);


--
-- Name: contact_notes contact_notes_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_notes
    ADD CONSTRAINT contact_notes_pkey PRIMARY KEY (id);


--
-- Name: contact_sources contact_sources_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_sources
    ADD CONSTRAINT contact_sources_pkey PRIMARY KEY (id);


--
-- Name: contact_sources contact_sources_tenant_id_name_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_sources
    ADD CONSTRAINT contact_sources_tenant_id_name_key UNIQUE (tenant_id, name);


--
-- Name: contact_tags contact_tags_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_tags
    ADD CONSTRAINT contact_tags_pkey PRIMARY KEY (id);


--
-- Name: contact_tags contact_tags_tenant_id_name_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_tags
    ADD CONSTRAINT contact_tags_tenant_id_name_key UNIQUE (tenant_id, name);


--
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: contacts contacts_tenant_id_email_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contacts
    ADD CONSTRAINT contacts_tenant_id_email_key UNIQUE (tenant_id, email);


--
-- Name: llms_conversations_turns conversation_llms_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations_turns
    ADD CONSTRAINT conversation_llms_pkey PRIMARY KEY (id);


--
-- Name: llms_conversations conversations_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: conversion_journeys conversion_journeys_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.conversion_journeys
    ADD CONSTRAINT conversion_journeys_pkey PRIMARY KEY (id);


--
-- Name: coupons coupons_code_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.coupons
    ADD CONSTRAINT coupons_code_key UNIQUE (code);


--
-- Name: coupons coupons_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.coupons
    ADD CONSTRAINT coupons_pkey PRIMARY KEY (id);


--
-- Name: custom_reports custom_reports_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.custom_reports
    ADD CONSTRAINT custom_reports_pkey PRIMARY KEY (id);


--
-- Name: email_verification_tokens email_verification_tokens_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.email_verification_tokens
    ADD CONSTRAINT email_verification_tokens_pkey PRIMARY KEY (id);


--
-- Name: workflow_execution_metrics execution_metrics_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_metrics
    ADD CONSTRAINT execution_metrics_pkey PRIMARY KEY (id);


--
-- Name: workflow_execution_queue execution_queue_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_queue
    ADD CONSTRAINT execution_queue_pkey PRIMARY KEY (id);


--
-- Name: features features_key_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.features
    ADD CONSTRAINT features_key_key UNIQUE (key);


--
-- Name: features features_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.features
    ADD CONSTRAINT features_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_invoice_number_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.invoices
    ADD CONSTRAINT invoices_invoice_number_key UNIQUE (invoice_number);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: knowledge_bases knowledge_bases_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.knowledge_bases
    ADD CONSTRAINT knowledge_bases_pkey PRIMARY KEY (kb_id);


--
-- Name: llms llms_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms
    ADD CONSTRAINT llms_pkey PRIMARY KEY (id);


--
-- Name: marketplace_components marketplace_components_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.marketplace_components
    ADD CONSTRAINT marketplace_components_pkey PRIMARY KEY (id);


--
-- Name: message_feedbacks message_feedbacks_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.message_feedbacks
    ADD CONSTRAINT message_feedbacks_pkey PRIMARY KEY (id);


--
-- Name: llms_messages messages_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: node_categories node_categories_name_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_categories
    ADD CONSTRAINT node_categories_name_key UNIQUE (name);


--
-- Name: node_categories node_categories_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_categories
    ADD CONSTRAINT node_categories_pkey PRIMARY KEY (id);


--
-- Name: node_executions node_executions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_executions
    ADD CONSTRAINT node_executions_pkey PRIMARY KEY (id);


--
-- Name: node_ratings node_ratings_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_ratings
    ADD CONSTRAINT node_ratings_pkey PRIMARY KEY (id);


--
-- Name: node_templates node_templates_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_templates
    ADD CONSTRAINT node_templates_pkey PRIMARY KEY (id);


--
-- Name: nodes nodes_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: payment_customers payment_customers_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_customers
    ADD CONSTRAINT payment_customers_pkey PRIMARY KEY (id);


--
-- Name: payment_customers payment_customers_provider_id_external_customer_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_customers
    ADD CONSTRAINT payment_customers_provider_id_external_customer_id_key UNIQUE (provider_id, external_customer_id);


--
-- Name: payment_customers payment_customers_tenant_id_provider_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_customers
    ADD CONSTRAINT payment_customers_tenant_id_provider_id_key UNIQUE (tenant_id, provider_id);


--
-- Name: payment_methods payment_methods_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_methods
    ADD CONSTRAINT payment_methods_pkey PRIMARY KEY (id);


--
-- Name: payment_providers payment_providers_name_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_providers
    ADD CONSTRAINT payment_providers_name_key UNIQUE (name);


--
-- Name: payment_providers payment_providers_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_providers
    ADD CONSTRAINT payment_providers_pkey PRIMARY KEY (id);


--
-- Name: plan_entitlements plan_entitlements_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_entitlements
    ADD CONSTRAINT plan_entitlements_pkey PRIMARY KEY (id);


--
-- Name: plan_entitlements plan_entitlements_plan_id_feature_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_entitlements
    ADD CONSTRAINT plan_entitlements_plan_id_feature_id_key UNIQUE (plan_id, feature_id);


--
-- Name: plan_features plan_features_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_features
    ADD CONSTRAINT plan_features_pkey PRIMARY KEY (id);


--
-- Name: plan_features plan_features_plan_id_feature_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_features
    ADD CONSTRAINT plan_features_plan_id_feature_id_key UNIQUE (plan_id, feature_id);


--
-- Name: plan_provider_mappings plan_provider_mappings_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_provider_mappings
    ADD CONSTRAINT plan_provider_mappings_pkey PRIMARY KEY (id);


--
-- Name: plan_provider_mappings plan_provider_mappings_provider_id_external_plan_id_external_pr; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_provider_mappings
    ADD CONSTRAINT plan_provider_mappings_provider_id_external_plan_id_external_pr UNIQUE (provider_id, external_plan_id, external_price_id);


--
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- Name: plans plans_slug_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plans
    ADD CONSTRAINT plans_slug_key UNIQUE (slug);


--
-- Name: project_collaborators project_collaborators_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_collaborators
    ADD CONSTRAINT project_collaborators_pkey PRIMARY KEY (id);


--
-- Name: project_comments project_comments_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_comments
    ADD CONSTRAINT project_comments_pkey PRIMARY KEY (id);


--
-- Name: project_versions project_versions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_versions
    ADD CONSTRAINT project_versions_pkey PRIMARY KEY (id);


--
-- Name: rbac_permissions rbac_permissions_key_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_permissions
    ADD CONSTRAINT rbac_permissions_key_key UNIQUE (key);


--
-- Name: rbac_permissions rbac_permissions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_permissions
    ADD CONSTRAINT rbac_permissions_pkey PRIMARY KEY (id);


--
-- Name: rbac_role_permissions rbac_role_permissions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_role_permissions
    ADD CONSTRAINT rbac_role_permissions_pkey PRIMARY KEY (id);


--
-- Name: rbac_role_permissions rbac_role_permissions_role_id_permission_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_role_permissions
    ADD CONSTRAINT rbac_role_permissions_role_id_permission_id_key UNIQUE (role_id, permission_id);


--
-- Name: rbac_roles rbac_roles_name_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_roles
    ADD CONSTRAINT rbac_roles_name_key UNIQUE (name);


--
-- Name: rbac_roles rbac_roles_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_roles
    ADD CONSTRAINT rbac_roles_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: report_executions report_executions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.report_executions
    ADD CONSTRAINT report_executions_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: system_performance_metrics system_performance_metrics_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.system_performance_metrics
    ADD CONSTRAINT system_performance_metrics_pkey PRIMARY KEY (id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: template_collections template_collections_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_collections
    ADD CONSTRAINT template_collections_pkey PRIMARY KEY (id);


--
-- Name: template_downloads template_downloads_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_downloads
    ADD CONSTRAINT template_downloads_pkey PRIMARY KEY (id);


--
-- Name: template_favorites template_favorites_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_favorites
    ADD CONSTRAINT template_favorites_pkey PRIMARY KEY (id);


--
-- Name: template_reviews template_reviews_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_reviews
    ADD CONSTRAINT template_reviews_pkey PRIMARY KEY (id);


--
-- Name: template_usage template_usage_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_usage
    ADD CONSTRAINT template_usage_pkey PRIMARY KEY (id);


--
-- Name: tenant_features tenant_features_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenant_features
    ADD CONSTRAINT tenant_features_pkey PRIMARY KEY (id);


--
-- Name: tenant_features tenant_features_tenant_id_feature_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenant_features
    ADD CONSTRAINT tenant_features_tenant_id_feature_id_key UNIQUE (tenant_id, feature_id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_slug_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenants
    ADD CONSTRAINT tenants_slug_key UNIQUE (slug);


--
-- Name: tools tools_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tools
    ADD CONSTRAINT tools_pkey PRIMARY KEY (tool_id);


--
-- Name: llms_usage_logs usage_logs_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT usage_logs_pkey PRIMARY KEY (id);


--
-- Name: user_behavior_metrics user_behavior_metrics_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_behavior_metrics
    ADD CONSTRAINT user_behavior_metrics_pkey PRIMARY KEY (id);


--
-- Name: user_insights user_insights_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_insights
    ADD CONSTRAINT user_insights_pkey PRIMARY KEY (id);


--
-- Name: user_subscriptions user_subscriptions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_subscriptions
    ADD CONSTRAINT user_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: user_tenant_roles user_tenant_roles_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_tenant_roles
    ADD CONSTRAINT user_tenant_roles_pkey PRIMARY KEY (id);


--
-- Name: user_tenant_roles user_tenant_roles_user_id_tenant_id_role_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_tenant_roles
    ADD CONSTRAINT user_tenant_roles_user_id_tenant_id_role_id_key UNIQUE (user_id, tenant_id, role_id);


--
-- Name: user_variables user_variables_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_variables
    ADD CONSTRAINT user_variables_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: webhook_logs webhook_logs_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.webhook_logs
    ADD CONSTRAINT webhook_logs_pkey PRIMARY KEY (id);


--
-- Name: workflow_connections workflow_connections_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_connections
    ADD CONSTRAINT workflow_connections_pkey PRIMARY KEY (id);


--
-- Name: workflow_executions workflow_executions_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_executions
    ADD CONSTRAINT workflow_executions_pkey PRIMARY KEY (id);


--
-- Name: workflow_nodes workflow_nodes_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_nodes
    ADD CONSTRAINT workflow_nodes_pkey PRIMARY KEY (id);


--
-- Name: workflow_templates workflow_templates_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_templates
    ADD CONSTRAINT workflow_templates_pkey PRIMARY KEY (id);


--
-- Name: workflows workflows_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflows
    ADD CONSTRAINT workflows_pkey PRIMARY KEY (id);


--
-- Name: workspace_activities workspace_activities_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_activities
    ADD CONSTRAINT workspace_activities_pkey PRIMARY KEY (id);


--
-- Name: workspace_features workspace_features_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_features
    ADD CONSTRAINT workspace_features_pkey PRIMARY KEY (id);


--
-- Name: workspace_features workspace_features_workspace_id_feature_id_key; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_features
    ADD CONSTRAINT workspace_features_workspace_id_feature_id_key UNIQUE (workspace_id, feature_id);


--
-- Name: workspace_invitations workspace_invitations_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_invitations
    ADD CONSTRAINT workspace_invitations_pkey PRIMARY KEY (id);


--
-- Name: workspace_members workspace_members_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_members
    ADD CONSTRAINT workspace_members_pkey PRIMARY KEY (id);


--
-- Name: workspace_projects workspace_projects_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_projects
    ADD CONSTRAINT workspace_projects_pkey PRIMARY KEY (id);


--
-- Name: workspaces workspaces_pkey; Type: CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspaces
    ADD CONSTRAINT workspaces_pkey PRIMARY KEY (id);


--
-- Name: idx_agent_kbs_config; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agent_kbs_config ON synapscale_db.agent_kbs USING gin (config);


--
-- Name: idx_agent_tools_config; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agent_tools_config ON synapscale_db.agent_tools USING gin (config);


--
-- Name: idx_agents_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_name ON synapscale_db.agents USING btree (name);


--
-- Name: idx_agents_priority; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_priority ON synapscale_db.agents USING btree (priority);


--
-- Name: idx_agents_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_status ON synapscale_db.agents USING btree (status) WHERE ((status)::text <> 'archived'::text);


--
-- Name: idx_agents_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_tenant_id ON synapscale_db.agents USING btree (tenant_id);


--
-- Name: idx_agents_tenant_user; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_tenant_user ON synapscale_db.agents USING btree (tenant_id, user_id);


--
-- Name: idx_agents_tenant_workspace; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_tenant_workspace ON synapscale_db.agents USING btree (tenant_id, workspace_id);


--
-- Name: idx_agents_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_agents_user_id ON synapscale_db.agents USING btree (user_id);


--
-- Name: idx_analytics_alerts_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_alerts_tenant_id ON synapscale_db.analytics_alerts USING btree (tenant_id);


--
-- Name: idx_analytics_dashboards_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_dashboards_status ON synapscale_db.analytics_dashboards USING btree (status);


--
-- Name: idx_analytics_dashboards_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_dashboards_tenant_id ON synapscale_db.analytics_dashboards USING btree (tenant_id);


--
-- Name: idx_analytics_events_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_events_tenant_id ON synapscale_db.analytics_events USING btree (tenant_id);


--
-- Name: idx_analytics_events_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_events_user_id ON synapscale_db.analytics_events USING btree (user_id);


--
-- Name: idx_analytics_exports_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_exports_status ON synapscale_db.analytics_exports USING btree (status);


--
-- Name: idx_analytics_exports_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_exports_tenant_id ON synapscale_db.analytics_exports USING btree (tenant_id);


--
-- Name: idx_analytics_metrics_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_metrics_tenant_id ON synapscale_db.analytics_metrics USING btree (tenant_id);


--
-- Name: idx_analytics_reports_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_analytics_reports_tenant_id ON synapscale_db.analytics_reports USING btree (tenant_id);


--
-- Name: idx_billing_events_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_billing_events_tenant_id ON synapscale_db.billing_events USING btree (tenant_id);


--
-- Name: idx_business_metrics_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_business_metrics_tenant_id ON synapscale_db.business_metrics USING btree (tenant_id);


--
-- Name: idx_campaign_contacts_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_campaign_contacts_status ON synapscale_db.campaign_contacts USING btree (status);


--
-- Name: idx_campaign_contacts_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_campaign_contacts_tenant_id ON synapscale_db.campaign_contacts USING btree (tenant_id);


--
-- Name: idx_campaigns_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_campaigns_status ON synapscale_db.campaigns USING btree (status);


--
-- Name: idx_campaigns_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_campaigns_tenant_id ON synapscale_db.campaigns USING btree (tenant_id);


--
-- Name: idx_component_downloads_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_downloads_status ON synapscale_db.component_downloads USING btree (status);


--
-- Name: idx_component_downloads_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_downloads_tenant_id ON synapscale_db.component_downloads USING btree (tenant_id);


--
-- Name: idx_component_purchases_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_purchases_status ON synapscale_db.component_purchases USING btree (status);


--
-- Name: idx_component_purchases_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_purchases_tenant_id ON synapscale_db.component_purchases USING btree (tenant_id);


--
-- Name: idx_component_ratings_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_ratings_status ON synapscale_db.component_ratings USING btree (status);


--
-- Name: idx_component_ratings_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_ratings_tenant_id ON synapscale_db.component_ratings USING btree (tenant_id);


--
-- Name: idx_component_versions_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_versions_status ON synapscale_db.component_versions USING btree (status);


--
-- Name: idx_component_versions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_component_versions_tenant_id ON synapscale_db.component_versions USING btree (tenant_id);


--
-- Name: idx_contact_events_contact_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_events_contact_id ON synapscale_db.contact_events USING btree (contact_id);


--
-- Name: idx_contact_events_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_events_tenant_id ON synapscale_db.contact_events USING btree (tenant_id);


--
-- Name: idx_contact_interactions_contact_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_interactions_contact_id ON synapscale_db.contact_interactions USING btree (contact_id);


--
-- Name: idx_contact_interactions_created_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_interactions_created_at ON synapscale_db.contact_interactions USING btree (created_at);


--
-- Name: idx_contact_interactions_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_interactions_status ON synapscale_db.contact_interactions USING btree (status);


--
-- Name: idx_contact_interactions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_interactions_tenant_id ON synapscale_db.contact_interactions USING btree (tenant_id);


--
-- Name: idx_contact_interactions_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_interactions_user_id ON synapscale_db.contact_interactions USING btree (user_id);


--
-- Name: idx_contact_list_memberships_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_list_memberships_status ON synapscale_db.contact_list_memberships USING btree (status);


--
-- Name: idx_contact_list_memberships_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_list_memberships_tenant_id ON synapscale_db.contact_list_memberships USING btree (tenant_id);


--
-- Name: idx_contact_lists_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_lists_tenant_id ON synapscale_db.contact_lists USING btree (tenant_id);


--
-- Name: idx_contact_notes_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_notes_tenant_id ON synapscale_db.contact_notes USING btree (tenant_id);


--
-- Name: idx_contact_notes_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contact_notes_user_id ON synapscale_db.contact_notes USING btree (user_id);


--
-- Name: idx_contacts_email; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contacts_email ON synapscale_db.contacts USING btree (email);


--
-- Name: idx_contacts_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contacts_status ON synapscale_db.contacts USING btree (status);


--
-- Name: idx_contacts_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_contacts_tenant_id ON synapscale_db.contacts USING btree (tenant_id);


--
-- Name: idx_conv_turns_conversation_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_conv_turns_conversation_id ON synapscale_db.llms_conversations_turns USING btree (conversation_id);


--
-- Name: idx_conversations_tenant_user; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_conversations_tenant_user ON synapscale_db.llms_conversations USING btree (tenant_id, user_id);


--
-- Name: idx_conversion_journeys_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_conversion_journeys_tenant_id ON synapscale_db.conversion_journeys USING btree (tenant_id);


--
-- Name: idx_coupons_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_coupons_tenant_id ON synapscale_db.coupons USING btree (tenant_id);


--
-- Name: idx_custom_reports_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_custom_reports_status ON synapscale_db.custom_reports USING btree (status);


--
-- Name: idx_custom_reports_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_custom_reports_tenant_id ON synapscale_db.custom_reports USING btree (tenant_id);


--
-- Name: idx_email_verification_tokens_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_email_verification_tokens_user_id ON synapscale_db.email_verification_tokens USING btree (user_id);


--
-- Name: idx_features_category; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_features_category ON synapscale_db.features USING btree (category);


--
-- Name: idx_features_key; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_features_key ON synapscale_db.features USING btree (key);


--
-- Name: idx_feedback_message_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_feedback_message_id ON synapscale_db.message_feedbacks USING btree (message_id);


--
-- Name: idx_file_created_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_file_created_at ON synapscale_db.files USING btree (created_at);


--
-- Name: idx_file_filename; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_file_filename ON synapscale_db.files USING btree (filename);


--
-- Name: idx_files_scan_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_files_scan_status ON synapscale_db.files USING btree (scan_status) WHERE ((scan_status)::text <> 'clean'::text);


--
-- Name: idx_files_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_files_status ON synapscale_db.files USING btree (status);


--
-- Name: idx_files_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_files_tenant_id ON synapscale_db.files USING btree (tenant_id);


--
-- Name: idx_files_tenant_user; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_files_tenant_user ON synapscale_db.files USING btree (tenant_id, user_id);


--
-- Name: idx_files_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_files_user_id ON synapscale_db.files USING btree (user_id);


--
-- Name: idx_invoices_due_date; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_invoices_due_date ON synapscale_db.invoices USING btree (due_date);


--
-- Name: idx_invoices_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_invoices_status ON synapscale_db.invoices USING btree (status);


--
-- Name: idx_invoices_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_invoices_tenant_id ON synapscale_db.invoices USING btree (tenant_id);


--
-- Name: idx_kbs_content; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_kbs_content ON synapscale_db.knowledge_bases USING gin (content);


--
-- Name: idx_llms_conversations_agent_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_agent_id ON synapscale_db.llms_conversations USING btree (agent_id);


--
-- Name: idx_llms_conversations_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_status ON synapscale_db.llms_conversations USING btree (status);


--
-- Name: idx_llms_conversations_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_tenant_id ON synapscale_db.llms_conversations USING btree (tenant_id);


--
-- Name: idx_llms_conversations_turns_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_turns_tenant_id ON synapscale_db.llms_conversations_turns USING btree (tenant_id);


--
-- Name: idx_llms_conversations_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_user_id ON synapscale_db.llms_conversations USING btree (user_id);


--
-- Name: idx_llms_conversations_user_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_user_status ON synapscale_db.llms_conversations USING btree (user_id, status);


--
-- Name: idx_llms_conversations_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_conversations_workspace_id ON synapscale_db.llms_conversations USING btree (workspace_id);


--
-- Name: idx_llms_message_feedbacks_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_message_feedbacks_tenant_id ON synapscale_db.message_feedbacks USING btree (tenant_id);


--
-- Name: idx_llms_messages_conv_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_messages_conv_id ON synapscale_db.llms_messages USING btree (conversation_id);


--
-- Name: idx_llms_messages_created_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_messages_created_at ON synapscale_db.llms_messages USING btree (created_at);


--
-- Name: idx_llms_messages_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_messages_status ON synapscale_db.llms_messages USING btree (status);


--
-- Name: idx_llms_messages_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_messages_tenant_id ON synapscale_db.llms_messages USING btree (tenant_id);


--
-- Name: idx_llms_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_status ON synapscale_db.llms USING btree (status);


--
-- Name: idx_llms_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_tenant_id ON synapscale_db.llms USING btree (tenant_id);


--
-- Name: idx_llms_usage_conv_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_usage_conv_id ON synapscale_db.llms_usage_logs USING btree (conversation_id);


--
-- Name: idx_llms_usage_logs_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_usage_logs_status ON synapscale_db.llms_usage_logs USING btree (status);


--
-- Name: idx_llms_usage_logs_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_llms_usage_logs_tenant_id ON synapscale_db.llms_usage_logs USING btree (tenant_id);


--
-- Name: idx_marketplace_components_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_marketplace_components_name ON synapscale_db.marketplace_components USING btree (name);


--
-- Name: idx_marketplace_components_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_marketplace_components_status ON synapscale_db.marketplace_components USING btree (status);


--
-- Name: idx_marketplace_components_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_marketplace_components_tenant_id ON synapscale_db.marketplace_components USING btree (tenant_id);


--
-- Name: idx_messages_conversation_created; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_messages_conversation_created ON synapscale_db.llms_messages USING btree (conversation_id, created_at);


--
-- Name: idx_node_categories_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_node_categories_tenant_id ON synapscale_db.node_categories USING btree (tenant_id);


--
-- Name: idx_node_executions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_node_executions_tenant_id ON synapscale_db.node_executions USING btree (tenant_id);


--
-- Name: idx_node_ratings_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_node_ratings_tenant_id ON synapscale_db.node_ratings USING btree (tenant_id);


--
-- Name: idx_node_templates_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_node_templates_tenant_id ON synapscale_db.node_templates USING btree (tenant_id);


--
-- Name: idx_nodes_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_nodes_status ON synapscale_db.nodes USING btree (status);


--
-- Name: idx_nodes_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_nodes_tenant_id ON synapscale_db.nodes USING btree (tenant_id);


--
-- Name: idx_password_reset_tokens_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_password_reset_tokens_user_id ON synapscale_db.password_reset_tokens USING btree (user_id);


--
-- Name: idx_payment_customers_provider_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_payment_customers_provider_id ON synapscale_db.payment_customers USING btree (provider_id);


--
-- Name: idx_payment_customers_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_payment_customers_tenant_id ON synapscale_db.payment_customers USING btree (tenant_id);


--
-- Name: idx_payment_methods_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_payment_methods_tenant_id ON synapscale_db.payment_methods USING btree (tenant_id);


--
-- Name: idx_plan_entitlements_feature_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_plan_entitlements_feature_id ON synapscale_db.plan_entitlements USING btree (feature_id);


--
-- Name: idx_plan_entitlements_plan_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_plan_entitlements_plan_id ON synapscale_db.plan_entitlements USING btree (plan_id);


--
-- Name: idx_plans_is_active; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_plans_is_active ON synapscale_db.plans USING btree (is_active);


--
-- Name: idx_project_collaborators_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_project_collaborators_tenant_id ON synapscale_db.project_collaborators USING btree (tenant_id);


--
-- Name: idx_project_comments_node_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_project_comments_node_id ON synapscale_db.project_comments USING btree (node_id);


--
-- Name: idx_project_comments_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_project_comments_tenant_id ON synapscale_db.project_comments USING btree (tenant_id);


--
-- Name: idx_project_versions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_project_versions_tenant_id ON synapscale_db.project_versions USING btree (tenant_id);


--
-- Name: idx_rbac_permissions_category; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_rbac_permissions_category ON synapscale_db.rbac_permissions USING btree (category);


--
-- Name: idx_rbac_permissions_key; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_rbac_permissions_key ON synapscale_db.rbac_permissions USING btree (key);


--
-- Name: idx_rbac_role_permissions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_rbac_role_permissions_tenant_id ON synapscale_db.rbac_role_permissions USING btree (tenant_id);


--
-- Name: idx_report_executions_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_report_executions_status ON synapscale_db.report_executions USING btree (status);


--
-- Name: idx_report_executions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_report_executions_tenant_id ON synapscale_db.report_executions USING btree (tenant_id);


--
-- Name: idx_subscriptions_current_period_end; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_subscriptions_current_period_end ON synapscale_db.subscriptions USING btree (current_period_end);


--
-- Name: idx_subscriptions_plan_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_subscriptions_plan_id ON synapscale_db.subscriptions USING btree (plan_id);


--
-- Name: idx_subscriptions_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_subscriptions_status ON synapscale_db.subscriptions USING btree (status);


--
-- Name: idx_subscriptions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_subscriptions_tenant_id ON synapscale_db.subscriptions USING btree (tenant_id);


--
-- Name: idx_system_performance_metrics_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_system_performance_metrics_tenant_id ON synapscale_db.system_performance_metrics USING btree (tenant_id);


--
-- Name: idx_tags_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tags_tenant_id ON synapscale_db.tags USING btree (tenant_id);


--
-- Name: idx_template_collections_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_template_collections_tenant_id ON synapscale_db.template_collections USING btree (tenant_id);


--
-- Name: idx_template_downloads_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_template_downloads_tenant_id ON synapscale_db.template_downloads USING btree (tenant_id);


--
-- Name: idx_template_favorites_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_template_favorites_tenant_id ON synapscale_db.template_favorites USING btree (tenant_id);


--
-- Name: idx_template_reviews_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_template_reviews_tenant_id ON synapscale_db.template_reviews USING btree (tenant_id);


--
-- Name: idx_template_usage_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_template_usage_tenant_id ON synapscale_db.template_usage USING btree (tenant_id);


--
-- Name: idx_tenant_features_feature_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenant_features_feature_id ON synapscale_db.tenant_features USING btree (feature_id);


--
-- Name: idx_tenant_features_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenant_features_tenant_id ON synapscale_db.tenant_features USING btree (tenant_id);


--
-- Name: idx_tenants_enabled_features; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_enabled_features ON synapscale_db.tenants USING gin (enabled_features);


--
-- Name: idx_tenants_language; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_language ON synapscale_db.tenants USING btree (default_language);


--
-- Name: idx_tenants_max_api_calls_per_day; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_max_api_calls_per_day ON synapscale_db.tenants USING btree (max_api_calls_per_day);


--
-- Name: idx_tenants_max_storage_mb; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_max_storage_mb ON synapscale_db.tenants USING btree (max_storage_mb);


--
-- Name: idx_tenants_max_workspaces; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_max_workspaces ON synapscale_db.tenants USING btree (max_workspaces);


--
-- Name: idx_tenants_mfa_required; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_mfa_required ON synapscale_db.tenants USING btree (mfa_required);


--
-- Name: idx_tenants_plan_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_plan_id ON synapscale_db.tenants USING btree (plan_id);


--
-- Name: idx_tenants_slug; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_slug ON synapscale_db.tenants USING btree (slug);


--
-- Name: idx_tenants_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_status ON synapscale_db.tenants USING btree (status);


--
-- Name: idx_tenants_theme; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tenants_theme ON synapscale_db.tenants USING btree (theme);


--
-- Name: idx_tools_base_config; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_tools_base_config ON synapscale_db.tools USING gin (base_config);


--
-- Name: idx_user_behavior_metrics_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_behavior_metrics_tenant_id ON synapscale_db.user_behavior_metrics USING btree (tenant_id);


--
-- Name: idx_user_insights_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_insights_tenant_id ON synapscale_db.user_insights USING btree (tenant_id);


--
-- Name: idx_user_subscriptions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_subscriptions_tenant_id ON synapscale_db.user_subscriptions USING btree (tenant_id);


--
-- Name: idx_user_subscriptions_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_subscriptions_user_id ON synapscale_db.user_subscriptions USING btree (user_id);


--
-- Name: idx_user_tenant_roles_role_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_tenant_roles_role_id ON synapscale_db.user_tenant_roles USING btree (role_id);


--
-- Name: idx_user_tenant_roles_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_tenant_roles_tenant_id ON synapscale_db.user_tenant_roles USING btree (tenant_id);


--
-- Name: idx_user_tenant_roles_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_tenant_roles_user_id ON synapscale_db.user_tenant_roles USING btree (user_id);


--
-- Name: idx_user_variables_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_variables_tenant_id ON synapscale_db.user_variables USING btree (tenant_id);


--
-- Name: idx_user_variables_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_user_variables_user_id ON synapscale_db.user_variables USING btree (user_id);


--
-- Name: idx_users_failed_attempts; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_users_failed_attempts ON synapscale_db.users USING btree (failed_login_attempts) WHERE (failed_login_attempts > 0);


--
-- Name: idx_users_last_login; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_users_last_login ON synapscale_db.users USING btree (last_login_at);


--
-- Name: idx_users_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_users_status ON synapscale_db.users USING btree (status) WHERE ((status)::text <> 'deleted'::text);


--
-- Name: idx_webhook_logs_event_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_webhook_logs_event_type ON synapscale_db.webhook_logs USING btree (event_type);


--
-- Name: idx_webhook_logs_provider_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_webhook_logs_provider_id ON synapscale_db.webhook_logs USING btree (provider_id);


--
-- Name: idx_webhook_logs_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_webhook_logs_status ON synapscale_db.webhook_logs USING btree (status);


--
-- Name: idx_webhook_logs_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_webhook_logs_tenant_id ON synapscale_db.webhook_logs USING btree (tenant_id);


--
-- Name: idx_workflow_connections_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_connections_tenant_id ON synapscale_db.workflow_connections USING btree (tenant_id);


--
-- Name: idx_workflow_execution_metrics_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_execution_metrics_tenant_id ON synapscale_db.workflow_execution_metrics USING btree (tenant_id);


--
-- Name: idx_workflow_execution_queue_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_execution_queue_tenant_id ON synapscale_db.workflow_execution_queue USING btree (tenant_id);


--
-- Name: idx_workflow_executions_created_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_executions_created_at ON synapscale_db.workflow_executions USING btree (created_at);


--
-- Name: idx_workflow_executions_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_executions_status ON synapscale_db.workflow_executions USING btree (status);


--
-- Name: idx_workflow_executions_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_executions_tenant_id ON synapscale_db.workflow_executions USING btree (tenant_id);


--
-- Name: idx_workflow_executions_tenant_workflow; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_executions_tenant_workflow ON synapscale_db.workflow_executions USING btree (tenant_id, workflow_id);


--
-- Name: idx_workflow_nodes_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_nodes_tenant_id ON synapscale_db.workflow_nodes USING btree (tenant_id);


--
-- Name: idx_workflow_templates_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflow_templates_tenant_id ON synapscale_db.workflow_templates USING btree (tenant_id);


--
-- Name: idx_workflows_definition_connections; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_definition_connections ON synapscale_db.workflows USING gin (((definition -> 'connections'::text)));


--
-- Name: idx_workflows_definition_nodes; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_definition_nodes ON synapscale_db.workflows USING gin (((definition -> 'nodes'::text)));


--
-- Name: idx_workflows_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_name ON synapscale_db.workflows USING btree (name);


--
-- Name: idx_workflows_priority; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_priority ON synapscale_db.workflows USING btree (priority);


--
-- Name: idx_workflows_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_status ON synapscale_db.workflows USING btree (status);


--
-- Name: idx_workflows_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_tenant_id ON synapscale_db.workflows USING btree (tenant_id);


--
-- Name: idx_workflows_tenant_user; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_tenant_user ON synapscale_db.workflows USING btree (tenant_id, user_id);


--
-- Name: idx_workflows_tenant_workspace; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_tenant_workspace ON synapscale_db.workflows USING btree (tenant_id, workspace_id);


--
-- Name: idx_workflows_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workflows_user_id ON synapscale_db.workflows USING btree (user_id);


--
-- Name: idx_workspace_activities_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_activities_tenant_id ON synapscale_db.workspace_activities USING btree (tenant_id);


--
-- Name: idx_workspace_features_feature_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_features_feature_id ON synapscale_db.workspace_features USING btree (feature_id);


--
-- Name: idx_workspace_features_is_enabled; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_features_is_enabled ON synapscale_db.workspace_features USING btree (is_enabled);


--
-- Name: idx_workspace_features_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_features_tenant_id ON synapscale_db.workspace_features USING btree (tenant_id);


--
-- Name: idx_workspace_features_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_features_workspace_id ON synapscale_db.workspace_features USING btree (workspace_id);


--
-- Name: idx_workspace_invitations_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_invitations_status ON synapscale_db.workspace_invitations USING btree (status);


--
-- Name: idx_workspace_invitations_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_invitations_tenant_id ON synapscale_db.workspace_invitations USING btree (tenant_id);


--
-- Name: idx_workspace_members_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_members_status ON synapscale_db.workspace_members USING btree (status);


--
-- Name: idx_workspace_members_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_members_tenant_id ON synapscale_db.workspace_members USING btree (tenant_id);


--
-- Name: idx_workspace_members_workspace_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_members_workspace_status ON synapscale_db.workspace_members USING btree (workspace_id, status);


--
-- Name: idx_workspace_projects_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_projects_status ON synapscale_db.workspace_projects USING btree (status);


--
-- Name: idx_workspace_projects_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspace_projects_tenant_id ON synapscale_db.workspace_projects USING btree (tenant_id);


--
-- Name: idx_workspaces_api_calls_today; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspaces_api_calls_today ON synapscale_db.workspaces USING btree (api_calls_today);


--
-- Name: idx_workspaces_email_notifications; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspaces_email_notifications ON synapscale_db.workspaces USING btree (email_notifications);


--
-- Name: idx_workspaces_last_api_reset_daily; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspaces_last_api_reset_daily ON synapscale_db.workspaces USING btree (last_api_reset_daily);


--
-- Name: idx_workspaces_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspaces_status ON synapscale_db.workspaces USING btree (status);


--
-- Name: idx_workspaces_tenant_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX idx_workspaces_tenant_id ON synapscale_db.workspaces USING btree (tenant_id);


--
-- Name: ix_billing_events_created_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_billing_events_created_at ON synapscale_db.billing_events USING btree (created_at);


--
-- Name: ix_billing_events_event_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_billing_events_event_type ON synapscale_db.billing_events USING btree (event_type);


--
-- Name: ix_billing_events_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_billing_events_status ON synapscale_db.billing_events USING btree (status);


--
-- Name: ix_billing_events_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_billing_events_user_id ON synapscale_db.billing_events USING btree (user_id);


--
-- Name: ix_billing_events_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_billing_events_workspace_id ON synapscale_db.billing_events USING btree (workspace_id);


--
-- Name: ix_conversation_llms_conversation_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_conversation_llms_conversation_id ON synapscale_db.llms_conversations_turns USING btree (conversation_id);


--
-- Name: ix_conversation_llms_llm_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_conversation_llms_llm_id ON synapscale_db.llms_conversations_turns USING btree (llm_id);


--
-- Name: ix_llms_is_active; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_llms_is_active ON synapscale_db.llms USING btree (is_active);


--
-- Name: ix_llms_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_llms_name ON synapscale_db.llms USING btree (name);


--
-- Name: ix_llms_provider; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_llms_provider ON synapscale_db.llms USING btree (provider);


--
-- Name: ix_message_feedbacks_message_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_message_feedbacks_message_id ON synapscale_db.message_feedbacks USING btree (message_id);


--
-- Name: ix_message_feedbacks_rating_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_message_feedbacks_rating_type ON synapscale_db.message_feedbacks USING btree (rating_type);


--
-- Name: ix_message_feedbacks_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_message_feedbacks_user_id ON synapscale_db.message_feedbacks USING btree (user_id);


--
-- Name: ix_public_agents_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_agents_workspace_id ON synapscale_db.agents USING btree (workspace_id);


--
-- Name: ix_public_analytics_dashboards_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_dashboards_user_id ON synapscale_db.analytics_dashboards USING btree (user_id);


--
-- Name: ix_public_analytics_dashboards_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_dashboards_workspace_id ON synapscale_db.analytics_dashboards USING btree (workspace_id);


--
-- Name: ix_public_analytics_events_action; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_action ON synapscale_db.analytics_events USING btree (action);


--
-- Name: ix_public_analytics_events_anonymous_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_anonymous_id ON synapscale_db.analytics_events USING btree (anonymous_id);


--
-- Name: ix_public_analytics_events_category; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_category ON synapscale_db.analytics_events USING btree (category);


--
-- Name: ix_public_analytics_events_event_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_public_analytics_events_event_id ON synapscale_db.analytics_events USING btree (event_id);


--
-- Name: ix_public_analytics_events_label; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_label ON synapscale_db.analytics_events USING btree (label);


--
-- Name: ix_public_analytics_events_project_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_project_id ON synapscale_db.analytics_events USING btree (project_id);


--
-- Name: ix_public_analytics_events_workflow_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_workflow_id ON synapscale_db.analytics_events USING btree (workflow_id);


--
-- Name: ix_public_analytics_events_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_analytics_events_workspace_id ON synapscale_db.analytics_events USING btree (workspace_id);


--
-- Name: ix_public_business_metrics_date; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_business_metrics_date ON synapscale_db.business_metrics USING btree (date);


--
-- Name: ix_public_business_metrics_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_business_metrics_id ON synapscale_db.business_metrics USING btree (id);


--
-- Name: ix_public_component_downloads_component_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_downloads_component_id ON synapscale_db.component_downloads USING btree (component_id);


--
-- Name: ix_public_component_downloads_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_downloads_user_id ON synapscale_db.component_downloads USING btree (user_id);


--
-- Name: ix_public_component_purchases_component_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_purchases_component_id ON synapscale_db.component_purchases USING btree (component_id);


--
-- Name: ix_public_component_purchases_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_purchases_user_id ON synapscale_db.component_purchases USING btree (user_id);


--
-- Name: ix_public_component_ratings_component_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_ratings_component_id ON synapscale_db.component_ratings USING btree (component_id);


--
-- Name: ix_public_component_ratings_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_ratings_user_id ON synapscale_db.component_ratings USING btree (user_id);


--
-- Name: ix_public_component_versions_component_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_component_versions_component_id ON synapscale_db.component_versions USING btree (component_id);


--
-- Name: ix_public_custom_reports_category; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_custom_reports_category ON synapscale_db.custom_reports USING btree (category);


--
-- Name: ix_public_custom_reports_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_custom_reports_user_id ON synapscale_db.custom_reports USING btree (user_id);


--
-- Name: ix_public_custom_reports_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_custom_reports_workspace_id ON synapscale_db.custom_reports USING btree (workspace_id);


--
-- Name: ix_public_execution_metrics_context; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_context ON synapscale_db.workflow_execution_metrics USING btree (context);


--
-- Name: ix_public_execution_metrics_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_id ON synapscale_db.workflow_execution_metrics USING btree (id);


--
-- Name: ix_public_execution_metrics_measured_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_measured_at ON synapscale_db.workflow_execution_metrics USING btree (measured_at);


--
-- Name: ix_public_execution_metrics_metric_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_metric_name ON synapscale_db.workflow_execution_metrics USING btree (metric_name);


--
-- Name: ix_public_execution_metrics_metric_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_metric_type ON synapscale_db.workflow_execution_metrics USING btree (metric_type);


--
-- Name: ix_public_execution_metrics_node_execution_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_node_execution_id ON synapscale_db.workflow_execution_metrics USING btree (node_execution_id);


--
-- Name: ix_public_execution_metrics_workflow_execution_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_metrics_workflow_execution_id ON synapscale_db.workflow_execution_metrics USING btree (workflow_execution_id);


--
-- Name: ix_public_execution_queue_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_id ON synapscale_db.workflow_execution_queue USING btree (id);


--
-- Name: ix_public_execution_queue_priority; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_priority ON synapscale_db.workflow_execution_queue USING btree (priority);


--
-- Name: ix_public_execution_queue_queue_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_public_execution_queue_queue_id ON synapscale_db.workflow_execution_queue USING btree (queue_id);


--
-- Name: ix_public_execution_queue_scheduled_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_scheduled_at ON synapscale_db.workflow_execution_queue USING btree (scheduled_at);


--
-- Name: ix_public_execution_queue_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_status ON synapscale_db.workflow_execution_queue USING btree (status);


--
-- Name: ix_public_execution_queue_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_user_id ON synapscale_db.workflow_execution_queue USING btree (user_id);


--
-- Name: ix_public_execution_queue_worker_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_worker_id ON synapscale_db.workflow_execution_queue USING btree (worker_id);


--
-- Name: ix_public_execution_queue_workflow_execution_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_execution_queue_workflow_execution_id ON synapscale_db.workflow_execution_queue USING btree (workflow_execution_id);


--
-- Name: ix_public_marketplace_components_subcategory; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_marketplace_components_subcategory ON synapscale_db.marketplace_components USING btree (subcategory);


--
-- Name: ix_public_node_executions_execution_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_execution_id ON synapscale_db.node_executions USING btree (execution_id);


--
-- Name: ix_public_node_executions_execution_order; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_execution_order ON synapscale_db.node_executions USING btree (execution_order);


--
-- Name: ix_public_node_executions_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_id ON synapscale_db.node_executions USING btree (id);


--
-- Name: ix_public_node_executions_node_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_node_id ON synapscale_db.node_executions USING btree (node_id);


--
-- Name: ix_public_node_executions_node_key; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_node_key ON synapscale_db.node_executions USING btree (node_key);


--
-- Name: ix_public_node_executions_node_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_node_type ON synapscale_db.node_executions USING btree (node_type);


--
-- Name: ix_public_node_executions_workflow_execution_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_node_executions_workflow_execution_id ON synapscale_db.node_executions USING btree (workflow_execution_id);


--
-- Name: ix_public_nodes_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_nodes_user_id ON synapscale_db.nodes USING btree (user_id);


--
-- Name: ix_public_nodes_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_nodes_workspace_id ON synapscale_db.nodes USING btree (workspace_id);


--
-- Name: ix_public_project_collaborators_project_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_collaborators_project_id ON synapscale_db.project_collaborators USING btree (project_id);


--
-- Name: ix_public_project_collaborators_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_collaborators_user_id ON synapscale_db.project_collaborators USING btree (user_id);


--
-- Name: ix_public_project_comments_parent_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_comments_parent_id ON synapscale_db.project_comments USING btree (parent_id);


--
-- Name: ix_public_project_comments_project_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_comments_project_id ON synapscale_db.project_comments USING btree (project_id);


--
-- Name: ix_public_project_comments_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_comments_user_id ON synapscale_db.project_comments USING btree (user_id);


--
-- Name: ix_public_project_versions_project_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_versions_project_id ON synapscale_db.project_versions USING btree (project_id);


--
-- Name: ix_public_project_versions_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_project_versions_user_id ON synapscale_db.project_versions USING btree (user_id);


--
-- Name: ix_public_report_executions_report_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_report_executions_report_id ON synapscale_db.report_executions USING btree (report_id);


--
-- Name: ix_public_report_executions_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_report_executions_user_id ON synapscale_db.report_executions USING btree (user_id);


--
-- Name: ix_public_system_performance_metrics_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_system_performance_metrics_id ON synapscale_db.system_performance_metrics USING btree (id);


--
-- Name: ix_public_system_performance_metrics_metric_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_system_performance_metrics_metric_name ON synapscale_db.system_performance_metrics USING btree (metric_name);


--
-- Name: ix_public_system_performance_metrics_service; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_system_performance_metrics_service ON synapscale_db.system_performance_metrics USING btree (service);


--
-- Name: ix_public_system_performance_metrics_timestamp; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_system_performance_metrics_timestamp ON synapscale_db.system_performance_metrics USING btree ("timestamp");


--
-- Name: ix_public_template_collections_collection_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_public_template_collections_collection_id ON synapscale_db.template_collections USING btree (collection_id);


--
-- Name: ix_public_template_collections_creator_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_collections_creator_id ON synapscale_db.template_collections USING btree (creator_id);


--
-- Name: ix_public_template_collections_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_collections_id ON synapscale_db.template_collections USING btree (id);


--
-- Name: ix_public_template_downloads_downloaded_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_downloads_downloaded_at ON synapscale_db.template_downloads USING btree (downloaded_at);


--
-- Name: ix_public_template_downloads_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_downloads_id ON synapscale_db.template_downloads USING btree (id);


--
-- Name: ix_public_template_downloads_template_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_downloads_template_id ON synapscale_db.template_downloads USING btree (template_id);


--
-- Name: ix_public_template_downloads_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_downloads_user_id ON synapscale_db.template_downloads USING btree (user_id);


--
-- Name: ix_public_template_favorites_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_favorites_id ON synapscale_db.template_favorites USING btree (id);


--
-- Name: ix_public_template_favorites_template_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_favorites_template_id ON synapscale_db.template_favorites USING btree (template_id);


--
-- Name: ix_public_template_favorites_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_favorites_user_id ON synapscale_db.template_favorites USING btree (user_id);


--
-- Name: ix_public_template_reviews_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_reviews_id ON synapscale_db.template_reviews USING btree (id);


--
-- Name: ix_public_template_reviews_template_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_reviews_template_id ON synapscale_db.template_reviews USING btree (template_id);


--
-- Name: ix_public_template_reviews_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_reviews_user_id ON synapscale_db.template_reviews USING btree (user_id);


--
-- Name: ix_public_template_usage_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_usage_id ON synapscale_db.template_usage USING btree (id);


--
-- Name: ix_public_template_usage_template_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_usage_template_id ON synapscale_db.template_usage USING btree (template_id);


--
-- Name: ix_public_template_usage_used_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_usage_used_at ON synapscale_db.template_usage USING btree (used_at);


--
-- Name: ix_public_template_usage_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_usage_user_id ON synapscale_db.template_usage USING btree (user_id);


--
-- Name: ix_public_template_usage_workflow_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_template_usage_workflow_id ON synapscale_db.template_usage USING btree (workflow_id);


--
-- Name: ix_public_user_behavior_metrics_date; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_user_behavior_metrics_date ON synapscale_db.user_behavior_metrics USING btree (date);


--
-- Name: ix_public_user_behavior_metrics_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_user_behavior_metrics_user_id ON synapscale_db.user_behavior_metrics USING btree (user_id);


--
-- Name: ix_public_user_insights_category; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_user_insights_category ON synapscale_db.user_insights USING btree (category);


--
-- Name: ix_public_user_insights_insight_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_user_insights_insight_type ON synapscale_db.user_insights USING btree (insight_type);


--
-- Name: ix_public_user_insights_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_user_insights_user_id ON synapscale_db.user_insights USING btree (user_id);


--
-- Name: ix_public_workflow_connections_workflow_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_connections_workflow_id ON synapscale_db.workflow_connections USING btree (workflow_id);


--
-- Name: ix_public_workflow_executions_execution_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_public_workflow_executions_execution_id ON synapscale_db.workflow_executions USING btree (execution_id);


--
-- Name: ix_public_workflow_executions_priority; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_executions_priority ON synapscale_db.workflow_executions USING btree (priority);


--
-- Name: ix_public_workflow_executions_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_executions_user_id ON synapscale_db.workflow_executions USING btree (user_id);


--
-- Name: ix_public_workflow_nodes_node_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_nodes_node_id ON synapscale_db.workflow_nodes USING btree (node_id);


--
-- Name: ix_public_workflow_nodes_workflow_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_nodes_workflow_id ON synapscale_db.workflow_nodes USING btree (workflow_id);


--
-- Name: ix_public_workflow_templates_download_count; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_templates_download_count ON synapscale_db.workflow_templates USING btree (download_count);


--
-- Name: ix_public_workflow_templates_is_verified; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_templates_is_verified ON synapscale_db.workflow_templates USING btree (is_verified);


--
-- Name: ix_public_workflow_templates_license_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_templates_license_type ON synapscale_db.workflow_templates USING btree (license_type);


--
-- Name: ix_public_workflow_templates_original_workflow_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_templates_original_workflow_id ON synapscale_db.workflow_templates USING btree (original_workflow_id);


--
-- Name: ix_public_workflow_templates_published_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_templates_published_at ON synapscale_db.workflow_templates USING btree (published_at);


--
-- Name: ix_public_workflow_templates_status; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflow_templates_status ON synapscale_db.workflow_templates USING btree (status);


--
-- Name: ix_public_workflows_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workflows_workspace_id ON synapscale_db.workflows USING btree (workspace_id);


--
-- Name: ix_public_workspace_activities_action; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_activities_action ON synapscale_db.workspace_activities USING btree (action);


--
-- Name: ix_public_workspace_activities_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_activities_user_id ON synapscale_db.workspace_activities USING btree (user_id);


--
-- Name: ix_public_workspace_activities_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_activities_workspace_id ON synapscale_db.workspace_activities USING btree (workspace_id);


--
-- Name: ix_public_workspace_invitations_email; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_invitations_email ON synapscale_db.workspace_invitations USING btree (email);


--
-- Name: ix_public_workspace_invitations_invited_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_invitations_invited_user_id ON synapscale_db.workspace_invitations USING btree (invited_user_id);


--
-- Name: ix_public_workspace_invitations_inviter_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_invitations_inviter_id ON synapscale_db.workspace_invitations USING btree (inviter_id);


--
-- Name: ix_public_workspace_invitations_token; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_public_workspace_invitations_token ON synapscale_db.workspace_invitations USING btree (token);


--
-- Name: ix_public_workspace_invitations_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_invitations_workspace_id ON synapscale_db.workspace_invitations USING btree (workspace_id);


--
-- Name: ix_public_workspace_members_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_members_id ON synapscale_db.workspace_members USING btree (id);


--
-- Name: ix_public_workspace_members_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_members_user_id ON synapscale_db.workspace_members USING btree (user_id);


--
-- Name: ix_public_workspace_members_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_members_workspace_id ON synapscale_db.workspace_members USING btree (workspace_id);


--
-- Name: ix_public_workspace_projects_workflow_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_projects_workflow_id ON synapscale_db.workspace_projects USING btree (workflow_id);


--
-- Name: ix_public_workspace_projects_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_public_workspace_projects_workspace_id ON synapscale_db.workspace_projects USING btree (workspace_id);


--
-- Name: ix_public_workspaces_slug; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_public_workspaces_slug ON synapscale_db.workspaces USING btree (slug);


--
-- Name: ix_synapscale_db_email_verification_tokens_token; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_synapscale_db_email_verification_tokens_token ON synapscale_db.email_verification_tokens USING btree (token);


--
-- Name: ix_synapscale_db_email_verification_tokens_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_synapscale_db_email_verification_tokens_user_id ON synapscale_db.email_verification_tokens USING btree (user_id);


--
-- Name: ix_synapscale_db_node_ratings_node_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_synapscale_db_node_ratings_node_id ON synapscale_db.node_ratings USING btree (node_id);


--
-- Name: ix_synapscale_db_node_ratings_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_synapscale_db_node_ratings_user_id ON synapscale_db.node_ratings USING btree (user_id);


--
-- Name: ix_synapscale_db_password_reset_tokens_token; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_synapscale_db_password_reset_tokens_token ON synapscale_db.password_reset_tokens USING btree (token);


--
-- Name: ix_synapscale_db_password_reset_tokens_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_synapscale_db_password_reset_tokens_user_id ON synapscale_db.password_reset_tokens USING btree (user_id);


--
-- Name: ix_synapscale_db_refresh_tokens_token; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_synapscale_db_refresh_tokens_token ON synapscale_db.refresh_tokens USING btree (token);


--
-- Name: ix_synapscale_db_refresh_tokens_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_synapscale_db_refresh_tokens_user_id ON synapscale_db.refresh_tokens USING btree (user_id);


--
-- Name: ix_synapscale_db_users_email; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_synapscale_db_users_email ON synapscale_db.users USING btree (email);


--
-- Name: ix_synapscale_db_users_username; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE UNIQUE INDEX ix_synapscale_db_users_username ON synapscale_db.users USING btree (username);


--
-- Name: ix_tags_created_by_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_tags_created_by_user_id ON synapscale_db.tags USING btree (created_by_user_id);


--
-- Name: ix_tags_is_system_tag; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_tags_is_system_tag ON synapscale_db.tags USING btree (is_system_tag);


--
-- Name: ix_tags_tag_category; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_tags_tag_category ON synapscale_db.tags USING btree (tag_category);


--
-- Name: ix_tags_tag_name; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_tags_tag_name ON synapscale_db.tags USING btree (tag_name);


--
-- Name: ix_tags_target_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_tags_target_id ON synapscale_db.tags USING btree (target_id);


--
-- Name: ix_tags_target_type; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_tags_target_type ON synapscale_db.tags USING btree (target_type);


--
-- Name: ix_usage_logs_conversation_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_usage_logs_conversation_id ON synapscale_db.llms_usage_logs USING btree (conversation_id);


--
-- Name: ix_usage_logs_created_at; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_usage_logs_created_at ON synapscale_db.llms_usage_logs USING btree (created_at);


--
-- Name: ix_usage_logs_llm_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_usage_logs_llm_id ON synapscale_db.llms_usage_logs USING btree (llm_id);


--
-- Name: ix_usage_logs_user_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_usage_logs_user_id ON synapscale_db.llms_usage_logs USING btree (user_id);


--
-- Name: ix_usage_logs_workspace_id; Type: INDEX; Schema: synapscale_db; Owner: -
--

CREATE INDEX ix_usage_logs_workspace_id ON synapscale_db.llms_usage_logs USING btree (workspace_id);


--
-- Name: agent_configurations trg_audit_agent_configurations; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_agent_configurations AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.agent_configurations FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: agent_kbs trg_audit_agent_kbs; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_agent_kbs AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.agent_kbs FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: agent_models trg_audit_agent_models; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_agent_models AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.agent_models FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: agent_tools trg_audit_agent_tools; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_agent_tools AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.agent_tools FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: agent_triggers trg_audit_agent_triggers; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_agent_triggers AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.agent_triggers FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: knowledge_bases trg_audit_knowledge_bases; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_knowledge_bases AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.knowledge_bases FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: tools trg_audit_tools; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_audit_tools AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.tools FOR EACH ROW EXECUTE FUNCTION synapscale_db.fn_audit();


--
-- Name: agent_configurations trg_updated_at_agent_configurations; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_updated_at_agent_configurations BEFORE UPDATE ON synapscale_db.agent_configurations FOR EACH ROW EXECUTE FUNCTION synapscale_db.update_timestamp();


--
-- Name: knowledge_bases trg_updated_at_knowledge_bases; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_updated_at_knowledge_bases BEFORE UPDATE ON synapscale_db.knowledge_bases FOR EACH ROW EXECUTE FUNCTION synapscale_db.update_timestamp();


--
-- Name: tools trg_updated_at_tools; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trg_updated_at_tools BEFORE UPDATE ON synapscale_db.tools FOR EACH ROW EXECUTE FUNCTION synapscale_db.update_timestamp();


--
-- Name: workspaces trigger_check_workspace_limits; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_check_workspace_limits BEFORE INSERT ON synapscale_db.workspaces FOR EACH ROW EXECUTE FUNCTION synapscale_db.check_workspace_limits();


--
-- Name: plans trigger_plans_sync; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_plans_sync AFTER UPDATE ON synapscale_db.plans FOR EACH STATEMENT EXECUTE FUNCTION synapscale_db.refresh_tenant_plan_sync();


--
-- Name: subscriptions trigger_subscriptions_sync; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_subscriptions_sync AFTER INSERT OR UPDATE ON synapscale_db.subscriptions FOR EACH STATEMENT EXECUTE FUNCTION synapscale_db.refresh_tenant_plan_sync();


--
-- Name: subscriptions trigger_sync_on_subscription_change; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_sync_on_subscription_change AFTER INSERT OR UPDATE ON synapscale_db.subscriptions FOR EACH ROW EXECUTE FUNCTION synapscale_db.sync_tenant_from_plan();


--
-- Name: files trigger_sync_storage_usage; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_sync_storage_usage AFTER INSERT OR DELETE OR UPDATE ON synapscale_db.files FOR EACH ROW EXECUTE FUNCTION synapscale_db.sync_storage_usage();


--
-- Name: workspace_members trigger_validate_member_limits; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_validate_member_limits BEFORE INSERT OR DELETE ON synapscale_db.workspace_members FOR EACH ROW EXECUTE FUNCTION synapscale_db.validate_workspace_member_limits();


--
-- Name: workspace_projects trigger_validate_project_limits; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_validate_project_limits BEFORE INSERT OR DELETE ON synapscale_db.workspace_projects FOR EACH ROW EXECUTE FUNCTION synapscale_db.validate_workspace_project_limits();


--
-- Name: workspaces trigger_validate_workspace_limits; Type: TRIGGER; Schema: synapscale_db; Owner: -
--

CREATE TRIGGER trigger_validate_workspace_limits BEFORE INSERT OR UPDATE ON synapscale_db.workspaces FOR EACH ROW EXECUTE FUNCTION synapscale_db.validate_workspace_limits();


--
-- Name: agent_acl agent_acl_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_acl
    ADD CONSTRAINT agent_acl_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON DELETE CASCADE;


--
-- Name: agent_acl agent_acl_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_acl
    ADD CONSTRAINT agent_acl_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: agent_configurations agent_configurations_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_configurations
    ADD CONSTRAINT agent_configurations_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON DELETE CASCADE;


--
-- Name: agent_configurations agent_configurations_created_by_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_configurations
    ADD CONSTRAINT agent_configurations_created_by_fkey FOREIGN KEY (created_by) REFERENCES synapscale_db.users(id);


--
-- Name: agent_error_logs agent_error_logs_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_error_logs
    ADD CONSTRAINT agent_error_logs_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id);


--
-- Name: agent_hierarchy agent_hierarchy_ancestor_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_hierarchy
    ADD CONSTRAINT agent_hierarchy_ancestor_fkey FOREIGN KEY (ancestor) REFERENCES synapscale_db.agents(id);


--
-- Name: agent_hierarchy agent_hierarchy_descendant_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_hierarchy
    ADD CONSTRAINT agent_hierarchy_descendant_fkey FOREIGN KEY (descendant) REFERENCES synapscale_db.agents(id);


--
-- Name: agent_kbs agent_kbs_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_kbs
    ADD CONSTRAINT agent_kbs_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON DELETE CASCADE;


--
-- Name: agent_kbs agent_kbs_kb_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_kbs
    ADD CONSTRAINT agent_kbs_kb_id_fkey FOREIGN KEY (kb_id) REFERENCES synapscale_db.knowledge_bases(kb_id) ON DELETE CASCADE;


--
-- Name: agent_models agent_models_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_models
    ADD CONSTRAINT agent_models_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON DELETE CASCADE;


--
-- Name: agent_models agent_models_llm_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_models
    ADD CONSTRAINT agent_models_llm_id_fkey FOREIGN KEY (llm_id) REFERENCES synapscale_db.llms(id) ON DELETE CASCADE;


--
-- Name: agent_quotas agent_quotas_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_quotas
    ADD CONSTRAINT agent_quotas_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id);


--
-- Name: agent_quotas agent_quotas_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_quotas
    ADD CONSTRAINT agent_quotas_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id);


--
-- Name: agent_tools agent_tools_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_tools
    ADD CONSTRAINT agent_tools_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON DELETE CASCADE;


--
-- Name: agent_tools agent_tools_tool_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_tools
    ADD CONSTRAINT agent_tools_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES synapscale_db.tools(tool_id) ON DELETE CASCADE;


--
-- Name: agent_triggers agent_triggers_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_triggers
    ADD CONSTRAINT agent_triggers_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON DELETE CASCADE;


--
-- Name: agent_usage_metrics agent_usage_metrics_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agent_usage_metrics
    ADD CONSTRAINT agent_usage_metrics_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id);


--
-- Name: agents agents_current_config_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agents
    ADD CONSTRAINT agents_current_config_fkey FOREIGN KEY (current_config) REFERENCES synapscale_db.agent_configurations(config_id);


--
-- Name: agents agents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agents
    ADD CONSTRAINT agents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: agents agents_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agents
    ADD CONSTRAINT agents_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: agents agents_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.agents
    ADD CONSTRAINT agents_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE CASCADE;


--
-- Name: analytics_alerts analytics_alerts_owner_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_alerts
    ADD CONSTRAINT analytics_alerts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_alerts analytics_alerts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_alerts
    ADD CONSTRAINT analytics_alerts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_dashboards analytics_dashboards_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_dashboards
    ADD CONSTRAINT analytics_dashboards_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_dashboards analytics_dashboards_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_dashboards
    ADD CONSTRAINT analytics_dashboards_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: analytics_events analytics_events_project_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_events
    ADD CONSTRAINT analytics_events_project_id_fkey FOREIGN KEY (project_id) REFERENCES synapscale_db.workspace_projects(id);


--
-- Name: analytics_events analytics_events_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_events
    ADD CONSTRAINT analytics_events_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: analytics_events analytics_events_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_events
    ADD CONSTRAINT analytics_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: analytics_exports analytics_exports_owner_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_exports
    ADD CONSTRAINT analytics_exports_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_exports analytics_exports_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_exports
    ADD CONSTRAINT analytics_exports_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_metrics analytics_metrics_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_metrics
    ADD CONSTRAINT analytics_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_reports analytics_reports_owner_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_reports
    ADD CONSTRAINT analytics_reports_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: analytics_reports analytics_reports_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.analytics_reports
    ADD CONSTRAINT analytics_reports_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: audit_log audit_log_changed_by_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.audit_log
    ADD CONSTRAINT audit_log_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES synapscale_db.users(id);


--
-- Name: billing_events billing_events_related_message_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.billing_events
    ADD CONSTRAINT billing_events_related_message_id_fkey FOREIGN KEY (related_message_id) REFERENCES synapscale_db.llms_messages(id) ON DELETE SET NULL;


--
-- Name: billing_events billing_events_related_usage_log_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.billing_events
    ADD CONSTRAINT billing_events_related_usage_log_id_fkey FOREIGN KEY (related_usage_log_id) REFERENCES synapscale_db.llms_usage_logs(id) ON DELETE SET NULL;


--
-- Name: billing_events billing_events_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.billing_events
    ADD CONSTRAINT billing_events_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: billing_events billing_events_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.billing_events
    ADD CONSTRAINT billing_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: billing_events billing_events_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.billing_events
    ADD CONSTRAINT billing_events_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: business_metrics business_metrics_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.business_metrics
    ADD CONSTRAINT business_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: campaign_contacts campaign_contacts_campaign_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaign_contacts
    ADD CONSTRAINT campaign_contacts_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES synapscale_db.campaigns(id) ON DELETE CASCADE;


--
-- Name: campaign_contacts campaign_contacts_contact_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaign_contacts
    ADD CONSTRAINT campaign_contacts_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES synapscale_db.contacts(id) ON DELETE CASCADE;


--
-- Name: campaign_contacts campaign_contacts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaign_contacts
    ADD CONSTRAINT campaign_contacts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: campaigns campaigns_created_by_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaigns
    ADD CONSTRAINT campaigns_created_by_fkey FOREIGN KEY (created_by) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: campaigns campaigns_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.campaigns
    ADD CONSTRAINT campaigns_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: component_downloads component_downloads_component_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_downloads
    ADD CONSTRAINT component_downloads_component_id_fkey FOREIGN KEY (component_id) REFERENCES synapscale_db.marketplace_components(id);


--
-- Name: component_downloads component_downloads_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_downloads
    ADD CONSTRAINT component_downloads_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: component_downloads component_downloads_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_downloads
    ADD CONSTRAINT component_downloads_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: component_purchases component_purchases_component_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_purchases
    ADD CONSTRAINT component_purchases_component_id_fkey FOREIGN KEY (component_id) REFERENCES synapscale_db.marketplace_components(id);


--
-- Name: component_purchases component_purchases_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_purchases
    ADD CONSTRAINT component_purchases_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: component_purchases component_purchases_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_purchases
    ADD CONSTRAINT component_purchases_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: component_ratings component_ratings_component_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_ratings
    ADD CONSTRAINT component_ratings_component_id_fkey FOREIGN KEY (component_id) REFERENCES synapscale_db.marketplace_components(id);


--
-- Name: component_ratings component_ratings_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_ratings
    ADD CONSTRAINT component_ratings_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: component_ratings component_ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_ratings
    ADD CONSTRAINT component_ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: component_versions component_versions_component_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_versions
    ADD CONSTRAINT component_versions_component_id_fkey FOREIGN KEY (component_id) REFERENCES synapscale_db.marketplace_components(id);


--
-- Name: component_versions component_versions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.component_versions
    ADD CONSTRAINT component_versions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: contact_events contact_events_contact_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_events
    ADD CONSTRAINT contact_events_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES synapscale_db.contacts(id) ON DELETE CASCADE;


--
-- Name: contact_events contact_events_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_events
    ADD CONSTRAINT contact_events_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: contact_interactions contact_interactions_contact_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_interactions
    ADD CONSTRAINT contact_interactions_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES synapscale_db.contacts(id) ON DELETE CASCADE;


--
-- Name: contact_interactions contact_interactions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_interactions
    ADD CONSTRAINT contact_interactions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: contact_interactions contact_interactions_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_interactions
    ADD CONSTRAINT contact_interactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: contact_list_memberships contact_list_memberships_added_by_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_list_memberships
    ADD CONSTRAINT contact_list_memberships_added_by_fkey FOREIGN KEY (added_by) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: contact_list_memberships contact_list_memberships_contact_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_list_memberships
    ADD CONSTRAINT contact_list_memberships_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES synapscale_db.contacts(id) ON DELETE CASCADE;


--
-- Name: contact_list_memberships contact_list_memberships_list_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_list_memberships
    ADD CONSTRAINT contact_list_memberships_list_id_fkey FOREIGN KEY (list_id) REFERENCES synapscale_db.contact_lists(id) ON DELETE CASCADE;


--
-- Name: contact_list_memberships contact_list_memberships_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_list_memberships
    ADD CONSTRAINT contact_list_memberships_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: contact_lists contact_lists_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_lists
    ADD CONSTRAINT contact_lists_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: contact_notes contact_notes_contact_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_notes
    ADD CONSTRAINT contact_notes_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES synapscale_db.contacts(id) ON DELETE CASCADE;


--
-- Name: contact_notes contact_notes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_notes
    ADD CONSTRAINT contact_notes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: contact_notes contact_notes_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_notes
    ADD CONSTRAINT contact_notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: contact_sources contact_sources_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_sources
    ADD CONSTRAINT contact_sources_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: contact_tags contact_tags_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contact_tags
    ADD CONSTRAINT contact_tags_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: contacts contacts_source_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contacts
    ADD CONSTRAINT contacts_source_id_fkey FOREIGN KEY (source_id) REFERENCES synapscale_db.contact_sources(id);


--
-- Name: contacts contacts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.contacts
    ADD CONSTRAINT contacts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_conversations_turns conversation_llms_conversation_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations_turns
    ADD CONSTRAINT conversation_llms_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES synapscale_db.llms_conversations(id) ON DELETE CASCADE;


--
-- Name: llms_conversations_turns conversation_llms_llm_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations_turns
    ADD CONSTRAINT conversation_llms_llm_id_fkey FOREIGN KEY (llm_id) REFERENCES synapscale_db.llms(id) ON DELETE CASCADE;


--
-- Name: llms_conversations conversations_agent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations
    ADD CONSTRAINT conversations_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: llms_conversations conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations
    ADD CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: conversion_journeys conversion_journeys_contact_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.conversion_journeys
    ADD CONSTRAINT conversion_journeys_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES synapscale_db.contacts(id) ON DELETE CASCADE;


--
-- Name: conversion_journeys conversion_journeys_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.conversion_journeys
    ADD CONSTRAINT conversion_journeys_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: coupons coupons_created_by_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.coupons
    ADD CONSTRAINT coupons_created_by_fkey FOREIGN KEY (created_by) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: coupons coupons_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.coupons
    ADD CONSTRAINT coupons_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: custom_reports custom_reports_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.custom_reports
    ADD CONSTRAINT custom_reports_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: custom_reports custom_reports_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.custom_reports
    ADD CONSTRAINT custom_reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: custom_reports custom_reports_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.custom_reports
    ADD CONSTRAINT custom_reports_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: email_verification_tokens email_verification_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.email_verification_tokens
    ADD CONSTRAINT email_verification_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: workflow_execution_queue execution_queue_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_queue
    ADD CONSTRAINT execution_queue_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_execution_queue execution_queue_workflow_execution_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_queue
    ADD CONSTRAINT execution_queue_workflow_execution_id_fkey FOREIGN KEY (workflow_execution_id) REFERENCES synapscale_db.workflow_executions(id) ON DELETE SET NULL;


--
-- Name: files files_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.files
    ADD CONSTRAINT files_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: files files_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.files
    ADD CONSTRAINT files_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: llms_conversations_turns fk_conv_turns_conv; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations_turns
    ADD CONSTRAINT fk_conv_turns_conv FOREIGN KEY (conversation_id) REFERENCES synapscale_db.llms_conversations(id) ON DELETE CASCADE;


--
-- Name: llms_conversations_turns fk_conv_turns_llm; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations_turns
    ADD CONSTRAINT fk_conv_turns_llm FOREIGN KEY (llm_id) REFERENCES synapscale_db.llms(id) ON DELETE CASCADE;


--
-- Name: message_feedbacks fk_feedback_msg; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.message_feedbacks
    ADD CONSTRAINT fk_feedback_msg FOREIGN KEY (message_id) REFERENCES synapscale_db.llms_messages(id) ON DELETE CASCADE;


--
-- Name: message_feedbacks fk_feedback_user; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.message_feedbacks
    ADD CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: llms_conversations fk_llms_conversations_agent; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations
    ADD CONSTRAINT fk_llms_conversations_agent FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: llms_conversations fk_llms_conversations_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations
    ADD CONSTRAINT fk_llms_conversations_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_conversations_turns fk_llms_conversations_turns_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations_turns
    ADD CONSTRAINT fk_llms_conversations_turns_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: message_feedbacks fk_llms_message_feedbacks_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.message_feedbacks
    ADD CONSTRAINT fk_llms_message_feedbacks_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_messages fk_llms_messages_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_messages
    ADD CONSTRAINT fk_llms_messages_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs fk_llms_usage_logs_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT fk_llms_usage_logs_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_messages fk_messages_conv; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_messages
    ADD CONSTRAINT fk_messages_conv FOREIGN KEY (conversation_id) REFERENCES synapscale_db.llms_conversations(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: node_templates fk_node_templates_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_templates
    ADD CONSTRAINT fk_node_templates_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: template_collections fk_template_collections_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_collections
    ADD CONSTRAINT fk_template_collections_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: template_downloads fk_template_downloads_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_downloads
    ADD CONSTRAINT fk_template_downloads_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: template_favorites fk_template_favorites_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_favorites
    ADD CONSTRAINT fk_template_favorites_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: template_reviews fk_template_reviews_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_reviews
    ADD CONSTRAINT fk_template_reviews_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: template_usage fk_template_usage_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_usage
    ADD CONSTRAINT fk_template_usage_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: tenants fk_tenants_plan_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenants
    ADD CONSTRAINT fk_tenants_plan_id FOREIGN KEY (plan_id) REFERENCES synapscale_db.plans(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: llms_usage_logs fk_usage_conv; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT fk_usage_conv FOREIGN KEY (conversation_id) REFERENCES synapscale_db.llms_conversations(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs fk_usage_llm; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT fk_usage_llm FOREIGN KEY (llm_id) REFERENCES synapscale_db.llms(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs fk_usage_msg; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT fk_usage_msg FOREIGN KEY (message_id) REFERENCES synapscale_db.llms_messages(id) ON DELETE CASCADE;


--
-- Name: workflow_templates fk_workflow_templates_tenant_id; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_templates
    ADD CONSTRAINT fk_workflow_templates_tenant_id FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: invoices invoices_subscription_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.invoices
    ADD CONSTRAINT invoices_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES synapscale_db.subscriptions(id);


--
-- Name: invoices invoices_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.invoices
    ADD CONSTRAINT invoices_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_conversations llms_conversations_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_conversations
    ADD CONSTRAINT llms_conversations_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: llms llms_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms
    ADD CONSTRAINT llms_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: marketplace_components marketplace_components_author_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.marketplace_components
    ADD CONSTRAINT marketplace_components_author_id_fkey FOREIGN KEY (author_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: marketplace_components marketplace_components_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.marketplace_components
    ADD CONSTRAINT marketplace_components_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: message_feedbacks message_feedbacks_message_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.message_feedbacks
    ADD CONSTRAINT message_feedbacks_message_id_fkey FOREIGN KEY (message_id) REFERENCES synapscale_db.llms_messages(id) ON DELETE CASCADE;


--
-- Name: message_feedbacks message_feedbacks_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.message_feedbacks
    ADD CONSTRAINT message_feedbacks_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: llms_messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES synapscale_db.llms_conversations(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: node_categories node_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_categories
    ADD CONSTRAINT node_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES synapscale_db.node_categories(id);


--
-- Name: node_categories node_categories_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_categories
    ADD CONSTRAINT node_categories_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: node_executions node_executions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_executions
    ADD CONSTRAINT node_executions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: node_executions node_executions_workflow_execution_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_executions
    ADD CONSTRAINT node_executions_workflow_execution_id_fkey FOREIGN KEY (workflow_execution_id) REFERENCES synapscale_db.workflow_executions(id) ON DELETE SET NULL;


--
-- Name: node_ratings node_ratings_node_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_ratings
    ADD CONSTRAINT node_ratings_node_id_fkey FOREIGN KEY (node_id) REFERENCES synapscale_db.nodes(id) ON DELETE CASCADE;


--
-- Name: node_ratings node_ratings_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_ratings
    ADD CONSTRAINT node_ratings_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: node_ratings node_ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.node_ratings
    ADD CONSTRAINT node_ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: nodes nodes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.nodes
    ADD CONSTRAINT nodes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: nodes nodes_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.nodes
    ADD CONSTRAINT nodes_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: nodes nodes_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.nodes
    ADD CONSTRAINT nodes_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: payment_customers payment_customers_provider_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_customers
    ADD CONSTRAINT payment_customers_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES synapscale_db.payment_providers(id) ON DELETE CASCADE;


--
-- Name: payment_customers payment_customers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_customers
    ADD CONSTRAINT payment_customers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: payment_methods payment_methods_customer_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_methods
    ADD CONSTRAINT payment_methods_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES synapscale_db.payment_customers(id) ON DELETE CASCADE;


--
-- Name: payment_methods payment_methods_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.payment_methods
    ADD CONSTRAINT payment_methods_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: plan_entitlements plan_entitlements_feature_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_entitlements
    ADD CONSTRAINT plan_entitlements_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES synapscale_db.features(id) ON DELETE CASCADE;


--
-- Name: plan_entitlements plan_entitlements_plan_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_entitlements
    ADD CONSTRAINT plan_entitlements_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES synapscale_db.plans(id) ON DELETE RESTRICT;


--
-- Name: plan_features plan_features_feature_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_features
    ADD CONSTRAINT plan_features_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES synapscale_db.features(id) ON DELETE CASCADE;


--
-- Name: plan_features plan_features_plan_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_features
    ADD CONSTRAINT plan_features_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES synapscale_db.plans(id) ON DELETE RESTRICT;


--
-- Name: plan_provider_mappings plan_provider_mappings_plan_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_provider_mappings
    ADD CONSTRAINT plan_provider_mappings_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES synapscale_db.plans(id) ON DELETE RESTRICT;


--
-- Name: plan_provider_mappings plan_provider_mappings_provider_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.plan_provider_mappings
    ADD CONSTRAINT plan_provider_mappings_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES synapscale_db.payment_providers(id) ON DELETE CASCADE;


--
-- Name: project_collaborators project_collaborators_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_collaborators
    ADD CONSTRAINT project_collaborators_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: project_collaborators project_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_collaborators
    ADD CONSTRAINT project_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: project_comments project_comments_parent_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_comments
    ADD CONSTRAINT project_comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES synapscale_db.project_comments(id);


--
-- Name: project_comments project_comments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_comments
    ADD CONSTRAINT project_comments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: project_comments project_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_comments
    ADD CONSTRAINT project_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: project_versions project_versions_project_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_versions
    ADD CONSTRAINT project_versions_project_id_fkey FOREIGN KEY (project_id) REFERENCES synapscale_db.workspace_projects(id) ON DELETE SET NULL;


--
-- Name: project_versions project_versions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_versions
    ADD CONSTRAINT project_versions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: project_versions project_versions_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.project_versions
    ADD CONSTRAINT project_versions_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: rbac_permissions rbac_permissions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_permissions
    ADD CONSTRAINT rbac_permissions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: rbac_role_permissions rbac_role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_role_permissions
    ADD CONSTRAINT rbac_role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES synapscale_db.rbac_permissions(id) ON DELETE CASCADE;


--
-- Name: rbac_role_permissions rbac_role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_role_permissions
    ADD CONSTRAINT rbac_role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES synapscale_db.rbac_roles(id) ON DELETE CASCADE;


--
-- Name: rbac_role_permissions rbac_role_permissions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_role_permissions
    ADD CONSTRAINT rbac_role_permissions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: rbac_roles rbac_roles_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.rbac_roles
    ADD CONSTRAINT rbac_roles_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: report_executions report_executions_report_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.report_executions
    ADD CONSTRAINT report_executions_report_id_fkey FOREIGN KEY (report_id) REFERENCES synapscale_db.custom_reports(id) ON DELETE SET NULL;


--
-- Name: report_executions report_executions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.report_executions
    ADD CONSTRAINT report_executions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: report_executions report_executions_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.report_executions
    ADD CONSTRAINT report_executions_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_coupon_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.subscriptions
    ADD CONSTRAINT subscriptions_coupon_id_fkey FOREIGN KEY (coupon_id) REFERENCES synapscale_db.coupons(id);


--
-- Name: subscriptions subscriptions_payment_method_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.subscriptions
    ADD CONSTRAINT subscriptions_payment_method_id_fkey FOREIGN KEY (payment_method_id) REFERENCES synapscale_db.payment_methods(id);


--
-- Name: subscriptions subscriptions_plan_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.subscriptions
    ADD CONSTRAINT subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES synapscale_db.plans(id) ON DELETE RESTRICT;


--
-- Name: subscriptions subscriptions_provider_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.subscriptions
    ADD CONSTRAINT subscriptions_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES synapscale_db.payment_providers(id);


--
-- Name: subscriptions subscriptions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.subscriptions
    ADD CONSTRAINT subscriptions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: system_performance_metrics system_performance_metrics_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.system_performance_metrics
    ADD CONSTRAINT system_performance_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tags tags_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tags
    ADD CONSTRAINT tags_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: tags tags_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tags
    ADD CONSTRAINT tags_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: template_collections template_collections_creator_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_collections
    ADD CONSTRAINT template_collections_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: template_downloads template_downloads_template_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_downloads
    ADD CONSTRAINT template_downloads_template_id_fkey FOREIGN KEY (template_id) REFERENCES synapscale_db.workflow_templates(id);


--
-- Name: template_downloads template_downloads_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_downloads
    ADD CONSTRAINT template_downloads_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: template_favorites template_favorites_template_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_favorites
    ADD CONSTRAINT template_favorites_template_id_fkey FOREIGN KEY (template_id) REFERENCES synapscale_db.workflow_templates(id);


--
-- Name: template_favorites template_favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_favorites
    ADD CONSTRAINT template_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: template_reviews template_reviews_template_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_reviews
    ADD CONSTRAINT template_reviews_template_id_fkey FOREIGN KEY (template_id) REFERENCES synapscale_db.workflow_templates(id);


--
-- Name: template_reviews template_reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_reviews
    ADD CONSTRAINT template_reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: template_usage template_usage_template_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_usage
    ADD CONSTRAINT template_usage_template_id_fkey FOREIGN KEY (template_id) REFERENCES synapscale_db.workflow_templates(id);


--
-- Name: template_usage template_usage_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_usage
    ADD CONSTRAINT template_usage_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: template_usage template_usage_workflow_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.template_usage
    ADD CONSTRAINT template_usage_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES synapscale_db.workflows(id);


--
-- Name: tenant_features tenant_features_feature_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenant_features
    ADD CONSTRAINT tenant_features_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES synapscale_db.features(id) ON DELETE CASCADE;


--
-- Name: tenant_features tenant_features_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.tenant_features
    ADD CONSTRAINT tenant_features_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs usage_logs_conversation_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT usage_logs_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES synapscale_db.llms_conversations(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs usage_logs_llm_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT usage_logs_llm_id_fkey FOREIGN KEY (llm_id) REFERENCES synapscale_db.llms(id) ON DELETE SET NULL;


--
-- Name: llms_usage_logs usage_logs_message_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT usage_logs_message_id_fkey FOREIGN KEY (message_id) REFERENCES synapscale_db.llms_messages(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs usage_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT usage_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: llms_usage_logs usage_logs_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.llms_usage_logs
    ADD CONSTRAINT usage_logs_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: user_behavior_metrics user_behavior_metrics_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_behavior_metrics
    ADD CONSTRAINT user_behavior_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_behavior_metrics user_behavior_metrics_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_behavior_metrics
    ADD CONSTRAINT user_behavior_metrics_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: user_insights user_insights_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_insights
    ADD CONSTRAINT user_insights_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_insights user_insights_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_insights
    ADD CONSTRAINT user_insights_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: user_subscriptions user_subscriptions_plan_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_subscriptions
    ADD CONSTRAINT user_subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES synapscale_db.plans(id) ON DELETE RESTRICT;


--
-- Name: user_subscriptions user_subscriptions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_subscriptions
    ADD CONSTRAINT user_subscriptions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_subscriptions user_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_subscriptions
    ADD CONSTRAINT user_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: user_tenant_roles user_tenant_roles_granted_by_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_tenant_roles
    ADD CONSTRAINT user_tenant_roles_granted_by_fkey FOREIGN KEY (granted_by) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: user_tenant_roles user_tenant_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_tenant_roles
    ADD CONSTRAINT user_tenant_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES synapscale_db.rbac_roles(id) ON DELETE CASCADE;


--
-- Name: user_tenant_roles user_tenant_roles_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_tenant_roles
    ADD CONSTRAINT user_tenant_roles_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: user_tenant_roles user_tenant_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_tenant_roles
    ADD CONSTRAINT user_tenant_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: user_variables user_variables_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_variables
    ADD CONSTRAINT user_variables_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_variables user_variables_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.user_variables
    ADD CONSTRAINT user_variables_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id);


--
-- Name: webhook_logs webhook_logs_provider_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.webhook_logs
    ADD CONSTRAINT webhook_logs_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES synapscale_db.payment_providers(id) ON DELETE CASCADE;


--
-- Name: webhook_logs webhook_logs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.webhook_logs
    ADD CONSTRAINT webhook_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_connections workflow_connections_source_node_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_connections
    ADD CONSTRAINT workflow_connections_source_node_id_fkey FOREIGN KEY (source_node_id) REFERENCES synapscale_db.workflow_nodes(id) ON DELETE CASCADE;


--
-- Name: workflow_connections workflow_connections_target_node_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_connections
    ADD CONSTRAINT workflow_connections_target_node_id_fkey FOREIGN KEY (target_node_id) REFERENCES synapscale_db.workflow_nodes(id) ON DELETE CASCADE;


--
-- Name: workflow_connections workflow_connections_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_connections
    ADD CONSTRAINT workflow_connections_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_connections workflow_connections_workflow_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_connections
    ADD CONSTRAINT workflow_connections_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES synapscale_db.workflows(id) ON DELETE CASCADE;


--
-- Name: workflow_execution_metrics workflow_execution_metrics_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_metrics
    ADD CONSTRAINT workflow_execution_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_execution_queue workflow_execution_queue_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_execution_queue
    ADD CONSTRAINT workflow_execution_queue_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_executions workflow_executions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_executions
    ADD CONSTRAINT workflow_executions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: workflow_executions workflow_executions_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_executions
    ADD CONSTRAINT workflow_executions_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_executions workflow_executions_workflow_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_executions
    ADD CONSTRAINT workflow_executions_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES synapscale_db.workflows(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_nodes workflow_nodes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_nodes
    ADD CONSTRAINT workflow_nodes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_nodes workflow_nodes_workflow_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_nodes
    ADD CONSTRAINT workflow_nodes_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES synapscale_db.workflows(id) ON DELETE CASCADE;


--
-- Name: workflow_templates workflow_templates_author_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_templates
    ADD CONSTRAINT workflow_templates_author_id_fkey FOREIGN KEY (author_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflow_templates workflow_templates_original_workflow_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflow_templates
    ADD CONSTRAINT workflow_templates_original_workflow_id_fkey FOREIGN KEY (original_workflow_id) REFERENCES synapscale_db.workflows(id) ON DELETE SET NULL;


--
-- Name: workflows workflows_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflows
    ADD CONSTRAINT workflows_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: workflows workflows_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflows
    ADD CONSTRAINT workflows_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workflows workflows_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workflows
    ADD CONSTRAINT workflows_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE CASCADE;


--
-- Name: workspace_activities workspace_activities_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_activities
    ADD CONSTRAINT workspace_activities_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workspace_activities workspace_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_activities
    ADD CONSTRAINT workspace_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: workspace_activities workspace_activities_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_activities
    ADD CONSTRAINT workspace_activities_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: workspace_features workspace_features_feature_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_features
    ADD CONSTRAINT workspace_features_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES synapscale_db.features(id) ON DELETE CASCADE;


--
-- Name: workspace_features workspace_features_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_features
    ADD CONSTRAINT workspace_features_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workspace_features workspace_features_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_features
    ADD CONSTRAINT workspace_features_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE CASCADE;


--
-- Name: workspace_invitations workspace_invitations_invited_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_invitations
    ADD CONSTRAINT workspace_invitations_invited_user_id_fkey FOREIGN KEY (invited_user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: workspace_invitations workspace_invitations_inviter_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_invitations
    ADD CONSTRAINT workspace_invitations_inviter_id_fkey FOREIGN KEY (inviter_id) REFERENCES synapscale_db.users(id) ON DELETE SET NULL;


--
-- Name: workspace_invitations workspace_invitations_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_invitations
    ADD CONSTRAINT workspace_invitations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workspace_invitations workspace_invitations_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_invitations
    ADD CONSTRAINT workspace_invitations_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: workspace_members workspace_members_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_members
    ADD CONSTRAINT workspace_members_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workspace_members workspace_members_user_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_members
    ADD CONSTRAINT workspace_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES synapscale_db.users(id) ON DELETE CASCADE;


--
-- Name: workspace_members workspace_members_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_members
    ADD CONSTRAINT workspace_members_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: workspace_projects workspace_projects_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_projects
    ADD CONSTRAINT workspace_projects_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workspace_projects workspace_projects_workflow_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_projects
    ADD CONSTRAINT workspace_projects_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES synapscale_db.workflows(id);


--
-- Name: workspace_projects workspace_projects_workspace_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspace_projects
    ADD CONSTRAINT workspace_projects_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id) ON DELETE SET NULL;


--
-- Name: workspaces workspaces_owner_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspaces
    ADD CONSTRAINT workspaces_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES synapscale_db.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: workspaces workspaces_tenant_id_fkey; Type: FK CONSTRAINT; Schema: synapscale_db; Owner: -
--

ALTER TABLE ONLY synapscale_db.workspaces
    ADD CONSTRAINT workspaces_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES synapscale_db.tenants(id) ON DELETE CASCADE;


--
-- Name: agents; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.agents ENABLE ROW LEVEL SECURITY;

--
-- Name: analytics_events; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.analytics_events ENABLE ROW LEVEL SECURITY;

--
-- Name: billing_events; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.billing_events ENABLE ROW LEVEL SECURITY;

--
-- Name: campaigns; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.campaigns ENABLE ROW LEVEL SECURITY;

--
-- Name: contact_lists; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.contact_lists ENABLE ROW LEVEL SECURITY;

--
-- Name: contacts; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.contacts ENABLE ROW LEVEL SECURITY;

--
-- Name: files; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.files ENABLE ROW LEVEL SECURITY;

--
-- Name: invoices; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.invoices ENABLE ROW LEVEL SECURITY;

--
-- Name: knowledge_bases; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.knowledge_bases ENABLE ROW LEVEL SECURITY;

--
-- Name: llms; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.llms ENABLE ROW LEVEL SECURITY;

--
-- Name: llms_conversations; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.llms_conversations ENABLE ROW LEVEL SECURITY;

--
-- Name: llms_messages; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.llms_messages ENABLE ROW LEVEL SECURITY;

--
-- Name: marketplace_components; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.marketplace_components ENABLE ROW LEVEL SECURITY;

--
-- Name: node_templates; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.node_templates ENABLE ROW LEVEL SECURITY;

--
-- Name: nodes; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.nodes ENABLE ROW LEVEL SECURITY;

--
-- Name: rbac_permissions; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.rbac_permissions ENABLE ROW LEVEL SECURITY;

--
-- Name: rbac_roles; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.rbac_roles ENABLE ROW LEVEL SECURITY;

--
-- Name: subscriptions; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.subscriptions ENABLE ROW LEVEL SECURITY;

--
-- Name: tags; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.tags ENABLE ROW LEVEL SECURITY;

--
-- Name: agents tenant_isolation; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation ON synapscale_db.agents USING ((tenant_id = (current_setting('app.current_tenant'::text))::uuid));


--
-- Name: agents tenant_isolation_agents; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_agents ON synapscale_db.agents USING ((tenant_id = public.current_tenant_id()));


--
-- Name: agents tenant_isolation_agents_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_agents_insert ON synapscale_db.agents FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: analytics_events tenant_isolation_analytics_events; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_analytics_events ON synapscale_db.analytics_events USING ((tenant_id = public.current_tenant_id()));


--
-- Name: analytics_events tenant_isolation_analytics_events_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_analytics_events_insert ON synapscale_db.analytics_events FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: billing_events tenant_isolation_billing_events; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_billing_events ON synapscale_db.billing_events USING ((tenant_id = public.current_tenant_id()));


--
-- Name: billing_events tenant_isolation_billing_events_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_billing_events_insert ON synapscale_db.billing_events FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: campaigns tenant_isolation_campaigns_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_campaigns_delete ON synapscale_db.campaigns FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: campaigns tenant_isolation_campaigns_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_campaigns_insert ON synapscale_db.campaigns FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: campaigns tenant_isolation_campaigns_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_campaigns_select ON synapscale_db.campaigns FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: campaigns tenant_isolation_campaigns_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_campaigns_update ON synapscale_db.campaigns FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: contact_lists tenant_isolation_contact_lists; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_contact_lists ON synapscale_db.contact_lists USING ((tenant_id = public.current_tenant_id()));


--
-- Name: contact_lists tenant_isolation_contact_lists_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_contact_lists_insert ON synapscale_db.contact_lists FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: contacts tenant_isolation_contacts_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_contacts_delete ON synapscale_db.contacts FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: contacts tenant_isolation_contacts_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_contacts_insert ON synapscale_db.contacts FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: contacts tenant_isolation_contacts_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_contacts_select ON synapscale_db.contacts FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: contacts tenant_isolation_contacts_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_contacts_update ON synapscale_db.contacts FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: files tenant_isolation_files_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_files_delete ON synapscale_db.files FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: files tenant_isolation_files_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_files_insert ON synapscale_db.files FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: files tenant_isolation_files_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_files_select ON synapscale_db.files FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: files tenant_isolation_files_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_files_update ON synapscale_db.files FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: invoices tenant_isolation_invoices; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_invoices ON synapscale_db.invoices USING ((tenant_id = public.current_tenant_id()));


--
-- Name: invoices tenant_isolation_invoices_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_invoices_insert ON synapscale_db.invoices FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: knowledge_bases tenant_isolation_knowledge_bases; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_knowledge_bases ON synapscale_db.knowledge_bases USING ((tenant_id = public.current_tenant_id()));


--
-- Name: knowledge_bases tenant_isolation_knowledge_bases_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_knowledge_bases_insert ON synapscale_db.knowledge_bases FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: llms tenant_isolation_llms; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_llms ON synapscale_db.llms USING ((tenant_id = public.current_tenant_id()));


--
-- Name: llms tenant_isolation_llms_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_llms_insert ON synapscale_db.llms FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: marketplace_components tenant_isolation_marketplace_components; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_marketplace_components ON synapscale_db.marketplace_components USING ((tenant_id = public.current_tenant_id()));


--
-- Name: marketplace_components tenant_isolation_marketplace_components_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_marketplace_components_insert ON synapscale_db.marketplace_components FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: node_templates tenant_isolation_node_templates; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_node_templates ON synapscale_db.node_templates USING ((tenant_id = public.current_tenant_id()));


--
-- Name: node_templates tenant_isolation_node_templates_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_node_templates_insert ON synapscale_db.node_templates FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: nodes tenant_isolation_nodes_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_nodes_delete ON synapscale_db.nodes FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: nodes tenant_isolation_nodes_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_nodes_insert ON synapscale_db.nodes FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: nodes tenant_isolation_nodes_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_nodes_select ON synapscale_db.nodes FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: nodes tenant_isolation_nodes_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_nodes_update ON synapscale_db.nodes FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: rbac_permissions tenant_isolation_rbac_permissions; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_rbac_permissions ON synapscale_db.rbac_permissions USING ((tenant_id = public.current_tenant_id()));


--
-- Name: rbac_permissions tenant_isolation_rbac_permissions_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_rbac_permissions_insert ON synapscale_db.rbac_permissions FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: rbac_roles tenant_isolation_rbac_roles; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_rbac_roles ON synapscale_db.rbac_roles USING ((tenant_id = public.current_tenant_id()));


--
-- Name: rbac_roles tenant_isolation_rbac_roles_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_rbac_roles_insert ON synapscale_db.rbac_roles FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: subscriptions tenant_isolation_subscriptions; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_subscriptions ON synapscale_db.subscriptions USING ((tenant_id = public.current_tenant_id()));


--
-- Name: subscriptions tenant_isolation_subscriptions_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_subscriptions_insert ON synapscale_db.subscriptions FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: tags tenant_isolation_tags_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_tags_delete ON synapscale_db.tags FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: tags tenant_isolation_tags_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_tags_insert ON synapscale_db.tags FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: tags tenant_isolation_tags_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_tags_select ON synapscale_db.tags FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: tags tenant_isolation_tags_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_tags_update ON synapscale_db.tags FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: tools tenant_isolation_tools; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_tools ON synapscale_db.tools USING ((tenant_id = public.current_tenant_id()));


--
-- Name: tools tenant_isolation_tools_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_tools_insert ON synapscale_db.tools FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: user_tenant_roles tenant_isolation_user_tenant_roles_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_user_tenant_roles_delete ON synapscale_db.user_tenant_roles FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: user_tenant_roles tenant_isolation_user_tenant_roles_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_user_tenant_roles_insert ON synapscale_db.user_tenant_roles FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: user_tenant_roles tenant_isolation_user_tenant_roles_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_user_tenant_roles_select ON synapscale_db.user_tenant_roles FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: user_tenant_roles tenant_isolation_user_tenant_roles_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_user_tenant_roles_update ON synapscale_db.user_tenant_roles FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workflow_connections tenant_isolation_workflow_connections; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_connections ON synapscale_db.workflow_connections USING ((tenant_id = public.current_tenant_id()));


--
-- Name: workflow_connections tenant_isolation_workflow_connections_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_connections_insert ON synapscale_db.workflow_connections FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: workflow_executions tenant_isolation_workflow_executions_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_executions_delete ON synapscale_db.workflow_executions FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workflow_executions tenant_isolation_workflow_executions_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_executions_insert ON synapscale_db.workflow_executions FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workflow_executions tenant_isolation_workflow_executions_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_executions_select ON synapscale_db.workflow_executions FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workflow_executions tenant_isolation_workflow_executions_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_executions_update ON synapscale_db.workflow_executions FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workflow_nodes tenant_isolation_workflow_nodes; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_nodes ON synapscale_db.workflow_nodes USING ((tenant_id = public.current_tenant_id()));


--
-- Name: workflow_nodes tenant_isolation_workflow_nodes_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflow_nodes_insert ON synapscale_db.workflow_nodes FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: workflows tenant_isolation_workflows_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflows_delete ON synapscale_db.workflows FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workflows tenant_isolation_workflows_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflows_insert ON synapscale_db.workflows FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workflows tenant_isolation_workflows_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflows_select ON synapscale_db.workflows FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workflows tenant_isolation_workflows_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workflows_update ON synapscale_db.workflows FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workspace_members tenant_isolation_workspace_members_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspace_members_delete ON synapscale_db.workspace_members FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workspace_members tenant_isolation_workspace_members_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspace_members_insert ON synapscale_db.workspace_members FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workspace_members tenant_isolation_workspace_members_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspace_members_select ON synapscale_db.workspace_members FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workspace_members tenant_isolation_workspace_members_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspace_members_update ON synapscale_db.workspace_members FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workspace_projects tenant_isolation_workspace_projects; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspace_projects ON synapscale_db.workspace_projects USING ((tenant_id = public.current_tenant_id()));


--
-- Name: workspace_projects tenant_isolation_workspace_projects_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspace_projects_insert ON synapscale_db.workspace_projects FOR INSERT WITH CHECK ((tenant_id = public.current_tenant_id()));


--
-- Name: workspaces tenant_isolation_workspaces_delete; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspaces_delete ON synapscale_db.workspaces FOR DELETE USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workspaces tenant_isolation_workspaces_insert; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspaces_insert ON synapscale_db.workspaces FOR INSERT WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: workspaces tenant_isolation_workspaces_select; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspaces_select ON synapscale_db.workspaces FOR SELECT USING (public.is_authorized_tenant(tenant_id));


--
-- Name: workspaces tenant_isolation_workspaces_update; Type: POLICY; Schema: synapscale_db; Owner: -
--

CREATE POLICY tenant_isolation_workspaces_update ON synapscale_db.workspaces FOR UPDATE USING (public.is_authorized_tenant(tenant_id)) WITH CHECK (public.is_authorized_tenant(tenant_id));


--
-- Name: tools; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.tools ENABLE ROW LEVEL SECURITY;

--
-- Name: user_tenant_roles; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.user_tenant_roles ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_connections; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workflow_connections ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_executions; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workflow_executions ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_nodes; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workflow_nodes ENABLE ROW LEVEL SECURITY;

--
-- Name: workflows; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workflows ENABLE ROW LEVEL SECURITY;

--
-- Name: workspace_members; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workspace_members ENABLE ROW LEVEL SECURITY;

--
-- Name: workspace_projects; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workspace_projects ENABLE ROW LEVEL SECURITY;

--
-- Name: workspaces; Type: ROW SECURITY; Schema: synapscale_db; Owner: -
--

ALTER TABLE synapscale_db.workspaces ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

