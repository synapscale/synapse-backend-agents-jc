"""Custom Report Model"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class CustomReport(Base):
    """User-created custom reports"""
    
    __tablename__ = "custom_reports"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    query_config = Column(JSONB, nullable=False)
    visualization_config = Column(JSONB, nullable=True)
    filters = Column(JSONB, nullable=True)
    is_scheduled = Column(Boolean, nullable=False)
    schedule_config = Column(JSONB, nullable=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    is_public = Column(Boolean, nullable=False)
    shared_with = Column(JSONB, nullable=True)
    cached_data = Column(JSONB, nullable=True)
    cache_expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="custom_reports")
    workspace = relationship("Workspace", back_populates="custom_reports")
    tenant = relationship("Tenant", back_populates="custom_reports")
    # NOTE: Temporarily commented to resolve conflict with AnalyticsReport.executions
    # executions = relationship("ReportExecution", back_populates="report")

    def __str__(self):
        return f"CustomReport(name={self.name}, status={self.status})"

    @property
    def is_active(self):
        """Check if report is active"""
        return self.status == "active"

    @property
    def has_cached_data(self):
        """Check if report has valid cached data"""
        if not self.cached_data or not self.cache_expires_at:
            return False
        return self.cache_expires_at > func.now()

    @property
    def visualization_type(self):
        """Get visualization type"""
        if not self.visualization_config:
            return "table"
        return self.visualization_config.get("type", "table")

    def invalidate_cache(self):
        """Invalidate cached data"""
        self.cached_data = None
        self.cache_expires_at = None
        self.updated_at = func.now()

    def update_cache(self, data, expires_in_hours=24):
        """Update cached data"""
        from datetime import timedelta
        
        self.cached_data = data
        self.cache_expires_at = func.now() + timedelta(hours=expires_in_hours)
        self.updated_at = func.now()

    @classmethod
    def create_report(cls, session, name, query_config, user_id, **kwargs):
        """Create a new custom report"""
        report = cls(
            name=name,
            query_config=query_config,
            user_id=user_id,
            status="active",
            is_scheduled=False,
            is_public=False,
            created_at=func.now(),
            updated_at=func.now(),
            **kwargs
        )
        
        session.add(report)
        return report

    @classmethod
    def get_user_reports(cls, session, user_id, status="active"):
        """Get reports for a user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.updated_at.desc()).all()
