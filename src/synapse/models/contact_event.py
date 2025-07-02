"""
Model para Contact Events (CRM)
ALINHADO PERFEITAMENTE COM A TABELA contact_events
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class ContactEvent(Base):
    """Model para eventos de contatos - ALINHADO COM contact_events TABLE"""
    
    __tablename__ = "contact_events"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    contact_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contacts.id"), nullable=False)
    event_type = Column(String, nullable=False)
    event_name = Column(String, nullable=True)
    event_data = Column(JSONB, nullable=True, default={})
    description = Column(Text, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    source = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    contact = relationship("Contact", back_populates="contact_events")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ContactEvent(id={self.id}, contact_id={self.contact_id}, event_type='{self.event_type}', event_name='{self.event_name}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "contact_id": str(self.contact_id),
            "event_type": self.event_type,
            "event_name": self.event_name,
            "event_data": self.event_data,
            "description": self.description,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "source": self.source,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referrer": self.referrer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    # Event type categorization
    def is_web_event(self) -> bool:
        """Verifica se é um evento web"""
        web_types = ["page_view", "click", "form_submit", "download", "scroll", "video_play", "video_pause"]
        return self.event_type in web_types

    def is_email_event(self) -> bool:
        """Verifica se é um evento de email"""
        email_types = ["email_open", "email_click", "email_bounce", "email_unsubscribe", "email_sent"]
        return self.event_type in email_types

    def is_behavioral_event(self) -> bool:
        """Verifica se é um evento comportamental"""
        behavioral_types = ["purchase", "signup", "login", "logout", "subscription", "cancellation"]
        return self.event_type in behavioral_types

    def is_custom_event(self) -> bool:
        """Verifica se é um evento customizado"""
        standard_types = [
            "page_view", "click", "form_submit", "download", "scroll", "video_play", "video_pause",
            "email_open", "email_click", "email_bounce", "email_unsubscribe", "email_sent",
            "purchase", "signup", "login", "logout", "subscription", "cancellation"
        ]
        return self.event_type not in standard_types

    # Event analysis
    def has_value(self) -> bool:
        """Verifica se o evento tem valor monetário"""
        return bool(self.event_data and self.event_data.get("value"))

    def get_event_value(self) -> float:
        """Retorna o valor monetário do evento"""
        if self.event_data and "value" in self.event_data:
            try:
                return float(self.event_data["value"])
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def get_duration(self) -> int:
        """Retorna a duração do evento em segundos"""
        if self.event_data and "duration" in self.event_data:
            try:
                return int(self.event_data["duration"])
            except (ValueError, TypeError):
                return 0
        return 0

    def get_page_url(self) -> str:
        """Retorna a URL da página (para eventos web)"""
        if self.event_data and "url" in self.event_data:
            return str(self.event_data["url"])
        return ""

    def get_element_id(self) -> str:
        """Retorna o ID do elemento clicado"""
        if self.event_data and "element_id" in self.event_data:
            return str(self.event_data["element_id"])
        return ""

    def get_campaign_info(self) -> dict:
        """Retorna informações de campanha associadas"""
        campaign_data = {}
        if self.event_data:
            for key in ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]:
                if key in self.event_data:
                    campaign_data[key] = self.event_data[key]
        return campaign_data

    # Device and browser info
    def get_device_type(self) -> str:
        """Retorna o tipo de dispositivo"""
        if self.event_data and "device_type" in self.event_data:
            return str(self.event_data["device_type"])
        elif self.user_agent:
            # Análise básica do user agent
            user_agent_lower = self.user_agent.lower()
            if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
                return "mobile"
            elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
                return "tablet"
            else:
                return "desktop"
        return "unknown"

    def get_browser(self) -> str:
        """Retorna o navegador (análise básica)"""
        if self.event_data and "browser" in self.event_data:
            return str(self.event_data["browser"])
        elif self.user_agent:
            user_agent_lower = self.user_agent.lower()
            if "chrome" in user_agent_lower:
                return "Chrome"
            elif "firefox" in user_agent_lower:
                return "Firefox"
            elif "safari" in user_agent_lower:
                return "Safari"
            elif "edge" in user_agent_lower:
                return "Edge"
            else:
                return "Other"
        return "unknown"

    def get_location_info(self) -> dict:
        """Retorna informações de localização"""
        location_data = {}
        if self.event_data:
            for key in ["country", "region", "city", "latitude", "longitude"]:
                if key in self.event_data:
                    location_data[key] = self.event_data[key]
        return location_data

    # Event scoring and qualification
    def get_engagement_score(self) -> int:
        """Retorna uma pontuação de engajamento para o evento (0-100)"""
        base_scores = {
            "page_view": 5,
            "click": 15,
            "form_submit": 30,
            "download": 25,
            "email_open": 10,
            "email_click": 20,
            "purchase": 100,
            "signup": 80,
            "subscription": 90,
            "login": 20,
        }
        
        score = base_scores.get(self.event_type, 10)
        
        # Bonus por duração longa
        duration = self.get_duration()
        if duration > 300:  # 5 minutos
            score += 10
        elif duration > 60:  # 1 minuto
            score += 5
        
        # Bonus por valor monetário
        if self.has_value():
            value = self.get_event_value()
            if value > 100:
                score += 20
            elif value > 10:
                score += 10
            else:
                score += 5
        
        return min(100, score)

    def is_high_intent(self) -> bool:
        """Verifica se é um evento de alta intenção de compra"""
        high_intent_events = ["purchase", "subscription", "form_submit", "download"]
        return self.event_type in high_intent_events

    def is_conversion_event(self) -> bool:
        """Verifica se é um evento de conversão"""
        conversion_events = ["purchase", "signup", "subscription", "form_submit"]
        return self.event_type in conversion_events

    # Utility methods
    @classmethod
    def create_event(
        cls,
        contact_id: str,
        event_type: str,
        event_name: str = None,
        event_data: dict = None,
        description: str = None,
        source: str = None,
        session_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        referrer: str = None,
        tenant_id: str = None,
        occurred_at = None
    ):
        """Cria um novo evento de contato"""
        from datetime import datetime
        
        return cls(
            contact_id=contact_id,
            event_type=event_type,
            event_name=event_name,
            event_data=event_data or {},
            description=description,
            source=source,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            tenant_id=tenant_id,
            occurred_at=occurred_at or datetime.utcnow()
        )

    @classmethod
    def get_contact_timeline(cls, session, contact_id: str, limit: int = 50):
        """Retorna a timeline de eventos de um contato"""
        return session.query(cls).filter(
            cls.contact_id == contact_id
        ).order_by(cls.occurred_at.desc()).limit(limit).all()

    @classmethod
    def get_event_counts_by_type(cls, session, contact_id: str):
        """Retorna contagens de eventos por tipo para um contato"""
        from sqlalchemy import func
        
        return session.query(
            cls.event_type,
            func.count(cls.id).label('count')
        ).filter(
            cls.contact_id == contact_id
        ).group_by(cls.event_type).all()

    @classmethod
    def get_recent_events(cls, session, contact_id: str, days: int = 30):
        """Retorna eventos recentes de um contato"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return session.query(cls).filter(
            cls.contact_id == contact_id,
            cls.occurred_at >= cutoff_date
        ).order_by(cls.occurred_at.desc()).all()

    @classmethod
    def calculate_engagement_score(cls, session, contact_id: str, days: int = 30):
        """Calcula a pontuação total de engajamento de um contato"""
        events = cls.get_recent_events(session, contact_id, days)
        return sum(event.get_engagement_score() for event in events)

    @classmethod
    def get_conversion_events(cls, session, contact_id: str):
        """Retorna eventos de conversão de um contato"""
        conversion_types = ["purchase", "signup", "subscription", "form_submit"]
        return session.query(cls).filter(
            cls.contact_id == contact_id,
            cls.event_type.in_(conversion_types)
        ).order_by(cls.occurred_at.desc()).all()

    @classmethod
    def track_page_view(
        cls,
        contact_id: str,
        url: str,
        title: str = None,
        duration: int = None,
        **kwargs
    ):
        """Método conveniente para rastrear visualizações de página"""
        event_data = {"url": url}
        if title:
            event_data["title"] = title
        if duration:
            event_data["duration"] = duration
        
        return cls.create_event(
            contact_id=contact_id,
            event_type="page_view",
            event_name=f"Viewed: {title or url}",
            event_data=event_data,
            **kwargs
        )

    @classmethod
    def track_email_interaction(
        cls,
        contact_id: str,
        interaction_type: str,  # open, click, bounce, unsubscribe
        email_id: str = None,
        campaign_id: str = None,
        link_url: str = None,
        **kwargs
    ):
        """Método conveniente para rastrear interações de email"""
        event_data = {}
        if email_id:
            event_data["email_id"] = email_id
        if campaign_id:
            event_data["campaign_id"] = campaign_id
        if link_url:
            event_data["link_url"] = link_url
        
        return cls.create_event(
            contact_id=contact_id,
            event_type=f"email_{interaction_type}",
            event_name=f"Email {interaction_type.title()}",
            event_data=event_data,
            **kwargs
        )

    @classmethod
    def track_purchase(
        cls,
        contact_id: str,
        value: float,
        currency: str = "USD",
        product_id: str = None,
        product_name: str = None,
        quantity: int = 1,
        **kwargs
    ):
        """Método conveniente para rastrear compras"""
        event_data = {
            "value": value,
            "currency": currency,
            "quantity": quantity
        }
        if product_id:
            event_data["product_id"] = product_id
        if product_name:
            event_data["product_name"] = product_name
        
        return cls.create_event(
            contact_id=contact_id,
            event_type="purchase",
            event_name=f"Purchase: {product_name or product_id or 'Product'}",
            event_data=event_data,
            **kwargs
        )

    def add_custom_data(self, key: str, value):
        """Adiciona dados customizados ao evento"""
        if not self.event_data:
            self.event_data = {}
        self.event_data[key] = value

    def get_custom_data(self, key: str, default=None):
        """Retorna um dado customizado do evento"""
        if self.event_data and key in self.event_data:
            return self.event_data[key]
        return default 