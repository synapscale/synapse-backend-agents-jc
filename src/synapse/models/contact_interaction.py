"""
Model para Contact Interactions (CRM)
ALINHADO PERFEITAMENTE COM A TABELA contact_interactions
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from synapse.database import Base


class InteractionType(PyEnum):
    """Tipos de interação disponíveis"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    MEETING = "meeting"
    VIDEO_CALL = "video_call"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    NOTE = "note"
    TASK = "task"
    DEMO = "demo"
    FOLLOW_UP = "follow_up"


class InteractionDirection(PyEnum):
    """Direção da interação"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class InteractionStatus(PyEnum):
    """Status da interação"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class ContactInteraction(Base):
    """Model para interações com contatos - ALINHADO COM contact_interactions TABLE"""
    
    __tablename__ = "contact_interactions"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    contact_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contacts.id"), nullable=False)
    interaction_type = Column(String, nullable=False)  # email, phone, sms, meeting, etc.
    direction = Column(String, nullable=True)  # inbound, outbound
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    status = Column(String, nullable=True)  # scheduled, completed, cancelled, no_show, rescheduled
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(String, nullable=True)  # Duration in minutes as string
    outcome = Column(String, nullable=True)
    next_action = Column(String, nullable=True)
    interaction_metadata = Column("metadata", JSONB, nullable=True, server_default="{}")
    created_by = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    contact = relationship("Contact", back_populates="contact_interactions")
    created_by_user = relationship("User")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ContactInteraction(id={self.id}, contact_id={self.contact_id}, type='{self.interaction_type}', subject='{self.subject}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "contact_id": str(self.contact_id),
            "interaction_type": self.interaction_type,
            "direction": self.direction,
            "subject": self.subject,
            "content": self.content,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_minutes": self.duration_minutes,
            "outcome": self.outcome,
            "next_action": self.next_action,
            "metadata": self.interaction_metadata,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    # Type check methods
    def is_email(self) -> bool:
        """Verifica se é uma interação por email"""
        return self.interaction_type == "email"

    def is_phone_call(self) -> bool:
        """Verifica se é uma ligação telefônica"""
        return self.interaction_type == "phone"

    def is_meeting(self) -> bool:
        """Verifica se é uma reunião"""
        return self.interaction_type in ["meeting", "video_call", "demo"]

    def is_message(self) -> bool:
        """Verifica se é uma mensagem (SMS, chat)"""
        return self.interaction_type in ["sms", "chat"]

    def is_note(self) -> bool:
        """Verifica se é uma nota"""
        return self.interaction_type == "note"

    def is_inbound(self) -> bool:
        """Verifica se é uma interação de entrada"""
        return self.direction == "inbound"

    def is_outbound(self) -> bool:
        """Verifica se é uma interação de saída"""
        return self.direction == "outbound"

    # Status check methods
    def is_scheduled(self) -> bool:
        """Verifica se está agendado"""
        return self.status == "scheduled"

    def is_completed(self) -> bool:
        """Verifica se foi concluído"""
        return self.status == "completed"

    def is_cancelled(self) -> bool:
        """Verifica se foi cancelado"""
        return self.status == "cancelled"

    def is_no_show(self) -> bool:
        """Verifica se houve não comparecimento"""
        return self.status == "no_show"

    def is_rescheduled(self) -> bool:
        """Verifica se foi reagendado"""
        return self.status == "rescheduled"

    # Status update methods
    def mark_as_completed(self, outcome: str = None, next_action: str = None):
        """Marca como concluído"""
        from datetime import datetime
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        if outcome:
            self.outcome = outcome
        if next_action:
            self.next_action = next_action

    def mark_as_cancelled(self, reason: str = None):
        """Marca como cancelado"""
        self.status = "cancelled"
        if reason and self.interaction_metadata:
            self.interaction_metadata["cancellation_reason"] = reason
        elif reason:
            self.interaction_metadata = {"cancellation_reason": reason}

    def mark_as_no_show(self):
        """Marca como não comparecimento"""
        self.status = "no_show"

    def reschedule(self, new_datetime):
        """Reagenda a interação"""
        self.status = "rescheduled"
        self.scheduled_at = new_datetime

    # Duration and timing
    def get_duration_minutes(self) -> int:
        """Retorna a duração em minutos"""
        if self.duration_minutes:
            try:
                return int(self.duration_minutes)
            except (ValueError, TypeError):
                return 0
        return 0

    def set_duration_minutes(self, minutes: int):
        """Define a duração em minutos"""
        self.duration_minutes = str(minutes)

    def calculate_actual_duration(self) -> int:
        """Calcula a duração real baseada nos timestamps"""
        if self.scheduled_at and self.completed_at:
            delta = self.completed_at - self.scheduled_at
            return int(delta.total_seconds() / 60)
        return 0

    def is_overdue(self) -> bool:
        """Verifica se está atrasado"""
        from datetime import datetime
        return (
            self.scheduled_at and 
            self.scheduled_at < datetime.utcnow() and 
            self.status == "scheduled"
        )

    def is_upcoming(self, hours: int = 24) -> bool:
        """Verifica se está programado para breve"""
        from datetime import datetime, timedelta
        if not self.scheduled_at or self.status != "scheduled":
            return False
        return self.scheduled_at <= datetime.utcnow() + timedelta(hours=hours)

    # Analysis and scoring
    def get_interaction_score(self) -> int:
        """Retorna uma pontuação para a interação (0-100)"""
        base_scores = {
            "email": 10,
            "phone": 30,
            "sms": 15,
            "meeting": 50,
            "video_call": 45,
            "chat": 20,
            "demo": 60,
            "follow_up": 25,
            "note": 5,
        }
        
        score = base_scores.get(self.interaction_type, 20)
        
        # Bonus por duração (para reuniões)
        if self.is_meeting():
            duration = self.get_duration_minutes()
            if duration >= 60:
                score += 20
            elif duration >= 30:
                score += 10
            elif duration >= 15:
                score += 5
        
        # Bonus por outcome positivo
        if self.outcome:
            positive_outcomes = ["sale", "qualified", "interested", "demo_scheduled", "meeting_scheduled"]
            if any(outcome in self.outcome.lower() for outcome in positive_outcomes):
                score += 30
        
        # Penalização por no-show
        if self.is_no_show():
            score = max(0, score - 20)
        
        return min(100, score)

    def is_positive_outcome(self) -> bool:
        """Verifica se teve um resultado positivo"""
        if not self.outcome:
            return False
        
        positive_indicators = [
            "sale", "qualified", "interested", "demo", "meeting", 
            "proposal", "contract", "follow-up", "positive"
        ]
        outcome_lower = self.outcome.lower()
        return any(indicator in outcome_lower for indicator in positive_indicators)

    def is_negative_outcome(self) -> bool:
        """Verifica se teve um resultado negativo"""
        if not self.outcome:
            return False
        
        negative_indicators = [
            "not interested", "rejected", "declined", "cancelled", 
            "competitor", "budget", "timing", "negative"
        ]
        outcome_lower = self.outcome.lower()
        return any(indicator in outcome_lower for indicator in negative_indicators)

    def needs_follow_up(self) -> bool:
        """Verifica se precisa de follow-up"""
        return bool(self.next_action) or self.is_positive_outcome()

    # Metadata helpers
    def add_metadata(self, key: str, value):
        """Adiciona metadados"""
        if not self.interaction_metadata:
            self.interaction_metadata = {}
        self.interaction_metadata[key] = value

    def get_metadata(self, key: str, default=None):
        """Retorna um metadado"""
        if self.interaction_metadata and key in self.interaction_metadata:
            return self.interaction_metadata[key]
        return default

    def get_call_quality(self) -> str:
        """Retorna a qualidade da chamada (se aplicável)"""
        return self.get_metadata("call_quality", "unknown")

    def get_recording_url(self) -> str:
        """Retorna a URL da gravação (se aplicável)"""
        return self.get_metadata("recording_url", "")

    def get_meeting_link(self) -> str:
        """Retorna o link da reunião"""
        return self.get_metadata("meeting_link", "")

    def get_participants(self) -> list:
        """Retorna lista de participantes"""
        return self.get_metadata("participants", [])

    # Utility methods
    @classmethod
    def create_interaction(
        cls,
        contact_id: str,
        interaction_type: str,
        subject: str = None,
        content: str = None,
        direction: str = "outbound",
        status: str = "scheduled",
        scheduled_at = None,
        duration_minutes: int = None,
        created_by: str = None,
        tenant_id: str = None,
        **kwargs
    ):
        """Cria uma nova interação"""
        interaction = cls(
            contact_id=contact_id,
            interaction_type=interaction_type,
            subject=subject,
            content=content,
            direction=direction,
            status=status,
            scheduled_at=scheduled_at,
            created_by=created_by,
            tenant_id=tenant_id,
            **kwargs
        )
        
        if duration_minutes:
            interaction.set_duration_minutes(duration_minutes)
        
        return interaction

    @classmethod
    def create_email(
        cls,
        contact_id: str,
        subject: str,
        content: str,
        direction: str = "outbound",
        **kwargs
    ):
        """Cria uma interação de email"""
        return cls.create_interaction(
            contact_id=contact_id,
            interaction_type="email",
            subject=subject,
            content=content,
            direction=direction,
            status="completed",
            **kwargs
        )

    @classmethod
    def create_phone_call(
        cls,
        contact_id: str,
        subject: str = None,
        direction: str = "outbound",
        duration_minutes: int = None,
        outcome: str = None,
        **kwargs
    ):
        """Cria uma interação de ligação telefônica"""
        return cls.create_interaction(
            contact_id=contact_id,
            interaction_type="phone",
            subject=subject or "Phone Call",
            direction=direction,
            status="completed",
            duration_minutes=duration_minutes,
            outcome=outcome,
            **kwargs
        )

    @classmethod
    def create_meeting(
        cls,
        contact_id: str,
        subject: str,
        scheduled_at,
        duration_minutes: int = 60,
        meeting_link: str = None,
        **kwargs
    ):
        """Cria uma reunião"""
        interaction = cls.create_interaction(
            contact_id=contact_id,
            interaction_type="meeting",
            subject=subject,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            status="scheduled",
            **kwargs
        )
        
        if meeting_link:
            interaction.add_metadata("meeting_link", meeting_link)
        
        return interaction

    @classmethod
    def create_note(
        cls,
        contact_id: str,
        subject: str,
        content: str,
        created_by: str = None,
        **kwargs
    ):
        """Cria uma nota"""
        return cls.create_interaction(
            contact_id=contact_id,
            interaction_type="note",
            subject=subject,
            content=content,
            status="completed",
            created_by=created_by,
            **kwargs
        )

    @classmethod
    def get_contact_interactions(cls, session, contact_id: str, limit: int = 50):
        """Retorna interações de um contato"""
        return session.query(cls).filter(
            cls.contact_id == contact_id
        ).order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_upcoming_interactions(cls, session, user_id: str = None, hours: int = 24):
        """Retorna interações próximas"""
        from datetime import datetime, timedelta
        
        future_time = datetime.utcnow() + timedelta(hours=hours)
        query = session.query(cls).filter(
            cls.status == "scheduled",
            cls.scheduled_at <= future_time,
            cls.scheduled_at >= datetime.utcnow()
        )
        
        if user_id:
            query = query.filter(cls.created_by == user_id)
        
        return query.order_by(cls.scheduled_at.asc()).all()

    @classmethod
    def get_overdue_interactions(cls, session, user_id: str = None):
        """Retorna interações em atraso"""
        from datetime import datetime
        
        query = session.query(cls).filter(
            cls.status == "scheduled",
            cls.scheduled_at < datetime.utcnow()
        )
        
        if user_id:
            query = query.filter(cls.created_by == user_id)
        
        return query.order_by(cls.scheduled_at.asc()).all()

    @classmethod
    def get_interaction_stats(cls, session, contact_id: str):
        """Retorna estatísticas de interação de um contato"""
        from sqlalchemy import func
        
        stats = session.query(
            func.count(cls.id).label('total'),
            func.sum(func.case([(cls.status == 'completed', 1)], else_=0)).label('completed'),
            func.sum(func.case([(cls.status == 'scheduled', 1)], else_=0)).label('scheduled'),
            func.sum(func.case([(cls.direction == 'inbound', 1)], else_=0)).label('inbound'),
            func.sum(func.case([(cls.direction == 'outbound', 1)], else_=0)).label('outbound'),
        ).filter(cls.contact_id == contact_id).first()
        
        return {
            'total': stats.total or 0,
            'completed': stats.completed or 0,
            'scheduled': stats.scheduled or 0,
            'inbound': stats.inbound or 0,
            'outbound': stats.outbound or 0,
        } 