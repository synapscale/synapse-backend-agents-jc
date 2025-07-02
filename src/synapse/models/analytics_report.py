"""Analytics Report Model"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AnalyticsReport(Base):
    """Analytics reports and scheduled reporting"""
    
    __tablename__ = "analytics_reports"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_query = Column("query", JSONB, nullable=False)
    schedule = Column(String(50), nullable=True)  # cron expression or frequency
    owner_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="analytics_reports")
    tenant = relationship("Tenant", back_populates="analytics_reports")
    executions = relationship("ReportExecution", back_populates="report")

    def __str__(self):
        return f"AnalyticsReport(name={self.name}, active={self.is_active})"

    @property
    def is_scheduled(self):
        """Check if report is scheduled"""
        return self.schedule is not None and self.schedule.strip() != ""

    @property
    def schedule_display(self):
        """Get human-readable schedule"""
        if not self.schedule:
            return "Manual"
        
        # Common schedule patterns
        schedule_mappings = {
            "0 0 * * *": "Daily at midnight",
            "0 9 * * *": "Daily at 9 AM",
            "0 0 * * 0": "Weekly on Sunday",
            "0 0 1 * *": "Monthly on 1st",
            "0 */6 * * *": "Every 6 hours",
            "*/30 * * * *": "Every 30 minutes",
            "hourly": "Every hour",
            "daily": "Every day",
            "weekly": "Every week",
            "monthly": "Every month"
        }
        
        return schedule_mappings.get(self.schedule, self.schedule)

    @property
    def query_summary(self):
        """Get summary of report query"""
        if not self.query:
            return "No query defined"
        
        summary_parts = []
        
        # Extract key information from query
        if "data_source" in self.query:
            summary_parts.append(f"Source: {self.query['data_source']}")
        
        if "metrics" in self.query and isinstance(self.query["metrics"], list):
            metric_count = len(self.query["metrics"])
            summary_parts.append(f"Metrics: {metric_count}")
        
        if "filters" in self.query and isinstance(self.query["filters"], list):
            filter_count = len(self.query["filters"])
            summary_parts.append(f"Filters: {filter_count}")
        
        if "date_range" in self.query:
            date_range = self.query["date_range"]
            if isinstance(date_range, dict):
                period = date_range.get("period", "custom")
                summary_parts.append(f"Period: {period}")
        
        return " | ".join(summary_parts) if summary_parts else "Custom query"

    @property
    def metrics_list(self):
        """Get list of metrics in the report"""
        if not self.query or "metrics" not in self.query:
            return []
        
        metrics = self.query["metrics"]
        if isinstance(metrics, list):
            return metrics
        return []

    def activate(self):
        """Activate the report"""
        self.is_active = True
        self.updated_at = func.now()

    def deactivate(self):
        """Deactivate the report"""
        self.is_active = False
        self.updated_at = func.now()

    def update_query(self, new_query):
        """Update report query"""
        self.query = new_query
        self.updated_at = func.now()

    def update_schedule(self, new_schedule):
        """Update report schedule"""
        self.schedule = new_schedule
        self.updated_at = func.now()

    def add_metric(self, metric_name, aggregation="sum", filters=None):
        """Add a metric to the report"""
        if not self.query:
            self.query = {"metrics": []}
        elif "metrics" not in self.query:
            self.query["metrics"] = []
        
        metric_config = {
            "name": metric_name,
            "aggregation": aggregation,
            "filters": filters or {}
        }
        
        self.query["metrics"].append(metric_config)
        self.updated_at = func.now()

    def remove_metric(self, metric_name):
        """Remove a metric from the report"""
        if not self.query or "metrics" not in self.query:
            return False
        
        original_count = len(self.query["metrics"])
        self.query["metrics"] = [
            m for m in self.query["metrics"] 
            if m.get("name") != metric_name
        ]
        
        if len(self.query["metrics"]) < original_count:
            self.updated_at = func.now()
            return True
        return False

    def set_date_range(self, start_date=None, end_date=None, period=None):
        """Set date range for the report"""
        if not self.query:
            self.query = {}
        
        if period:
            self.query["date_range"] = {"period": period}
        elif start_date and end_date:
            self.query["date_range"] = {
                "start": start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date,
                "end": end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date
            }
        
        self.updated_at = func.now()

    def add_filter(self, field, operator, value):
        """Add a filter to the report"""
        if not self.query:
            self.query = {"filters": []}
        elif "filters" not in self.query:
            self.query["filters"] = []
        
        filter_config = {
            "field": field,
            "operator": operator,
            "value": value
        }
        
        self.query["filters"].append(filter_config)
        self.updated_at = func.now()

    def remove_filter(self, field):
        """Remove a filter from the report"""
        if not self.query or "filters" not in self.query:
            return False
        
        original_count = len(self.query["filters"])
        self.query["filters"] = [
            f for f in self.query["filters"] 
            if f.get("field") != field
        ]
        
        if len(self.query["filters"]) < original_count:
            self.updated_at = func.now()
            return True
        return False

    @classmethod
    def get_active_reports(cls, session, owner_id=None, tenant_id=None):
        """Get active reports"""
        query = session.query(cls).filter(cls.is_active.is_(True))
        
        if owner_id:
            query = query.filter(cls.owner_id == owner_id)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_scheduled_reports(cls, session, tenant_id=None):
        """Get scheduled reports that are active"""
        query = session.query(cls).filter(
            cls.is_active.is_(True),
            cls.schedule.isnot(None),
            cls.schedule != ""
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.all()

    @classmethod
    def get_user_reports(cls, session, user_id, include_inactive=False):
        """Get reports for a specific user"""
        query = session.query(cls).filter(cls.owner_id == user_id)
        
        if not include_inactive:
            query = query.filter(cls.is_active.is_(True))
        
        return query.order_by(cls.updated_at.desc()).all()

    @classmethod
    def search_reports(cls, session, search_term, tenant_id=None, user_id=None):
        """Search reports by name or description"""
        query = session.query(cls).filter(
            cls.name.ilike(f"%{search_term}%") |
            cls.description.ilike(f"%{search_term}%")
        ).filter(cls.is_active.is_(True))
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if user_id:
            query = query.filter(cls.owner_id == user_id)
        
        return query.order_by(cls.updated_at.desc()).all()

    @classmethod
    def get_reports_by_metric(cls, session, metric_name, tenant_id=None):
        """Get reports that include a specific metric"""
        query = session.query(cls).filter(
            cls.is_active.is_(True),
            cls.query.op('?')('metrics')
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        reports = query.all()
        
        # Filter reports that actually contain the metric
        matching_reports = []
        for report in reports:
            metrics = report.query.get("metrics", [])
            for metric in metrics:
                if isinstance(metric, dict) and metric.get("name") == metric_name:
                    matching_reports.append(report)
                    break
        
        return matching_reports

    @classmethod
    def create_report(cls, session, name, query, owner_id, description=None, 
                     schedule=None, tenant_id=None):
        """Create a new analytics report"""
        report = cls(
            name=name,
            description=description,
            query=query,
            schedule=schedule,
            owner_id=owner_id,
            tenant_id=tenant_id,
            created_at=func.now(),
            updated_at=func.now()
        )
        
        session.add(report)
        return report

    def get_recent_executions(self, session, limit=10):
        """Get recent executions of this report"""
        from synapse.models.report_execution import ReportExecution
        
        return session.query(ReportExecution).filter(
            ReportExecution.report_id == self.id
        ).order_by(ReportExecution.started_at.desc()).limit(limit).all()

    def get_execution_stats(self, session, days=30):
        """Get execution statistics for this report"""
        from synapse.models.report_execution import ReportExecution
        
        cutoff_date = func.now() - func.interval(f'{days} days')
        
        executions = session.query(ReportExecution).filter(
            ReportExecution.report_id == self.id,
            ReportExecution.started_at >= cutoff_date
        ).all()
        
        stats = {
            "total": len(executions),
            "successful": len([e for e in executions if e.status == "completed"]),
            "failed": len([e for e in executions if e.status == "failed"]),
            "avg_duration": 0
        }
        
        # Calculate average duration for completed executions
        completed_executions = [e for e in executions if e.status == "completed" and e.execution_time_ms]
        if completed_executions:
            avg_duration_ms = sum(e.execution_time_ms for e in completed_executions) / len(completed_executions)
            stats["avg_duration"] = avg_duration_ms / 1000  # Convert to seconds
        
        return stats
