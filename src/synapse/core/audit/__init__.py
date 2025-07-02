"""
Audit Core Module - Complete Audit System
Tasks 5.1, 5.2, 5.3: Sistema completo de auditoria

Módulo central de auditoria do SynapScale com:
- AuditLog model (já implementado)
- Automatic logging via SQLAlchemy events
- Retention policies with automated cleanup
- Comprehensive audit schemas
"""

from .service import (
    AuditService,
    audit_service,
    set_audit_user,
    clear_audit_user,
    audit_context,
    manual_audit_log,
    get_audit_stats,
    setup_audit_logging
)

from .retention import (
    RetentionManager,
    RetentionPolicy,
    RetentionPolicyType,
    RetentionAction,
    retention_manager,
    add_retention_policy,
    execute_retention_policy,
    execute_all_retention_policies,
    get_retention_report
)

__all__ = [
    # Audit Service
    'AuditService',
    'audit_service',
    'set_audit_user',
    'clear_audit_user',
    'audit_context',
    'manual_audit_log',
    'get_audit_stats',
    'setup_audit_logging',
    
    # Retention Management
    'RetentionManager',
    'RetentionPolicy',
    'RetentionPolicyType',
    'RetentionAction',
    'retention_manager',
    'add_retention_policy',
    'execute_retention_policy',
    'execute_all_retention_policies',
    'get_retention_report'
] 