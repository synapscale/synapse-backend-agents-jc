"""
SQLAlchemy Models

VERSÃO LIMPA - APENAS MODELOS ESSENCIAIS
"""

from typing import Dict, Any

# Import individual models
def safe_import(module_name, class_names):
    """Importa modelos de forma segura"""
    try:
        module = __import__(f"synapse.models.{module_name}", fromlist=class_names)
        result = {}
        for class_name in class_names:
            if hasattr(module, class_name):
                result[class_name] = getattr(module, class_name)
            else:
                print(f"⚠️ {class_name} não encontrado em {module_name}")
        return result
    except Exception as e:
        print(f"❌ Erro ao importar {module_name}: {e}")
        return {}

# Dicionário central para armazenar todos os imports
_imports = {}

# ==================== MODELOS PRINCIPAIS ====================
_imports.update(safe_import("user", ['User']))
_imports.update(safe_import("tenant", ['Tenant']))
_imports.update(safe_import("workspace", ['Workspace']))
_imports.update(safe_import("agent", ["Agent"]))
_imports.update(safe_import("agent_configuration", ["AgentConfiguration"]))
_imports.update(safe_import("conversation", ["Conversation"]))
_imports.update(safe_import("message", ["Message"]))

# ==================== WORKFLOW & NODES ====================
_imports.update(safe_import("workflow", ['Workflow']))
_imports.update(safe_import("node", ['Node']))
_imports.update(safe_import("workflow_node", ["WorkflowNode"]))
_imports.update(safe_import("workflow_execution", ["WorkflowExecution"]))
_imports.update(safe_import("node_execution", ["NodeExecution"]))
_imports.update(safe_import("workflow_connection", ["WorkflowConnection"]))
_imports.update(safe_import("workflow_execution_queue", ["WorkflowExecutionQueue"]))
_imports.update(safe_import("workflow_template", ["WorkflowTemplate"]))

# ==================== TIPOS E STATUS ====================
_imports.update(safe_import("agent_type", ["AgentType"]))
_imports.update(safe_import("agent_status", ["AgentStatus"]))
_imports.update(safe_import("node_type", ["NodeType"]))
_imports.update(safe_import("node_status", ["NodeStatus"]))
_imports.update(safe_import("execution_status", ["ExecutionStatus"]))
_imports.update(safe_import("node_execution_status", ["NodeExecutionStatus"]))
_imports.update(safe_import("event_type", ["EventType"]))
_imports.update(safe_import("metric_type", ["MetricType"]))

# ==================== PAGAMENTOS & PLANOS ====================
_imports.update(safe_import("plan", ["Plan"]))
_imports.update(safe_import("subscription", ["Subscription"]))
_imports.update(safe_import("user_subscription", ["UserSubscription"]))
_imports.update(safe_import("payment_customer", ["PaymentCustomer"]))
_imports.update(safe_import("payment_method", ["PaymentMethod"]))
_imports.update(safe_import("payment_provider", ["PaymentProvider"]))
_imports.update(safe_import("invoice", ["Invoice"]))
_imports.update(safe_import("billing_event", ["BillingEvent"]))
_imports.update(safe_import("coupon", ["Coupon"]))

# ==================== FEATURES & PERMISSÕES ====================
_imports.update(safe_import("feature", ["Feature"]))
_imports.update(safe_import("tenant_feature", ["TenantFeature"]))
_imports.update(safe_import("plan_feature", ["PlanFeature"]))
_imports.update(safe_import("plan_entitlement", ["PlanEntitlement"]))
_imports.update(safe_import("plan_provider_mapping", ["PlanProviderMapping"]))
_imports.update(safe_import("rbac_role", ["RBACRole"]))
_imports.update(safe_import("rbac_permission", ["RBACPermission"]))
_imports.update(safe_import("rbac_role_permission", ["RBACRolePermission"]))
_imports.update(safe_import("user_tenant_role", ["UserTenantRole"]))

# ==================== ANALYTICS & MÉTRICAS ====================
_imports.update(safe_import("analytics_metric", ["AnalyticsMetric"]))
_imports.update(safe_import("analytics_event", ["AnalyticsEvent"]))
_imports.update(safe_import("analytics_report", ["AnalyticsReport"]))
_imports.update(safe_import("analytics_dashboard", ["AnalyticsDashboard"]))
_imports.update(safe_import("analytics_alert", ["AnalyticsAlert"]))
_imports.update(safe_import("analytics_export", ["AnalyticsExport"]))
_imports.update(safe_import("business_metric", ["BusinessMetric"]))
_imports.update(safe_import("agent_usage_metric", ["AgentUsageMetric"]))
_imports.update(safe_import("user_behavior_metric", ["UserBehaviorMetric"]))
_imports.update(safe_import("workflow_execution_metric", ["WorkflowExecutionMetric"]))
_imports.update(safe_import("analytics", ["SystemPerformanceMetric"]))

