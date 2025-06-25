from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid

class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = {"schema": "synapscale_db"}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("synapscale_db.users.id"), nullable=False)
    collection_id = Column(String, ForeignKey("synapscale_db.memory_collections.id"), nullable=False)
    
    # Conteúdo da memória
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, image, code, etc.
    
    # Metadados
    title = Column(String(255))
    description = Column(Text)
    tags = Column(JSON, default=list)
    
    # Dados de embedding para busca semântica
    embedding = Column(JSON, nullable=True)
    embedding_model = Column(String(100), nullable=True)
    
    # Controle de uso
    importance_score = Column(Integer, default=1)  # 1-10
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Controle de tempo
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relações
    user = relationship("User", back_populates="memories")
    collection = relationship("MemoryCollection", back_populates="memories")
    
    def __repr__(self):
        return f"<Memory(id={self.id}, title='{self.title}')>"
