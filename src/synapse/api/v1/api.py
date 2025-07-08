from fastapi import APIRouter

from synapse.api.v1.endpoints import (
    auth,
    users,
    tenants,  # ✅ Adicionado - endpoints de tenant (Task 5)
    workspaces,
    files,
    contacts, # CRM
    contact_lists, # CRM
    campaigns, # CRM
    contact_tags, # CRM
    contact_sources, # CRM
    contact_notes, # CRM
    analytics_dashboards, # Analytics
    analytics_alerts, # Analytics
    analytics_exports, # Analytics
    billing_events, # Enterprise
    invoices, # Enterprise
    plans, # Enterprise
    subscriptions, # Enterprise
    node_categories, # Workflows
    node_execution_statuses, # Workflows
    node_ratings, # Workflows
    node_executions, # Workflows
    node_statuses, # Workflows
    node_templates, # Workflows
    node_types, # Workflows
    llms,  # 🆕 Adicionado - novos endpoints completos de LLM
    analytics,
    workflows,
    executions,  # ✅ Adicionado - existe no diretório
    nodes,  # ✅ Adicionado - existe no diretório
    agents,  # ✅ Adicionado - existe no diretório
    agent_tools,  # 🆕 Adicionado - gestão de ferramentas de agents
    agent_models,  # 🆕 Adicionado - gestão de modelos LLM de agents
    agent_configurations,  # 🆕 Adicionado - versionamento de configurações
    agent_advanced,  # 🆕 Adicionado - ACL, errors, metrics, etc
    conversations,  # ✅ Adicionado - existe no diretório
    feedback,  # ✅ Adicionado - existe no diretório
    templates,
    user_variables,
    user_insights, # Data
    user_tenant_roles, # Enterprise
    usage_log,  # ✅ Adicionado
    workspace_members,  # ✅ Adicionado
    tag,  # ✅ Corrigido de 'tags' para 'tag'
    websockets,
    marketplace,
    admin,  # ✅ Novo arquivo completo de admin
    # 🆕 NEW ENTERPRISE ENDPOINTS 🆕
    rbac,  # ✅ RBAC - Role-Based Access Control
    features,  # ✅ Features - Feature Management System
    payments,  # ✅ Payments - Payment Processing System
    # 🆕 NEW CRITICAL ENDPOINTS 🆕
    agent_quotas,  # ✅ Agent Quotas - Usage Control System
    knowledge_bases,  # ✅ Knowledge Bases - Knowledge Management
    refresh_tokens,  # ✅ Refresh Tokens - Token Management
    payment_customers,  # ✅ Payment Customers - Customer Management
    # 🆕 AUTO-GENERATED HIGH PRIORITY ENDPOINTS 🆕
    # metric_types,  # 🆕 Auto-generated - temporarily disabled
    # event_types,  # 🆕 Auto-generated - temporarily disabled
    # coupons,  # 🆕 Auto-generated - temporarily disabled
    # conversion_journeys,  # 🆕 Auto-generated - temporarily disabled
    # Low priority endpoints - temporarily disabled
    # project_versions,
    # webhook_logs,
    # email_verification_tokens,
    # project_comments,
    # custom_reports,
    # audits,
    # component_versions,
    # project_collaborators,
    # messages,
    # password_reset_tokens,
    # audit_logs,
    # business_metrics,
)

# Importar a integração do Memory Bank (comentado temporariamente - arquivo não existe)
# from synapse.api.v1.memory_bank_integration import integrate_memory_bank

# Criar o router principal da API
api_router = APIRouter()

# =================== CONSOLIDAÇÃO DE ROUTERS - ESTRUTURA FINAL ===================

# 🔐 AUTHENTICATION (CONSOLIDADO)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["authentication"])  # Tenants são parte da auth
api_router.include_router(refresh_tokens.router, prefix="/auth/refresh-tokens", tags=["authentication"])

