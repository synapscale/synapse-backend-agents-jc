"""
Model para log de auditoria
ALINHADO PERFEITAMENTE COM A TABELA audit_log
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AuditLog(Base):
    """Model para log de auditoria - ALINHADO COM audit_log TABLE"""

    __tablename__ = "audit_log"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    audit_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    table_name = Column(Text, nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    changed_by = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True
    )
    changed_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    operation = Column(Text, nullable=False)
    diffs = Column(JSONB, nullable=True)

    # Relacionamentos
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(audit_id={self.audit_id}, table_name='{self.table_name}', operation='{self.operation}')>"

    @classmethod
    def create_log(cls, table_name, record_id, operation, changed_by=None, diffs=None):
        """Cria um novo log de auditoria"""
        return cls(
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            changed_by=changed_by,
            diffs=diffs or {},
        )

    def get_operation_type(self):
        """Retorna o tipo de operação de forma legível"""
        operation_map = {
            "CREATE": "Criação",
            "UPDATE": "Atualização",
            "DELETE": "Exclusão",
            "READ": "Leitura",
            "LOGIN": "Login",
            "LOGOUT": "Logout",
            "FAILED_LOGIN": "Login Falhado",
            "PERMISSION_GRANTED": "Permissão Concedida",
            "PERMISSION_REVOKED": "Permissão Revogada",
            "EXPORT": "Exportação",
            "IMPORT": "Importação",
            "BACKUP": "Backup",
            "RESTORE": "Restauração",
        }
        return operation_map.get(self.operation, self.operation)

    def has_changes(self):
        """Verifica se o log contém mudanças"""
        return bool(self.diffs)

    def get_changed_fields(self):
        """Retorna os campos que foram alterados"""
        if not self.diffs:
            return []
        return list(self.diffs.keys())
