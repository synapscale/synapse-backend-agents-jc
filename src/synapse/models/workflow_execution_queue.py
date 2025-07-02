"""Workflow Execution Queue Model"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkflowExecutionQueue(Base):
    """Queue management for workflow executions"""
    
    __tablename__ = "workflow_execution_queue"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    queue_id = Column(String(36), nullable=True)
    workflow_execution_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_executions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    priority = Column(Integer, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=True)
    worker_id = Column(String(100), nullable=True)
    max_execution_time = Column(Integer, nullable=True)  # seconds
    retry_count = Column(Integer, nullable=True)
    max_retries = Column(Integer, nullable=True)
    queue_metadata = Column("meta_data", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    workflow_execution = relationship("WorkflowExecution", back_populates="queue_entries")
    user = relationship("User", back_populates="workflow_queue_entries")
    tenant = relationship("Tenant", back_populates="workflow_execution_queue")

    def __str__(self):
        return f"WorkflowExecutionQueue(id={self.id}, status={self.status}, priority={self.priority})"

    @property
    def is_pending(self):
        """Check if execution is pending"""
        return self.status == "pending"

    @property
    def is_running(self):
        """Check if execution is running"""
        return self.status == "running"

    @property
    def is_completed(self):
        """Check if execution is completed"""
        return self.status in ["completed", "failed", "cancelled"]

    @property
    def is_scheduled(self):
        """Check if execution is scheduled for future"""
        if not self.scheduled_at:
            return False
        return self.scheduled_at > func.now()

    @property
    def is_overdue(self):
        """Check if scheduled execution is overdue"""
        if not self.scheduled_at or self.status != "pending":
            return False
        return self.scheduled_at < func.now()

    @property
    def is_timed_out(self):
        """Check if execution has timed out"""
        if not self.started_at or not self.max_execution_time:
            return False
        
        from datetime import datetime, timedelta
        timeout_at = self.started_at + timedelta(seconds=self.max_execution_time)
        return datetime.now() > timeout_at and self.status == "running"

    @property
    def wait_time_seconds(self):
        """Get wait time in queue (seconds)"""
        if not self.started_at:
            return None
        
        start_time = self.scheduled_at or self.created_at
        if not start_time:
            return None
        
        return (self.started_at - start_time).total_seconds()

    @property
    def execution_duration_seconds(self):
        """Get execution duration (seconds)"""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or func.now()
        return (end_time - self.started_at).total_seconds()

    @property
    def can_retry(self):
        """Check if execution can be retried"""
        if not self.max_retries:
            return False
        return (self.retry_count or 0) < self.max_retries

    def start_execution(self, worker_id=None):
        """Mark execution as started"""
        self.status = "running"
        self.started_at = func.now()
        if worker_id:
            self.worker_id = worker_id
        self.updated_at = func.now()

    def complete_execution(self, success=True):
        """Mark execution as completed"""
        self.status = "completed" if success else "failed"
        self.completed_at = func.now()
        self.updated_at = func.now()

    def cancel_execution(self):
        """Cancel the execution"""
        self.status = "cancelled"
        self.completed_at = func.now()
        self.updated_at = func.now()

    def retry_execution(self):
        """Retry the execution"""
        if not self.can_retry:
            return False
        
        self.retry_count = (self.retry_count or 0) + 1
        self.status = "pending"
        self.started_at = None
        self.completed_at = None
        self.worker_id = None
        self.updated_at = func.now()
        return True

    def update_metadata(self, key, value):
        """Update queue metadata"""
        if not self.queue_metadata:
            self.queue_metadata = {}
        self.queue_metadata[key] = value
        self.updated_at = func.now()

    def get_metadata(self, key, default=None):
        """Get metadata value"""
        if not self.queue_metadata:
            return default
        return self.queue_metadata.get(key, default)

    @classmethod
    def enqueue_execution(cls, session, workflow_execution_id, user_id, 
                         priority=0, scheduled_at=None, max_execution_time=None,
                         max_retries=3, queue_metadata=None, tenant_id=None):
        """Add execution to queue"""
        import uuid
        
        queue_entry = cls(
            queue_id=str(uuid.uuid4()),
            workflow_execution_id=workflow_execution_id,
            user_id=user_id,
            priority=priority,
            scheduled_at=scheduled_at,
            status="pending",
            max_execution_time=max_execution_time,
            retry_count=0,
            max_retries=max_retries,
            queue_metadata=queue_metadata,
            tenant_id=tenant_id,
            created_at=func.now(),
            updated_at=func.now()
        )
        
        session.add(queue_entry)
        return queue_entry

    @classmethod
    def get_next_pending(cls, session, worker_id=None, tenant_id=None):
        """Get next pending execution from queue"""
        query = session.query(cls).filter(
            cls.status == "pending"
        ).filter(
            (cls.scheduled_at.is_(None)) | 
            (cls.scheduled_at <= func.now())
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        # Order by priority (higher first) then by created_at
        return query.order_by(
            cls.priority.desc(),
            cls.created_at.asc()
        ).first()

    @classmethod
    def get_pending_count(cls, session, tenant_id=None):
        """Get count of pending executions"""
        query = session.query(cls).filter(cls.status == "pending")
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.count()

    @classmethod
    def get_running_executions(cls, session, worker_id=None, tenant_id=None):
        """Get running executions"""
        query = session.query(cls).filter(cls.status == "running")
        
        if worker_id:
            query = query.filter(cls.worker_id == worker_id)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.all()

    @classmethod
    def get_user_queue(cls, session, user_id, status=None, limit=50):
        """Get queue entries for a user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_queue_stats(cls, session, tenant_id=None, hours=24):
        """Get queue statistics"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        query = session.query(cls).filter(cls.created_at >= cutoff_time)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        entries = query.all()
        
        stats = {
            "total": len(entries),
            "pending": len([e for e in entries if e.status == "pending"]),
            "running": len([e for e in entries if e.status == "running"]),
            "completed": len([e for e in entries if e.status == "completed"]),
            "failed": len([e for e in entries if e.status == "failed"]),
            "cancelled": len([e for e in entries if e.status == "cancelled"]),
            "avg_wait_time": 0,
            "avg_execution_time": 0
        }
        
        # Calculate averages
        wait_times = [e.wait_time_seconds for e in entries if e.wait_time_seconds]
        if wait_times:
            stats["avg_wait_time"] = sum(wait_times) / len(wait_times)
        
        exec_times = [e.execution_duration_seconds for e in entries if e.execution_duration_seconds]
        if exec_times:
            stats["avg_execution_time"] = sum(exec_times) / len(exec_times)
        
        # Calculate success rate
        completed_entries = [e for e in entries if e.is_completed]
        if completed_entries:
            successful = len([e for e in completed_entries if e.status == "completed"])
            stats["success_rate"] = (successful / len(completed_entries)) * 100
        else:
            stats["success_rate"] = 0
        
        return stats

    @classmethod
    def cleanup_old_entries(cls, session, days=30, tenant_id=None):
        """Clean up old completed queue entries"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(
            cls.completed_at < cutoff_date,
            cls.status.in_(["completed", "failed", "cancelled"])
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        old_entries = query.all()
        for entry in old_entries:
            session.delete(entry)
        
        return len(old_entries)

    @classmethod
    def handle_timeouts(cls, session, tenant_id=None):
        """Handle timed out executions"""
        running_entries = cls.get_running_executions(session, tenant_id=tenant_id)
        timed_out = []
        
        for entry in running_entries:
            if entry.is_timed_out:
                entry.status = "failed"
                entry.completed_at = func.now()
                entry.update_metadata("timeout_reason", "execution_timeout")
                entry.updated_at = func.now()
                timed_out.append(entry)
        
        return timed_out
