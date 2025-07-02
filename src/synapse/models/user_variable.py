"""User Variable Model"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class UserVariable(Base):
    """User-defined variables for workflows and automation"""
    
    __tablename__ = "user_variables"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    is_secret = Column(Boolean, nullable=False, server_default="false")
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, nullable=False, server_default="false")
    is_active = Column(Boolean, nullable=False, server_default="true")
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="variables")
    tenant = relationship("Tenant", back_populates="user_variables")

    def __str__(self):
        return f"UserVariable(key={self.key}, user_id={self.user_id})"

    @property
    def display_value(self):
        """Return masked value for secrets"""
        if self.is_secret:
            return "***HIDDEN***"
        return self.value

    def get_value(self, mask_secrets=True):
        """Get variable value with optional secret masking"""
        if mask_secrets and self.is_secret:
            return "***HIDDEN***"
        return self.value
