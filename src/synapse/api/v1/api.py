from fastapi import APIRouter

from synapse.api.v1.endpoints import (
    auth,
    users,
    tenants,  # ✅ Adicionado - endpoints de tenant (Task 5)
    workspaces,
    files,
    llm,  # ✅ Adicionado de volta - existe no diretório
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
    admin_migration,  # ✅ Existe (migração)
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
api_router.include_router(llm.router, prefix="/llm", tags=["ai"])
api_router.include_router(llms.router, prefix="/llms", tags=["ai"])  # Novos endpoints completos de LLM
api_router.include_router(llm_catalog.router, prefix="/llm-catalog", tags=["ai"])  # Catálogo de modelos
api_router.include_router(conversations.router, prefix="/conversations", tags=["ai"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["ai"])

# 🎯 AGENTS (CONSOLIDADO) - Todos os endpoints de agentes em um só bloco
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(agent_tools.router, prefix="/agents/tools", tags=["agents"])  # Mudança: /agents/tools
api_router.include_router(agent_models.router, prefix="/agents/models", tags=["agents"])  # Mudança: /agents/models  
api_router.include_router(agent_configurations.router, prefix="/agents/configs", tags=["agents"])  # Mudança: /agents/configs
api_router.include_router(agent_advanced.router, prefix="/agents/advanced", tags=["agents"])  # Mudança: /agents/advanced

# ⚙️ WORKFLOWS (YÁ ESTÁ ORGANIZADO)
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["workflows"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["workflows"])

# 📊 ANALYTICS (CONSOLIDADO)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(usage_log.router, prefix="/usage-log", tags=["analytics"])

# 💾 DATA (CONSOLIDADO) - Todos os dados e arquivos
api_router.include_router(files.router, prefix="/files", tags=["data"])
api_router.include_router(user_variables.router, prefix="/user-variables", tags=["data"])
api_router.include_router(tag.router, prefix="/tags", tags=["data"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["data"])  # Workspaces são dados também
api_router.include_router(workspace_members.router, prefix="/workspace-members", tags=["data"])

# 🏢 ENTERPRISE (CONSOLIDADO) - Todas as funcionalidades empresariais
api_router.include_router(rbac.router, prefix="/enterprise/rbac", tags=["enterprise"])  # Mudança: /enterprise/rbac
api_router.include_router(features.router, prefix="/enterprise/features", tags=["enterprise"])  # Mudança: /enterprise/features
api_router.include_router(payments.router, prefix="/enterprise/payments", tags=["enterprise"])  # Mudança: /enterprise/payments

# 🛒 MARKETPLACE (YÁ ESTÁ ORGANIZADO)
api_router.include_router(templates.router, prefix="/templates", tags=["marketplace"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])

# 👨‍💼 ADMIN (CONSOLIDADO)
api_router.include_router(admin_migration.router, prefix="/admin/migration", tags=["admin"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# 🏠 SYSTEM (YÁ ESTÁ ORGANIZADO)
api_router.include_router(websockets.router, prefix="/ws", tags=["system"])

# Integrar o Memory Bank (comentado temporariamente - arquivo não existe)
# integrate_memory_bank(api_router)
