"""
Audit Service - Automatic Audit Logging System
Task 5.2: Configurar logging automático

Sistema avançado de auditoria com captura automática de mudanças
via SQLAlchemy events para todas as operações críticas do sistema.
"""

import json
import logging
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timezone
from contextlib import contextmanager
from threading import local

from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import Pool
from sqlalchemy.inspection import inspect

from synapse.models.audit_log import AuditLog
from synapse.database import Base, SessionLocal

logger = logging.getLogger(__name__)

# Thread-local storage for tracking user context
_audit_context = local()

class AuditService:
    """
    Serviço central de auditoria com logging automático
    Implementa captura automática via SQLAlchemy events
    """
    
    def __init__(self):
        """Inicializa o serviço de auditoria"""
        self.enabled = True
        self.critical_tables = {
            # Core entities
            'users', 'tenants', 'workspaces', 'agents',
            # RBAC
            'rbac_roles', 'rbac_permissions', 'rbac_role_permissions', 'user_tenant_roles',
            # Authentication
            'password_reset_tokens', 'email_verification_tokens',
            # Agent system
            'agent_acl', 'agent_configurations', 'agent_quotas', 'agent_triggers',
            # Payments & billing
            'payment_customers', 'payment_methods', 'invoices', 'subscriptions',
            # Knowledge & tools
            'knowledge_bases', 'tools', 'agent_kbs', 'agent_tools'
        }
        self.sensitive_fields = {
            'password', 'hashed_password', 'token', 'secret_key', 'api_key',
            'private_key', 'refresh_token', 'access_token', 'credit_card'
        }
        self.exclude_tables = {
            'audit_log', 'analytics_events', 'usage_logs', 'agent_error_logs'
        }
        
        # Performance tracking
        self.audit_stats = {
            'total_events': 0,
            'failed_events': 0,
            'last_error': None
        }
        
        logger.info("Audit Service initialized")
    
    def set_user_context(self, user_id: str, session_id: Optional[str] = None, 
                        ip_address: Optional[str] = None):
        """Define contexto do usuário atual para auditoria"""
        _audit_context.user_id = user_id
        _audit_context.session_id = session_id
        _audit_context.ip_address = ip_address
    
    def clear_user_context(self):
        """Limpa contexto do usuário"""
        for attr in ['user_id', 'session_id', 'ip_address']:
            if hasattr(_audit_context, attr):
                delattr(_audit_context, attr)
    
    @contextmanager
    def audit_context(self, user_id: str, session_id: Optional[str] = None, 
                     ip_address: Optional[str] = None):
        """Context manager para definir contexto de auditoria temporariamente"""
        self.set_user_context(user_id, session_id, ip_address)
        try:
            yield
        finally:
            self.clear_user_context()
    
    def get_current_user_id(self) -> Optional[str]:
        """Retorna o ID do usuário atual do contexto"""
        return getattr(_audit_context, 'user_id', None)
    
    def is_table_auditable(self, table_name: str) -> bool:
        """Verifica se uma tabela deve ser auditada"""
        if not self.enabled:
            return False
        
        # Remove schema prefix se existir
        clean_table = table_name.split('.')[-1]
        
        # Excluir tabelas específicas
        if clean_table in self.exclude_tables:
            return False
        
        # Auditar apenas tabelas críticas
        return clean_table in self.critical_tables
    
    def sanitize_field_value(self, field_name: str, value: Any) -> Any:
        """Sanitiza valores de campos sensíveis"""
        if any(sensitive in field_name.lower() for sensitive in self.sensitive_fields):
            return "***MASKED***" if value is not None else None
        return value
    
    def extract_record_changes(self, instance, operation: str) -> Dict[str, Any]:
        """Extrai mudanças de um registro SQLAlchemy"""
        changes = {}
        state = inspect(instance)
        
        if operation == 'CREATE':
            # Para criação, capturar todos os campos não-nulos
            for attr in state.attrs:
                value = getattr(instance, attr.key, None)
                if value is not None:
                    changes[attr.key] = {
                        'new': self.sanitize_field_value(attr.key, value)
                    }
        
        elif operation == 'UPDATE':
            # Para atualização, capturar apenas campos modificados
            for attr in state.attrs:
                if attr.history.has_changes():
                    old_value = attr.history.deleted[0] if attr.history.deleted else None
                    new_value = getattr(instance, attr.key, None)
                    
                    changes[attr.key] = {
                        'old': self.sanitize_field_value(attr.key, old_value),
                        'new': self.sanitize_field_value(attr.key, new_value)
                    }
        
        elif operation == 'DELETE':
            # Para deleção, capturar valores atuais
            for attr in state.attrs:
                value = getattr(instance, attr.key, None)
                if value is not None:
                    changes[attr.key] = {
                        'old': self.sanitize_field_value(attr.key, value)
                    }
        
        return changes
    
    def create_audit_log(self, session: Session, table_name: str, record_id: str, 
                        operation: str, changes: Dict[str, Any]):
        """Cria um log de auditoria"""
        try:
            audit_log = AuditLog(
                table_name=table_name,
                record_id=record_id,
                operation=operation,
                changed_by=self.get_current_user_id(),
                diffs=changes
            )
            
            session.add(audit_log)
            session.flush()  # Força inserção sem commit
            
            self.audit_stats['total_events'] += 1
            logger.debug(f"Audit log created: {operation} on {table_name}:{record_id}")
            
        except Exception as e:
            self.audit_stats['failed_events'] += 1
            self.audit_stats['last_error'] = str(e)
            logger.error(f"Failed to create audit log: {e}")
    
    def setup_automatic_logging(self, engine: Engine):
        """Configura logging automático via SQLAlchemy events"""
        
        @event.listens_for(Session, 'before_commit')
        def before_commit(session):
            """Captura mudanças antes do commit"""
            if not self.enabled:
                return
            
            # Coletar todos os objetos modificados
            audit_entries = []
            
            # Objetos novos (CREATE)
            for instance in session.new:
                table_name = instance.__tablename__
                if self.is_table_auditable(table_name):
                    record_id = str(getattr(instance, 'id', 'unknown'))
                    changes = self.extract_record_changes(instance, 'CREATE')
                    audit_entries.append((table_name, record_id, 'CREATE', changes))
            
            # Objetos modificados (UPDATE)
            for instance in session.dirty:
                table_name = instance.__tablename__
                if self.is_table_auditable(table_name):
                    record_id = str(getattr(instance, 'id', 'unknown'))
                    changes = self.extract_record_changes(instance, 'UPDATE')
                    if changes:  # Só auditar se há mudanças reais
                        audit_entries.append((table_name, record_id, 'UPDATE', changes))
            
            # Objetos deletados (DELETE)
            for instance in session.deleted:
                table_name = instance.__tablename__
                if self.is_table_auditable(table_name):
                    record_id = str(getattr(instance, 'id', 'unknown'))
                    changes = self.extract_record_changes(instance, 'DELETE')
                    audit_entries.append((table_name, record_id, 'DELETE', changes))
            
            # Criar logs de auditoria
            for table_name, record_id, operation, changes in audit_entries:
                self.create_audit_log(session, table_name, record_id, operation, changes)
        
        @event.listens_for(Pool, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Configurações específicas do banco se necessário"""
            pass
        
        logger.info("Automatic audit logging configured successfully")
    
    def disable_temporarily(self):
        """Desabilita auditoria temporariamente"""
        self.enabled = False
        logger.warning("Audit logging temporarily disabled")
    
    def enable(self):
        """Reabilita auditoria"""
        self.enabled = True
        logger.info("Audit logging enabled")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de auditoria"""
        return {
            'enabled': self.enabled,
            'total_events': self.audit_stats['total_events'],
            'failed_events': self.audit_stats['failed_events'],
            'success_rate': (
                (self.audit_stats['total_events'] - self.audit_stats['failed_events']) /
                max(self.audit_stats['total_events'], 1)
            ) * 100,
            'last_error': self.audit_stats['last_error'],
            'critical_tables_count': len(self.critical_tables),
            'excluded_tables_count': len(self.exclude_tables)
        }
    
    def add_critical_table(self, table_name: str):
        """Adiciona uma tabela à lista de tabelas críticas"""
        self.critical_tables.add(table_name)
        logger.info(f"Added {table_name} to critical tables")
    
    def remove_critical_table(self, table_name: str):
        """Remove uma tabela da lista de tabelas críticas"""
        self.critical_tables.discard(table_name)
        logger.info(f"Removed {table_name} from critical tables")
    
    def manual_audit_log(self, table_name: str, record_id: str, operation: str, 
                        changes: Dict[str, Any], user_id: Optional[str] = None):
        """Cria um log de auditoria manual"""
        with SessionLocal() as session:
            try:
                audit_log = AuditLog(
                    table_name=table_name,
                    record_id=record_id,
                    operation=operation,
                    changed_by=user_id or self.get_current_user_id(),
                    diffs=changes
                )
                
                session.add(audit_log)
                session.commit()
                
                self.audit_stats['total_events'] += 1
                logger.info(f"Manual audit log created: {operation} on {table_name}:{record_id}")
                
            except Exception as e:
                session.rollback()
                self.audit_stats['failed_events'] += 1
                self.audit_stats['last_error'] = str(e)
                logger.error(f"Failed to create manual audit log: {e}")
                raise

# Global audit service instance
audit_service = AuditService()

# Convenience functions
def set_audit_user(user_id: str, session_id: Optional[str] = None, 
                  ip_address: Optional[str] = None):
    """Define usuário atual para auditoria"""
    audit_service.set_user_context(user_id, session_id, ip_address)

def clear_audit_user():
    """Limpa contexto de usuário da auditoria"""
    audit_service.clear_user_context()

def audit_context(user_id: str, session_id: Optional[str] = None, 
                 ip_address: Optional[str] = None):
    """Context manager para auditoria"""
    return audit_service.audit_context(user_id, session_id, ip_address)

def manual_audit_log(table_name: str, record_id: str, operation: str, 
                    changes: Dict[str, Any], user_id: Optional[str] = None):
    """Cria log de auditoria manual"""
    audit_service.manual_audit_log(table_name, record_id, operation, changes, user_id)

def get_audit_stats():
    """Retorna estatísticas de auditoria"""
    return audit_service.get_statistics()

def setup_audit_logging(engine: Engine):
    """Configura logging automático de auditoria"""
    audit_service.setup_automatic_logging(engine) 