# ==================== CONTATOS & CAMPANHAS ====================
_imports.update(safe_import("contact", ["Contact"]))
_imports.update(safe_import("contact_source", ["ContactSource"]))
_imports.update(safe_import("contact_list", ["ContactList"]))
_imports.update(safe_import("contact_list_membership", ["ContactListMembership"]))
_imports.update(safe_import("contact_note", ["ContactNote"]))
_imports.update(safe_import("contact_tag", ["ContactTag"]))
_imports.update(safe_import("contact_event", ["ContactEvent"]))
_imports.update(safe_import("contact_interaction", ["ContactInteraction"]))
_imports.update(safe_import("campaign", ["Campaign"]))
_imports.update(safe_import("campaign_contact", ["CampaignContact"]))

# ==================== PROJETOS & COLABORAÇÃO ====================
_imports.update(safe_import("workspace_project", ["WorkspaceProject"]))
_imports.update(safe_import("workspace_member", ["WorkspaceMember"]))
_imports.update(safe_import("workspace_invitation", ["WorkspaceInvitation"]))
_imports.update(safe_import("workspace_activity", ["WorkspaceActivity"]))
_imports.update(safe_import("project_collaborator", ["ProjectCollaborator"]))
_imports.update(safe_import("project_comment", ["ProjectComment"]))
_imports.update(safe_import("project_version", ["ProjectVersion"]))

# ==================== AGENTES & FERRAMENTAS ====================
_imports.update(safe_import("agent_quota", ["AgentQuota"]))
_imports.update(safe_import("agent_acl", ["AgentACL"]))
_imports.update(safe_import("agent_trigger", ["AgentTrigger"]))
_imports.update(safe_import("agent_error_log", ["AgentErrorLog"]))
_imports.update(safe_import("agent_hierarchy", ["AgentHierarchy"]))
_imports.update(safe_import("agent_model", ["AgentModel"]))
_imports.update(safe_import("agent_tool", ["AgentTool"]))
_imports.update(safe_import("agent_knowledge_base", ["AgentKnowledgeBase"]))
_imports.update(safe_import("tool", ["Tool"]))

# ==================== LLM & CONVERSAS ====================
_imports.update(safe_import("llm", ["LLM"]))
_imports.update(safe_import("conversation_llm", ["ConversationLLM"]))
_imports.update(safe_import("message_feedback", ["MessageFeedback"]))

# ==================== TEMPLATES & NODOS ====================
_imports.update(safe_import("node_template", ["NodeTemplate"]))
_imports.update(safe_import("node_rating", ["NodeRating"]))
_imports.update(safe_import("node_category", ["NodeCategory"]))
_imports.update(safe_import("template", [
    "TemplateReview", "TemplateDownload", "TemplateFavorite", 
    "TemplateCollection", "TemplateUsage"
]))

# ==================== TOKENS & SEGURANÇA ====================
_imports.update(safe_import("refresh_token", ["RefreshToken"]))
_imports.update(safe_import("password_reset_token", ["PasswordResetToken"]))
_imports.update(safe_import("email_verification_token", ["EmailVerificationToken"]))

# ==================== MARKPLACE ====================
_imports.update(safe_import("marketplace", [
    "MarketplaceComponent", "ComponentRating", "ComponentDownload", "ComponentPurchase"
]))
_imports.update(safe_import("component_version", ["ComponentVersion"]))

# ==================== OUTROS ====================
_imports.update(safe_import("file", ["File"]))
_imports.update(safe_import("tag", ["Tag"]))
_imports.update(safe_import("audit_log", ["AuditLog"]))
_imports.update(safe_import("usage_log", ["UsageLog"]))
_imports.update(safe_import("webhook_log", ["WebhookLog"]))
_imports.update(safe_import("custom_report", ["CustomReport"]))
_imports.update(safe_import("report_execution", ["ReportExecution"]))
_imports.update(safe_import("knowledge_base", ["KnowledgeBase"]))
_imports.update(safe_import("user_digitalocean", ["UserDigitalOcean"]))
_imports.update(safe_import("user_variable", ["UserVariable"]))
_imports.update(safe_import("user_insight", ["UserInsight"]))
_imports.update(safe_import("conversion_journey", ["ConversionJourney"]))

# ==================== ALIASES DE COMPATIBILIDADE ====================
if 'Conversation' in _imports:
    globals()['LLMConversation'] = _imports['Conversation']
    _imports['LLMConversation'] = _imports['Conversation']

if 'Message' in _imports:
    globals()['LLMMessage'] = _imports['Message']
    _imports['LLMMessage'] = _imports['Message']

# Fazer todas as classes disponíveis no namespace
globals().update(_imports)

# Lista de todos os modelos importados para controle de exportações
__all__ = list(_imports.keys())

print(f"✅ Models importados: {len(_imports)} classes")
