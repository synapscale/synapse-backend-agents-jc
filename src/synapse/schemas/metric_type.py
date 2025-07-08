"""
Schemas para MetricType
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class MetricTypeBase(BaseModel):
    """Base schema for MetricType"""
    name: str = Field(..., max_length=100, description="Unique metric name")
    display_name: str = Field(..., max_length=255, description="Display name for the metric")
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100, description="Metric category (performance, usage, business, etc.)")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement (count, percentage, seconds, etc.)")
    data_type: str = Field(default="number", description="Data type (number, boolean, string)")
    aggregation_method: Optional[str] = Field(None, max_length=50, description="Aggregation method (sum, avg, max, min, count)")
    aggregation_window: Optional[str] = Field(None, max_length=50, description="Aggregation window (hour, day, week, month)")
    collection_config: Optional[Dict[str, Any]] = Field(None, description="Collection configuration")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    is_active: bool = Field(default=True, description="Whether the metric type is active")
    is_system: bool = Field(default=False, description="Whether this is a system metric")
    
    @validator('data_type')
    def validate_data_type(cls, v):
        if v not in ['number', 'boolean', 'string']:
            raise ValueError("Data type must be 'number', 'boolean', or 'string'")
        return v
    
    @validator('aggregation_method')
    def validate_aggregation_method(cls, v):
        if v is not None and v not in ['sum', 'avg', 'max', 'min', 'count']:
            raise ValueError("Aggregation method must be one of: sum, avg, max, min, count")
        return v
    
    @validator('aggregation_window')
    def validate_aggregation_window(cls, v):
        if v is not None and v not in ['hour', 'day', 'week', 'month']:
            raise ValueError("Aggregation window must be one of: hour, day, week, month")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Name must contain only alphanumeric characters, hyphens, and underscores")
        return v
    
    class Config:
        from_attributes = True

class MetricTypeCreate(MetricTypeBase):
    """Schema for creating MetricType"""
    pass

class MetricTypeRead(MetricTypeBase):
    """Schema for reading MetricType"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MetricTypeUpdate(BaseModel):
    """Schema for updating MetricType"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    data_type: Optional[str] = None
    aggregation_method: Optional[str] = Field(None, max_length=50)
    aggregation_window: Optional[str] = Field(None, max_length=50)
    collection_config: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None
    
    @validator('data_type')
    def validate_data_type(cls, v):
        if v is not None and v not in ['number', 'boolean', 'string']:
            raise ValueError("Data type must be 'number', 'boolean', or 'string'")
        return v
    
    @validator('aggregation_method')
    def validate_aggregation_method(cls, v):
        if v is not None and v not in ['sum', 'avg', 'max', 'min', 'count']:
            raise ValueError("Aggregation method must be one of: sum, avg, max, min, count")
        return v
    
    @validator('aggregation_window')
    def validate_aggregation_window(cls, v):
        if v is not None and v not in ['hour', 'day', 'week', 'month']:
            raise ValueError("Aggregation window must be one of: hour, day, week, month")
        return v
    
    class Config:
        from_attributes = True

class MetricTypeSummary(BaseModel):
    """Schema for metric type summary"""
    total_metrics: int
    active_metrics: int
    system_metrics: int
    by_category: Dict[str, int]
    by_data_type: Dict[str, int]
    
    class Config:
        from_attributes = True
