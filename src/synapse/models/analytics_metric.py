"""Analytics Metric Model"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AnalyticsMetric(Base):
    """Analytics metrics storage and tracking"""
    
    __tablename__ = "analytics_metrics"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric, nullable=False)
    dimensions = Column(JSONB, nullable=False, server_default="{}")
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    tenant = relationship("Tenant", back_populates="analytics_metrics")

    def __str__(self):
        return f"AnalyticsMetric({self.metric_name}={self.metric_value})"

    @property
    def metric_display_name(self):
        """Get human-readable metric name"""
        name_mappings = {
            "user_count": "Total Users",
            "active_users": "Active Users",
            "session_duration": "Session Duration",
            "conversion_rate": "Conversion Rate",
            "revenue": "Revenue",
            "error_rate": "Error Rate",
            "response_time": "Response Time",
            "page_views": "Page Views",
            "bounce_rate": "Bounce Rate",
            "retention_rate": "Retention Rate"
        }
        return name_mappings.get(self.metric_name, self.metric_name.replace("_", " ").title())

    @property
    def formatted_value(self):
        """Get formatted metric value based on metric type"""
        value = float(self.metric_value)
        
        # Format based on metric name patterns
        if "rate" in self.metric_name or "percentage" in self.metric_name:
            return f"{value:.2f}%"
        elif "revenue" in self.metric_name or "cost" in self.metric_name:
            return f"${value:,.2f}"
        elif "duration" in self.metric_name or "time" in self.metric_name:
            if value < 60:
                return f"{value:.1f}s"
            elif value < 3600:
                return f"{value/60:.1f}m"
            else:
                return f"{value/3600:.1f}h"
        elif "count" in self.metric_name or self.metric_name.endswith("_users"):
            return f"{int(value):,}"
        else:
            return f"{value:.2f}"

    @property
    def dimension_summary(self):
        """Get summary of dimensions"""
        if not self.dimensions:
            return "No dimensions"
        
        summary_parts = []
        for key, value in self.dimensions.items():
            if len(str(value)) > 20:
                summary_parts.append(f"{key}: {str(value)[:17]}...")
            else:
                summary_parts.append(f"{key}: {value}")
        
        return " | ".join(summary_parts)

    def get_dimension(self, key, default=None):
        """Get specific dimension value"""
        if not self.dimensions:
            return default
        return self.dimensions.get(key, default)

    def set_dimension(self, key, value):
        """Set dimension value"""
        if not self.dimensions:
            self.dimensions = {}
        self.dimensions[key] = value
        self.updated_at = func.current_timestamp()

    def add_dimensions(self, new_dimensions):
        """Add multiple dimensions"""
        if not self.dimensions:
            self.dimensions = {}
        self.dimensions.update(new_dimensions)
        self.updated_at = func.current_timestamp()

    @classmethod
    def record_metric(cls, session, metric_name, value, dimensions=None, 
                     timestamp=None, tenant_id=None):
        """Record a new metric value"""
        metric = cls(
            metric_name=metric_name,
            metric_value=value,
            dimensions=dimensions or {},
            timestamp=timestamp or func.now(),
            tenant_id=tenant_id,
            created_at=func.now()
        )
        
        session.add(metric)
        return metric

    @classmethod
    def get_metric_values(cls, session, metric_name, start_date=None, end_date=None, 
                         tenant_id=None, dimensions=None, limit=1000):
        """Get metric values for a specific metric"""
        query = session.query(cls).filter(cls.metric_name == metric_name)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        if dimensions:
            for key, value in dimensions.items():
                query = query.filter(cls.dimensions.op('->>')(key) == str(value))
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_metric_aggregate(cls, session, metric_name, aggregation="avg", 
                           start_date=None, end_date=None, tenant_id=None, dimensions=None):
        """Get aggregated metric value"""
        query = session.query(cls.metric_value).filter(cls.metric_name == metric_name)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        if dimensions:
            for key, value in dimensions.items():
                query = query.filter(cls.dimensions.op('->>')(key) == str(value))
        
        if aggregation == "avg":
            result = query.with_entities(func.avg(cls.metric_value)).scalar()
        elif aggregation == "sum":
            result = query.with_entities(func.sum(cls.metric_value)).scalar()
        elif aggregation == "max":
            result = query.with_entities(func.max(cls.metric_value)).scalar()
        elif aggregation == "min":
            result = query.with_entities(func.min(cls.metric_value)).scalar()
        elif aggregation == "count":
            result = query.count()
        else:
            result = query.with_entities(func.avg(cls.metric_value)).scalar()
        
        return float(result) if result is not None else 0.0

    @classmethod
    def get_metric_trend(cls, session, metric_name, timeframe="day", periods=30, 
                        tenant_id=None, dimensions=None):
        """Get metric trend over time"""
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
            func.avg(cls.metric_value).label('avg_value'),
            func.sum(cls.metric_value).label('sum_value'),
            func.count(cls.metric_value).label('count')
        ).filter(cls.metric_name == metric_name)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if dimensions:
            for key, value in dimensions.items():
                query = query.filter(cls.dimensions.op('->>')(key) == str(value))
        
        return query.group_by(time_trunc).order_by(time_trunc.desc()).limit(periods).all()

    @classmethod
    def get_available_metrics(cls, session, tenant_id=None):
        """Get list of available metric names"""
        query = session.query(cls.metric_name).distinct()
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return [result[0] for result in query.all()]

    @classmethod
    def get_metric_dimensions(cls, session, metric_name, tenant_id=None):
        """Get available dimensions for a metric"""
        query = session.query(cls.dimensions).filter(cls.metric_name == metric_name)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        all_dimensions = {}
        for result in query.all():
            if result[0]:  # dimensions is not null
                for key, value in result[0].items():
                    if key not in all_dimensions:
                        all_dimensions[key] = set()
                    all_dimensions[key].add(str(value))
        
        # Convert sets to lists for JSON serialization
        return {key: list(values) for key, values in all_dimensions.items()}

    @classmethod
    def cleanup_old_metrics(cls, session, days=365, tenant_id=None):
        """Clean up old metric data"""
        cutoff_date = func.now() - func.interval(f'{days} days')
        
        query = session.query(cls).filter(cls.timestamp < cutoff_date)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        old_metrics = query.all()
        
        for metric in old_metrics:
            session.delete(metric)
        
        return len(old_metrics)

    @classmethod
    def get_metric_summary(cls, session, metric_names=None, tenant_id=None, hours=24):
        """Get summary of multiple metrics"""
        cutoff_time = func.now() - func.interval(f'{hours} hours')
        
        query = session.query(cls).filter(cls.timestamp >= cutoff_time)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        if metric_names:
            query = query.filter(cls.metric_name.in_(metric_names))
        
        metrics = query.all()
        
        summary = {}
        for metric in metrics:
            name = metric.metric_name
            if name not in summary:
                summary[name] = {
                    "values": [],
                    "latest": None,
                    "avg": 0,
                    "min": None,
                    "max": None,
                    "count": 0
                }
            
            summary[name]["values"].append(float(metric.metric_value))
            summary[name]["count"] += 1
            
            if summary[name]["latest"] is None or metric.timestamp > summary[name]["latest"]:
                summary[name]["latest"] = metric.timestamp
        
        # Calculate statistics
        for name, data in summary.items():
            values = data["values"]
            if values:
                data["avg"] = sum(values) / len(values)
                data["min"] = min(values)
                data["max"] = max(values)
        
        return summary
