"""
Schemas for AgentQuota - managing agent quotas and limits.
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, validator, computed_field
from uuid import UUID


class AgentQuotaBase(BaseModel):
    """Base schema for AgentQuota attributes."""
    model_config = ConfigDict(from_attributes=True)
    
    agent_id: UUID = Field(..., description="Agent ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    max_calls: int = Field(..., ge=0, description="Maximum number of calls allowed")
    max_tokens: int = Field(..., ge=0, description="Maximum number of tokens allowed")
    period: timedelta = Field(..., description="Quota period duration")
    
    @validator('period')
    def validate_period(cls, v):
        """Validate that period is positive."""
        if v.total_seconds() <= 0:
            raise ValueError('period must be positive')
        return v


class AgentQuotaCreate(AgentQuotaBase):
    """Schema for creating a new agent quota."""
    pass


class AgentQuotaUpdate(BaseModel):
    """Schema for updating an agent quota."""
    model_config = ConfigDict(from_attributes=True)
    
    max_calls: Optional[int] = Field(None, ge=0, description="Maximum number of calls allowed")
    max_tokens: Optional[int] = Field(None, ge=0, description="Maximum number of tokens allowed")
    period: Optional[timedelta] = Field(None, description="Quota period duration")
    
    @validator('period')
    def validate_period(cls, v):
        """Validate that period is positive."""
        if v is not None and v.total_seconds() <= 0:
            raise ValueError('period must be positive')
        return v


class AgentQuotaRead(AgentQuotaBase):
    """Schema for reading an agent quota."""
    quota_id: UUID = Field(..., description="Unique identifier for the quota")
    created_at: datetime = Field(..., description="Timestamp when the quota was created")
    
    # Computed fields
    @computed_field
    @property
    def period_in_seconds(self) -> float:
        """Get period duration in seconds."""
        return self.period.total_seconds()
    
    @computed_field
    @property
    def period_in_hours(self) -> float:
        """Get period duration in hours."""
        return self.period_in_seconds / 3600
    
    @computed_field
    @property
    def period_in_days(self) -> float:
        """Get period duration in days."""
        return self.period_in_hours / 24
    
    @computed_field
    @property
    def period_description(self) -> str:
        """Get human-readable period description."""
        if self.is_hourly_quota:
            return "por hora"
        elif self.is_daily_quota:
            return "por dia"
        elif self.is_monthly_quota:
            return "por mês"
        else:
            return f"por {self.period_in_hours:.1f} horas"
    
    @computed_field
    @property
    def calls_per_second_limit(self) -> float:
        """Get calls per second limit."""
        return self.max_calls / self.period_in_seconds
    
    @computed_field
    @property
    def tokens_per_second_limit(self) -> float:
        """Get tokens per second limit."""
        return self.max_tokens / self.period_in_seconds
    
    @computed_field
    @property
    def is_daily_quota(self) -> bool:
        """Check if this is a daily quota."""
        return self.period_in_days == 1.0
    
    @computed_field
    @property
    def is_hourly_quota(self) -> bool:
        """Check if this is an hourly quota."""
        return self.period_in_hours == 1.0
    
    @computed_field
    @property
    def is_monthly_quota(self) -> bool:
        """Check if this is a monthly quota (approximately 30 days)."""
        return abs(self.period_in_days - 30) < 1


class AgentQuotaUsageCheck(BaseModel):
    """Schema for checking quota usage."""
    current_calls: int = Field(..., ge=0, description="Current number of calls")
    current_tokens: int = Field(..., ge=0, description="Current number of tokens")
    calls_limit_exceeded: bool = Field(..., description="Whether calls limit is exceeded")
    tokens_limit_exceeded: bool = Field(..., description="Whether tokens limit is exceeded")
    quota_exceeded: bool = Field(..., description="Whether any quota is exceeded")
    remaining_calls: int = Field(..., ge=0, description="Remaining calls")
    remaining_tokens: int = Field(..., ge=0, description="Remaining tokens")
    calls_usage_percentage: float = Field(..., ge=0, le=100, description="Calls usage percentage")
    tokens_usage_percentage: float = Field(..., ge=0, le=100, description="Tokens usage percentage")


class AgentQuotaResponse(AgentQuotaRead):
    """Response schema for agent quota."""
    pass


class AgentQuotaListResponse(BaseModel):
    """Paginated list of agent quotas."""
    items: list[AgentQuotaResponse] = Field(..., description="List of agent quotas")
    total: int = Field(..., description="Total number of quotas")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")


class AgentQuotaCreateDaily(BaseModel):
    """Schema for creating a daily quota."""
    agent_id: UUID = Field(..., description="Agent ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    max_calls: int = Field(..., ge=0, description="Maximum number of calls allowed per day")
    max_tokens: int = Field(..., ge=0, description="Maximum number of tokens allowed per day")


class AgentQuotaCreateHourly(BaseModel):
    """Schema for creating an hourly quota."""
    agent_id: UUID = Field(..., description="Agent ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    max_calls: int = Field(..., ge=0, description="Maximum number of calls allowed per hour")
    max_tokens: int = Field(..., ge=0, description="Maximum number of tokens allowed per hour")


class AgentQuotaCreateMonthly(BaseModel):
    """Schema for creating a monthly quota."""
    agent_id: UUID = Field(..., description="Agent ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    max_calls: int = Field(..., ge=0, description="Maximum number of calls allowed per month")
    max_tokens: int = Field(..., ge=0, description="Maximum number of tokens allowed per month")
