"""
Model para Contact Lists (CRM)
ALINHADO PERFEITAMENTE COM A TABELA contact_lists
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class ContactList(Base):
    """Model para listas de contatos do CRM - ALINHADO COM contact_lists TABLE"""
    
    __tablename__ = "contact_lists"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=True)  # static, dynamic, smart
    filters = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="contact_lists")

    def __repr__(self):
        return f"<ContactList(id={self.id}, name='{self.name}', type='{self.type}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "filters": self.filters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_static_list(self) -> bool:
        """Verifica se é uma lista estática"""
        return self.type == "static"

    def is_dynamic_list(self) -> bool:
        """Verifica se é uma lista dinâmica"""
        return self.type == "dynamic"

    def is_smart_list(self) -> bool:
        """Verifica se é uma lista inteligente"""
        return self.type == "smart"

    def get_filter_criteria(self):
        """Retorna os critérios de filtro"""
        return self.filters or {}

    def set_filter_criteria(self, criteria: dict):
        """Define os critérios de filtro"""
        self.filters = criteria

    def add_filter_criteria(self, key: str, value):
        """Adiciona um critério de filtro"""
        if self.filters is None:
            self.filters = {}
        self.filters[key] = value

    def remove_filter_criteria(self, key: str):
        """Remove um critério de filtro"""
        if self.filters and key in self.filters:
            del self.filters[key]

    def get_contacts_query(self, session):
        """
        Retorna uma query para buscar contatos baseados nos filtros da lista
        Para listas dinâmicas e inteligentes
        """
        from synapse.models.contact import Contact
        
        query = session.query(Contact).filter(Contact.tenant_id == self.tenant_id)
        
        if not self.filters:
            return query

        # Aplicar filtros baseados no conteúdo de self.filters
        filters = self.get_filter_criteria()
        
        # Filtro por status
        if "status" in filters:
            query = query.filter(Contact.status == filters["status"])
        
        # Filtro por lead score mínimo
        if "min_lead_score" in filters:
            query = query.filter(Contact.lead_score >= filters["min_lead_score"])
        
        # Filtro por lead score máximo
        if "max_lead_score" in filters:
            query = query.filter(Contact.lead_score <= filters["max_lead_score"])
        
        # Filtro por empresa
        if "company" in filters:
            query = query.filter(Contact.company.ilike(f"%{filters['company']}%"))
        
        # Filtro por tags
        if "tags" in filters:
            for tag in filters["tags"]:
                query = query.filter(Contact.tags.contains(tag))
        
        # Filtro por source_id
        if "source_id" in filters:
            query = query.filter(Contact.source_id == filters["source_id"])

        # Filtro por campos customizados
        if "custom_fields" in filters:
            for field_name, field_value in filters["custom_fields"].items():
                query = query.filter(Contact.custom_fields[field_name].astext == str(field_value))

        return query

    def get_contact_count(self, session) -> int:
        """Retorna o número de contatos na lista"""
        if self.is_static_list():
            # Para listas estáticas, seria necessário uma tabela de relacionamento
            # Por ora, retorna 0 como placeholder
            return 0
        else:
            # Para listas dinâmicas/inteligentes, conta baseado nos filtros
            return self.get_contacts_query(session).count()

    def get_contacts(self, session, limit: int = None, offset: int = None):
        """Retorna os contatos da lista"""
        query = self.get_contacts_query(session)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()

    @classmethod
    def create_static_list(
        cls,
        tenant_id: str,
        name: str,
        description: str = None
    ):
        """Cria uma lista estática"""
        return cls(
            tenant_id=tenant_id,
            name=name,
            description=description,
            type="static",
            filters={}
        )

    @classmethod
    def create_dynamic_list(
        cls,
        tenant_id: str,
        name: str,
        filters: dict,
        description: str = None
    ):
        """Cria uma lista dinâmica"""
        return cls(
            tenant_id=tenant_id,
            name=name,
            description=description,
            type="dynamic",
            filters=filters
        )

    @classmethod
    def create_smart_list(
        cls,
        tenant_id: str,
        name: str,
        filters: dict,
        description: str = None
    ):
        """Cria uma lista inteligente"""
        return cls(
            tenant_id=tenant_id,
            name=name,
            description=description,
            type="smart",
            filters=filters
        )

    def update_filters_for_qualified_leads(self):
        """Atualiza os filtros para capturar leads qualificados"""
        self.set_filter_criteria({
            "min_lead_score": 70,
            "status": "qualified"
        })

    def update_filters_for_customers(self):
        """Atualiza os filtros para capturar clientes"""
        self.set_filter_criteria({
            "status": "customer"
        })

    def update_filters_for_recent_contacts(self, days: int = 30):
        """Atualiza os filtros para capturar contatos recentes"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        self.set_filter_criteria({
            "created_after": cutoff_date.isoformat()
        })

    @classmethod
    def find_by_name(cls, session, name: str, tenant_id: str):
        """Busca lista por nome e tenant"""
        return session.query(cls).filter(
            cls.name == name,
            cls.tenant_id == tenant_id
        ).first()

    def duplicate(self, new_name: str):
        """Cria uma cópia da lista com um novo nome"""
        return self.__class__(
            tenant_id=self.tenant_id,
            name=new_name,
            description=f"Cópia de {self.name}",
            type=self.type,
            filters=self.filters.copy() if self.filters else None
        ) 