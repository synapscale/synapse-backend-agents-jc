"""
Schemas for AgentUsageMetric - tracking agent usage metrics.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, validator
from uuid import UUID
from decimal import Decimal


class AgentUsageMetricBase(BaseModel):
    """Base schema for AgentUsageMetric attributes."""
    model_config = ConfigDict(from_attributes=True)
    
    agent_id: UUID = Field(..., description="Agent ID")
    period_start: datetime = Field(..., description="Start of the measurement period")
    period_end: datetime = Field(..., description="End of the measurement period")
    calls_count: int = Field(..., ge=0, description="Number of API calls made")
    tokens_used: int = Field(..., ge=0, description="Number of tokens consumed")
    cost_est: Decimal = Field(..., ge=0, description="Estimated cost for the usage")
    
    @validator('period_end')
    def validate_period_end(cls, v, values):
        """Validate that period_end is after period_start."""
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('period_end must be after period_start')
        return v


class AgentUsageMetricCreate(AgentUsageMetricBase):
    """Schema for creating a new agent usage metric."""
    pass


class AgentUsageMetricUpdate(BaseModel):
    """Schema for updating an agent usage metric."""
    model_config = ConfigDict(from_attributes=True)
    
    period_start: Optional[datetime] = Field(None, description="Start of the measurement period")
    period_end: Optional[datetime] = Field(None, description="End of the measurement period")
    calls_count: Optional[int] = Field(None, ge=0, description="Number of API calls made")
    tokens_used: Optional[int] = Field(None, ge=0, description="Number of tokens consumed")
    cost_est: Optional[Decimal] = Field(None, ge=0, description="Estimated cost for the usage")


class AgentUsageMetricRead(AgentUsageMetricBase):
    """Schema for reading an agent usage metric."""
    metric_id: UUID = Field(..., description="Unique identifier for the metric")
    created_at: datetime = Field(..., description="Timestamp when the metric was created")
    
    # Computed fields
    period_duration_minutes: Optional[int] = Field(None, description="Duration of the period in minutes")
    cost_per_call: Optional[Decimal] = Field(None, description="Cost per API call")
    cost_per_token: Optional[Decimal] = Field(None, description="Cost per token")
    calls_per_minute: Optional[float] = Field(None, description="Average calls per minute")
    tokens_per_minute: Optional[float] = Field(None, description="Average tokens per minute")
    
    @property
    def period_duration_minutes(self) -> int:
        """Calculate period duration in minutes."""
        return int((self.period_end - self.period_start).total_seconds() / 60)
    
    @property
    def cost_per_call(self) -> Optional[Decimal]:
        """Calculate cost per call."""
        if self.calls_count > 0:
            return self.cost_est / self.calls_count
        return None
    
    @property
    def cost_per_token(self) -> Optional[Decimal]:
        """Calculate cost per token."""
        if self.tokens_used > 0:
            return self.cost_est / self.tokens_used
        return None
    
    @property
    def calls_per_minute(self) -> Optional[float]:
        """Calculate calls per minute."""
        duration = self.period_duration_minutes
        if duration > 0:
            return self.calls_count / duration
        return None
    
    @property
    def tokens_per_minute(self) -> Optional[float]:
        """Calculate tokens per minute."""
        duration = self.period_duration_minutes
        if duration > 0:
            return self.tokens_used / duration
        return None


class AgentUsageMetricResponse(AgentUsageMetricRead):
    """Response schema for agent usage metric."""
    pass


class AgentUsageMetricListResponse(BaseModel):
    """Paginated list of agent usage metrics."""
    items: list[AgentUsageMetricResponse] = Field(..., description="List of agent usage metrics")
    total: int = Field(..., description="Total number of metrics")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
