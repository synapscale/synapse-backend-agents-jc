"""
Modelo para logs de erro de agentes
ALINHADO PERFEITAMENTE COM A TABELA agent_error_logs
"""

from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import json
from datetime import datetime, timezone, timedelta
from synapse.database import Base


class AgentErrorLog(Base):
    """Model para logs de erro de agentes - ALINHADO COM agent_error_logs TABLE"""
    
    __tablename__ = "agent_error_logs"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    error_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    error_code = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=True)

    # Relacionamentos
    agent = relationship("Agent", back_populates="error_logs")

    def __repr__(self):
        return f"<AgentErrorLog(error_id={self.error_id}, agent_id={self.agent_id}, error_code={self.error_code})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "error_id": str(self.error_id),
            "agent_id": str(self.agent_id),
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "error_code": self.error_code,
            "payload": self.payload,
        }

    def get_error_message(self) -> str:
        """Extrai mensagem de erro do payload"""
        if not self.payload:
            return "No error message available"
            
        if isinstance(self.payload, dict):
            return self.payload.get("message", self.payload.get("error", "Unknown error"))
        
        return str(self.payload)

    def get_stack_trace(self) -> str:
        """Extrai stack trace do payload"""
        if not self.payload or not isinstance(self.payload, dict):
            return None
            
        return self.payload.get("stack_trace", self.payload.get("traceback"))

    def get_error_context(self) -> dict:
        """Extrai contexto do erro do payload"""
        if not self.payload or not isinstance(self.payload, dict):
            return {}
            
        context = {}
        for key in ["context", "details", "metadata", "request_id", "user_id"]:
            if key in self.payload:
                context[key] = self.payload[key]
                
        return context

    def get_severity_level(self) -> str:
        """Determina nível de severidade baseado no error_code"""
        if not self.error_code:
            return "unknown"
            
        error_code_lower = self.error_code.lower()
        
        if any(keyword in error_code_lower for keyword in ["critical", "fatal", "crash"]):
            return "critical"
        elif any(keyword in error_code_lower for keyword in ["error", "exception", "failed"]):
            return "error"
        elif any(keyword in error_code_lower for keyword in ["warning", "warn"]):
            return "warning"
        elif any(keyword in error_code_lower for keyword in ["info", "notice"]):
            return "info"
        else:
            return "error"  # Default para erros

    def is_recent(self, hours: int = 24) -> bool:
        """Verifica se o erro ocorreu recentemente"""
        if not self.occurred_at:
            return False
            
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        return self.occurred_at >= cutoff_time

    def is_critical(self) -> bool:
        """Verifica se é um erro crítico"""
        return self.get_severity_level() == "critical"

    def format_error_summary(self) -> str:
        """Formata um resumo do erro"""
        timestamp = self.occurred_at.strftime("%Y-%m-%d %H:%M:%S UTC") if self.occurred_at else "Unknown time"
        severity = self.get_severity_level().upper()
        message = self.get_error_message()
        
        return f"[{timestamp}] {severity} - {self.error_code or 'UNKNOWN'}: {message}"

    @classmethod
    def log_error(
        cls,
        agent_id: str,
        error_code: str = None,
        error_message: str = None,
        stack_trace: str = None,
        context: dict = None,
        occurred_at: datetime = None
    ):
        """Cria um novo log de erro"""
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
            
        payload = {}
        
        if error_message:
            payload["message"] = error_message
        if stack_trace:
            payload["stack_trace"] = stack_trace
        if context:
            payload["context"] = context
            
        return cls(
            agent_id=agent_id,
            error_code=error_code,
            occurred_at=occurred_at,
            payload=payload if payload else None
        )

    @classmethod
    def log_exception(
        cls,
        agent_id: str,
        exception: Exception,
        error_code: str = None,
        context: dict = None
    ):
        """Cria log de erro a partir de uma exceção"""
        import traceback
        
        payload = {
            "message": str(exception),
            "exception_type": type(exception).__name__,
            "stack_trace": traceback.format_exc()
        }
        
        if context:
            payload["context"] = context
            
        return cls(
            agent_id=agent_id,
            error_code=error_code or type(exception).__name__,
            payload=payload
        )

    @classmethod
    def find_by_agent(cls, session, agent_id: str, limit: int = 100):
        """Busca logs de erro por agente"""
        return session.query(cls).filter(
            cls.agent_id == agent_id
        ).order_by(cls.occurred_at.desc()).limit(limit).all()

    @classmethod
    def find_by_error_code(cls, session, error_code: str, limit: int = 100):
        """Busca logs por código de erro"""
        return session.query(cls).filter(
            cls.error_code == error_code
        ).order_by(cls.occurred_at.desc()).limit(limit).all()

    @classmethod
    def find_recent_errors(cls, session, hours: int = 24, limit: int = 100):
        """Busca erros recentes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return session.query(cls).filter(
            cls.occurred_at >= cutoff_time
        ).order_by(cls.occurred_at.desc()).limit(limit).all()

    @classmethod
    def find_critical_errors(cls, session, hours: int = 24):
        """Busca erros críticos recentes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        errors = session.query(cls).filter(
            cls.occurred_at >= cutoff_time
        ).order_by(cls.occurred_at.desc()).all()
        
        critical_errors = [error for error in errors if error.is_critical()]
        return critical_errors

    @classmethod
    def get_error_statistics(cls, session, agent_id: str = None, hours: int = 24):
        """Retorna estatísticas de erro"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = session.query(cls).filter(cls.occurred_at >= cutoff_time)
        
        if agent_id:
            query = query.filter(cls.agent_id == agent_id)
            
        errors = query.all()
        
        stats = {
            "total_errors": len(errors),
            "by_severity": {"critical": 0, "error": 0, "warning": 0, "info": 0, "unknown": 0},
            "by_error_code": {},
            "by_agent": {},
            "recent_count": 0
        }
        
        for error in errors:
            # Contar por severidade
            severity = error.get_severity_level()
            stats["by_severity"][severity] += 1
            
            # Contar por código de erro
            code = error.error_code or "unknown"
            stats["by_error_code"][code] = stats["by_error_code"].get(code, 0) + 1
            
            # Contar por agente
            agent_id_str = str(error.agent_id)
            stats["by_agent"][agent_id_str] = stats["by_agent"].get(agent_id_str, 0) + 1
            
            # Contar erros recentes (última hora)
            if error.is_recent(hours=1):
                stats["recent_count"] += 1
                
        return stats

    @classmethod
    def get_top_error_codes(cls, session, limit: int = 10, hours: int = 24):
        """Retorna os códigos de erro mais frequentes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        errors = session.query(cls).filter(
            cls.occurred_at >= cutoff_time,
            cls.error_code.isnot(None)
        ).all()
        
        error_counts = {}
        for error in errors:
            code = error.error_code
            error_counts[code] = error_counts.get(code, 0) + 1
            
        # Ordenar por frequência
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:limit]

    @classmethod
    def cleanup_old_logs(cls, session, days_to_keep: int = 30):
        """Remove logs antigos"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        removed_count = session.query(cls).filter(
            cls.occurred_at < cutoff_date
        ).delete()
        
        return removed_count

    @classmethod
    def get_error_timeline(cls, session, agent_id: str = None, hours: int = 24):
        """Retorna timeline de erros"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = session.query(cls).filter(cls.occurred_at >= cutoff_time)
        
        if agent_id:
            query = query.filter(cls.agent_id == agent_id)
            
        errors = query.order_by(cls.occurred_at).all()
        
        timeline = []
        for error in errors:
            timeline.append({
                "timestamp": error.occurred_at.isoformat(),
                "error_code": error.error_code,
                "severity": error.get_severity_level(),
                "message": error.get_error_message(),
                "agent_id": str(error.agent_id)
            })
            
        return timeline

    @classmethod
    def find_similar_errors(cls, session, error_code: str, hours: int = 24, limit: int = 10):
        """Busca erros similares"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return session.query(cls).filter(
            cls.error_code == error_code,
            cls.occurred_at >= cutoff_time
        ).order_by(cls.occurred_at.desc()).limit(limit).all()

    @classmethod
    def get_agent_error_rate(cls, session, agent_id: str, hours: int = 24):
        """Calcula taxa de erro de um agente"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        error_count = session.query(cls).filter(
            cls.agent_id == agent_id,
            cls.occurred_at >= cutoff_time
        ).count()
        
        # Taxa por hora
        error_rate = error_count / max(hours, 1)
        
        return {
            "agent_id": agent_id,
            "error_count": error_count,
            "hours_period": hours,
            "errors_per_hour": round(error_rate, 2),
            "period_start": cutoff_time.isoformat(),
            "period_end": datetime.now(timezone.utc).isoformat()
        }
