"""
WebhookLog model for tracking webhook events and processing
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from synapse.database import Base


class WebhookLog(Base):
    """
    Model for webhook logs and event tracking
    
    Tracks webhook events from external providers with processing status,
    retry logic, and error handling capabilities.
    """
    
    __tablename__ = "webhook_logs"
    __table_args__ = {"schema": "synapscale_db"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Provider information
    provider_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    event_id = Column(String(255), nullable=True, index=True)
    payload = Column(JSONB, nullable=False)
    headers = Column(JSONB, nullable=True)
    
    # Processing status
    status = Column(String(50), nullable=True, default="pending", index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=True, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=True, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, default=func.now(), onupdate=func.now())
    
    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    def __init__(self, **kwargs):
        """Initialize WebhookLog with defaults"""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()
        if self.status is None:
            self.status = "pending"
        if self.retry_count is None:
            self.retry_count = 0
    
    @property
    def is_pending(self) -> bool:
        """Check if webhook is pending processing"""
        return self.status == "pending"
    
    @property
    def is_processed(self) -> bool:
        """Check if webhook was successfully processed"""
        return self.status == "processed"
    
    @property
    def is_failed(self) -> bool:
        """Check if webhook processing failed"""
        return self.status == "failed"
    
    @property
    def is_retrying(self) -> bool:
        """Check if webhook is in retry state"""
        return self.status == "retrying"
    
    def mark_as_processed(self) -> None:
        """Mark webhook as successfully processed"""
        self.status = "processed"
        self.processed_at = datetime.utcnow()
        self.error_message = None
    
    def mark_as_failed(self, error_message: str) -> None:
        """Mark webhook as failed with error message"""
        self.status = "failed"
        self.error_message = error_message
        self.processed_at = datetime.utcnow()
    
    def mark_as_retrying(self, error_message: str) -> None:
        """Mark webhook for retry with error message"""
        self.status = "retrying"
        self.error_message = error_message
        self.retry_count = (self.retry_count or 0) + 1
    
    def increment_retry(self) -> None:
        """Increment retry count"""
        self.retry_count = (self.retry_count or 0) + 1
    
    def get_payload_field(self, field_name: str, default: Any = None) -> Any:
        """Get specific field from payload"""
        if not self.payload:
            return default
        return self.payload.get(field_name, default)
    
    def get_header_field(self, header_name: str, default: Any = None) -> Any:
        """Get specific header from headers"""
        if not self.headers:
            return default
        return self.headers.get(header_name, default)
    
    @classmethod
    def get_by_event_id(cls, session, event_id: str, provider_id: Optional[uuid.UUID] = None):
        """Get webhook log by event ID and optionally provider ID"""
        query = session.query(cls).filter(cls.event_id == event_id)
        if provider_id:
            query = query.filter(cls.provider_id == provider_id)
        return query.first()
    
    @classmethod
    def get_pending_webhooks(cls, session, limit: int = 100):
        """Get pending webhooks for processing"""
        return session.query(cls).filter(
            cls.status == "pending"
        ).order_by(cls.created_at).limit(limit).all()
    
    @classmethod
    def get_failed_webhooks(cls, session, max_retries: int = 3, limit: int = 100):
        """Get failed webhooks that can be retried"""
        return session.query(cls).filter(
            cls.status.in_(["failed", "retrying"]),
            cls.retry_count < max_retries
        ).order_by(cls.created_at).limit(limit).all()
    
    @classmethod
    def get_by_provider(cls, session, provider_id: uuid.UUID, limit: int = 100):
        """Get webhooks by provider ID"""
        return session.query(cls).filter(
            cls.provider_id == provider_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_event_type(cls, session, event_type: str, limit: int = 100):
        """Get webhooks by event type"""
        return session.query(cls).filter(
            cls.event_type == event_type
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_statistics(cls, session, provider_id: Optional[uuid.UUID] = None, 
                      days_back: int = 30) -> Dict[str, Any]:
        """Get webhook processing statistics"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = session.query(cls).filter(cls.created_at >= cutoff_date)
        
        if provider_id:
            query = query.filter(cls.provider_id == provider_id)
        
        webhooks = query.all()
        
        total = len(webhooks)
        processed = len([w for w in webhooks if w.is_processed])
        failed = len([w for w in webhooks if w.is_failed])
        pending = len([w for w in webhooks if w.is_pending])
        retrying = len([w for w in webhooks if w.is_retrying])
        
        return {
            "total": total,
            "processed": processed,
            "failed": failed,
            "pending": pending,
            "retrying": retrying,
            "success_rate": round((processed / total * 100) if total > 0 else 0, 2),
            "failure_rate": round((failed / total * 100) if total > 0 else 0, 2),
            "average_retries": round(
                sum(w.retry_count or 0 for w in webhooks) / total if total > 0 else 0, 2
            )
        }
    
    @classmethod
    def cleanup_old_logs(cls, session, days_to_keep: int = 90) -> int:
        """Clean up old webhook logs"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted_count = session.query(cls).filter(
            cls.created_at < cutoff_date,
            cls.status.in_(["processed", "failed"])
        ).delete()
        
        return deleted_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert webhook log to dictionary"""
        return {
            "id": str(self.id),
            "provider_id": str(self.provider_id),
            "event_type": self.event_type,
            "event_id": self.event_id,
            "payload": self.payload,
            "headers": self.headers,
            "status": self.status,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None
        }
    
    def __repr__(self):
        return f"<WebhookLog(id={self.id}, event_type={self.event_type}, status={self.status})>" 