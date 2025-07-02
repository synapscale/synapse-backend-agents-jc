#!/usr/bin/env python3
"""
Análise e priorização dos modelos restantes por categoria
"""

# Todos os 103 tabelas no banco
ALL_TABLES = [
    'agent_acl', 'agent_configurations', 'agent_error_logs', 'agent_hierarchy', 'agent_kbs',
    'agent_models', 'agent_quotas', 'agent_tools', 'agent_triggers', 'agent_usage_metrics',
    'agents', 'alembic_version', 'analytics_alerts', 'analytics_dashboards', 'analytics_events',
    'analytics_exports', 'analytics_metrics', 'analytics_reports', 'audit_log', 'billing_events',
    'business_metrics', 'campaign_contacts', 'campaigns', 'component_downloads', 'component_purchases',
    'component_ratings', 'component_versions', 'contact_events', 'contact_interactions',
    'contact_list_memberships', 'contact_lists', 'contact_notes', 'contact_sources', 'contact_tags',
    'contacts', 'conversion_journeys', 'coupons', 'custom_reports', 'email_verification_tokens',
    'features', 'files', 'invoices', 'knowledge_bases', 'llms', 'llms_conversations',
    'llms_conversations_turns', 'llms_messages', 'llms_usage_logs', 'marketplace_components',
    'message_feedbacks', 'node_categories', 'node_executions', 'node_ratings', 'node_templates',
    'nodes', 'password_reset_tokens', 'payment_customers', 'payment_methods', 'payment_providers',
    'plan_entitlements', 'plan_features', 'plan_provider_mappings', 'plans', 'project_collaborators',
    'project_comments', 'project_versions', 'rbac_permissions', 'rbac_role_permissions', 'rbac_roles',
    'refresh_tokens', 'report_executions', 'subscriptions', 'system_health', 'system_performance_metrics',
    'tags', 'template_collections', 'template_downloads', 'template_favorites', 'template_reviews',
    'template_usage', 'tenant_features', 'tenants', 'tools', 'user_behavior_metrics', 'user_insights',
    'user_subscriptions', 'user_tenant_roles', 'user_variables', 'users', 'webhook_logs',
    'workflow_connections', 'workflow_execution_metrics', 'workflow_execution_queue', 'workflow_executions',
    'workflow_nodes', 'workflow_templates', 'workflows', 'workspace_activities', 'workspace_features',
    'workspace_invitations', 'workspace_members', 'workspace_projects', 'workspaces'
]

# Modelos já existentes (via análise anterior)
EXISTING_MODELS = [
    'agent_acl', 'agent_configurations', 'agent_error_logs', 'agent_hierarchy', 'agent_kbs',
    'agent_models', 'agent_quotas', 'agent_tools', 'agent_triggers', 'agents', 'audit_log',
    'billing_events', 'campaign_contacts', 'campaigns', 'contact_events', 'contact_interactions',
    'contacts', 'coupons', 'email_verification_tokens', 'features', 'files', 'invoices', 
    'llms', 'llms_conversations', 'llms_messages', 'llms_usage_logs', 'nodes', 'payment_methods',
    'payment_providers', 'plan_entitlements', 'plan_features', 'plans', 'project_collaborators',
    'project_comments', 'rbac_roles', 'tags', 'tenant_features', 'tenants', 'tools', 'users',
    'workflow_executions', 'workflows', 'workspaces'
]

# Modelos criados recentemente (12 modelos)
NEWLY_CREATED = [
    'agent_usage_metrics', 'user_subscriptions', 'user_variables', 'user_insights',
    'rbac_permissions', 'rbac_role_permissions', 'refresh_tokens', 'password_reset_tokens',
    'knowledge_bases', 'message_feedbacks', 'subscriptions', 'workspace_members'
]

# Sistema (não precisa de modelo)
SYSTEM_TABLES = ['alembic_version']

def categorize_remaining_models():
    """Categorizar modelos restantes por funcionalidade"""
    
    # Calcular modelos faltantes
    all_models_needed = set(ALL_TABLES) - set(SYSTEM_TABLES)
    existing_models_set = set(EXISTING_MODELS + NEWLY_CREATED)
    missing_models = list(all_models_needed - existing_models_set)
    
    print(f"📊 ANÁLISE DE MODELOS:")
    print(f"  Total de tabelas: {len(ALL_TABLES)}")
    print(f"  Modelos existentes: {len(EXISTING_MODELS)}")
    print(f"  Modelos criados recentemente: {len(NEWLY_CREATED)}")
    print(f"  Tabelas do sistema: {len(SYSTEM_TABLES)}")
    print(f"  Modelos ainda faltantes: {len(missing_models)}")
    print()
    
    # Categorização por funcionalidade
    categories = {
        "📊 Analytics & Reports": [
            'analytics_alerts', 'analytics_dashboards', 'analytics_events', 'analytics_exports',
            'analytics_metrics', 'analytics_reports', 'business_metrics', 'custom_reports',
            'report_executions', 'user_behavior_metrics'
        ],
        "🏢 Workspace & Projects": [
            'workspace_activities', 'workspace_features', 'workspace_invitations', 'workspace_projects',
            'project_versions', 'project_comments'
        ],
        "🛒 Marketplace & Templates": [
            'marketplace_components', 'component_downloads', 'component_purchases', 'component_ratings',
            'component_versions', 'template_collections', 'template_downloads', 'template_favorites',
            'template_reviews', 'template_usage'
        ],
        "🔗 Workflows & Nodes": [
            'workflow_connections', 'workflow_execution_metrics', 'workflow_execution_queue',
            'workflow_nodes', 'workflow_templates', 'node_categories', 'node_executions',
            'node_ratings', 'node_templates'
        ],
        "📞 Contacts & Campaigns": [
            'contact_list_memberships', 'contact_lists', 'contact_notes', 'contact_sources',
            'contact_tags', 'conversion_journeys'
        ],
        "💰 Billing & Payments": [
            'payment_customers', 'plan_provider_mappings'
        ],
        "🗨️ LLM & Conversations": [
            'llms_conversations_turns'
        ],
        "🔧 System & Monitoring": [
            'system_health', 'system_performance_metrics', 'webhook_logs'
        ],
        "👥 User Management": [
            'user_tenant_roles'
        ]
    }
    
    for category, tables in categories.items():
        category_missing = [t for t in tables if t in missing_models]
        if category_missing:
            print(f"{category} ({len(category_missing)} faltantes):")
            for table in category_missing:
                priority = "HIGH" if category in ["🏢 Workspace & Projects", "📊 Analytics & Reports"] else "MEDIUM"
                print(f"  ⚡ {table} [{priority}]")
            print()
    
    return missing_models, categories

def main():
    print("🔍 ANÁLISE DOS MODELOS RESTANTES\n")
    missing_models, categories = categorize_remaining_models()
    
    # Sugestão de próximos passos
    print("🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("1. Criar modelos de Workspace & Projects (críticos para funcionalidade)")
    print("2. Criar modelos de Analytics & Reports (importante para insights)")
    print("3. Criar modelos de Workflows & Nodes (para execução de automações)")
    print("4. Criar modelos de Marketplace & Templates (para extensibilidade)")
    print("5. Criar modelos restantes por ordem de importância")
    print()
    
    print("💡 STRATEGY:")
    print("- Focar primeiro nos modelos que afetam funcionalidades principais")
    print("- Implementar em lotes de 5-10 modelos por vez")
    print("- Testar cada lote antes de prosseguir")
    print("- Criar schemas Pydantic correspondentes em paralelo")

if __name__ == "__main__":
    main()
