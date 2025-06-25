from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid

class MemoryCollection(Base):
    __tablename__ = "memory_collections"
    __table_args__ = {"schema": "synapscale_db"}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("synapscale_db.users.id"), nullable=False)
    workspace_id = Column(String, ForeignKey("synapscale_db.workspaces.id"), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Configurações
    is_private = Column(Boolean, default=True)
    max_memories = Column(Integer, default=1000)
    retention_days = Column(Integer, default=90)  # 0 = sem expiração
    
    # Estatísticas
    memory_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Controle de tempo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relações
    user = relationship("User", back_populates="memory_collections")
    workspace = relationship("Workspace", back_populates="memory_collections")
    memories = relationship("Memory", back_populates="collection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MemoryCollection(id={self.id}, name='{self.name}')>"
