"""
Schemas para AgentTrigger
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4, validator

class AgentTriggerBase(BaseModel):
    """Base schema for AgentTrigger"""
    agent_id: UUID4
    trigger_type: str = Field(..., description="Type of trigger (cron, event, manual, webhook)")
    cron_expr: Optional[str] = Field(None, description="Cron expression for scheduled triggers")
    event_name: Optional[str] = Field(None, description="Event name for event-based triggers")
    active: bool = Field(default=True, description="Whether the trigger is active")
    
    @validator('trigger_type')
    def validate_trigger_type(cls, v):
        valid_types = ['cron', 'event', 'manual', 'webhook']
        if v not in valid_types:
            raise ValueError(f"Trigger type must be one of: {', '.join(valid_types)}")
        return v
    
    @validator('cron_expr')
    def validate_cron_expr(cls, v, values):
        trigger_type = values.get('trigger_type')
        if trigger_type == 'cron' and not v:
            raise ValueError("Cron expression is required for cron triggers")
        return v
    
    @validator('event_name')
    def validate_event_name(cls, v, values):
        trigger_type = values.get('trigger_type')
        if trigger_type == 'event' and not v:
            raise ValueError("Event name is required for event triggers")
        return v
    
    class Config:
        from_attributes = True

class AgentTriggerCreate(AgentTriggerBase):
    """Schema for creating AgentTrigger"""
    pass

class AgentTriggerRead(AgentTriggerBase):
    """Schema for reading AgentTrigger"""
    trigger_id: UUID4
    last_run_at: Optional[datetime] = None
    
    # Computed fields
    is_cron_trigger: Optional[bool] = None
    is_event_trigger: Optional[bool] = None
    is_manual_trigger: Optional[bool] = None
    is_webhook_trigger: Optional[bool] = None
    trigger_description: Optional[str] = None
    
    class Config:
        from_attributes = True

class AgentTriggerUpdate(BaseModel):
    """Schema for updating AgentTrigger"""
    trigger_type: Optional[str] = None
    cron_expr: Optional[str] = None
    event_name: Optional[str] = None
    active: Optional[bool] = None
    
    @validator('trigger_type')
    def validate_trigger_type(cls, v):
        if v is not None:
            valid_types = ['cron', 'event', 'manual', 'webhook']
            if v not in valid_types:
                raise ValueError(f"Trigger type must be one of: {', '.join(valid_types)}")
        return v
    
    class Config:
        from_attributes = True

class AgentTriggerExecute(BaseModel):
    """Schema for executing a trigger"""
    trigger_id: UUID4
    force: bool = Field(default=False, description="Force execution even if inactive")
    context: Optional[dict] = Field(default={}, description="Execution context")
    
    class Config:
        from_attributes = True

class AgentTriggerExecution(BaseModel):
    """Schema for trigger execution result"""
    trigger_id: UUID4
    agent_id: UUID4
    executed_at: datetime
    success: bool
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    result: Optional[dict] = None
    
    class Config:
        from_attributes = True

class AgentTriggerStats(BaseModel):
    """Schema for trigger statistics"""
    total_triggers: int
    active_triggers: int
    cron_triggers: int
    event_triggers: int
    manual_triggers: int
    webhook_triggers: int
    executions_last_24h: int
    successful_executions: int
    failed_executions: int
    
    class Config:
        from_attributes = True

class AgentTriggerSchedule(BaseModel):
    """Schema for trigger scheduling information"""
    trigger_id: UUID4
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    is_due: bool = False
    schedule_description: str
    
    class Config:
        from_attributes = True

class AgentTriggerList(BaseModel):
    """Schema for trigger list with pagination"""
    triggers: list[AgentTriggerRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class AgentTriggerBulkOperation(BaseModel):
    """Schema for bulk trigger operations"""
    trigger_ids: list[UUID4] = Field(..., description="List of trigger IDs")
    operation: str = Field(..., description="Operation to perform (activate, deactivate, delete)")
    
    @validator('operation')
    def validate_operation(cls, v):
        valid_operations = ['activate', 'deactivate', 'delete']
        if v not in valid_operations:
            raise ValueError(f"Operation must be one of: {', '.join(valid_operations)}")
        return v
    
    class Config:
        from_attributes = True
