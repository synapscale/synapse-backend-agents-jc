"""
Model para Agent Quotas
ALINHADO PERFEITAMENTE COM A TABELA agent_quotas
"""

from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentQuota(Base):
    """Model para quotas de agentes - ALINHADO COM agent_quotas TABLE"""
    
    __tablename__ = "agent_quotas"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    quota_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    max_calls = Column(BigInteger, nullable=False)
    max_tokens = Column(BigInteger, nullable=False)
    period = Column(Interval, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_quotas")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<AgentQuota(quota_id={self.quota_id}, agent_id={self.agent_id}, max_calls={self.max_calls})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "quota_id": str(self.quota_id),
            "agent_id": str(self.agent_id),
            "tenant_id": str(self.tenant_id),
            "max_calls": self.max_calls,
            "max_tokens": self.max_tokens,
            "period": str(self.period),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_period_in_seconds(self):
        """Retorna o período em segundos"""
        return self.period.total_seconds()

    def get_period_in_hours(self):
        """Retorna o período em horas"""
        return self.get_period_in_seconds() / 3600

    def get_period_in_days(self):
        """Retorna o período em dias"""
        return self.get_period_in_hours() / 24

    def is_daily_quota(self) -> bool:
        """Verifica se é uma quota diária"""
        return self.get_period_in_days() == 1

    def is_hourly_quota(self) -> bool:
        """Verifica se é uma quota por hora"""
        return self.get_period_in_hours() == 1

    def is_monthly_quota(self) -> bool:
        """Verifica se é uma quota mensal (aproximadamente 30 dias)"""
        return abs(self.get_period_in_days() - 30) < 1

    def get_calls_per_second_limit(self):
        """Retorna o limite de chamadas por segundo"""
        return self.max_calls / self.get_period_in_seconds()

    def get_tokens_per_second_limit(self):
        """Retorna o limite de tokens por segundo"""
        return self.max_tokens / self.get_period_in_seconds()

    @classmethod
    def create_daily_quota(
        cls,
        agent_id: str,
        tenant_id: str,
        max_calls: int,
        max_tokens: int
    ):
        """Cria uma quota diária"""
        from datetime import timedelta
        return cls(
            agent_id=agent_id,
            tenant_id=tenant_id,
            max_calls=max_calls,
            max_tokens=max_tokens,
            period=timedelta(days=1)
        )

    @classmethod
    def create_hourly_quota(
        cls,
        agent_id: str,
        tenant_id: str,
        max_calls: int,
        max_tokens: int
    ):
        """Cria uma quota por hora"""
        from datetime import timedelta
        return cls(
            agent_id=agent_id,
            tenant_id=tenant_id,
            max_calls=max_calls,
            max_tokens=max_tokens,
            period=timedelta(hours=1)
        )

    @classmethod
    def create_monthly_quota(
        cls,
        agent_id: str,
        tenant_id: str,
        max_calls: int,
        max_tokens: int
    ):
        """Cria uma quota mensal"""
        from datetime import timedelta
        return cls(
            agent_id=agent_id,
            tenant_id=tenant_id,
            max_calls=max_calls,
            max_tokens=max_tokens,
            period=timedelta(days=30)
        )

    def check_calls_limit(self, current_calls: int) -> bool:
        """Verifica se o limite de chamadas foi excedido"""
        return current_calls >= self.max_calls

    def check_tokens_limit(self, current_tokens: int) -> bool:
        """Verifica se o limite de tokens foi excedido"""
        return current_tokens >= self.max_tokens

    def get_remaining_calls(self, current_calls: int):
        """Retorna o número de chamadas restantes"""
        return max(0, self.max_calls - current_calls)

    def get_remaining_tokens(self, current_tokens: int):
        """Retorna o número de tokens restantes"""
        return max(0, self.max_tokens - current_tokens)

    def get_usage_percentage_calls(self, current_calls: int):
        """Retorna a porcentagem de uso das chamadas"""
        if self.max_calls == 0:
            return 0
        return min(100, (current_calls / self.max_calls) * 100)

    def get_usage_percentage_tokens(self, current_tokens: int):
        """Retorna a porcentagem de uso dos tokens"""
        if self.max_tokens == 0:
            return 0
        return min(100, (current_tokens / self.max_tokens) * 100)

    def is_quota_exceeded(self, current_calls: int, current_tokens: int) -> bool:
        """Verifica se alguma quota foi excedida"""
        return (
            self.check_calls_limit(current_calls) or 
            self.check_tokens_limit(current_tokens)
        )

    def get_period_description(self):
        """Retorna uma descrição legível do período"""
        if self.is_hourly_quota():
            return "por hora"
        elif self.is_daily_quota():
            return "por dia"
        elif self.is_monthly_quota():
            return "por mês"
        else:
            return f"por {self.get_period_in_hours():.1f} horas"
