"""
Schemas para WorkflowExecutionMetric
"""

from datetime import datetime
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, UUID4, validator

class WorkflowExecutionMetricBase(BaseModel):
    """Base schema for WorkflowExecutionMetric"""
    workflow_execution_id: UUID4
    node_execution_id: Optional[int] = None
    metric_type: str = Field(..., max_length=100, description="Type of metric (performance, count, size, custom)")
    metric_name: str = Field(..., max_length=255, description="Name of the metric")
    value_numeric: Optional[int] = None
    value_float: Optional[str] = Field(None, max_length=50)
    value_text: Optional[str] = None
    value_json: Optional[Dict[str, Any]] = None
    context: Optional[str] = Field(None, max_length=255, description="Context information")
    tags: Optional[Dict[str, Any]] = Field(None, description="Additional tags")
    measured_at: Optional[datetime] = None
    tenant_id: Optional[UUID4] = None
    
    @validator('metric_type')
    def validate_metric_type(cls, v):
        valid_types = ['performance', 'count', 'size', 'custom', 'error', 'success']
        if v not in valid_types:
            raise ValueError(f"Metric type must be one of: {', '.join(valid_types)}")
        return v
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricCreate(WorkflowExecutionMetricBase):
    """Schema for creating WorkflowExecutionMetric"""
    pass

class WorkflowExecutionMetricRead(WorkflowExecutionMetricBase):
    """Schema for reading WorkflowExecutionMetric"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    metric_display_name: Optional[str] = None
    formatted_value: Optional[str] = None
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricUpdate(BaseModel):
    """Schema for updating WorkflowExecutionMetric"""
    metric_type: Optional[str] = Field(None, max_length=100)
    metric_name: Optional[str] = Field(None, max_length=255)
    value_numeric: Optional[int] = None
    value_float: Optional[str] = Field(None, max_length=50)
    value_text: Optional[str] = None
    value_json: Optional[Dict[str, Any]] = None
    context: Optional[str] = Field(None, max_length=255)
    tags: Optional[Dict[str, Any]] = None
    measured_at: Optional[datetime] = None
    
    @validator('metric_type')
    def validate_metric_type(cls, v):
        if v is not None:
            valid_types = ['performance', 'count', 'size', 'custom', 'error', 'success']
            if v not in valid_types:
                raise ValueError(f"Metric type must be one of: {', '.join(valid_types)}")
        return v
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricValue(BaseModel):
    """Schema for setting metric value"""
    value: Union[int, float, str, Dict[str, Any]]
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricSummary(BaseModel):
    """Schema for metrics summary"""
    total_metrics: int
    metric_types: Dict[str, int]
    performance: Dict[str, str]
    errors: int
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricTrend(BaseModel):
    """Schema for metric trends"""
    metric_name: str
    data_points: list[Dict[str, Any]]
    average_value: Optional[float] = None
    trend_direction: Optional[str] = None
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricList(BaseModel):
    """Schema for metric list with pagination"""
    metrics: list[WorkflowExecutionMetricRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class WorkflowExecutionMetricStats(BaseModel):
    """Schema for metric statistics"""
    total_metrics: int
    by_type: Dict[str, int]
    by_execution: Dict[str, int]
    recent_metrics: int
    
    class Config:
        from_attributes = True
