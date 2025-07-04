"""
Model para Contact Notes (CRM)
ALINHADO PERFEITAMENTE COM A TABELA contact_notes
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class ContactNote(Base):
    """Model para notas de contatos do CRM - ALINHADO COM contact_notes TABLE"""
    
    __tablename__ = "contact_notes"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    contact_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contacts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=True, server_default="note")
    is_private = Column(Boolean, nullable=True, server_default=func.text("false"))
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    contact = relationship("Contact", back_populates="contact_notes")
    user = relationship("User", back_populates="contact_notes")
    tenant = relationship("Tenant", back_populates="contact_notes")

    def __repr__(self):
        return f"<ContactNote(id={self.id}, contact_id={self.contact_id}, type='{self.type}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "contact_id": str(self.contact_id),
            "user_id": str(self.user_id),
            "content": self.content,
            "type": self.type,
            "is_private": self.is_private,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    @classmethod
    def create_note(
        cls,
        contact_id: str,
        user_id: str,
        content: str,
        tenant_id: str = None,
        note_type: str = "note",
        is_private: bool = False
    ):
        """Cria uma nova nota para o contato"""
        return cls(
            contact_id=contact_id,
            user_id=user_id,
            content=content,
            tenant_id=tenant_id,
            type=note_type,
            is_private=is_private
        )

    def is_accessible_by_user(self, user_id: str) -> bool:
        """Verifica se a nota é acessível pelo usuário"""
        # A nota é acessível se não é privada ou se o usuário é o autor
        return not self.is_private or str(self.user_id) == user_id

    def update_content(self, new_content: str):
        """Atualiza o conteúdo da nota"""
        self.content = new_content
        self.updated_at = func.current_timestamp()

    def mark_as_private(self):
        """Marca a nota como privada"""
        self.is_private = True

    def mark_as_public(self):
        """Marca a nota como pública"""
        self.is_private = False

    @classmethod
    def get_notes_for_contact(cls, session, contact_id: str, user_id: str = None, include_private: bool = False):
        """Busca notas para um contato específico"""
        query = session.query(cls).filter(cls.contact_id == contact_id)
        
        if not include_private and user_id:
            # Inclui apenas notas públicas ou notas privadas do próprio usuário
            query = query.filter(
                (cls.is_private == False) | (cls.user_id == user_id)
            )
        elif not include_private:
            # Inclui apenas notas públicas
            query = query.filter(cls.is_private == False)
            
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_notes_by_user(cls, session, user_id: str, tenant_id: str = None):
        """Busca notas criadas por um usuário específico"""
        query = session.query(cls).filter(cls.user_id == user_id)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
            
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_recent_notes(cls, session, tenant_id: str = None, limit: int = 10):
        """Busca notas recentes"""
        query = session.query(cls)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
            
        return query.order_by(cls.created_at.desc()).limit(limit).all()

    def get_note_age_days(self) -> int:
        """Retorna a idade da nota em dias"""
        if self.created_at:
            from datetime import datetime
            return (datetime.utcnow() - self.created_at).days
        return 0 