"""User Insight Model"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class UserInsight(Base):
    """AI-generated insights and recommendations for users"""
    
    __tablename__ = "user_insights"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    insight_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    supporting_data = Column(JSONB, nullable=True)
    confidence_score = Column(Float, nullable=False)
    suggested_action = Column(String(100), nullable=True)
    action_url = Column(String(500), nullable=True)
    action_data = Column(JSONB, nullable=True)
    is_read = Column(Boolean, nullable=False)
    is_dismissed = Column(Boolean, nullable=False)
    is_acted_upon = Column(Boolean, nullable=False)
    user_feedback = Column(String(20), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_evergreen = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)  
    acted_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="insights", overlaps="user")
    tenant = relationship("Tenant", back_populates="user_insights")

    def __str__(self):
        return f"UserInsight(type={self.insight_type}, title={self.title[:50]}...)"

    @property
    def is_expired(self):
        """Check if insight has expired"""
        if self.is_evergreen or self.expires_at is None:
            return False
        return self.expires_at < func.now()

    @property
    def priority_weight(self):
        """Get numeric weight for priority sorting"""
        weights = {
            "low": 1,
            "medium": 2, 
            "high": 3,
            "critical": 4
        }
        return weights.get(self.priority.lower(), 1)

    def mark_as_read(self):
        """Mark insight as read"""
        self.is_read = True
        self.read_at = func.now()

    def mark_as_acted(self):
        """Mark insight as acted upon"""
        self.is_acted_upon = True
        self.acted_at = func.now()

    def dismiss(self):
        """Dismiss the insight"""
        self.is_dismissed = True
