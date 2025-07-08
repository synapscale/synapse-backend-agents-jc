from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ExecutionType(str, Enum):
    """Enum for execution types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"
    BATCH = "batch"


class ExecutionStatus(str, Enum):
    """Enum for execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ReportExecutionBase(BaseModel):
    """Base schema for ReportExecution"""
    report_id: UUID = Field(..., description="Report ID")
    user_id: Optional[UUID] = Field(None, description="User ID")
    execution_type: ExecutionType = Field(..., description="Execution type")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution parameters")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, description="Execution status")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Execution result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    rows_processed: Optional[int] = Field(None, description="Number of rows processed")
    data_size_bytes: Optional[int] = Field(None, description="Data size in bytes")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class ReportExecutionCreate(ReportExecutionBase):
    """Schema for creating a new report execution"""
    pass


class ReportExecutionUpdate(BaseModel):
    """Schema for updating an existing report execution"""
    status: Optional[ExecutionStatus] = Field(None, description="Execution status")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Execution result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    rows_processed: Optional[int] = Field(None, description="Number of rows processed")
    data_size_bytes: Optional[int] = Field(None, description="Data size in bytes")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class ReportExecutionInDB(ReportExecutionBase):
    """Schema for report execution in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Execution ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ReportExecutionResponse(ReportExecutionInDB):
    """Schema for report execution response"""
    is_completed: bool = Field(..., description="Whether execution is completed")
    is_running: bool = Field(..., description="Whether execution is running")
    is_failed: bool = Field(..., description="Whether execution failed")
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    formatted_duration: str = Field(..., description="Formatted duration")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")


class ReportExecutionListResponse(BaseModel):
    """Schema for report execution list response"""
    model_config = ConfigDict(from_attributes=True)
    
    executions: List[ReportExecutionResponse] = Field(..., description="List of report executions")
    total: int = Field(..., description="Total number of executions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of executions per page")
    pages: int = Field(..., description="Total number of pages")


class ReportExecutionTrigger(BaseModel):
    """Schema for triggering a report execution"""
    report_id: UUID = Field(..., description="Report ID")
    execution_type: ExecutionType = Field(default=ExecutionType.MANUAL, description="Execution type")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Execution parameters")
    priority: int = Field(default=5, ge=1, le=10, description="Execution priority (1-10)")
    timeout_seconds: Optional[int] = Field(None, description="Execution timeout")
    callback_url: Optional[str] = Field(None, description="Callback URL for completion")


class ReportExecutionTriggerResponse(BaseModel):
    """Schema for report execution trigger response"""
    execution_id: UUID = Field(..., description="Execution ID")
    status: ExecutionStatus = Field(..., description="Initial execution status")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    queue_position: Optional[int] = Field(None, description="Position in queue")
    message: str = Field(..., description="Response message")


class ReportExecutionCancel(BaseModel):
    """Schema for canceling a report execution"""
    execution_id: UUID = Field(..., description="Execution ID")
    reason: Optional[str] = Field(None, description="Cancellation reason")


class ReportExecutionCancelResponse(BaseModel):
    """Schema for report execution cancel response"""
    success: bool = Field(..., description="Cancellation success")
    message: str = Field(..., description="Response message")
    execution_status: ExecutionStatus = Field(..., description="Final execution status")


class ReportExecutionStatistics(BaseModel):
    """Schema for report execution statistics"""
    report_id: UUID = Field(..., description="Report ID")
    total_executions: int = Field(..., description="Total number of executions")
    successful_executions: int = Field(..., description="Successful executions")
    failed_executions: int = Field(..., description="Failed executions")
    cancelled_executions: int = Field(..., description="Cancelled executions")
    average_execution_time: float = Field(..., description="Average execution time in seconds")
    median_execution_time: float = Field(..., description="Median execution time in seconds")
    min_execution_time: float = Field(..., description="Minimum execution time in seconds")
    max_execution_time: float = Field(..., description="Maximum execution time in seconds")
    total_rows_processed: int = Field(..., description="Total rows processed")
    total_data_size_bytes: int = Field(..., description="Total data size in bytes")
    execution_frequency: Dict[str, int] = Field(..., description="Execution frequency by type")
    recent_executions: List[ReportExecutionResponse] = Field(..., description="Recent executions")
    performance_trend: List[Dict[str, Any]] = Field(..., description="Performance trend data")


class ReportExecutionMonitoring(BaseModel):
    """Schema for report execution monitoring"""
    execution_id: UUID = Field(..., description="Execution ID")
    current_status: ExecutionStatus = Field(..., description="Current execution status")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current execution step")
    elapsed_time_seconds: float = Field(..., description="Elapsed time in seconds")
    estimated_remaining_seconds: Optional[float] = Field(None, description="Estimated remaining time")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")
    rows_processed_so_far: Optional[int] = Field(None, description="Rows processed so far")
    last_checkpoint: Optional[datetime] = Field(None, description="Last checkpoint timestamp")


class ReportExecutionRetry(BaseModel):
    """Schema for retrying a failed report execution"""
    execution_id: UUID = Field(..., description="Execution ID")
    retry_parameters: Optional[Dict[str, Any]] = Field(None, description="Retry parameters")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(default=60, description="Delay between retries")


class ReportExecutionRetryResponse(BaseModel):
    """Schema for report execution retry response"""
    new_execution_id: UUID = Field(..., description="New execution ID")
    retry_attempt: int = Field(..., description="Retry attempt number")
    status: ExecutionStatus = Field(..., description="Retry execution status")
    message: str = Field(..., description="Response message")


class ReportExecutionFilter(BaseModel):
    """Schema for report execution filtering"""
    report_id: Optional[UUID] = Field(None, description="Filter by report ID")
    user_id: Optional[UUID] = Field(None, description="Filter by user ID")
    execution_type: Optional[ExecutionType] = Field(None, description="Filter by execution type")
    status: Optional[ExecutionStatus] = Field(None, description="Filter by execution status")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    min_execution_time: Optional[int] = Field(None, description="Minimum execution time filter")
    max_execution_time: Optional[int] = Field(None, description="Maximum execution time filter")
    has_error: Optional[bool] = Field(None, description="Filter by error presence")
    min_rows_processed: Optional[int] = Field(None, description="Minimum rows processed filter")


class ReportExecutionExport(BaseModel):
    """Schema for report execution export"""
    filters: Optional[ReportExecutionFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_result_data: bool = Field(default=False, description="Include result data")
    include_parameters: bool = Field(default=True, description="Include execution parameters")
    include_performance_metrics: bool = Field(default=True, description="Include performance metrics")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for export")
    max_records: Optional[int] = Field(None, description="Maximum records to export")


class ReportExecutionBatch(BaseModel):
    """Schema for batch report execution operations"""
    execution_ids: List[UUID] = Field(..., description="List of execution IDs")
    action: str = Field(..., description="Batch action (cancel, retry, archive)")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action-specific data")


class ReportExecutionBatchResponse(BaseModel):
    """Schema for batch report execution response"""
    total_processed: int = Field(..., description="Total executions processed")
    successful: int = Field(..., description="Successful operations")
    failed: int = Field(..., description="Failed operations")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    results: List[Dict[str, Any]] = Field(..., description="Operation results")
