"""
Inicialização do pacote de modelos - IMPORTAÇÃO ROBUSTA
Importa apenas os models que existem e funcionam
"""


# Função auxiliar para importação segura
def safe_import(module_name, class_names, exclude_classes=None):
    """Importa classes de um módulo de forma segura"""
    try:
        module = __import__(f"synapse.models.{module_name}", fromlist=class_names)
        exclude_classes = exclude_classes or []
        return {
            name: getattr(module, name) for name in class_names 
            if hasattr(module, name) and name not in exclude_classes
        }
    except ImportError:
        return {}


# Core models
_imports = {}
_imports.update(safe_import("user", ["User", "UserStatus"]))
_imports.update(safe_import("tenant", ["Tenant", "TenantStatus"]))
_imports.update(safe_import("plan", ["Plan"]))
_imports.update(safe_import("workspace", ["Workspace"]))
_imports.update(safe_import("agent", ["Agent"]))
_imports.update(safe_import("llm", ["LLM"]))
_imports.update(safe_import("file", ["File"]))
_imports.update(safe_import("node", ["Node"]))

# Feature system
_imports.update(safe_import("feature", ["Feature", "WorkspaceFeature"]))
_imports.update(safe_import("plan_feature", ["PlanFeature"]))
_imports.update(safe_import("plan_entitlement", ["PlanEntitlement"]))
_imports.update(safe_import("tenant_feature", ["TenantFeature"]))

# Authentication
_imports.update(safe_import("refresh_token", ["RefreshToken"]))
_imports.update(safe_import("email_verification_token", ["EmailVerificationToken"]))
_imports.update(safe_import("password_reset_token", ["PasswordResetToken"]))
_imports.update(safe_import("user_tenant_role", ["UserTenantRole"]))

# RBAC System - NOVOS MODELS
_imports.update(safe_import("rbac_role", ["RBACRole"]))
_imports.update(safe_import("rbac_permission", ["RBACPermission"]))
_imports.update(safe_import("rbac_role_permission", ["RBACRolePermission"]))

# Audit and Analytics - NOVOS MODELS
_imports.update(safe_import("audit_log", ["AuditLog"]))
_imports.update(safe_import("user_behavior_metric", ["UserBehaviorMetric"]))
_imports.update(safe_import("user_insight", ["UserInsight"]))
_imports.update(safe_import("user_subscription", ["UserSubscription"]))

# Workspace related
_imports.update(safe_import("workspace_member", ["WorkspaceMember"]))
_imports.update(safe_import("workspace_activity", ["WorkspaceActivity"]))
_imports.update(safe_import("workspace_invitation", ["WorkspaceInvitation"]))

# Project related - NOVOS MODELS
_imports.update(safe_import("workspace_project", ["WorkspaceProject"]))
_imports.update(safe_import("project_comment", ["ProjectComment"]))
_imports.update(safe_import("project_version", ["ProjectVersion"]))

# Billing and payments
_imports.update(safe_import("subscription", ["Subscription"]))

# User-related models - NOVOS MODELS  
_imports.update(safe_import("user_variable", ["UserVariable"]))

# LLM and conversation
_imports.update(safe_import("conversation", ["Conversation"]))
_imports.update(safe_import("message", ["Message"]))
_imports.update(safe_import("message_feedback", ["MessageFeedback"]))
_imports.update(safe_import("conversation_llm", ["ConversationLLM"]))
_imports.update(safe_import("usage_log", ["UsageLog"]))
_imports.update(safe_import("billing_event", ["BillingEvent"]))

# Workflow and execution
_imports.update(safe_import("workflow", ["Workflow"]))
_imports.update(safe_import("workflow_node", ["WorkflowNode"]))
_imports.update(safe_import("workflow_connection", ["WorkflowConnection"]))
_imports.update(safe_import("workflow_execution", ["WorkflowExecution", "NodeExecution"], exclude_classes=["NodeExecution"]))

