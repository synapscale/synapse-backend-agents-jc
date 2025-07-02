"""Node Execution Model"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class NodeExecution(Base):
    """Individual node execution tracking within workflows"""
    
    __tablename__ = "node_executions"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(36), nullable=True)
    workflow_execution_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_executions.id"), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.nodes.id"), nullable=False)
    node_key = Column(String(255), nullable=False)
    node_type = Column(String(100), nullable=False)
    node_name = Column(String(255), nullable=True)
    execution_order = Column(Integer, nullable=False)
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    config_data = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    execution_log = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    debug_info = Column(JSONB, nullable=True)
    retry_count = Column(Integer, nullable=True)
    max_retries = Column(Integer, nullable=True)
    retry_delay = Column(Integer, nullable=True)  # seconds
    dependencies = Column(JSONB, nullable=True)
    dependents = Column(JSONB, nullable=True)
    execution_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    workflow_execution = relationship("WorkflowExecution", back_populates="node_executions")
    node = relationship("Node", back_populates="executions")
    tenant = relationship("Tenant", back_populates="node_executions")

    def __str__(self):
        return f"NodeExecution({self.node_name or self.node_key}, order={self.execution_order})"

    @property
    def status(self):
        """Get execution status"""
        if self.error_message:
            return "failed"
        elif self.completed_at:
            return "completed"
        elif self.started_at:
            return "running"
        else:
            return "pending"

    @property
    def is_completed(self):
        """Check if execution is completed"""
        return self.completed_at is not None

    @property
    def is_running(self):
        """Check if execution is running"""
        return self.started_at is not None and self.completed_at is None

    @property
    def is_failed(self):
        """Check if execution failed"""
        return self.error_message is not None

    @property
    def is_pending(self):
        """Check if execution is pending"""
        return self.started_at is None

    @property
    def duration_seconds(self):
        """Get duration in seconds"""
        if self.duration_ms:
            return self.duration_ms / 1000
        elif self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def duration_display(self):
        """Get human-readable duration"""
        duration = self.duration_seconds
        if not duration:
            return "N/A"
        
        if duration < 1:
            return f"{duration*1000:.0f}ms"
        elif duration < 60:
            return f"{duration:.1f}s"
        else:
            return f"{duration/60:.1f}m"

    @property
    def can_retry(self):
        """Check if execution can be retried"""
        if not self.max_retries:
            return False
        return (self.retry_count or 0) < self.max_retries

    def start_execution(self):
        """Mark execution as started"""
        self.started_at = func.now()
        self.updated_at = func.now()

    def complete_execution(self, output_data=None, duration_ms=None):
        """Mark execution as completed"""
        self.completed_at = func.now()
        if output_data is not None:
            self.output_data = output_data
        if duration_ms is not None:
            self.duration_ms = duration_ms
        elif self.started_at:
            # Calculate duration
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_ms = int(duration * 1000)
        self.updated_at = func.now()

    def fail_execution(self, error_message, error_details=None):
        """Mark execution as failed"""
        self.completed_at = func.now()
        self.error_message = error_message
        if error_details:
            self.error_details = error_details
        
        # Calculate duration even for failed executions
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_ms = int(duration * 1000)
        
        self.updated_at = func.now()

    def retry_execution(self):
        """Retry the execution"""
        if not self.can_retry:
            return False
        
        self.retry_count = (self.retry_count or 0) + 1
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.error_details = None
        self.output_data = None
        self.duration_ms = None
        self.updated_at = func.now()
        return True

    def add_log_entry(self, message, level="info"):
        """Add entry to execution log"""
        import datetime
        
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
        
        if self.execution_log:
            self.execution_log += log_entry
        else:
            self.execution_log = log_entry
        
        self.updated_at = func.now()

    def get_input_value(self, key, default=None):
        """Get input data value"""
        if not self.input_data:
            return default
        return self.input_data.get(key, default)

    def get_output_value(self, key, default=None):
        """Get output data value"""
        if not self.output_data:
            return default
        return self.output_data.get(key, default)

    def set_debug_info(self, key, value):
        """Set debug information"""
        if not self.debug_info:
            self.debug_info = {}
        self.debug_info[key] = value
        self.updated_at = func.now()

    @classmethod
    def create_execution(cls, session, workflow_execution_id, node_id, node_key, 
                        node_type, execution_order, input_data=None, config_data=None,
                        node_name=None, max_retries=3, tenant_id=None):
        """Create a new node execution"""
        import uuid
        
        execution = cls(
            execution_id=str(uuid.uuid4()),
            workflow_execution_id=workflow_execution_id,
            node_id=node_id,
            node_key=node_key,
            node_type=node_type,
            node_name=node_name,
            execution_order=execution_order,
            input_data=input_data,
            config_data=config_data,
            retry_count=0,
            max_retries=max_retries,
            tenant_id=tenant_id,
            created_at=func.now()
        )
        
        session.add(execution)
        return execution

    @classmethod
    def get_workflow_executions(cls, session, workflow_execution_id):
        """Get all node executions for a workflow execution"""
        return session.query(cls).filter(
            cls.workflow_execution_id == workflow_execution_id
        ).order_by(cls.execution_order.asc()).all()

    @classmethod
    def get_node_executions(cls, session, node_id, limit=50):
        """Get executions for a specific node"""
        return session.query(cls).filter(
            cls.node_id == node_id
        ).order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_failed_executions(cls, session, workflow_execution_id=None, tenant_id=None):
        """Get failed node executions"""
        query = session.query(cls).filter(cls.error_message.isnot(None))
        
        if workflow_execution_id:
            query = query.filter(cls.workflow_execution_id == workflow_execution_id)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_execution_stats(cls, session, workflow_execution_id=None, node_id=None, days=30):
        """Get execution statistics"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(cls.created_at >= cutoff_date)
        
        if workflow_execution_id:
            query = query.filter(cls.workflow_execution_id == workflow_execution_id)
        if node_id:
            query = query.filter(cls.node_id == node_id)
        
        executions = query.all()
        
        stats = {
            "total": len(executions),
            "completed": len([e for e in executions if e.is_completed and not e.is_failed]),
            "failed": len([e for e in executions if e.is_failed]),
            "running": len([e for e in executions if e.is_running]),
            "pending": len([e for e in executions if e.is_pending]),
            "avg_duration": 0,
            "success_rate": 0
        }
        
        # Calculate averages
        completed_executions = [e for e in executions if e.is_completed]
        if completed_executions:
            durations = [e.duration_ms for e in completed_executions if e.duration_ms]
            if durations:
                stats["avg_duration"] = sum(durations) / len(durations) / 1000  # Convert to seconds
        
        # Calculate success rate
        finished_executions = [e for e in executions if e.is_completed]
        if finished_executions:
            successful = [e for e in finished_executions if not e.is_failed]
            stats["success_rate"] = (len(successful) / len(finished_executions)) * 100
        
        return stats

    @classmethod
    def get_execution_timeline(cls, session, workflow_execution_id):
        """Get execution timeline for visualization"""
        executions = cls.get_workflow_executions(session, workflow_execution_id)
        
        timeline = []
        for execution in executions:
            timeline.append({
                "id": execution.id,
                "node_name": execution.node_name or execution.node_key,
                "node_type": execution.node_type,
                "execution_order": execution.execution_order,
                "status": execution.status,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "duration_ms": execution.duration_ms,
                "error_message": execution.error_message
            })
        
        return timeline

    @classmethod
    def get_slowest_nodes(cls, session, limit=10, days=30, tenant_id=None):
        """Get slowest executing nodes"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(
            cls.node_id,
            cls.node_type,
            func.avg(cls.duration_ms).label('avg_duration'),
            func.count(cls.id).label('execution_count')
        ).filter(
            cls.created_at >= cutoff_date,
            cls.duration_ms.isnot(None),
            cls.is_completed.is_(True)
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.group_by(cls.node_id, cls.node_type).order_by(
            func.avg(cls.duration_ms).desc()
        ).limit(limit).all()

    @classmethod
    def cleanup_old_executions(cls, session, days=90, tenant_id=None):
        """Clean up old execution records"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(cls.created_at < cutoff_date)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        old_executions = query.all()
        for execution in old_executions:
            session.delete(execution)
        
        return len(old_executions)
