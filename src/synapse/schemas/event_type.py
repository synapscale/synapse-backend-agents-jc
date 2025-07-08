"""
Schemas para EventType
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, UUID4, validator

class EventTypeBase(BaseModel):
    """Base schema for EventType"""
    name: str = Field(..., max_length=100, description="Unique event type name")
    display_name: str = Field(..., max_length=255, description="Display name for the event type")
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100, description="Event category (user, system, business, error, etc.)")
    severity: Optional[str] = Field(None, max_length=50, description="Event severity (info, warning, error, critical)")
    payload_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for event payload validation")
    required_fields: Optional[List[str]] = Field(None, description="List of required fields")
    should_alert: bool = Field(default=False, description="Whether this event should generate alerts")
    should_log: bool = Field(default=True, description="Whether this event should be logged")
    retention_days: Optional[str] = Field(None, max_length=10, description="Data retention period in days")
    generates_metrics: bool = Field(default=False, description="Whether this event generates metrics")
    metric_config: Optional[Dict[str, Any]] = Field(None, description="Metric generation configuration")
    is_active: bool = Field(default=True, description="Whether the event type is active")
    is_system: bool = Field(default=False, description="Whether this is a system event type")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError("Name must contain only alphanumeric characters, hyphens, underscores, and dots")
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        if v is not None and v not in ['info', 'warning', 'error', 'critical']:
            raise ValueError("Severity must be one of: info, warning, error, critical")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None and v not in ['user', 'system', 'business', 'error', 'security', 'performance']:
            raise ValueError("Category must be one of: user, system, business, error, security, performance")
        return v
    
    @validator('retention_days')
    def validate_retention_days(cls, v):
        if v is not None:
            try:
                days = int(v)
                if days < 1:
                    raise ValueError("Retention days must be positive")
            except ValueError:
                raise ValueError("Retention days must be a valid number")
        return v
    
    class Config:
        from_attributes = True

class EventTypeCreate(EventTypeBase):
    """Schema for creating EventType"""
    pass

class EventTypeRead(EventTypeBase):
    """Schema for reading EventType"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EventTypeUpdate(BaseModel):
    """Schema for updating EventType"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    severity: Optional[str] = Field(None, max_length=50)
    payload_schema: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    should_alert: Optional[bool] = None
    should_log: Optional[bool] = None
    retention_days: Optional[str] = Field(None, max_length=10)
    generates_metrics: Optional[bool] = None
    metric_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None
    
    @validator('severity')
    def validate_severity(cls, v):
        if v is not None and v not in ['info', 'warning', 'error', 'critical']:
            raise ValueError("Severity must be one of: info, warning, error, critical")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None and v not in ['user', 'system', 'business', 'error', 'security', 'performance']:
            raise ValueError("Category must be one of: user, system, business, error, security, performance")
        return v
    
    @validator('retention_days')
    def validate_retention_days(cls, v):
        if v is not None:
            try:
                days = int(v)
                if days < 1:
                    raise ValueError("Retention days must be positive")
            except ValueError:
                raise ValueError("Retention days must be a valid number")
        return v
    
    class Config:
        from_attributes = True

class EventTypeStats(BaseModel):
    """Schema for event type statistics"""
    total_event_types: int
    active_event_types: int
    system_event_types: int
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    alert_enabled: int
    metric_enabled: int
    
    class Config:
        from_attributes = True

class EventTypeValidation(BaseModel):
    """Schema for event type validation result"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    
    class Config:
        from_attributes = True

class EventTypeList(BaseModel):
    """Schema for event type list with pagination"""
    event_types: List[EventTypeRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True