# Tools and templates
_imports.update(safe_import("template", ["WorkflowTemplate"]))
_imports.update(safe_import("tag", ["Tag"]))
_imports.update(safe_import("marketplace", ["MarketplaceComponent"]))

# Analytics - NOVOS MODELS COMPLETOS
_imports.update(safe_import("analytics_alert", ["AnalyticsAlert"]))
_imports.update(safe_import("analytics_dashboard", ["AnalyticsDashboard"]))
_imports.update(safe_import("analytics_event", ["AnalyticsEvent"]))
_imports.update(safe_import("analytics_export", ["AnalyticsExport"]))
_imports.update(safe_import("analytics_metric", ["AnalyticsMetric"]))
_imports.update(safe_import("analytics_report", ["AnalyticsReport"]))
_imports.update(safe_import("business_metric", ["BusinessMetric"]))
_imports.update(safe_import("custom_report", ["CustomReport"]))
_imports.update(safe_import("report_execution", ["ReportExecution"]))

# Contact and Campaign models
_imports.update(safe_import("contact", ["Contact"]))
_imports.update(safe_import("contact_list", ["ContactList"]))
_imports.update(safe_import("contact_event", ["ContactEvent"]))
_imports.update(safe_import("contact_interaction", ["ContactInteraction"]))
_imports.update(safe_import("campaign", ["Campaign"]))
_imports.update(safe_import("campaign_contact", ["CampaignContact"]))
_imports.update(safe_import("conversion_journey", ["ConversionJourney"]))

# User variables (features) - já importado acima
# _imports.update(safe_import("user_variable", ["UserVariable"]))

# Agent-related models - NOVOS MODELS
_imports.update(safe_import("knowledge_base", ["KnowledgeBase"]))
_imports.update(safe_import("node_category", ["NodeCategory"]))
_imports.update(safe_import("node_execution", ["NodeExecution"]))
_imports.update(safe_import("tool", ["Tool"]))
_imports.update(safe_import("agent_knowledge_base", ["AgentKnowledgeBase"]))
_imports.update(safe_import("agent_tool", ["AgentTool"]))
_imports.update(safe_import("agent_model", ["AgentModel"]))
_imports.update(safe_import("agent_acl", ["AgentACL"]))
_imports.update(safe_import("agent_configuration", ["AgentConfiguration"]))
_imports.update(safe_import("agent_error_log", ["AgentErrorLog"]))
_imports.update(safe_import("agent_hierarchy", ["AgentHierarchy"]))
_imports.update(safe_import("agent_quota", ["AgentQuota"]))
_imports.update(safe_import("agent_trigger", ["AgentTrigger"]))
_imports.update(safe_import("agent_usage_metric", ["AgentUsageMetric"]))

# Billing and payment models - NOVOS MODELS  
_imports.update(safe_import("coupon", ["Coupon"]))
_imports.update(safe_import("invoice", ["Invoice"]))
_imports.update(safe_import("payment_customer", ["PaymentCustomer"]))
_imports.update(safe_import("payment_method", ["PaymentMethod"]))
_imports.update(safe_import("payment_provider", ["PaymentProvider"]))

# Project and workspace models - NOVOS MODELS
_imports.update(safe_import("project_collaborator", ["ProjectCollaborator"]))

# Advanced Resources - NOVOS MODELS
_imports.update(safe_import("webhook_log", ["WebhookLog"]))

# Adicionar todas as classes importadas ao namespace do módulo
globals().update(_imports)

# __all__ contém apenas classes que foram importadas com sucesso
__all__ = list(_imports.keys())

# Aliases para compatibilidade com endpoints específicos
if 'Conversation' in _imports:
    globals()['LLMConversation'] = _imports['Conversation']
    __all__.append('LLMConversation')

if 'Message' in _imports:
    globals()['LLMMessage'] = _imports['Message']
    __all__.append('LLMMessage')

# Relatório de importação
print(f"✅ Models importados: {len(__all__)} classes")
if len(__all__) < 20:
    print(f"   Classes: {', '.join(__all__)}")
