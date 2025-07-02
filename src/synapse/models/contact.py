"""
Model para Contacts (CRM)
ALINHADO PERFEITAMENTE COM A TABELA contacts
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class Contact(Base):
    """Model para contatos do CRM - ALINHADO COM contacts TABLE"""
    
    __tablename__ = "contacts"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    email = Column(String, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    status = Column(String, nullable=True)
    lead_score = Column(Integer, nullable=True)
    source_id = Column(UUID(as_uuid=True), nullable=True)  # Source de onde veio o contato
    custom_fields = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    tags = Column(String, nullable=True)  # Tags separadas por vírgula
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="contacts")
    
    # Relacionamentos CRM
    campaign_contacts = relationship(
        "CampaignContact", back_populates="contact", cascade="all, delete-orphan"
    )
    contact_events = relationship(
        "ContactEvent", back_populates="contact", cascade="all, delete-orphan"
    )
    contact_interactions = relationship(
        "ContactInteraction", back_populates="contact", cascade="all, delete-orphan"
    )
    conversion_journey = relationship(
        "ConversionJourney", back_populates="contact", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Contact(id={self.id}, email='{self.email}', name='{self.full_name}')>"

    @property
    def full_name(self):
        """Retorna o nome completo do contato"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.email

    @property
    def display_name(self):
        """Retorna o nome de exibição (nome ou email)"""
        full_name = self.full_name
        return full_name if full_name != self.email else self.email

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "company": self.company,
            "job_title": self.job_title,
            "status": self.status,
            "lead_score": self.lead_score,
            "source_id": str(self.source_id) if self.source_id else None,
            "custom_fields": self.custom_fields,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_tags_list(self):
        """Retorna as tags como lista"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def add_tag(self, tag: str):
        """Adiciona uma tag ao contato"""
        current_tags = self.get_tags_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ', '.join(current_tags)

    def remove_tag(self, tag: str):
        """Remove uma tag do contato"""
        current_tags = self.get_tags_list()
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = ', '.join(current_tags) if current_tags else None

    def update_lead_score(self, score: int):
        """Atualiza o lead score do contato"""
        self.lead_score = max(0, min(100, score))  # Score entre 0 e 100

    def is_qualified_lead(self) -> bool:
        """Verifica se é um lead qualificado"""
        return self.lead_score is not None and self.lead_score >= 70

    def get_custom_field(self, field_name: str):
        """Retorna o valor de um campo customizado"""
        if self.custom_fields:
            return self.custom_fields.get(field_name)
        return None

    def set_custom_field(self, field_name: str, value):
        """Define o valor de um campo customizado"""
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[field_name] = value

    def update_status(self, new_status: str):
        """Atualiza o status do contato"""
        valid_statuses = ["new", "contacted", "qualified", "opportunity", "customer", "lost"]
        if new_status in valid_statuses:
            self.status = new_status

    @classmethod
    def create_contact(
        cls,
        tenant_id: str,
        email: str,
        first_name: str = None,
        last_name: str = None,
        **kwargs
    ):
        """Cria um novo contato"""
        return cls(
            tenant_id=tenant_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )

    @classmethod
    def find_by_email(cls, session, email: str, tenant_id: str):
        """Busca contato por email e tenant"""
        return session.query(cls).filter(
            cls.email == email,
            cls.tenant_id == tenant_id
        ).first()

    def has_recent_interaction(self, days: int = 30) -> bool:
        """Verifica se teve interação recente"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        for interaction in self.contact_interactions:
            if interaction.created_at and interaction.created_at >= cutoff_date:
                return True
        return False

    def get_interaction_count(self) -> int:
        """Retorna o número total de interações"""
        return len(self.contact_interactions)

    def get_campaign_count(self) -> int:
        """Retorna o número de campanhas que o contato participou"""
        return len(self.campaign_contacts) 