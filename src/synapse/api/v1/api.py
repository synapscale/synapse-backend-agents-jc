from fastapi import APIRouter

from synapse.api.v1.endpoints import (
    auth,
    users,
    workspaces,
    files,
    llm,
    llm_catalog,  # ✅ Adicionado - rotas /llms/*
    analytics,
    workflows,
    templates,
    user_variables,
    tag,  # ✅ Corrigido de 'tags' para 'tag'
    websockets,
    # health,      # ❌ Removido - não existe
    billing,
    marketplace,
    # notifications,  # ❌ Removido - não existe
    # integrations,   # ❌ Removido - não existe
    # admin,          # ❌ Removido - não existe
    admin_migration  # ✅ Existe
)

# Importar a integração do Memory Bank
from synapse.api.v1.memory_bank_integration import integrate_memory_bank

# Criar o router principal da API
api_router = APIRouter()

# Incluir todos os routers de endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(llm_catalog.router, prefix="/llms", tags=["llms"])  # ✅ Rotas /llms/* restauradas
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(user_variables.router, prefix="/user-variables", tags=["user-variables"])
api_router.include_router(tag.router, prefix="/tags", tags=["tags"])  # ✅ Corrigido
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])
# api_router.include_router(health.router, prefix="/health", tags=["health"])  # ❌ Removido - não existe
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
# api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])  # ❌ Removido
# api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])  # ❌ Removido
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])  # ❌ Removido
api_router.include_router(admin_migration.router, prefix="/admin", tags=["admin", "migration"])

# Integrar o Memory Bank
integrate_memory_bank(api_router)
