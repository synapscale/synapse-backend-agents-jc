"""Analytics Event Model"""

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AnalyticsEvent(Base):
    """Analytics event tracking and data collection"""
    
    __tablename__ = "analytics_events"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    event_id = Column(String(36), nullable=False)  # External event ID
    event_type = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    label = Column(String(200), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    anonymous_id = Column(String(100), nullable=True)
    ip_address = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(1000), nullable=True)
    page_url = Column(String(1000), nullable=True)
    properties = Column(JSONB, nullable=False, server_default="{}")
    value = Column(Float, nullable=True)  # Numeric value for the event
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflows.id"), nullable=True)
    country = Column(String(2), nullable=True)  # ISO country code
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    device_type = Column(String(20), nullable=True)  # mobile, desktop, tablet
    os = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    screen_resolution = Column(String(20), nullable=True)  # 1920x1080
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="analytics_events")
    workspace = relationship("Workspace", back_populates="analytics_events")
    project = relationship("WorkspaceProject", back_populates="analytics_events")
    workflow = relationship("Workflow", back_populates="analytics_events")
    tenant = relationship("Tenant", back_populates="analytics_events")

    def __str__(self):
        return f"AnalyticsEvent({self.category}:{self.action}, user={self.user_id})"

    @property
    def event_full_name(self):
        """Get full event name"""
        if self.label:
            return f"{self.category}:{self.action}:{self.label}"
        return f"{self.category}:{self.action}"

    @property
    def location_display(self):
        """Get human-readable location"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.region:
            parts.append(self.region)
        if self.country:
            parts.append(self.country.upper())
        
        return ", ".join(parts) if parts else "Unknown"

    @property
    def device_info(self):
        """Get device information summary"""
        info = {}
        if self.device_type:
            info["type"] = self.device_type
        if self.os:
            info["os"] = self.os
        if self.browser:
            info["browser"] = self.browser
        if self.screen_resolution:
            info["resolution"] = self.screen_resolution
        return info

    @property
    def is_conversion_event(self):
        """Check if this is a conversion event"""
        conversion_actions = [
            "purchase", "signup", "subscribe", "upgrade", 
            "download", "install", "complete"
        ]
        return self.action.lower() in conversion_actions

    @property
    def is_engagement_event(self):
        """Check if this is an engagement event"""
        engagement_actions = [
            "click", "view", "scroll", "hover", "focus",
            "play", "pause", "share", "like", "comment"
        ]
        return self.action.lower() in engagement_actions

    def get_property(self, key, default=None):
        """Get a specific property value"""
        if not self.properties:
            return default
        return self.properties.get(key, default)

    def set_property(self, key, value):
        """Set a property value"""
        if not self.properties:
            self.properties = {}
        self.properties[key] = value
        self.updated_at = func.current_timestamp()

    def add_custom_dimension(self, dimension_name, value):
        """Add custom dimension to event"""
        if not self.properties:
            self.properties = {}
        
        if "custom_dimensions" not in self.properties:
            self.properties["custom_dimensions"] = {}
        
        self.properties["custom_dimensions"][dimension_name] = value
        self.updated_at = func.current_timestamp()

    @classmethod
    def track_event(cls, session, event_type, category, action, user_id=None, 
                   project_id=None, properties=None, value=None, **kwargs):
        """Track a new analytics event"""
        import uuid
        
        event = cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            category=category,
            action=action,
            user_id=user_id,
            project_id=project_id,
            properties=properties or {},
            value=value,
            timestamp=func.now(),
            **kwargs
        )
        
        session.add(event)
        return event

    @classmethod
    def get_events_by_user(cls, session, user_id, limit=100, category=None):
        """Get events for a specific user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        
        if category:
            query = query.filter(cls.category == category)
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_events_by_project(cls, session, project_id, limit=100, 
                             start_date=None, end_date=None):
        """Get events for a specific project"""
        query = session.query(cls).filter(cls.project_id == project_id)
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_conversion_events(cls, session, tenant_id=None, start_date=None, end_date=None):
        """Get conversion events"""
        conversion_actions = [
            "purchase", "signup", "subscribe", "upgrade", 
            "download", "install", "complete"
        ]
        
        query = session.query(cls).filter(cls.action.in_(conversion_actions))
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        
        return query.order_by(cls.timestamp.desc()).all()

    @classmethod
    def get_event_counts_by_category(cls, session, start_date=None, end_date=None, tenant_id=None):
        """Get event counts grouped by category"""
        query = session.query(cls.category, func.count(cls.id).label('count'))
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        
        return query.group_by(cls.category).order_by(func.count(cls.id).desc()).all()

    @classmethod
    def get_unique_users_count(cls, session, start_date=None, end_date=None, tenant_id=None):
        """Get count of unique users"""
        query = session.query(func.count(func.distinct(cls.user_id)))
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        
        return query.scalar() or 0

    @classmethod
    def get_events_by_timeframe(cls, session, timeframe="day", limit=30, tenant_id=None):
        """Get events grouped by timeframe"""
        if timeframe == "hour":
            time_trunc = func.date_trunc('hour', cls.timestamp)
        elif timeframe == "day":
            time_trunc = func.date_trunc('day', cls.timestamp)
        elif timeframe == "week":
            time_trunc = func.date_trunc('week', cls.timestamp)
        elif timeframe == "month":
            time_trunc = func.date_trunc('month', cls.timestamp)
        else:
            time_trunc = func.date_trunc('day', cls.timestamp)
        
        query = session.query(
            time_trunc.label('period'),
            func.count(cls.id).label('event_count'),
            func.count(func.distinct(cls.user_id)).label('unique_users')
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.group_by(time_trunc).order_by(time_trunc.desc()).limit(limit).all()
