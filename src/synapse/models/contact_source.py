"""
ContactSource model for storing contact integration sources.
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base


class ContactSource(Base):
    """
    ContactSource model for storing contact integration sources.
    
    Represents different sources from which contacts can be imported
    or integrated, such as email providers, CRM systems, etc.
    """
    
    __tablename__ = "contact_sources"
    __table_args__ = (
        {"schema": "synapscale_db", "extend_existing": True}
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign key to tenant
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Source details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    integration_type = Column(String(50))
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="contact_sources")
    contacts = relationship("Contact", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContactSource(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"
    
    def to_dict(self):
        """Convert the ContactSource instance to a dictionary."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "integration_type": self.integration_type,
            "config": self.config,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def is_valid_config(self):
        """Check if the source configuration is valid."""
        if not self.config:
            return False
        
        # Basic validation based on integration type
        if self.integration_type == "email":
            required_fields = ["host", "port", "username"]
            return all(field in self.config for field in required_fields)
        elif self.integration_type == "api":
            required_fields = ["endpoint", "api_key"]
            return all(field in self.config for field in required_fields)
        
        return True
    
    def get_active_contacts_count(self):
        """Get the number of active contacts from this source."""
        return len([contact for contact in self.contacts if contact.is_active]) 