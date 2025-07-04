"""
ContactTag model for organizing and categorizing contacts.
"""

from sqlalchemy import Column, String, Text, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base


class ContactTag(Base):
    """
    ContactTag model for organizing and categorizing contacts.
    
    Tags allow users to organize and filter their contacts by
    different categories like 'VIP', 'Prospects', 'Customers', etc.
    """
    
    __tablename__ = "contact_tags"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="contact_tags_tenant_id_name_key"),
        {"schema": "synapscale_db", "extend_existing": True}
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Basic information
    name = Column(String(100), nullable=False, doc="Name of the tag")
    color = Column(String(7), default="#6B7280", doc="Hex color code for the tag")
    description = Column(Text, nullable=True, doc="Optional description of the tag")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="contact_tags")
    
    # Utility methods
    def __repr__(self):
        return f"<ContactTag(id={self.id}, name={self.name}, color={self.color})>"
    
    def to_dict(self):
        """Convert tag to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_default_color(self):
        """Check if the tag is using the default color."""
        return self.color == "#6B7280" 