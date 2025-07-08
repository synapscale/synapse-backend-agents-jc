from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID


class AgentToolBase(BaseModel):
    """Base schema for AgentTool"""
    agent_id: UUID = Field(..., description="Agent ID")
    tool_id: UUID = Field(..., description="Tool ID")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool configuration")


class AgentToolCreate(AgentToolBase):
    """Schema for creating a new agent tool association"""
    pass


class AgentToolUpdate(BaseModel):
    """Schema for updating an existing agent tool association"""
    config: Optional[Dict[str, Any]] = Field(None, description="Tool configuration")


class AgentToolInDB(AgentToolBase):
    """Schema for agent tool association in database"""
    model_config = ConfigDict(from_attributes=True)


class AgentToolResponse(AgentToolInDB):
    """Schema for agent tool association response"""
    pass


class AgentToolListResponse(BaseModel):
    """Schema for agent tool association list response"""
    model_config = ConfigDict(from_attributes=True)
    
    agent_tools: list[AgentToolResponse] = Field(..., description="List of agent tool associations")
    total: int = Field(..., description="Total number of agent tools")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of agent tools per page")
    pages: int = Field(..., description="Total number of pages")


class AgentToolBatch(BaseModel):
    """Schema for batch operations on agent tools"""
    agent_id: UUID = Field(..., description="Agent ID")
    tool_configs: list[Dict[str, Any]] = Field(..., description="List of tool configurations")


class AgentToolBatchResponse(BaseModel):
    """Schema for batch operation response"""
    success: bool = Field(..., description="Operation success")
    created: int = Field(..., description="Number of associations created")
    updated: int = Field(..., description="Number of associations updated")
    errors: list[str] = Field(default_factory=list, description="List of errors")


class AgentToolStatistics(BaseModel):
    """Schema for agent tool statistics"""
    total_associations: int = Field(..., description="Total number of tool associations")
    unique_agents: int = Field(..., description="Number of unique agents")
    unique_tools: int = Field(..., description="Number of unique tools")
    most_used_tools: list[Dict[str, Any]] = Field(..., description="Most frequently used tools")
    agent_tool_count: Dict[str, int] = Field(..., description="Tool count per agent")
