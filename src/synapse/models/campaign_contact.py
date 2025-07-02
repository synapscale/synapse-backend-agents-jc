"""
Model para Campaign Contacts (CRM)
ALINHADO PERFEITAMENTE COM A TABELA campaign_contacts
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class CampaignContact(Base):
    """Model para relação entre campanhas e contatos - ALINHADO COM campaign_contacts TABLE"""
    
    __tablename__ = "campaign_contacts"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.campaigns.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contacts.id"), nullable=False)
    status = Column(String, nullable=True)  # pending, sent, delivered, opened, clicked, bounced, unsubscribed, failed
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    bounced_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    campaign = relationship("Campaign", back_populates="campaign_contacts")
    contact = relationship("Contact", back_populates="campaign_contacts")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<CampaignContact(id={self.id}, campaign_id={self.campaign_id}, contact_id={self.contact_id}, status='{self.status}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "campaign_id": str(self.campaign_id),
            "contact_id": str(self.contact_id),
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "bounced_at": self.bounced_at.isoformat() if self.bounced_at else None,
            "unsubscribed_at": self.unsubscribed_at.isoformat() if self.unsubscribed_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    # Status check methods
    def is_pending(self) -> bool:
        """Verifica se está pendente"""
        return self.status == "pending"

    def is_sent(self) -> bool:
        """Verifica se foi enviado"""
        return self.status == "sent"

    def is_delivered(self) -> bool:
        """Verifica se foi entregue"""
        return self.status == "delivered"

    def is_opened(self) -> bool:
        """Verifica se foi aberto"""
        return self.status == "opened" or self.opened_at is not None

    def is_clicked(self) -> bool:
        """Verifica se foi clicado"""
        return self.status == "clicked" or self.clicked_at is not None

    def is_bounced(self) -> bool:
        """Verifica se teve bounce"""
        return self.status == "bounced" or self.bounced_at is not None

    def is_unsubscribed(self) -> bool:
        """Verifica se foi descadastrado"""
        return self.status == "unsubscribed" or self.unsubscribed_at is not None

    def is_failed(self) -> bool:
        """Verifica se falhou"""
        return self.status == "failed"

    # Status update methods
    def mark_as_sent(self):
        """Marca como enviado"""
        from datetime import datetime
        self.status = "sent"
        self.sent_at = datetime.utcnow()

    def mark_as_delivered(self):
        """Marca como entregue"""
        self.status = "delivered"

    def mark_as_opened(self):
        """Marca como aberto"""
        from datetime import datetime
        self.status = "opened"
        if not self.opened_at:
            self.opened_at = datetime.utcnow()

    def mark_as_clicked(self):
        """Marca como clicado"""
        from datetime import datetime
        self.status = "clicked"
        if not self.clicked_at:
            self.clicked_at = datetime.utcnow()
        # Se clicou, também abriu
        if not self.opened_at:
            self.opened_at = datetime.utcnow()

    def mark_as_bounced(self, error_message: str = None):
        """Marca como bounce"""
        from datetime import datetime
        self.status = "bounced"
        self.bounced_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message

    def mark_as_unsubscribed(self):
        """Marca como descadastrado"""
        from datetime import datetime
        self.status = "unsubscribed"
        self.unsubscribed_at = datetime.utcnow()

    def mark_as_failed(self, error_message: str):
        """Marca como falhou"""
        self.status = "failed"
        self.error_message = error_message

    # Analytics methods
    def get_engagement_score(self) -> int:
        """Retorna uma pontuação de engajamento (0-100)"""
        score = 0
        
        if self.is_sent():
            score += 10
        
        if self.is_delivered():
            score += 20
        
        if self.is_opened():
            score += 40
        
        if self.is_clicked():
            score += 30
        
        # Penalizar bounces e unsubscribes
        if self.is_bounced():
            score = max(0, score - 50)
        
        if self.is_unsubscribed():
            score = max(0, score - 30)
        
        return min(100, score)

    def has_engaged(self) -> bool:
        """Verifica se o contato se engajou (abriu ou clicou)"""
        return self.is_opened() or self.is_clicked()

    def get_time_to_open(self):
        """Retorna o tempo entre envio e abertura"""
        if self.sent_at and self.opened_at:
            return self.opened_at - self.sent_at
        return None

    def get_time_to_click(self):
        """Retorna o tempo entre envio e clique"""
        if self.sent_at and self.clicked_at:
            return self.clicked_at - self.sent_at
        return None

    # Classification methods
    def get_engagement_level(self) -> str:
        """Retorna o nível de engajamento"""
        if self.is_unsubscribed():
            return "unsubscribed"
        elif self.is_bounced():
            return "bounced"
        elif self.is_clicked():
            return "high"
        elif self.is_opened():
            return "medium"
        elif self.is_delivered() or self.is_sent():
            return "low"
        else:
            return "none"

    def is_successful_delivery(self) -> bool:
        """Verifica se foi entregue com sucesso"""
        return self.is_delivered() or self.is_opened() or self.is_clicked()

    def needs_retry(self) -> bool:
        """Verifica se precisa de nova tentativa"""
        return self.is_failed() and not self.is_bounced()

    # Utility methods
    @classmethod
    def create_campaign_contact(
        cls,
        campaign_id: str,
        contact_id: str,
        tenant_id: str = None
    ):
        """Cria uma relação campanha-contato"""
        return cls(
            campaign_id=campaign_id,
            contact_id=contact_id,
            tenant_id=tenant_id,
            status="pending"
        )

    @classmethod
    def find_by_campaign_and_contact(cls, session, campaign_id: str, contact_id: str):
        """Busca por campanha e contato"""
        return session.query(cls).filter(
            cls.campaign_id == campaign_id,
            cls.contact_id == contact_id
        ).first()

    @classmethod
    def get_campaign_stats(cls, session, campaign_id: str):
        """Retorna estatísticas de uma campanha"""
        from sqlalchemy import func
        
        stats = session.query(
            func.count(cls.id).label('total'),
            func.sum(func.case([(cls.status == 'sent', 1)], else_=0)).label('sent'),
            func.sum(func.case([(cls.status == 'delivered', 1)], else_=0)).label('delivered'),
            func.sum(func.case([(cls.opened_at.isnot(None), 1)], else_=0)).label('opened'),
            func.sum(func.case([(cls.clicked_at.isnot(None), 1)], else_=0)).label('clicked'),
            func.sum(func.case([(cls.status == 'bounced', 1)], else_=0)).label('bounced'),
            func.sum(func.case([(cls.status == 'unsubscribed', 1)], else_=0)).label('unsubscribed'),
            func.sum(func.case([(cls.status == 'failed', 1)], else_=0)).label('failed')
        ).filter(cls.campaign_id == campaign_id).first()
        
        return {
            'total': stats.total or 0,
            'sent': stats.sent or 0,
            'delivered': stats.delivered or 0,
            'opened': stats.opened or 0,
            'clicked': stats.clicked or 0,
            'bounced': stats.bounced or 0,
            'unsubscribed': stats.unsubscribed or 0,
            'failed': stats.failed or 0
        }

    def process_webhook_event(self, event_type: str, event_data: dict = None):
        """Processa eventos de webhook do provedor de email"""
        if event_type == "delivered":
            self.mark_as_delivered()
        elif event_type == "opened":
            self.mark_as_opened()
        elif event_type == "clicked":
            self.mark_as_clicked()
        elif event_type == "bounced":
            error_msg = event_data.get("reason") if event_data else None
            self.mark_as_bounced(error_msg)
        elif event_type == "unsubscribed":
            self.mark_as_unsubscribed()
        elif event_type == "spam":
            self.mark_as_failed("Marcado como spam")

    def can_be_resent(self) -> bool:
        """Verifica se pode ser reenviado"""
        return self.is_failed() and not self.is_bounced() and not self.is_unsubscribed() 