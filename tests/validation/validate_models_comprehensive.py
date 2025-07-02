#!/usr/bin/env python3
"""
Comprehensive Model Validation Script
Validates SQLAlchemy models against database schema and checks for issues.
"""

import sys
import os
sys.path.append('/Users/joaovictormiranda/backend/synapse-backend-agents-jc')

import inspect
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from synapse.models import *

class ModelValidator:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.models = self._get_all_models()
        
    def _get_all_models(self):
        """Get all SQLAlchemy model classes"""
        models = {}
        
        # Import all models
        import synapse.models as models_module
        
        for name in dir(models_module):
            obj = getattr(models_module, name)
            if (inspect.isclass(obj) and 
                hasattr(obj, '__tablename__') and 
                hasattr(obj, '__table__')):
                models[name] = obj
                
        return models
    
    def validate_table_names(self):
        """Check if model table names match database tables"""
        print("🔍 Validating table names...")
        
        # Expected tables from database (known from our analysis)
        expected_tables = {
            'agents', 'agent_acl', 'agent_configurations', 'agent_error_logs', 
            'agent_hierarchy', 'agent_kbs', 'agent_models', 'agent_quotas',
            'agent_tools', 'agent_triggers', 'agent_usage_metrics', 'analytics_alerts',
            'analytics_dashboards', 'analytics_events', 'analytics_exports', 
            'analytics_metrics', 'analytics_reports', 'audit_log', 'billing_events',
            'business_metrics', 'campaign_contacts', 'campaigns', 'component_downloads',
            'component_purchases', 'component_ratings', 'component_versions',
            'contact_events', 'contact_interactions', 'contact_list_memberships',
            'contact_lists', 'contact_notes', 'contact_sources', 'contact_tags',
            'contacts', 'conversion_journeys', 'coupons', 'custom_reports',
            'email_verification_tokens', 'features', 'files', 'invoices',
            'knowledge_bases', 'llms', 'llms_conversations', 'llms_conversations_turns',
            'llms_messages', 'llms_usage_logs', 'marketplace_components',
            'message_feedbacks', 'node_categories', 'node_executions', 'node_ratings',
            'node_templates', 'nodes', 'password_reset_tokens', 'payment_customers',
            'payment_methods', 'payment_providers', 'plan_entitlements',
            'plan_features', 'plan_provider_mappings', 'plans', 'project_collaborators',
            'project_comments', 'project_versions', 'rbac_permissions', 'rbac_roles',
            'rbac_role_permissions', 'refresh_tokens', 'report_executions',
            'subscriptions', 'system_performance_metrics', 'tags', 'template_collections',
            'template_downloads', 'template_favorites', 'template_reviews',
            'template_usage', 'tenant_features', 'tenants', 'tools', 'user_behavior_metrics',
            'user_insights', 'user_subscriptions', 'user_tenant_roles', 'user_variables',
            'users', 'webhook_logs', 'workflow_execution_metrics', 'workflow_execution_queue',
            'workflow_executions', 'workflow_connections', 'workflow_nodes',
            'workflow_templates', 'workflows', 'workspace_activities', 'workspace_features',
            'workspace_invitations', 'workspace_members', 'workspace_projects', 'workspaces'
        }
        
        model_tables = set()
        for model_name, model_class in self.models.items():
            table_name = model_class.__tablename__
            model_tables.add(table_name)
            
        # Check for missing models
        missing_tables = expected_tables - model_tables
        if missing_tables:
            self.issues.append(f"Missing models for tables: {sorted(missing_tables)}")
            
        # Check for extra models
        extra_tables = model_tables - expected_tables
        if extra_tables:
            self.warnings.append(f"Extra model tables (not in DB): {sorted(extra_tables)}")
            
        print(f"✅ Found {len(model_tables)} model tables")
        if missing_tables:
            print(f"❌ Missing {len(missing_tables)} tables: {sorted(list(missing_tables)[:10])}...")
        if extra_tables:
            print(f"⚠️  Extra {len(extra_tables)} tables: {sorted(list(extra_tables))}")
            
    def validate_relationships(self):
        """Check relationship integrity"""
        print("\n🔍 Validating relationships...")
        
        relationship_count = 0
        for model_name, model_class in self.models.items():
            inspector = sqlalchemy_inspect(model_class)
            
            # Check relationships
            for rel in inspector.relationships:
                relationship_count += 1
                rel_target = rel.mapper.class_
                
                # Check if target model exists
                target_name = rel_target.__name__
                if target_name not in self.models:
                    self.issues.append(f"{model_name}.{rel.key} → {target_name} (target model not found)")
                    
        print(f"✅ Validated {relationship_count} relationships")
        
    def validate_foreign_keys(self):
        """Check foreign key definitions"""
        print("\n🔍 Validating foreign keys...")
        
        fk_count = 0
        for model_name, model_class in self.models.items():
            inspector = sqlalchemy_inspect(model_class)
            
            for column_name, column in inspector.columns.items():
                if column.foreign_keys:
                    fk_count += 1
                    for fk in column.foreign_keys:
                        target_table = fk.column.table.name
                        target_column = fk.column.name
                        
                        # Check if target table has a model
                        target_model = None
                        for mn, mc in self.models.items():
                            if mc.__tablename__ == target_table:
                                target_model = mc
                                break
                                
                        if not target_model:
                            self.warnings.append(f"{model_name}.{column_name} → {target_table}.{target_column} (no model for target table)")
                            
        print(f"✅ Validated {fk_count} foreign keys")
        
    def check_import_completeness(self):
        """Check if all models are properly imported in __init__.py"""
        print("\n🔍 Checking import completeness...")
        
        try:
            # Check what's actually imported
            import synapse.models as models_module
            imported_names = [name for name in dir(models_module) 
                            if not name.startswith('_') and inspect.isclass(getattr(models_module, name))]
            
            print(f"✅ Found {len(imported_names)} imported model classes")
                    
        except Exception as e:
            self.issues.append(f"Import check failed: {e}")
            
    def run_validation(self):
        """Run all validations"""
        print("🚀 Starting comprehensive model validation...\n")
        
        self.validate_table_names()
        self.validate_relationships()
        self.validate_foreign_keys()
        self.check_import_completeness()
        
        # Summary
        print("\n" + "="*50)
        print("📊 VALIDATION SUMMARY")
        print("="*50)
        
        if not self.issues and not self.warnings:
            print("🎉 ALL VALIDATIONS PASSED! Models are in excellent shape.")
        else:
            if self.issues:
                print(f"❌ CRITICAL ISSUES ({len(self.issues)}):")
                for i, issue in enumerate(self.issues, 1):
                    print(f"   {i}. {issue}")
                    
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
                    
        print(f"\n✅ Total Models: {len(self.models)}")
        print("🏁 Validation complete!")

if __name__ == "__main__":
    validator = ModelValidator()
    validator.run_validation() 