"""Analytics Alert Model"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AnalyticsAlert(Base):
    """Analytics alerts and notifications"""
    
    __tablename__ = "analytics_alerts"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    condition = Column(JSONB, nullable=False)
    notification_config = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    owner = relationship("synapse.models.user.User", back_populates="analytics_alerts")
    tenant = relationship("synapse.models.tenant.Tenant", back_populates="analytics_alerts")

    def __str__(self):
        return f"AnalyticsAlert(name={self.name}, active={self.is_active})"

    @property
    def condition_summary(self):
        """Get a summary of the alert condition"""
        if not self.condition:
            return "No condition defined"
        
        # Extract key information from condition
        metric = self.condition.get('metric', 'unknown')
        operator = self.condition.get('operator', '==')
        threshold = self.condition.get('threshold', 'N/A')
        
        return f"{metric} {operator} {threshold}"

    @property
    def notification_methods(self):
        """Get list of notification methods"""
        if not self.notification_config:
            return []
        
        methods = []
        if self.notification_config.get('email'):
            methods.append('email')
        if self.notification_config.get('slack'):
            methods.append('slack')
        if self.notification_config.get('webhook'):
            methods.append('webhook')
        if self.notification_config.get('sms'):
            methods.append('sms')
        
        return methods

    @property
    def has_been_triggered(self):
        """Check if alert has ever been triggered"""
        return self.last_triggered_at is not None

    def activate(self):
        """Activate the alert"""
        self.is_active = True
        self.updated_at = func.now()

    def deactivate(self):
        """Deactivate the alert"""
        self.is_active = False
        self.updated_at = func.now()

    def update_condition(self, new_condition):
        """Update alert condition"""
        self.condition = new_condition
        self.updated_at = func.now()

    def update_notification_config(self, new_config):
        """Update notification configuration"""
        self.notification_config = new_config
        self.updated_at = func.now()

    def record_trigger(self):
        """Record that the alert was triggered"""
        self.last_triggered_at = func.now()
        self.updated_at = func.now()

    def evaluate_condition(self, current_metrics):
        """Evaluate if current metrics trigger this alert"""
        if not self.is_active or not self.condition:
            return False
        
        metric_name = self.condition.get('metric')
        operator = self.condition.get('operator', '==')
        threshold = self.condition.get('threshold')
        
        if not metric_name or threshold is None:
            return False
        
        current_value = current_metrics.get(metric_name)
        if current_value is None:
            return False
        
        # Evaluate condition based on operator
        if operator == '>':
            return current_value > threshold
        elif operator == '>=':
            return current_value >= threshold
        elif operator == '<':
            return current_value < threshold
        elif operator == '<=':
            return current_value <= threshold
        elif operator == '==':
            return current_value == threshold
        elif operator == '!=':
            return current_value != threshold
        
        return False

    @classmethod
    def get_active_alerts(cls, session, owner_id=None, tenant_id=None):
        """Get active alerts"""
        query = session.query(cls).filter(cls.is_active.is_(True))
        
        if owner_id:
            query = query.filter(cls.owner_id == owner_id)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_alerts_by_metric(cls, session, metric_name):
        """Get alerts monitoring a specific metric"""
        return session.query(cls).filter(
            cls.is_active.is_(True),
            cls.condition.op('->>')('metric') == metric_name
        ).all()

    @classmethod
    def get_recently_triggered(cls, session, hours=24, tenant_id=None):
        """Get alerts triggered in the last N hours"""
        cutoff_time = func.now() - func.interval(f'{hours} hours')
        query = session.query(cls).filter(
            cls.last_triggered_at >= cutoff_time
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.last_triggered_at.desc()).all()

    @classmethod
    def create_alert(cls, session, name, condition, notification_config, 
                    owner_id, description=None, tenant_id=None):
        """Create a new analytics alert"""
        alert = cls(
            name=name,
            description=description,
            condition=condition,
            notification_config=notification_config,
            owner_id=owner_id,
            tenant_id=tenant_id,
            created_at=func.now(),
            updated_at=func.now()
        )
        
        session.add(alert)
        return alert
