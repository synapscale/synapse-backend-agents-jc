"""Agent Usage Metrics Model"""

from sqlalchemy import Column, String, DateTime, BigInteger, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AgentUsageMetric(Base):
    """Agent usage metrics tracking"""
    
    __tablename__ = "agent_usage_metrics"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    metric_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    calls_count = Column(BigInteger, nullable=False)
    tokens_used = Column(BigInteger, nullable=False)
    cost_est = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="agent_usage_metrics")

    def __str__(self):
        return f"AgentUsageMetric(agent_id={self.agent_id}, calls={self.calls_count})"
