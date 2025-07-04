import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from synapse.database import Base

class ContactListMembership(Base):
    """Model for contact list membership relationships."""
    
    __tablename__ = "contact_list_memberships"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    list_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contact_lists.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contacts.id"), nullable=False)
    added_by = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True)
    added_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    status = Column(String(50), default="active")
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="contact_list_memberships")
    contact_list = relationship("ContactList", back_populates="memberships")
    contact = relationship("Contact", back_populates="list_memberships")
    added_by_user = relationship("User", back_populates="added_contact_memberships") 