# 🤖 AI (CONSOLIDADO) - Tudo relacionado a IA exceto agentes específicos
api_router.include_router(llms.router, prefix="/llms", tags=["ai"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["ai"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["ai"])

# 🎯 AGENTS (CONSOLIDADO)
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(agent_tools.router, prefix="/agents/tools", tags=["agents"])
api_router.include_router(agent_models.router, prefix="/agents/models", tags=["agents"])
api_router.include_router(agent_configurations.router, prefix="/agents/configs", tags=["agents"])
api_router.include_router(agent_advanced.router, prefix="/agents/advanced", tags=["agents"])
api_router.include_router(agent_quotas.router, prefix="/agents/quotas", tags=["agents"])
api_router.include_router(knowledge_bases.router, prefix="/knowledge-bases", tags=["agents"])

# ⚙️ WORKFLOWS (YÁ ESTÁ ORGANIZADO)
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["workflows"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["workflows"])
api_router.include_router(node_categories.router, prefix="/workflows/node-categories", tags=["workflows"]) # Workflows
api_router.include_router(node_execution_statuses.router, prefix="/workflows/node-execution-statuses", tags=["workflows"]) # Workflows
api_router.include_router(node_ratings.router, prefix="/workflows/node-ratings", tags=["workflows"]) # Workflows
api_router.include_router(node_executions.router, prefix="/workflows/node-executions", tags=["workflows"]) # Workflows
api_router.include_router(node_statuses.router, prefix="/workflows/node-statuses", tags=["workflows"]) # Workflows
api_router.include_router(node_templates.router, prefix="/workflows/node-templates", tags=["workflows"]) # Workflows
api_router.include_router(node_types.router, prefix="/workflows/node-types", tags=["workflows"]) # Workflows

# 📊 ANALYTICS (CONSOLIDADO)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(usage_log.router, prefix="/usage-log", tags=["analytics"])
api_router.include_router(analytics_dashboards.router, prefix="/analytics/dashboards", tags=["analytics"]) # Analytics
api_router.include_router(analytics_alerts.router, prefix="/analytics/alerts", tags=["analytics"]) # Analytics
api_router.include_router(analytics_exports.router, prefix="/analytics/exports", tags=["analytics"]) # Analytics
#api_router.include_router(metric_types.router, prefix="/analytics/metric-types", tags=["analytics"]) # 🆕 Auto-generated
#api_router.include_router(event_types.router, prefix="/analytics/event-types", tags=["analytics"]) # 🆕 Auto-generated
#api_router.include_router(conversion_journeys.router, prefix="/analytics/conversion-journeys", tags=["analytics"]) # 🆕 Auto-generated

# 💾 DATA (CONSOLIDADO) - Todos os dados e arquivos
api_router.include_router(files.router, prefix="/files", tags=["data"])
api_router.include_router(user_variables.router, prefix="/user-variables", tags=["data"])
api_router.include_router(user_insights.router, prefix="/user-insights", tags=["data"])
api_router.include_router(tag.router, prefix="/tags", tags=["data"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["data"])
api_router.include_router(workspace_members.router, prefix="/workspace-members", tags=["data"])

# 📞 CRM (CONSOLIDADO)
api_router.include_router(contacts.router, prefix="/crm/contacts", tags=["crm"])
api_router.include_router(contact_lists.router, prefix="/crm/contact-lists", tags=["crm"])
api_router.include_router(campaigns.router, prefix="/crm/campaigns", tags=["crm"])
api_router.include_router(contact_tags.router, prefix="/crm/contact-tags", tags=["crm"])
api_router.include_router(contact_sources.router, prefix="/crm/contact-sources", tags=["crm"])
api_router.include_router(contact_notes.router, prefix="/crm/contact-notes", tags=["crm"]) 

# 🏢 ENTERPRISE (CONSOLIDADO) - Todas as funcionalidades empresariais
api_router.include_router(rbac.router, prefix="/enterprise/rbac", tags=["enterprise"])
api_router.include_router(features.router, prefix="/enterprise/features", tags=["enterprise"])
api_router.include_router(payments.router, prefix="/enterprise/payments", tags=["enterprise"])
api_router.include_router(payment_customers.router, prefix="/enterprise/payment-customers", tags=["enterprise"])
api_router.include_router(billing_events.router, prefix="/enterprise/billing-events", tags=["enterprise"]) # Enterprise
api_router.include_router(invoices.router, prefix="/enterprise/invoices", tags=["enterprise"]) # Enterprise
api_router.include_router(plans.router, prefix="/enterprise/plans", tags=["enterprise"]) # Enterprise
api_router.include_router(subscriptions.router, prefix="/enterprise/subscriptions", tags=["enterprise"]) # Enterprise
api_router.include_router(user_tenant_roles.router, prefix="/enterprise/user-tenant-roles", tags=["enterprise"]) # Enterprise
#api_router.include_router(coupons.router, prefix="/enterprise/coupons", tags=["enterprise"]) # 🆕 Auto-generated

# 🛒 MARKETPLACE (YÁ ESTÁ ORGANIZADO)
api_router.include_router(templates.router, prefix="/templates", tags=["marketplace"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])

# 👨‍💼 ADMIN (CONSOLIDADO)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# 🏠 SYSTEM (YÁ ESTÁ ORGANIZADO)
api_router.include_router(websockets.router, prefix="/ws", tags=["system"])

# 🆕 LOW PRIORITY ENDPOINTS
#api_router.include_router(project_versions.router, prefix="/project-versions", tags=["projects"])
#api_router.include_router(webhook_logs.router, prefix="/webhook-logs", tags=["system"])
#api_router.include_router(email_verification_tokens.router, prefix="/email-verification-tokens", tags=["auth"])
#api_router.include_router(project_comments.router, prefix="/project-comments", tags=["projects"])
#api_router.include_router(custom_reports.router, prefix="/custom-reports", tags=["reports"])
#api_router.include_router(audits.router, prefix="/audits", tags=["system"])
# models endpoint removido - era vazio e sem propósito
#api_router.include_router(component_versions.router, prefix="/component-versions", tags=["marketplace"])
#api_router.include_router(project_collaborators.router, prefix="/project-collaborators", tags=["projects"])
#api_router.include_router(messages.router, prefix="/messages", tags=["conversations"])
#api_router.include_router(password_reset_tokens.router, prefix="/password-reset-tokens", tags=["auth"])
#api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["system"])
#api_router.include_router(business_metrics.router, prefix="/business-metrics", tags=["analytics"])

# Integrar o Memory Bank (comentado temporariamente - arquivo não existe)
# from synapse.api.v1.memory_bank_integration import integrate_memory_bank
# integrate_memory_bank(api_router)
