"""
Model para Conversion Journeys (CRM)
ALINHADO PERFEITAMENTE COM A TABELA conversion_journeys
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from synapse.database import Base


class ConversionJourney(Base):
    """Model para jornadas de conversão - ALINHADO COM conversion_journeys TABLE"""
    
    __tablename__ = "conversion_journeys"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    contact_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.contacts.id"), nullable=False)
    journey_name = Column(String, nullable=True)
    stage = Column(String, nullable=False)  # awareness, interest, consideration, intent, purchase, retention
    previous_stage = Column(String, nullable=True)
    stage_entered_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    stage_duration_hours = Column(Numeric(10, 2), nullable=True)
    conversion_probability = Column(Numeric(5, 2), nullable=True)  # 0.00 to 100.00
    conversion_value = Column(Numeric(10, 2), nullable=True)
    touchpoints = Column(JSONB, nullable=True, default=[])
    attribution_data = Column(JSONB, nullable=True, default={})
    source_campaign = Column(String, nullable=True)
    source_medium = Column(String, nullable=True)
    source_channel = Column(String, nullable=True)
    first_touch_at = Column(DateTime(timezone=True), nullable=True)
    last_touch_at = Column(DateTime(timezone=True), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    conversion_event = Column(String, nullable=True)
    revenue_generated = Column(Numeric(10, 2), nullable=True)
    is_active = Column(String, nullable=True)  # true/false as string
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    contact = relationship("Contact", back_populates="conversion_journeys")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ConversionJourney(id={self.id}, contact_id={self.contact_id}, stage='{self.stage}', journey_name='{self.journey_name}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "contact_id": str(self.contact_id),
            "journey_name": self.journey_name,
            "stage": self.stage,
            "previous_stage": self.previous_stage,
            "stage_entered_at": self.stage_entered_at.isoformat() if self.stage_entered_at else None,
            "stage_duration_hours": float(self.stage_duration_hours) if self.stage_duration_hours else None,
            "conversion_probability": float(self.conversion_probability) if self.conversion_probability else None,
            "conversion_value": float(self.conversion_value) if self.conversion_value else None,
            "touchpoints": self.touchpoints,
            "attribution_data": self.attribution_data,
            "source_campaign": self.source_campaign,
            "source_medium": self.source_medium,
            "source_channel": self.source_channel,
            "first_touch_at": self.first_touch_at.isoformat() if self.first_touch_at else None,
            "last_touch_at": self.last_touch_at.isoformat() if self.last_touch_at else None,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
            "conversion_event": self.conversion_event,
            "revenue_generated": float(self.revenue_generated) if self.revenue_generated else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    # Stage management
    VALID_STAGES = ["awareness", "interest", "consideration", "intent", "purchase", "retention", "advocacy", "churn"]
    
    def is_in_stage(self, stage: str) -> bool:
        """Verifica se está no estágio específico"""
        return self.stage == stage

    def is_awareness_stage(self) -> bool:
        """Verifica se está no estágio de awareness"""
        return self.stage == "awareness"

    def is_interest_stage(self) -> bool:
        """Verifica se está no estágio de interest"""
        return self.stage == "interest"

    def is_consideration_stage(self) -> bool:
        """Verifica se está no estágio de consideration"""
        return self.stage == "consideration"

    def is_intent_stage(self) -> bool:
        """Verifica se está no estágio de intent"""
        return self.stage == "intent"

    def is_purchase_stage(self) -> bool:
        """Verifica se está no estágio de purchase"""
        return self.stage == "purchase"

    def is_retention_stage(self) -> bool:
        """Verifica se está no estágio de retention"""
        return self.stage == "retention"

    def is_advocacy_stage(self) -> bool:
        """Verifica se está no estágio de advocacy"""
        return self.stage == "advocacy"

    def is_churned(self) -> bool:
        """Verifica se está churned"""
        return self.stage == "churn"

    def has_converted(self) -> bool:
        """Verifica se já converteu"""
        return self.converted_at is not None

    def is_active_journey(self) -> bool:
        """Verifica se a jornada está ativa"""
        return self.is_active == "true"

    # Stage progression methods
    def advance_to_stage(self, new_stage: str, conversion_probability: float = None):
        """Avança para um novo estágio"""
        from datetime import datetime
        
        if new_stage not in self.VALID_STAGES:
            raise ValueError(f"Invalid stage: {new_stage}")
        
        # Calcular duração do estágio atual
        if self.stage_entered_at:
            duration = datetime.utcnow() - self.stage_entered_at
            self.stage_duration_hours = Decimal(str(duration.total_seconds() / 3600))
        
        self.previous_stage = self.stage
        self.stage = new_stage
        self.stage_entered_at = datetime.utcnow()
        self.last_touch_at = datetime.utcnow()
        
        if conversion_probability is not None:
            self.conversion_probability = Decimal(str(conversion_probability))

    def mark_as_converted(self, conversion_event: str = None, revenue: float = None):
        """Marca como convertido"""
        from datetime import datetime
        
        self.converted_at = datetime.utcnow()
        self.last_touch_at = datetime.utcnow()
        
        if conversion_event:
            self.conversion_event = conversion_event
        
        if revenue is not None:
            self.revenue_generated = Decimal(str(revenue))
        
        # Mover para estágio de purchase se não estiver
        if self.stage not in ["purchase", "retention", "advocacy"]:
            self.advance_to_stage("purchase", 100.0)

    def mark_as_churned(self):
        """Marca como churned"""
        self.advance_to_stage("churn", 0.0)
        self.is_active = "false"

    def reactivate_journey(self, starting_stage: str = "awareness"):
        """Reativa a jornada"""
        from datetime import datetime
        
        self.is_active = "true"
        self.advance_to_stage(starting_stage)
        self.converted_at = None
        self.conversion_event = None

    # Touchpoint management
    def add_touchpoint(self, touchpoint_data: dict):
        """Adiciona um ponto de contato"""
        from datetime import datetime
        
        touchpoint = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": self.stage,
            **touchpoint_data
        }
        
        if not self.touchpoints:
            self.touchpoints = []
        
        self.touchpoints.append(touchpoint)
        
        # Atualizar last_touch_at
        self.last_touch_at = datetime.utcnow()
        
        # Se for o primeiro touchpoint
        if not self.first_touch_at:
            self.first_touch_at = datetime.utcnow()

    def get_touchpoints_by_stage(self, stage: str) -> list:
        """Retorna touchpoints de um estágio específico"""
        if not self.touchpoints:
            return []
        
        return [tp for tp in self.touchpoints if tp.get("stage") == stage]

    def get_touchpoint_count(self) -> int:
        """Retorna o número de touchpoints"""
        return len(self.touchpoints) if self.touchpoints else 0

    def get_touchpoint_count_by_stage(self, stage: str) -> int:
        """Retorna o número de touchpoints por estágio"""
        return len(self.get_touchpoints_by_stage(stage))

    # Duration and timing analysis
    def get_total_journey_duration(self):
        """Retorna a duração total da jornada"""
        if self.first_touch_at:
            from datetime import datetime
            end_time = self.converted_at or datetime.utcnow()
            return end_time - self.first_touch_at
        return None

    def get_total_journey_duration_hours(self) -> float:
        """Retorna a duração total da jornada em horas"""
        duration = self.get_total_journey_duration()
        if duration:
            return duration.total_seconds() / 3600
        return 0.0

    def get_stage_duration_hours(self) -> float:
        """Retorna a duração do estágio atual em horas"""
        if self.stage_duration_hours:
            return float(self.stage_duration_hours)
        return 0.0

    def get_time_since_last_touch(self):
        """Retorna o tempo desde o último touchpoint"""
        if self.last_touch_at:
            from datetime import datetime
            return datetime.utcnow() - self.last_touch_at
        return None

    def get_time_since_last_touch_hours(self) -> float:
        """Retorna o tempo desde o último touchpoint em horas"""
        time_since = self.get_time_since_last_touch()
        if time_since:
            return time_since.total_seconds() / 3600
        return 0.0

    # Probability and value analysis
    def get_conversion_probability(self) -> float:
        """Retorna a probabilidade de conversão"""
        if self.conversion_probability:
            return float(self.conversion_probability)
        return 0.0

    def update_conversion_probability(self, probability: float):
        """Atualiza a probabilidade de conversão"""
        if 0 <= probability <= 100:
            self.conversion_probability = Decimal(str(probability))
        else:
            raise ValueError("Conversion probability must be between 0 and 100")

    def get_conversion_value(self) -> float:
        """Retorna o valor de conversão"""
        if self.conversion_value:
            return float(self.conversion_value)
        return 0.0

    def update_conversion_value(self, value: float):
        """Atualiza o valor de conversão"""
        self.conversion_value = Decimal(str(value))

    def get_revenue_generated(self) -> float:
        """Retorna a receita gerada"""
        if self.revenue_generated:
            return float(self.revenue_generated)
        return 0.0

    def calculate_roi(self) -> float:
        """Calcula o ROI baseado no valor investido vs receita gerada"""
        # Este cálculo pode ser melhorado com dados de custo real
        invested_value = self.get_conversion_value()
        revenue = self.get_revenue_generated()
        
        if invested_value > 0 and revenue > 0:
            return ((revenue - invested_value) / invested_value) * 100
        return 0.0

    # Attribution analysis
    def add_attribution_data(self, key: str, value):
        """Adiciona dados de atribuição"""
        if not self.attribution_data:
            self.attribution_data = {}
        self.attribution_data[key] = value

    def get_attribution_data(self, key: str, default=None):
        """Retorna dados de atribuição"""
        if self.attribution_data and key in self.attribution_data:
            return self.attribution_data[key]
        return default

    def get_first_touch_attribution(self) -> dict:
        """Retorna atribuição do primeiro toque"""
        return {
            "campaign": self.source_campaign,
            "medium": self.source_medium,
            "channel": self.source_channel,
            "timestamp": self.first_touch_at.isoformat() if self.first_touch_at else None
        }

    def get_last_touch_attribution(self) -> dict:
        """Retorna atribuição do último toque"""
        if self.touchpoints:
            last_touchpoint = self.touchpoints[-1]
            return {
                "type": last_touchpoint.get("type"),
                "source": last_touchpoint.get("source"),
                "campaign": last_touchpoint.get("campaign"),
                "timestamp": last_touchpoint.get("timestamp")
            }
        return self.get_first_touch_attribution()

    # Journey analysis and insights
    def get_journey_velocity(self) -> float:
        """Retorna a velocidade da jornada (estágios por hora)"""
        total_hours = self.get_total_journey_duration_hours()
        if total_hours > 0:
            stages_passed = len(set(tp.get("stage") for tp in self.touchpoints if tp.get("stage")))
            return stages_passed / total_hours
        return 0.0

    def get_stage_performance(self) -> dict:
        """Retorna performance por estágio"""
        stage_data = {}
        
        for stage in self.VALID_STAGES:
            touchpoints = self.get_touchpoints_by_stage(stage)
            stage_data[stage] = {
                "touchpoint_count": len(touchpoints),
                "unique_channels": len(set(tp.get("channel") for tp in touchpoints if tp.get("channel"))),
                "conversion_rate": self.get_conversion_probability() if stage == self.stage else 0
            }
        
        return stage_data

    def is_stagnant(self, hours_threshold: int = 168) -> bool:  # 1 week default
        """Verifica se a jornada está estagnada"""
        return self.get_time_since_last_touch_hours() > hours_threshold

    def needs_nurturing(self) -> bool:
        """Verifica se precisa de nurturing"""
        return (
            self.is_stagnant(72) or  # 3 days without touch
            (self.stage in ["awareness", "interest"] and self.get_conversion_probability() < 20) or
            (self.stage == "consideration" and self.get_conversion_probability() < 40)
        )

    # Utility methods
    @classmethod
    def create_journey(
        cls,
        contact_id: str,
        journey_name: str = None,
        starting_stage: str = "awareness",
        source_campaign: str = None,
        source_medium: str = None,
        source_channel: str = None,
        conversion_value: float = None,
        tenant_id: str = None
    ):
        """Cria uma nova jornada de conversão"""
        from datetime import datetime
        
        journey = cls(
            contact_id=contact_id,
            journey_name=journey_name,
            stage=starting_stage,
            stage_entered_at=datetime.utcnow(),
            source_campaign=source_campaign,
            source_medium=source_medium,
            source_channel=source_channel,
            first_touch_at=datetime.utcnow(),
            last_touch_at=datetime.utcnow(),
            is_active="true",
            tenant_id=tenant_id
        )
        
        if conversion_value:
            journey.conversion_value = Decimal(str(conversion_value))
        
        return journey

    @classmethod
    def get_active_journeys(cls, session, tenant_id: str = None):
        """Retorna jornadas ativas"""
        query = session.query(cls).filter(cls.is_active == "true")
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.all()

    @classmethod
    def get_converted_journeys(cls, session, tenant_id: str = None):
        """Retorna jornadas convertidas"""
        query = session.query(cls).filter(cls.converted_at.isnot(None))
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.converted_at.desc()).all()

    @classmethod
    def get_journeys_by_stage(cls, session, stage: str, tenant_id: str = None):
        """Retorna jornadas por estágio"""
        query = session.query(cls).filter(cls.stage == stage)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.all()

    @classmethod
    def get_stagnant_journeys(cls, session, hours_threshold: int = 168, tenant_id: str = None):
        """Retorna jornadas estagnadas"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_threshold)
        query = session.query(cls).filter(
            cls.is_active == "true",
            cls.last_touch_at < cutoff_time
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.all()

    @classmethod
    def get_journey_analytics(cls, session, tenant_id: str = None):
        """Retorna analytics agregados das jornadas"""
        from sqlalchemy import func
        
        query = session.query(cls)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        total_journeys = query.count()
        active_journeys = query.filter(cls.is_active == "true").count()
        converted_journeys = query.filter(cls.converted_at.isnot(None)).count()
        
        avg_conversion_probability = session.query(
            func.avg(cls.conversion_probability)
        ).filter(cls.is_active == "true")
        
        if tenant_id:
            avg_conversion_probability = avg_conversion_probability.filter(cls.tenant_id == tenant_id)
        
        avg_prob = avg_conversion_probability.scalar() or 0
        
        total_revenue = session.query(
            func.sum(cls.revenue_generated)
        ).filter(cls.revenue_generated.isnot(None))
        
        if tenant_id:
            total_revenue = total_revenue.filter(cls.tenant_id == tenant_id)
        
        revenue = total_revenue.scalar() or 0
        
        return {
            "total_journeys": total_journeys,
            "active_journeys": active_journeys,
            "converted_journeys": converted_journeys,
            "conversion_rate": (converted_journeys / total_journeys * 100) if total_journeys > 0 else 0,
            "average_conversion_probability": float(avg_prob),
            "total_revenue": float(revenue)
        }

    def track_email_open(self, campaign_id: str = None):
        """Rastreia abertura de email"""
        self.add_touchpoint({
            "type": "email_open",
            "channel": "email",
            "campaign_id": campaign_id
        })

    def track_website_visit(self, page_url: str, utm_data: dict = None):
        """Rastreia visita ao website"""
        touchpoint_data = {
            "type": "website_visit",
            "channel": "website",
            "page_url": page_url
        }
        
        if utm_data:
            touchpoint_data.update(utm_data)
        
        self.add_touchpoint(touchpoint_data)

    def track_demo_request(self):
        """Rastreia solicitação de demo"""
        self.add_touchpoint({
            "type": "demo_request",
            "channel": "website",
            "high_intent": True
        })
        
        # Aumentar probabilidade de conversão
        if self.conversion_probability:
            new_prob = min(90.0, float(self.conversion_probability) + 30.0)
            self.update_conversion_probability(new_prob)

    def track_proposal_sent(self, proposal_value: float = None):
        """Rastreia envio de proposta"""
        touchpoint_data = {
            "type": "proposal_sent",
            "channel": "sales",
            "high_intent": True
        }
        
        if proposal_value:
            touchpoint_data["proposal_value"] = proposal_value
            self.update_conversion_value(proposal_value)
        
        self.add_touchpoint(touchpoint_data)
        
        # Mover para estágio de intent se não estiver avançado
        if self.stage in ["awareness", "interest", "consideration"]:
            self.advance_to_stage("intent", 70.0)

    def track_purchase(self, purchase_value: float, product_info: dict = None):
        """Rastreia compra"""
        touchpoint_data = {
            "type": "purchase",
            "channel": "sales",
            "purchase_value": purchase_value
        }
        
        if product_info:
            touchpoint_data.update(product_info)
        
        self.add_touchpoint(touchpoint_data)
        self.mark_as_converted("purchase", purchase_value) 