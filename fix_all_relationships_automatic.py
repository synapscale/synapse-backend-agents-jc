#!/usr/bin/env python3
"""
Script para corrigir automaticamente TODOS os relacionamentos back_populates faltando
"""

import os
import re
import sys
from pathlib import Path

def main():
    """Corrige automaticamente todos os relacionamentos"""
    
    # Mapear todos os relacionamentos faltando
    missing_relationships = {
        'User': [
            'analytics_alerts', 'analytics_exports', 'analytics_reports', 'report_executions',
            'created_campaigns', 'user_behavior_metrics', 'user_variables', 'user_insights',
            'user_tenant_roles', 'user_subscriptions', 'workspace_members', 'workspace_invitations',
            'workspace_activities', 'payment_customers', 'usage_logs', 'billing_events'
        ],
        'Tenant': [
            'analytics_exports', 'analytics_reports', 'users', 'workspaces', 'contacts',
            'campaigns', 'contact_interactions', 'contact_events', 'conversion_journeys',
            'user_behavior_metrics', 'user_variables', 'user_insights', 'user_tenant_roles',
            'user_subscriptions', 'workspace_members', 'report_executions', 'usage_logs',
            'billing_events', 'contact_lists'
        ],
        'Workspace': [
            'analytics_dashboards', 'custom_reports', 'workspace_members', 'workspace_invitations',
            'workspace_activities'
        ],
        'Contact': [
            'conversion_journeys', 'contact_interactions', 'contact_events'
        ]
    }
    
    # Adicionar relacionamentos para cada modelo
    for model_name, relationships in missing_relationships.items():
        model_file = f"src/synapse/models/{model_name.lower()}.py"
        
        if not Path(model_file).exists():
            print(f"❌ Arquivo {model_file} não encontrado")
            continue
            
        print(f"🔧 Adicionando relacionamentos para {model_name}...")
        add_relationships_to_model(model_file, model_name, relationships)
    
    print("\n✅ TODOS os relacionamentos foram adicionados!")

def add_relationships_to_model(file_path, model_name, relationships):
    """Adiciona relacionamentos a um modelo específico"""
    
    content = Path(file_path).read_text()
    
    # Encontrar onde adicionar os relacionamentos (antes do final da classe)
    lines = content.split('\n')
    
    # Encontrar a última linha de relacionamento ou método da classe
    insert_index = -1
    for i, line in enumerate(lines):
        if 'relationship(' in line or 'def ' in line and not line.strip().startswith('#'):
            insert_index = i
    
    if insert_index == -1:
        # Se não encontrou, adicionar antes do final da classe
        for i, line in enumerate(lines):
            if line.strip() == '' and i > 0 and 'class ' in lines[i-10:i]:
                insert_index = i
                break
    
    # Gerar código dos relacionamentos
    relationship_code = []
    relationship_code.append(f"    # === RELACIONAMENTOS ADICIONADOS AUTOMATICAMENTE ===")
    
    for rel_name in relationships:
        source_model = infer_source_model(rel_name)
        back_populates = infer_back_populates(model_name, rel_name)
        cascade = "cascade=\"all, delete-orphan\"" if should_use_cascade(rel_name) else ""
        
        rel_code = f"""    {rel_name} = relationship(
        "{source_model}", back_populates="{back_populates}"{', ' + cascade if cascade else ''}
    )"""
        relationship_code.append(rel_code)
    
    # Inserir o código
    if insert_index > 0:
        lines.insert(insert_index + 1, '\n'.join(relationship_code))
    else:
        # Adicionar antes da última linha da classe
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() and not lines[i].startswith(' '):
                lines.insert(i, '\n'.join(relationship_code))
                break
    
    # Salvar arquivo
    Path(file_path).write_text('\n'.join(lines))

def infer_source_model(relationship_name):
    """Infere o modelo de origem baseado no nome do relacionamento"""
    
    mappings = {
        'analytics_alerts': 'AnalyticsAlert',
        'analytics_exports': 'AnalyticsExport', 
        'analytics_reports': 'AnalyticsReport',
        'analytics_dashboards': 'AnalyticsDashboard',
        'report_executions': 'ReportExecution',
        'created_campaigns': 'Campaign',
        'campaigns': 'Campaign',
        'user_behavior_metrics': 'UserBehaviorMetric',
        'user_variables': 'UserVariable',
        'user_insights': 'UserInsight',
        'user_tenant_roles': 'UserTenantRole',
        'user_subscriptions': 'UserSubscription',
        'workspace_members': 'WorkspaceMember',
        'workspace_invitations': 'WorkspaceInvitation',
        'workspace_activities': 'WorkspaceActivity',
        'payment_customers': 'PaymentCustomer',
        'usage_logs': 'UsageLog',
        'billing_events': 'BillingEvent',
        'custom_reports': 'CustomReport',
        'conversion_journeys': 'ConversionJourney',
        'contact_interactions': 'ContactInteraction',
        'contact_events': 'ContactEvent',
        'contact_lists': 'ContactList',
        'users': 'User',
        'workspaces': 'Workspace',
        'contacts': 'Contact'
    }
    
    return mappings.get(relationship_name, relationship_name.title().replace('_', ''))

def infer_back_populates(model_name, relationship_name):
    """Infere o nome do back_populates"""
    
    specific_mappings = {
        ('User', 'analytics_alerts'): 'owner',
        ('User', 'analytics_exports'): 'owner',
        ('User', 'analytics_reports'): 'owner',
        ('User', 'created_campaigns'): 'creator',
        ('Tenant', 'users'): 'tenant',
        ('Contact', 'conversion_journeys'): 'contact',
        ('Contact', 'contact_interactions'): 'contact',
        ('Contact', 'contact_events'): 'contact'
    }
    
    key = (model_name, relationship_name)
    if key in specific_mappings:
        return specific_mappings[key]
    
    # Padrão geral
    return model_name.lower()

def should_use_cascade(relationship_name):
    """Determina se deve usar cascade"""
    cascade_patterns = [
        'created_', 'owned_', 'user_', '_reports', '_events', '_metrics',
        '_executions', '_campaigns', '_journeys', '_alerts', '_exports',
        '_activities', '_variables', '_insights'
    ]
    
    return any(pattern in relationship_name for pattern in cascade_patterns)

if __name__ == "__main__":
    main() 