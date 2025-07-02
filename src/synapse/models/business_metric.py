"""Business Metric Model"""

from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class BusinessMetric(Base):
    """Business metrics and KPIs tracking"""
    
    __tablename__ = "business_metrics"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    total_users = Column(Integer, nullable=False)
    new_users = Column(Integer, nullable=False)
    active_users = Column(Integer, nullable=False)
    churned_users = Column(Integer, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    avg_session_duration = Column(Float, nullable=False)
    total_page_views = Column(Integer, nullable=False)
    bounce_rate = Column(Float, nullable=False)
    workflows_created = Column(Integer, nullable=False)
    workflows_executed = Column(Integer, nullable=False)
    components_published = Column(Integer, nullable=False)
    components_downloaded = Column(Integer, nullable=False)
    workspaces_created = Column(Integer, nullable=False)
    teams_formed = Column(Integer, nullable=False)
    collaborative_sessions = Column(Integer, nullable=False)
    total_revenue = Column(Float, nullable=False)
    recurring_revenue = Column(Float, nullable=False)
    marketplace_revenue = Column(Float, nullable=False)
    avg_revenue_per_user = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    avg_response_time = Column(Float, nullable=False)
    uptime_percentage = Column(Float, nullable=False)
    customer_satisfaction = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="business_metrics")

    def __str__(self):
        return f"BusinessMetric({self.period_type}, {self.date.date()}, users={self.total_users})"

    @property
    def user_growth_rate(self):
        """Calculate user growth rate as percentage"""
        if self.total_users == 0:
            return 0.0
        return (self.new_users / self.total_users) * 100

    @property
    def churn_rate(self):
        """Calculate churn rate as percentage"""
        if self.total_users == 0:
            return 0.0
        return (self.churned_users / self.total_users) * 100

    @property
    def user_engagement_score(self):
        """Calculate user engagement score (0-100)"""
        # Normalize metrics and combine into engagement score
        session_score = min(self.avg_session_duration / 1800, 1) * 25  # 30 min = max
        activity_score = min(self.workflows_executed / 100, 1) * 25   # 100 = max
        collaboration_score = min(self.collaborative_sessions / 50, 1) * 25  # 50 = max
        retention_score = max(0, (1 - self.churn_rate / 100)) * 25
        
        return session_score + activity_score + collaboration_score + retention_score

    @property
    def revenue_health_score(self):
        """Calculate revenue health score (0-100)"""
        # Weight recurring revenue higher
        recurring_weight = 0.7
        marketplace_weight = 0.3
        
        total_possible = self.total_revenue
        if total_possible == 0:
            return 0.0
        
        recurring_score = (self.recurring_revenue / total_possible) * recurring_weight * 100
        marketplace_score = (self.marketplace_revenue / total_possible) * marketplace_weight * 100
        
        return min(100, recurring_score + marketplace_score)

    @property
    def system_health_score(self):
        """Calculate system health score (0-100)"""
        uptime_score = self.uptime_percentage * 0.4
        error_score = max(0, (1 - self.error_rate / 10)) * 30  # 10% error = 0 score
        response_score = max(0, (1 - self.avg_response_time / 5000)) * 30  # 5s = 0 score
        
        return min(100, uptime_score + error_score + response_score)

    @property
    def formatted_metrics(self):
        """Get formatted version of key metrics"""
        return {
            "total_users": f"{self.total_users:,}",
            "new_users": f"{self.new_users:,}",
            "active_users": f"{self.active_users:,}",
            "total_revenue": f"${self.total_revenue:,.2f}",
            "avg_revenue_per_user": f"${self.avg_revenue_per_user:.2f}",
            "bounce_rate": f"{self.bounce_rate:.1f}%",
            "error_rate": f"{self.error_rate:.2f}%",
            "uptime": f"{self.uptime_percentage:.2f}%",
            "avg_session_duration": f"{self.avg_session_duration/60:.1f}m"
        }

    @classmethod
    def record_metrics(cls, session, date, period_type, metrics_data, tenant_id=None):
        """Record business metrics for a period"""
        metric = cls(
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
    def get_metrics_by_period(cls, session, period_type, start_date=None, end_date=None, 
                             tenant_id=None, limit=100):
        """Get metrics for a specific period type"""
        query = session.query(cls).filter(cls.period_type == period_type)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if start_date:
            query = query.filter(cls.date >= start_date)
        if end_date:
            query = query.filter(cls.date <= end_date)
        
        return query.order_by(cls.date.desc()).limit(limit).all()

    @classmethod
    def get_latest_metrics(cls, session, period_type="daily", tenant_id=None):
        """Get the latest metrics for a period"""
        query = session.query(cls).filter(cls.period_type == period_type)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.date.desc()).first()

    @classmethod
    def get_metrics_trend(cls, session, metric_name, period_type="daily", 
                         periods=30, tenant_id=None):
        """Get trend for a specific metric"""
        query = session.query(cls.date, getattr(cls, metric_name)).filter(
            cls.period_type == period_type
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.date.desc()).limit(periods).all()

    @classmethod
    def calculate_growth_rate(cls, session, metric_name, period_type="daily", 
                             periods=2, tenant_id=None):
        """Calculate growth rate for a metric"""
        trend = cls.get_metrics_trend(session, metric_name, period_type, periods, tenant_id)
        
        if len(trend) < 2:
            return 0.0
        
        current_value = float(trend[0][1]) if trend[0][1] else 0
        previous_value = float(trend[1][1]) if trend[1][1] else 0
        
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        
        return ((current_value - previous_value) / previous_value) * 100

    @classmethod
    def get_summary_stats(cls, session, period_type="daily", days=30, tenant_id=None):
        """Get summary statistics for the last N days"""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        metrics = cls.get_metrics_by_period(
            session, period_type, start_date, end_date, tenant_id
        )
        
        if not metrics:
            return {}
        
        # Calculate averages and totals
        total_metrics = len(metrics)
        
        summary = {
            "period": f"Last {days} days",
            "data_points": total_metrics,
            "averages": {
                "total_users": sum(m.total_users for m in metrics) / total_metrics,
                "active_users": sum(m.active_users for m in metrics) / total_metrics,
                "total_revenue": sum(m.total_revenue for m in metrics) / total_metrics,
                "avg_session_duration": sum(m.avg_session_duration for m in metrics) / total_metrics,
                "error_rate": sum(m.error_rate for m in metrics) / total_metrics,
                "uptime_percentage": sum(m.uptime_percentage for m in metrics) / total_metrics,
            },
            "totals": {
                "new_users": sum(m.new_users for m in metrics),
                "workflows_created": sum(m.workflows_created for m in metrics),
                "workflows_executed": sum(m.workflows_executed for m in metrics),
                "total_revenue": sum(m.total_revenue for m in metrics),
            }
        }
        
        return summary

    @classmethod
    def get_kpi_dashboard(cls, session, tenant_id=None):
        """Get KPI dashboard data"""
        latest_daily = cls.get_latest_metrics(session, "daily", tenant_id)
        latest_monthly = cls.get_latest_metrics(session, "monthly", tenant_id)
        
        if not latest_daily:
            return {}
        
        # Calculate growth rates
        user_growth = cls.calculate_growth_rate(session, "total_users", "daily", 7, tenant_id)
        revenue_growth = cls.calculate_growth_rate(session, "total_revenue", "monthly", 3, tenant_id)
        
        return {
            "current_metrics": latest_daily.formatted_metrics,
            "scores": {
                "user_engagement": latest_daily.user_engagement_score,
                "revenue_health": latest_daily.revenue_health_score,
                "system_health": latest_daily.system_health_score,
            },
            "growth_rates": {
                "user_growth_7d": user_growth,
                "revenue_growth_3m": revenue_growth,
            },
            "monthly_summary": latest_monthly.formatted_metrics if latest_monthly else {}
        }
