"""
Model para Campaigns (CRM)
ALINHADO PERFEITAMENTE COM A TABELA campaigns
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class Campaign(Base):
    """Model para campanhas de marketing - ALINHADO COM campaigns TABLE"""
    
    __tablename__ = "campaigns"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)  # email, sms, push, webinar, etc
    status = Column(String, nullable=True)  # draft, scheduled, sending, sent, paused, completed, cancelled
    subject = Column(String, nullable=True)  # Para campanhas de email
    content = Column(String, nullable=True)  # Conteúdo da campanha
    template_id = Column(UUID(as_uuid=True), nullable=True)  # Template usado
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    stats = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    settings = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="campaigns")
    creator = relationship("User", back_populates="created_campaigns")
    
    # Relacionamentos CRM
    campaign_contacts = relationship(
        "CampaignContact", back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "status": self.status,
            "subject": self.subject,
            "content": self.content,
            "template_id": str(self.template_id) if self.template_id else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "stats": self.stats,
            "settings": self.settings,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    # Status methods
    def is_draft(self) -> bool:
        """Verifica se a campanha está em rascunho"""
        return self.status == "draft"

    def is_scheduled(self) -> bool:
        """Verifica se a campanha está agendada"""
        return self.status == "scheduled"

    def is_sending(self) -> bool:
        """Verifica se a campanha está sendo enviada"""
        return self.status == "sending"

    def is_sent(self) -> bool:
        """Verifica se a campanha foi enviada"""
        return self.status == "sent"

    def is_completed(self) -> bool:
        """Verifica se a campanha foi completada"""
        return self.status == "completed"

    def is_cancelled(self) -> bool:
        """Verifica se a campanha foi cancelada"""
        return self.status == "cancelled"

    def is_paused(self) -> bool:
        """Verifica se a campanha está pausada"""
        return self.status == "paused"

    # Type methods
    def is_email_campaign(self) -> bool:
        """Verifica se é uma campanha de email"""
        return self.type == "email"

    def is_sms_campaign(self) -> bool:
        """Verifica se é uma campanha de SMS"""
        return self.type == "sms"

    def is_push_campaign(self) -> bool:
        """Verifica se é uma campanha de push notification"""
        return self.type == "push"

    def is_webinar_campaign(self) -> bool:
        """Verifica se é uma campanha de webinar"""
        return self.type == "webinar"

    # Status update methods
    def mark_as_scheduled(self, scheduled_at=None):
        """Marca a campanha como agendada"""
        self.status = "scheduled"
        if scheduled_at:
            self.scheduled_at = scheduled_at

    def mark_as_sending(self):
        """Marca a campanha como enviando"""
        self.status = "sending"

    def mark_as_sent(self):
        """Marca a campanha como enviada"""
        from datetime import datetime
        self.status = "sent"
        self.sent_at = datetime.utcnow()

    def mark_as_completed(self):
        """Marca a campanha como completada"""
        self.status = "completed"

    def mark_as_cancelled(self):
        """Marca a campanha como cancelada"""
        self.status = "cancelled"

    def mark_as_paused(self):
        """Marca a campanha como pausada"""
        self.status = "paused"

    def resume(self):
        """Resume uma campanha pausada"""
        if self.is_paused():
            self.status = "scheduled" if self.scheduled_at else "draft"

    # Statistics methods
    def get_stats(self):
        """Retorna as estatísticas da campanha"""
        return self.stats or {}

    def update_stats(self, new_stats: dict):
        """Atualiza as estatísticas da campanha"""
        if self.stats:
            self.stats.update(new_stats)
        else:
            self.stats = new_stats

    def get_stat(self, stat_name: str):
        """Retorna uma estatística específica"""
        return self.get_stats().get(stat_name, 0)

    def increment_stat(self, stat_name: str, increment: int = 1):
        """Incrementa uma estatística"""
        stats = self.get_stats()
        stats[stat_name] = stats.get(stat_name, 0) + increment
        self.stats = stats

    def get_sent_count(self) -> int:
        """Retorna o número de envios"""
        return self.get_stat("sent_count")

    def get_opened_count(self) -> int:
        """Retorna o número de aberturas"""
        return self.get_stat("opened_count")

    def get_clicked_count(self) -> int:
        """Retorna o número de cliques"""
        return self.get_stat("clicked_count")

    def get_bounced_count(self) -> int:
        """Retorna o número de bounces"""
        return self.get_stat("bounced_count")

    def get_unsubscribed_count(self) -> int:
        """Retorna o número de descadastros"""
        return self.get_stat("unsubscribed_count")

    def get_open_rate(self) -> float:
        """Retorna a taxa de abertura"""
        sent = self.get_sent_count()
        if sent == 0:
            return 0.0
        return (self.get_opened_count() / sent) * 100

    def get_click_rate(self) -> float:
        """Retorna a taxa de clique"""
        sent = self.get_sent_count()
        if sent == 0:
            return 0.0
        return (self.get_clicked_count() / sent) * 100

    def get_bounce_rate(self) -> float:
        """Retorna a taxa de bounce"""
        sent = self.get_sent_count()
        if sent == 0:
            return 0.0
        return (self.get_bounced_count() / sent) * 100

    # Settings methods
    def get_settings(self):
        """Retorna as configurações da campanha"""
        return self.settings or {}

    def get_setting(self, setting_name: str):
        """Retorna uma configuração específica"""
        return self.get_settings().get(setting_name)

    def set_setting(self, setting_name: str, value):
        """Define uma configuração"""
        if self.settings is None:
            self.settings = {}
        self.settings[setting_name] = value

    def update_settings(self, new_settings: dict):
        """Atualiza as configurações da campanha"""
        if self.settings:
            self.settings.update(new_settings)
        else:
            self.settings = new_settings

    # Campaign management methods
    def get_recipient_count(self) -> int:
        """Retorna o número de destinatários da campanha"""
        return len(self.campaign_contacts)

    def can_be_sent(self) -> bool:
        """Verifica se a campanha pode ser enviada"""
        return self.status in ["draft", "scheduled"] and self.content is not None

    def can_be_cancelled(self) -> bool:
        """Verifica se a campanha pode ser cancelada"""
        return self.status in ["draft", "scheduled", "paused"]

    def can_be_paused(self) -> bool:
        """Verifica se a campanha pode ser pausada"""
        return self.status in ["scheduled", "sending"]

    @classmethod
    def create_email_campaign(
        cls,
        tenant_id: str,
        created_by: str,
        name: str,
        subject: str,
        content: str,
        description: str = None
    ):
        """Cria uma campanha de email"""
        return cls(
            tenant_id=tenant_id,
            created_by=created_by,
            name=name,
            description=description,
            type="email",
            status="draft",
            subject=subject,
            content=content
        )

    @classmethod
    def create_sms_campaign(
        cls,
        tenant_id: str,
        created_by: str,
        name: str,
        content: str,
        description: str = None
    ):
        """Cria uma campanha de SMS"""
        return cls(
            tenant_id=tenant_id,
            created_by=created_by,
            name=name,
            description=description,
            type="sms",
            status="draft",
            content=content
        )

    @classmethod
    def find_by_name(cls, session, name: str, tenant_id: str):
        """Busca campanha por nome e tenant"""
        return session.query(cls).filter(
            cls.name == name,
            cls.tenant_id == tenant_id
        ).first()

    def duplicate(self, new_name: str):
        """Cria uma cópia da campanha"""
        return self.__class__(
            tenant_id=self.tenant_id,
            created_by=self.created_by,
            name=new_name,
            description=f"Cópia de {self.name}",
            type=self.type,
            status="draft",
            subject=self.subject,
            content=self.content,
            template_id=self.template_id,
            settings=self.settings.copy() if self.settings else None
        ) 