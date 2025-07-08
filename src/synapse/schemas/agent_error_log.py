"""
Schemas para AgentErrorLog
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class AgentErrorLogBase(BaseModel):
    """Base schema for AgentErrorLog"""
    agent_id: UUID4
    error_code: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class AgentErrorLogCreate(AgentErrorLogBase):
    """Schema for creating AgentErrorLog"""
    occurred_at: Optional[datetime] = Field(default=None, description="When the error occurred")
    
    @validator('payload')
    def validate_payload(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Payload must be a dictionary")
        return v

class AgentErrorLogRead(AgentErrorLogBase):
    """Schema for reading AgentErrorLog"""
    error_id: UUID4
    occurred_at: datetime
    
    # Additional computed fields
    error_message: Optional[str] = None
    severity_level: Optional[str] = None
    is_recent: Optional[bool] = None
    is_critical: Optional[bool] = None
    
    class Config:
        from_attributes = True

class AgentErrorLogUpdate(BaseModel):
    """Schema for updating AgentErrorLog"""
    error_code: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    
    @validator('payload')
    def validate_payload(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Payload must be a dictionary")
        return v
    
    class Config:
        from_attributes = True

class AgentErrorLogStats(BaseModel):
    """Schema for error statistics"""
    total_errors: int
    by_severity: Dict[str, int]
    by_error_code: Dict[str, int]
    by_agent: Dict[str, int]
    recent_count: int
    
    class Config:
        from_attributes = True

class AgentErrorLogTimeline(BaseModel):
    """Schema for error timeline"""
    timestamp: datetime
    error_code: Optional[str]
    severity: str
    message: str
    agent_id: UUID4
    
    class Config:
        from_attributes = True

class AgentErrorLogSummary(BaseModel):
    """Schema for error summary"""
    error_id: UUID4
    agent_id: UUID4
    occurred_at: datetime
    error_code: Optional[str]
    severity_level: str
    error_message: str
    is_recent: bool
    is_critical: bool
    
    class Config:
        from_attributes = True
