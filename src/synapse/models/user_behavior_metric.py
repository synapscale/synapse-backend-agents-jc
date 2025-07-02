"""User Behavior Metric Model"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class UserBehaviorMetric(Base):
    """User behavior tracking and analytics"""
    
    __tablename__ = "user_behavior_metrics"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    session_count = Column(Integer, nullable=False)
    total_session_duration = Column(Integer, nullable=False)  # seconds
    avg_session_duration = Column(Float, nullable=False)  # seconds
    page_views = Column(Integer, nullable=False)
    unique_pages_visited = Column(Integer, nullable=False)
    workflows_created = Column(Integer, nullable=False)
    workflows_executed = Column(Integer, nullable=False)
    components_used = Column(Integer, nullable=False)
    collaborations_initiated = Column(Integer, nullable=False)
    marketplace_purchases = Column(Integer, nullable=False)
    revenue_generated = Column(Float, nullable=False)
    components_published = Column(Integer, nullable=False)
    error_count = Column(Integer, nullable=False)
    support_tickets = Column(Integer, nullable=False)
    feature_requests = Column(Integer, nullable=False)
    engagement_score = Column(Float, nullable=False)  # 0-100
    satisfaction_score = Column(Float, nullable=False)  # 0-100
    value_score = Column(Float, nullable=False)  # 0-100
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="behavior_metrics")
    tenant = relationship("Tenant", back_populates="user_behavior_metrics")

    def __str__(self):
        return f"UserBehaviorMetric(user_id={self.user_id}, {self.period_type}, {self.date.date()})"

    @property
    def formatted_session_duration(self):
        """Get formatted average session duration"""
        duration = self.avg_session_duration
        if duration < 60:
            return f"{duration:.0f}s"
        elif duration < 3600:
            return f"{duration/60:.1f}m"
        else:
            return f"{duration/3600:.1f}h"

    @property
    def activity_level(self):
        """Determine user activity level"""
        if self.engagement_score >= 80:
            return "highly_active"
        elif self.engagement_score >= 60:
            return "active"
        elif self.engagement_score >= 40:
            return "moderately_active"
        elif self.engagement_score >= 20:
            return "low_activity"
        else:
            return "inactive"

    @property
    def user_type(self):
        """Determine user type based on behavior"""
        if self.components_published > 0:
            return "creator"
        elif self.marketplace_purchases > 0:
            return "consumer"
        elif self.collaborations_initiated > 0:
            return "collaborator"
        elif self.workflows_created > 0:
            return "builder"
        else:
            return "viewer"

    @property
    def productivity_score(self):
        """Calculate productivity score (0-100)"""
        # Weighted combination of productivity metrics
        workflow_score = min(self.workflows_created * 10, 30)
        execution_score = min(self.workflows_executed * 5, 25)
        component_score = min(self.components_used * 3, 20)
        collaboration_score = min(self.collaborations_initiated * 8, 25)
        
        return workflow_score + execution_score + component_score + collaboration_score

    @property
    def health_indicators(self):
        """Get user health indicators"""
        return {
            "engagement_level": self.activity_level,
            "satisfaction": "high" if self.satisfaction_score >= 70 else "medium" if self.satisfaction_score >= 40 else "low",
            "productivity": "high" if self.productivity_score >= 70 else "medium" if self.productivity_score >= 40 else "low",
            "error_prone": self.error_count > 10,
            "needs_support": self.support_tickets > 0
        }

    @classmethod
    def record_metrics(cls, session, user_id, date, period_type, metrics_data, tenant_id=None):
        """Record user behavior metrics"""
        metric = cls(
            user_id=user_id,
            date=date,
            period_type=period_type,
            tenant_id=tenant_id,
            created_at=func.now(),
            updated_at=func.now(),
            **metrics_data
        )
        
        session.add(metric)
        return metric

    @classmethod
    def get_user_metrics(cls, session, user_id, period_type="daily", limit=30):
        """Get metrics for a specific user"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.period_type == period_type
        ).order_by(cls.date.desc()).limit(limit).all()

    @classmethod
    def get_engagement_trend(cls, session, user_id, days=30):
        """Get user engagement trend"""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return session.query(cls.date, cls.engagement_score).filter(
            cls.user_id == user_id,
            cls.period_type == "daily",
            cls.date >= start_date,
            cls.date <= end_date
        ).order_by(cls.date.asc()).all()

    @classmethod
    def get_user_segments(cls, session, tenant_id=None, period_type="monthly"):
        """Get user segments based on behavior"""
        query = session.query(cls).filter(cls.period_type == period_type)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        # Get latest metrics for each user
        latest_metrics = query.order_by(cls.user_id, cls.date.desc()).all()
        
        segments = {
            "highly_active": 0,
            "active": 0,
            "moderately_active": 0,
            "low_activity": 0,
            "inactive": 0
        }
        
        user_latest = {}
        for metric in latest_metrics:
            if metric.user_id not in user_latest:
                user_latest[metric.user_id] = metric
        
        for metric in user_latest.values():
            segments[metric.activity_level] += 1
        
        return segments

    @classmethod
    def get_top_performers(cls, session, metric_name="engagement_score", 
                          limit=10, period_type="monthly", tenant_id=None):
        """Get top performing users for a metric"""
        query = session.query(cls).filter(cls.period_type == period_type)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        # Order by the specified metric
        metric_column = getattr(cls, metric_name)
        return query.order_by(metric_column.desc()).limit(limit).all()

    @classmethod
    def calculate_user_churn_risk(cls, session, user_id, days=30):
        """Calculate churn risk for a user"""
        recent_metrics = cls.get_user_metrics(session, user_id, "daily", days)
        
        if not recent_metrics:
            return {"risk_level": "unknown", "score": 0}
        
        # Calculate risk factors
        avg_engagement = sum(m.engagement_score for m in recent_metrics) / len(recent_metrics)
        recent_sessions = sum(m.session_count for m in recent_metrics[-7:]) if len(recent_metrics) >= 7 else 0
        error_rate = sum(m.error_count for m in recent_metrics) / len(recent_metrics)
        support_tickets = sum(m.support_tickets for m in recent_metrics)
        
        # Calculate churn risk score (0-100, higher = more risk)
        engagement_risk = max(0, (50 - avg_engagement) * 2)  # Low engagement = high risk
        activity_risk = max(0, (7 - recent_sessions) * 10)   # Low activity = high risk
        error_risk = min(50, error_rate * 5)                # High errors = high risk
        support_risk = min(25, support_tickets * 5)         # Many tickets = high risk
        
        total_risk = engagement_risk + activity_risk + error_risk + support_risk
        risk_score = min(100, total_risk)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        elif risk_score >= 20:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "risk_level": risk_level,
            "score": risk_score,
            "factors": {
                "engagement": avg_engagement,
                "recent_activity": recent_sessions,
                "error_rate": error_rate,
                "support_tickets": support_tickets
            }
        }

    @classmethod
    def get_cohort_analysis(cls, session, cohort_size="monthly", tenant_id=None):
        """Get cohort analysis data"""
        # This would be a complex query for cohort analysis
        # Simplified version for demonstration
        query = session.query(cls)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        metrics = query.filter(cls.period_type == cohort_size).all()
        
        # Group by user and calculate retention
        user_metrics = {}
        for metric in metrics:
            if metric.user_id not in user_metrics:
                user_metrics[metric.user_id] = []
            user_metrics[metric.user_id].append(metric)
        
        cohort_data = {
            "total_users": len(user_metrics),
            "active_users": len([u for u, m in user_metrics.items() if m[-1].engagement_score > 20]),
            "avg_engagement": sum(m[-1].engagement_score for m in user_metrics.values()) / len(user_metrics)
        }
        
        return cohort_data
