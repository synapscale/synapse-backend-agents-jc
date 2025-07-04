"""Knowledge Base Model"""

from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class KnowledgeBase(Base):
    """Knowledge base for storing structured information"""
    
    __tablename__ = "knowledge_bases"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    kb_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    title = Column(Text, nullable=False)
    content = Column(JSONB, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="knowledge_bases")
    agent_kbs = relationship("AgentKnowledgeBase", back_populates="knowledge_base")

    def __str__(self):
        return f"KnowledgeBase(id={self.kb_id}, title={self.title[:50]}...)"

    @property
    def content_summary(self):
        """Get a summary of the content structure"""
        if not self.content:
            return "Empty knowledge base"
        
        if isinstance(self.content, dict):
            keys = list(self.content.keys())
            return f"Contains: {', '.join(keys[:5])}" + ("..." if len(keys) > 5 else "")
        
        return "Complex content structure"

    @property
    def content_size(self):
        """Get approximate size of content in bytes"""
        import json
        return len(json.dumps(self.content, default=str))

    def get_content_by_key(self, key, default=None):
        """Get specific content by key"""
        if not self.content or not isinstance(self.content, dict):
            return default
        return self.content.get(key, default)

    def update_content(self, new_content):
        """Update knowledge base content"""
        self.content = new_content
        self.updated_at = func.now()

    def add_content_item(self, key, value):
        """Add or update a content item"""
        if not isinstance(self.content, dict):
            self.content = {}
        
        self.content[key] = value
        self.updated_at = func.now()

    def remove_content_item(self, key):
        """Remove a content item"""
        if isinstance(self.content, dict) and key in self.content:
            del self.content[key]
            self.updated_at = func.now()
            return True
        return False
