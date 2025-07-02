"""
Audit Log Retention Policy System
Task 5.3: Estabelecer políticas de retenção

Sistema avançado de retenção de dados de auditoria com limpeza
automática baseada em políticas configuráveis e compliance.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum
import asyncio

from sqlalchemy import func, select, delete, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.models.audit_log import AuditLog
from synapse.database import SessionLocal
from synapse.schemas.audit import AuditOperation, AuditSeverity, AuditCategory

logger = logging.getLogger(__name__)

class RetentionPolicyType(Enum):
    """Tipos de políticas de retenção"""
    TIME_BASED = "time_based"
    COUNT_BASED = "count_based"
    SIZE_BASED = "size_based"
    COMPLIANCE_BASED = "compliance_based"

class RetentionAction(Enum):
    """Ações de retenção"""
    DELETE = "delete"
    ARCHIVE = "archive"
    COMPRESS = "compress"
    NOTIFY = "notify"

@dataclass
class RetentionPolicy:
    """Definição de uma política de retenção"""
    
    name: str
    description: str
    policy_type: RetentionPolicyType
    action: RetentionAction
    
    # Parâmetros de tempo
    retention_days: Optional[int] = None
    
    # Parâmetros de contagem
    max_records: Optional[int] = None
    
    # Parâmetros de tamanho
    max_size_mb: Optional[int] = None
    
    # Filtros específicos
    operations: Optional[List[AuditOperation]] = None
    tables: Optional[List[str]] = None
    severity: Optional[AuditSeverity] = None
    category: Optional[AuditCategory] = None
    
    # Configurações
    enabled: bool = True
    dry_run: bool = False
    backup_before_delete: bool = True
    
    # Metadados
    created_at: Optional[datetime] = None
    last_executed: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None

class RetentionManager:
    """
    Gerenciador de políticas de retenção para logs de auditoria
    """
    
    def __init__(self):
        """Inicializa o gerenciador de retenção"""
        self.policies: Dict[str, RetentionPolicy] = {}
        self.execution_stats = {
            'total_executions': 0,
            'total_deleted': 0,
            'total_archived': 0,
            'last_execution': None,
            'last_error': None
        }
        
        # Carregar políticas padrão
        self._load_default_policies()
        
        logger.info("Retention Manager initialized")
    
    def _load_default_policies(self):
        """Carrega políticas de retenção padrão"""
        
        # Política 1: Logs antigos gerais (365 dias)
        self.add_policy(RetentionPolicy(
            name="general_retention",
            description="Retenção geral de logs de auditoria por 1 ano",
            policy_type=RetentionPolicyType.TIME_BASED,
            action=RetentionAction.DELETE,
            retention_days=365,
            backup_before_delete=True
        ))
        
        # Política 2: Logs de autenticação (90 dias)
        self.add_policy(RetentionPolicy(
            name="auth_retention",
            description="Retenção de logs de autenticação por 90 dias",
            policy_type=RetentionPolicyType.TIME_BASED,
            action=RetentionAction.ARCHIVE,
            retention_days=90,
            operations=[AuditOperation.LOGIN, AuditOperation.LOGOUT, AuditOperation.FAILED_LOGIN],
            backup_before_delete=True
        ))
        
        # Política 3: Logs críticos de segurança (7 anos - compliance)
        self.add_policy(RetentionPolicy(
            name="security_compliance",
            description="Retenção de logs críticos de segurança para compliance",
            policy_type=RetentionPolicyType.TIME_BASED,
            action=RetentionAction.ARCHIVE,
            retention_days=2555,  # ~7 anos
            operations=[
                AuditOperation.PERMISSION_GRANTED, 
                AuditOperation.PERMISSION_REVOKED,
                AuditOperation.DELETE
            ],
            backup_before_delete=True
        ))
        
        # Política 4: Controle de volume (máximo 100k registros)
        self.add_policy(RetentionPolicy(
            name="volume_control",
            description="Controle de volume - máximo 100k registros",
            policy_type=RetentionPolicyType.COUNT_BASED,
            action=RetentionAction.DELETE,
            max_records=100000,
            backup_before_delete=True
        ))
        
        # Política 5: Logs de READ operations (30 dias)
        self.add_policy(RetentionPolicy(
            name="read_operations",
            description="Logs de operações de leitura por 30 dias",
            policy_type=RetentionPolicyType.TIME_BASED,
            action=RetentionAction.DELETE,
            retention_days=30,
            operations=[AuditOperation.READ],
            backup_before_delete=False
        ))
    
    def add_policy(self, policy: RetentionPolicy):
        """Adiciona uma nova política de retenção"""
        if policy.created_at is None:
            policy.created_at = datetime.now(timezone.utc)
        
        self.policies[policy.name] = policy
        logger.info(f"Added retention policy: {policy.name}")
    
    def remove_policy(self, policy_name: str) -> bool:
        """Remove uma política de retenção"""
        if policy_name in self.policies:
            del self.policies[policy_name]
            logger.info(f"Removed retention policy: {policy_name}")
            return True
        return False
    
    def get_policy(self, policy_name: str) -> Optional[RetentionPolicy]:
        """Retorna uma política específica"""
        return self.policies.get(policy_name)
    
    def list_policies(self) -> Dict[str, RetentionPolicy]:
        """Lista todas as políticas"""
        return self.policies.copy()
    
    def build_query_filters(self, policy: RetentionPolicy, session: Session):
        """Constrói filtros SQL para uma política"""
        query = session.query(AuditLog)
        
        # Filtro de tempo
        if policy.policy_type == RetentionPolicyType.TIME_BASED and policy.retention_days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=policy.retention_days)
            query = query.filter(AuditLog.changed_at < cutoff_date)
        
        # Filtros específicos
        if policy.operations:
            query = query.filter(AuditLog.operation.in_([op.value for op in policy.operations]))
        
        if policy.tables:
            query = query.filter(AuditLog.table_name.in_(policy.tables))
        
        return query
    
    def estimate_affected_records(self, policy: RetentionPolicy) -> int:
        """Estima quantos registros serão afetados por uma política"""
        with SessionLocal() as session:
            try:
                query = self.build_query_filters(policy, session)
                
                if policy.policy_type == RetentionPolicyType.COUNT_BASED:
                    total_count = session.query(func.count(AuditLog.audit_id)).scalar()
                    if total_count > policy.max_records:
                        return total_count - policy.max_records
                    return 0
                
                return query.count()
                
            except Exception as e:
                logger.error(f"Error estimating affected records for {policy.name}: {e}")
                return 0
    
    def execute_policy(self, policy_name: str) -> Dict[str, Any]:
        """Executa uma política de retenção específica"""
        policy = self.policies.get(policy_name)
        if not policy:
            raise ValueError(f"Policy not found: {policy_name}")
        
        if not policy.enabled:
            return {
                'policy_name': policy_name,
                'status': 'skipped',
                'reason': 'Policy disabled',
                'affected_records': 0
            }
        
        result = {
            'policy_name': policy_name,
            'status': 'success',
            'affected_records': 0,
            'action_taken': policy.action.value,
            'dry_run': policy.dry_run,
            'backup_created': False,
            'execution_time': None,
            'error': None
        }
        
        start_time = datetime.now(timezone.utc)
        
        try:
            with SessionLocal() as session:
                # Construir query
                query = self.build_query_filters(policy, session)
                
                # Aplicar limite para políticas baseadas em contagem
                if policy.policy_type == RetentionPolicyType.COUNT_BASED and policy.max_records:
                    total_count = session.query(func.count(AuditLog.audit_id)).scalar()
                    if total_count > policy.max_records:
                        # Deletar os mais antigos primeiro
                        excess_count = total_count - policy.max_records
                        query = session.query(AuditLog).order_by(AuditLog.changed_at.asc()).limit(excess_count)
                
                # Obter registros afetados
                affected_records = query.all()
                result['affected_records'] = len(affected_records)
                
                if not affected_records:
                    result['status'] = 'no_action'
                    result['reason'] = 'No records match criteria'
                    return result
                
                # Executar ação
                if policy.action == RetentionAction.DELETE:
                    if not policy.dry_run:
                        # Deletar registros
                        for record in affected_records:
                            session.delete(record)
                        session.commit()
                        
                        self.execution_stats['total_deleted'] += len(affected_records)
                
                elif policy.action == RetentionAction.ARCHIVE:
                    if not policy.dry_run:
                        # Marcar como arquivados (implementação futura)
                        self.execution_stats['total_archived'] += len(affected_records)
                
                # Atualizar estatísticas da política
                policy.last_executed = start_time
                policy.last_result = result.copy()
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.execution_stats['last_error'] = str(e)
            logger.error(f"Error executing policy {policy_name}: {e}")
        
        # Calcular tempo de execução
        end_time = datetime.now(timezone.utc)
        result['execution_time'] = (end_time - start_time).total_seconds()
        
        # Atualizar estatísticas globais
        self.execution_stats['total_executions'] += 1
        self.execution_stats['last_execution'] = start_time
        
        logger.info(f"Policy {policy_name} executed: {result}")
        return result
    
    def execute_all_policies(self) -> Dict[str, Any]:
        """Executa todas as políticas ativas"""
        results = {}
        summary = {
            'total_policies': len(self.policies),
            'executed_policies': 0,
            'total_affected_records': 0,
            'total_execution_time': 0,
            'errors': []
        }
        
        start_time = datetime.now(timezone.utc)
        
        for policy_name, policy in self.policies.items():
            if policy.enabled:
                try:
                    result = self.execute_policy(policy_name)
                    results[policy_name] = result
                    
                    summary['executed_policies'] += 1
                    summary['total_affected_records'] += result['affected_records']
                    summary['total_execution_time'] += result.get('execution_time', 0)
                    
                    if result['status'] == 'error':
                        summary['errors'].append(f"{policy_name}: {result['error']}")
                        
                except Exception as e:
                    error_msg = f"Failed to execute policy {policy_name}: {e}"
                    summary['errors'].append(error_msg)
                    logger.error(error_msg)
        
        end_time = datetime.now(timezone.utc)
        summary['total_wall_time'] = (end_time - start_time).total_seconds()
        
        logger.info(f"Executed {summary['executed_policies']} retention policies")
        
        return {
            'summary': summary,
            'policy_results': results,
            'execution_timestamp': start_time.isoformat()
        }
    
    def get_retention_report(self) -> Dict[str, Any]:
        """Gera relatório de retenção"""
        with SessionLocal() as session:
            try:
                # Estatísticas gerais
                total_logs = session.query(func.count(AuditLog.audit_id)).scalar()
                oldest_log = session.query(func.min(AuditLog.changed_at)).scalar()
                newest_log = session.query(func.max(AuditLog.changed_at)).scalar()
                
                # Estatísticas por tabela
                table_stats = session.query(
                    AuditLog.table_name,
                    func.count(AuditLog.audit_id).label('count'),
                    func.min(AuditLog.changed_at).label('oldest'),
                    func.max(AuditLog.changed_at).label('newest')
                ).group_by(AuditLog.table_name).all()
                
                # Estatísticas por operação
                operation_stats = session.query(
                    AuditLog.operation,
                    func.count(AuditLog.audit_id).label('count')
                ).group_by(AuditLog.operation).all()
                
                # Estimativas de limpeza por política
                policy_estimates = {}
                for policy_name, policy in self.policies.items():
                    if policy.enabled:
                        estimate = self.estimate_affected_records(policy)
                        policy_estimates[policy_name] = {
                            'estimated_affected': estimate,
                            'policy_type': policy.policy_type.value,
                            'action': policy.action.value,
                            'last_executed': policy.last_executed.isoformat() if policy.last_executed else None
                        }
                
                return {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'total_logs': total_logs,
                    'date_range': {
                        'oldest': oldest_log.isoformat() if oldest_log else None,
                        'newest': newest_log.isoformat() if newest_log else None,
                        'span_days': (newest_log - oldest_log).days if oldest_log and newest_log else 0
                    },
                    'table_statistics': [
                        {
                            'table_name': stat.table_name,
                            'count': stat.count,
                            'oldest': stat.oldest.isoformat() if stat.oldest else None,
                            'newest': stat.newest.isoformat() if stat.newest else None
                        }
                        for stat in table_stats
                    ],
                    'operation_statistics': [
                        {
                            'operation': stat.operation,
                            'count': stat.count
                        }
                        for stat in operation_stats
                    ],
                    'policy_estimates': policy_estimates,
                    'execution_statistics': self.execution_stats
                }
                
            except Exception as e:
                logger.error(f"Error generating retention report: {e}")
                return {
                    'error': str(e),
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }

# Global retention manager instance
retention_manager = RetentionManager()

# Convenience functions
def add_retention_policy(policy: RetentionPolicy):
    """Adiciona política de retenção"""
    retention_manager.add_policy(policy)

def execute_retention_policy(policy_name: str):
    """Executa política específica"""
    return retention_manager.execute_policy(policy_name)

def execute_all_retention_policies():
    """Executa todas as políticas"""
    return retention_manager.execute_all_policies()

def get_retention_report():
    """Gera relatório de retenção"""
    return retention_manager.get_retention_report() 