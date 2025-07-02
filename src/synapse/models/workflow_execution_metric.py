"""Workflow Execution Metric Model"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkflowExecutionMetric(Base):
    """Metrics collected during workflow execution"""
    
    __tablename__ = "workflow_execution_metrics"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_execution_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_executions.id"), nullable=False)
    node_execution_id = Column(Integer, nullable=True)
    metric_type = Column(String(100), nullable=False)
    metric_name = Column(String(255), nullable=False)
    value_numeric = Column(Integer, nullable=True)
    value_float = Column(String(50), nullable=True)  # Note: DB stores as varchar
    value_text = Column(Text, nullable=True)
    value_json = Column(JSONB, nullable=True)
    context = Column(String(255), nullable=True)
    tags = Column(JSONB, nullable=True)
    measured_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    workflow_execution = relationship("WorkflowExecution", back_populates="metrics")
    tenant = relationship("Tenant", back_populates="workflow_execution_metrics")

    def __str__(self):
        return f"WorkflowExecutionMetric({self.metric_name}={self.get_value()})"

    @property
    def metric_display_name(self):
        """Get human-readable metric name"""
        name_mappings = {
            "execution_time": "Execution Time",
            "memory_usage": "Memory Usage",
            "cpu_usage": "CPU Usage",
            "network_calls": "Network Calls",
            "data_processed": "Data Processed",
            "error_count": "Error Count",
            "success_rate": "Success Rate",
            "throughput": "Throughput"
        }
        return name_mappings.get(self.metric_name, self.metric_name.replace("_", " ").title())

    def get_value(self):
        """Get the metric value in appropriate type"""
        if self.value_numeric is not None:
            return self.value_numeric
        elif self.value_float is not None:
            try:
                return float(self.value_float)
            except (ValueError, TypeError):
                return self.value_float
        elif self.value_text is not None:
            return self.value_text
        elif self.value_json is not None:
            return self.value_json
        return None

    def set_value(self, value):
        """Set metric value with automatic type detection"""
        # Clear all value fields first
        self.value_numeric = None
        self.value_float = None
        self.value_text = None
        self.value_json = None
        
        if isinstance(value, int):
            self.value_numeric = value
        elif isinstance(value, float):
            self.value_float = str(value)
        elif isinstance(value, str):
            self.value_text = value
        elif isinstance(value, (dict, list)):
            self.value_json = value
        else:
            self.value_text = str(value)

    def get_formatted_value(self):
        """Get formatted value based on metric type"""
        value = self.get_value()
        if value is None:
            return "N/A"
        
        # Format based on metric type and name
        if self.metric_type == "performance":
            if "time" in self.metric_name:
                return self._format_duration(value)
            elif "memory" in self.metric_name:
                return self._format_bytes(value)
            elif "rate" in self.metric_name or "percentage" in self.metric_name:
                return f"{value:.2f}%"
        elif self.metric_type == "count":
            return f"{int(value):,}"
        elif self.metric_type == "size":
            return self._format_bytes(value)
        
        return str(value)

    def _format_duration(self, ms_value):
        """Format duration in milliseconds to human readable"""
        if not isinstance(ms_value, (int, float)):
            return str(ms_value)
        
        if ms_value < 1000:
            return f"{ms_value:.0f}ms"
        elif ms_value < 60000:
            return f"{ms_value/1000:.1f}s"
        else:
            return f"{ms_value/60000:.1f}m"

    def _format_bytes(self, byte_value):
        """Format bytes to human readable"""
        if not isinstance(byte_value, (int, float)):
            return str(byte_value)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if byte_value < 1024:
                return f"{byte_value:.1f}{unit}"
            byte_value /= 1024
        return f"{byte_value:.1f}TB"

    def add_tag(self, key, value):
        """Add a tag to the metric"""
        if not self.tags:
            self.tags = {}
        self.tags[key] = value
        self.updated_at = func.current_timestamp()

    def get_tag(self, key, default=None):
        """Get a tag value"""
        if not self.tags:
            return default
        return self.tags.get(key, default)

    @classmethod
    def record_metric(cls, session, workflow_execution_id, metric_name, value,
                     metric_type="custom", context=None, tags=None, 
                     node_execution_id=None, tenant_id=None):
        """Record a new metric"""
        metric = cls(
            workflow_execution_id=workflow_execution_id,
            node_execution_id=node_execution_id,
            metric_type=metric_type,
            metric_name=metric_name,
            context=context,
            tags=tags,
            tenant_id=tenant_id,
            measured_at=func.now(),
            created_at=func.now()
        )
        
        metric.set_value(value)
        session.add(metric)
        return metric

    @classmethod
    def get_execution_metrics(cls, session, workflow_execution_id, metric_name=None):
        """Get metrics for a workflow execution"""
        query = session.query(cls).filter(cls.workflow_execution_id == workflow_execution_id)
        
        if metric_name:
            query = query.filter(cls.metric_name == metric_name)
        
        return query.order_by(cls.measured_at.asc()).all()

    @classmethod
    def get_node_metrics(cls, session, node_execution_id):
        """Get metrics for a specific node execution"""
        return session.query(cls).filter(
            cls.node_execution_id == node_execution_id
        ).order_by(cls.measured_at.asc()).all()

    @classmethod
    def get_metric_summary(cls, session, workflow_execution_id):
        """Get summary of metrics for an execution"""
        metrics = cls.get_execution_metrics(session, workflow_execution_id)
        
        summary = {
            "total_metrics": len(metrics),
            "metric_types": {},
            "performance": {},
            "errors": 0
        }
        
        for metric in metrics:
            # Count by type
            metric_type = metric.metric_type
            if metric_type not in summary["metric_types"]:
                summary["metric_types"][metric_type] = 0
            summary["metric_types"][metric_type] += 1
            
            # Collect performance metrics
            if metric.metric_type == "performance":
                summary["performance"][metric.metric_name] = metric.get_formatted_value()
            
            # Count errors
            if "error" in metric.metric_name.lower():
                summary["errors"] += 1
        
        return summary

    @classmethod
    def get_metric_trend(cls, session, metric_name, days=30, tenant_id=None):
        """Get trend for a specific metric across executions"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(
            cls.metric_name == metric_name,
            cls.measured_at >= cutoff_date
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.measured_at.asc()).all()

    @classmethod
    def get_average_metric(cls, session, metric_name, days=30, tenant_id=None):
        """Get average value for a metric over time"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(
            cls.metric_name == metric_name,
            cls.measured_at >= cutoff_date,
            cls.value_numeric.isnot(None)
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        metrics = query.all()
        if not metrics:
            return None
        
        total = sum(m.value_numeric for m in metrics)
        return total / len(metrics)

    @classmethod
    def cleanup_old_metrics(cls, session, days=90, tenant_id=None):
        """Clean up old metrics"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(cls.created_at < cutoff_date)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        old_metrics = query.all()
        for metric in old_metrics:
            session.delete(metric)
        
        return len(old_metrics)
