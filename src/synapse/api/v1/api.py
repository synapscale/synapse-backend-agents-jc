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
    llms,  # 🆕 Adicionado - novos endpoints completos de LLM
    llm_catalog,  # ✅ Adicionado - rotas /llms/*
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

# 🤖 AI (CONSOLIDADO) - Tudo relacionado a IA exceto agentes específicos
api_router.include_router(llms.router, prefix="/llms", tags=["ai"])
api_router.include_router(llm_catalog.router, prefix="/llm-catalog", tags=["ai"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["ai"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["ai"])

# 🎯 AGENTS (CONSOLIDADO) - Todos os endpoints de agentes em um só bloco
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(agent_tools.router, prefix="/agents/tools", tags=["agents"])
api_router.include_router(agent_models.router, prefix="/agents/models", tags=["agents"])
api_router.include_router(agent_configurations.router, prefix="/agents/configs", tags=["agents"])
api_router.include_router(agent_advanced.router, prefix="/agents/advanced", tags=["agents"])

# ⚙️ WORKFLOWS (YÁ ESTÁ ORGANIZADO)
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["workflows"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["workflows"])
api_router.include_router(node_categories.router, prefix="/workflows/node-categories", tags=["workflows"]) # Workflows
api_router.include_router(node_execution_statuses.router, prefix="/workflows/node-execution-statuses", tags=["workflows"]) # Workflows
api_router.include_router(node_ratings.router, prefix="/workflows/node-ratings", tags=["workflows"]) # Workflows

# 📊 ANALYTICS (CONSOLIDADO)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(usage_log.router, prefix="/usage-log", tags=["analytics"])
api_router.include_router(analytics_dashboards.router, prefix="/analytics/dashboards", tags=["analytics"]) # Analytics
api_router.include_router(analytics_alerts.router, prefix="/analytics/alerts", tags=["analytics"]) # Analytics
api_router.include_router(analytics_exports.router, prefix="/analytics/exports", tags=["analytics"]) # Analytics

# 💾 DATA (CONSOLIDADO) - Todos os dados e arquivos
api_router.include_router(files.router, prefix="/files", tags=["data"])
api_router.include_router(user_variables.router, prefix="/user-variables", tags=["data"])
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
api_router.include_router(rbac.router, prefix="/enterprise/rbac", tags=["enterprise"])  # Mudança: /enterprise/rbac
api_router.include_router(features.router, prefix="/enterprise/features", tags=["enterprise"])  # Mudança: /enterprise/features
api_router.include_router(payments.router, prefix="/enterprise/payments", tags=["enterprise"])  # Mudança: /enterprise/payments
api_router.include_router(billing_events.router, prefix="/enterprise/billing-events", tags=["enterprise"]) # Enterprise
api_router.include_router(invoices.router, prefix="/enterprise/invoices", tags=["enterprise"]) # Enterprise
api_router.include_router(plans.router, prefix="/enterprise/plans", tags=["enterprise"]) # Enterprise
api_router.include_router(subscriptions.router, prefix="/enterprise/subscriptions", tags=["enterprise"]) # Enterprise

# 🛒 MARKETPLACE (YÁ ESTÁ ORGANIZADO)
api_router.include_router(templates.router, prefix="/templates", tags=["marketplace"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])

# 👨‍💼 ADMIN (CONSOLIDADO)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# 🏠 SYSTEM (YÁ ESTÁ ORGANIZADO)
api_router.include_router(websockets.router, prefix="/ws", tags=["system"])

# Integrar o Memory Bank (comentado temporariamente - arquivo não existe)
# from synapse.api.v1.memory_bank_integration import integrate_memory_bank
# integrate_memory_bank(api_router)
