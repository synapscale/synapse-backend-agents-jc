# SynapScale Error Handling - Developer Guide

## Overview

This guide provides developers with practical information for working with the SynapScale error handling system, including how to use custom exceptions, implement proper error handling in endpoints, and follow best practices.

## Using Custom Exceptions

### Basic Usage

```python
from synapse.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    AuthenticationError,
    ResourceConflictError
)

# Simple exception with message
raise ValidationError("Invalid email format")

# Exception with error code and details
raise ResourceNotFoundError(
    message="Workflow not found",
    error_code="WORKFLOW_NOT_FOUND",
    details={
        "workflow_id": workflow_id,
        "user_id": current_user.id
    }
)
```

### Exception with Rich Details

```python
# Validation error with field-specific details
raise ValidationError(
    message="Multiple validation errors occurred",
    details={
        "field_errors": [
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too short"}
        ],
        "total_errors": 2
    }
)

# Resource conflict with context
raise ResourceConflictError(
    message="Email already registered",
    details={
        "conflict_field": "email",
        "conflict_value": email,
        "existing_user_id": existing_user.id,
        "registration_date": existing_user.created_at.isoformat()
    }
)
```

## Exception Hierarchy Usage

### Authentication & Authorization

```python
from synapse.exceptions import AuthenticationError, AuthorizationError, TokenExpiredError

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("JWT token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid JWT token")

async def check_permissions(user: User, required_permission: str):
    if required_permission not in user.permissions:
        raise AuthorizationError(
            message="Insufficient permissions",
            details={
                "required_permission": required_permission,
                "user_permissions": user.permissions
            }
        )
```

### Resource Management

```python
from synapse.exceptions import ResourceNotFoundError, ResourceLimitExceededError

async def get_workflow(workflow_id: str, user_id: str):
    workflow = await db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == user_id
    ).first()
    
    if not workflow:
        raise ResourceNotFoundError(
            message="Workflow not found",
            details={
                "resource_type": "workflow",
                "resource_id": workflow_id,
                "user_id": user_id
            }
        )
    
    return workflow

async def create_workflow(user: User, workflow_data: dict):
    # Check user's workflow limit
    user_workflow_count = await db.query(Workflow).filter(
        Workflow.user_id == user.id
    ).count()
    
    if user_workflow_count >= user.workflow_limit:
        raise ResourceLimitExceededError(
            message="Workflow limit exceeded",
            details={
                "current_count": user_workflow_count,
                "limit": user.workflow_limit,
                "upgrade_required": True
            }
        )
```

### Business Logic Exceptions

```python
from synapse.exceptions import WorkflowExecutionError, NodeExecutionError

async def execute_workflow_node(node: Node, input_data: dict):
    try:
        result = await node.execute(input_data)
        return result
    except Exception as e:
        raise NodeExecutionError(
            message=f"Node execution failed: {node.name}",
            details={
                "node_id": node.id,
                "node_type": node.type,
                "input_data": input_data,
                "error_details": str(e)
            }
        )

async def execute_workflow(workflow: Workflow, input_data: dict):
    try:
        execution_context = WorkflowExecutionContext(workflow, input_data)
        
        for node in workflow.nodes:
            await execute_workflow_node(node, execution_context.get_node_input(node))
            
        return execution_context.get_output()
        
    except NodeExecutionError:
        # Re-raise node errors as-is
        raise
    except Exception as e:
        raise WorkflowExecutionError(
            message="Workflow execution failed",
            details={
                "workflow_id": workflow.id,
                "execution_stage": execution_context.current_stage,
                "error_details": str(e)
            }
        )
```

### External Service Integration

```python
from synapse.exceptions import LLMProviderError, ExternalServiceError
import httpx

async def call_llm_provider(provider: str, prompt: str, model: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.{provider}.com/v1/completions",
                json={"prompt": prompt, "model": model},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        raise LLMProviderError(
            message="LLM provider request timed out",
            details={
                "provider": provider,
                "model": model,
                "timeout": 30.0,
                "retry_suggested": True
            }
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise LLMProviderError(
                message="LLM provider rate limit exceeded",
                details={
                    "provider": provider,
                    "status_code": e.response.status_code,
                    "retry_after": e.response.headers.get("Retry-After", 60)
                }
            )
        else:
            raise LLMProviderError(
                message=f"LLM provider error: {e.response.status_code}",
                details={
                    "provider": provider,
                    "status_code": e.response.status_code,
                    "response_text": e.response.text
                }
            )
```

## FastAPI Endpoint Error Handling

### Basic Endpoint with Error Handling

```python
from fastapi import APIRouter, Depends, HTTPException
from synapse.exceptions import ResourceNotFoundError, ValidationError
from synapse.schemas.error import ErrorResponse

router = APIRouter()

@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific workflow.
    
    Raises:
        ResourceNotFoundError: If workflow doesn't exist or user doesn't have access
        AuthorizationError: If user doesn't have permission to view workflow
    """
    try:
        workflow = await get_workflow_by_id(workflow_id, current_user.id, db)
        return WorkflowResponse.from_orm(workflow)
    except ResourceNotFoundError:
        # Let the global exception handler process this
        raise
    except Exception as e:
        # Log unexpected errors and re-raise as internal server error
        logger.exception(f"Unexpected error getting workflow {workflow_id}")
        raise InternalServerError("An unexpected error occurred")
```

### Endpoint with Input Validation

```python
@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new workflow.
    
    Raises:
        ValidationError: If workflow data is invalid
        ResourceLimitExceededError: If user has reached workflow limit
        ResourceConflictError: If workflow name already exists
    """
    # Additional business logic validation
    if not workflow_data.name or len(workflow_data.name.strip()) == 0:
        raise ValidationError(
            message="Workflow name is required",
            details={"field": "name", "value": workflow_data.name}
        )
    
    # Check for name conflicts
    existing_workflow = await db.query(Workflow).filter(
        Workflow.name == workflow_data.name,
        Workflow.user_id == current_user.id
    ).first()
    
    if existing_workflow:
        raise ResourceConflictError(
            message="Workflow name already exists",
            details={
                "field": "name",
                "value": workflow_data.name,
                "existing_workflow_id": existing_workflow.id
            }
        )
    
    # Create workflow (this may raise ResourceLimitExceededError)
    workflow = await create_workflow(current_user, workflow_data.dict(), db)
    return WorkflowResponse.from_orm(workflow)
```

### Endpoint with Complex Error Scenarios

```python
@router.post("/workflows/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    execution_data: ExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a workflow.
    
    Raises:
        ResourceNotFoundError: If workflow doesn't exist
        ValidationError: If execution data is invalid
        WorkflowExecutionError: If workflow execution fails
        ResourceLimitExceededError: If execution quota exceeded
    """
    # Get and validate workflow
    workflow = await get_workflow(workflow_id, current_user.id)
    
    # Validate workflow is executable
    if not workflow.is_active:
        raise ValidationError(
            message="Cannot execute inactive workflow",
            details={
                "workflow_id": workflow_id,
                "workflow_status": workflow.status
            }
        )
    
    # Check execution quota
    daily_executions = await get_daily_execution_count(current_user.id)
    if daily_executions >= current_user.daily_execution_limit:
        raise ResourceLimitExceededError(
            message="Daily execution limit exceeded",
            details={
                "current_count": daily_executions,
                "limit": current_user.daily_execution_limit,
                "reset_time": get_next_reset_time().isoformat()
            }
        )
    
    # Execute workflow (may raise WorkflowExecutionError)
    execution = await execute_workflow(workflow, execution_data.input_data)
    return ExecutionResponse.from_orm(execution)
```

## Database Error Handling

### SQLAlchemy Error Handling

```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from synapse.exceptions import DatabaseError, ResourceConflictError

async def create_user(user_data: UserCreate, db: Session):
    try:
        user = User(**user_data.dict())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
        
    except IntegrityError as e:
        await db.rollback()
        
        # Handle specific constraint violations
        if "email" in str(e.orig):
            raise ResourceConflictError(
                message="Email address already registered",
                details={
                    "field": "email",
                    "value": user_data.email
                }
            )
        elif "username" in str(e.orig):
            raise ResourceConflictError(
                message="Username already taken",
                details={
                    "field": "username", 
                    "value": user_data.username
                }
            )
        else:
            raise ResourceConflictError("Data conflict occurred")
            
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error creating user: {e}")
        raise DatabaseError("Database operation failed")
```

## Async Error Handling

### Background Task Error Handling

```python
import asyncio
from synapse.exceptions import WorkflowExecutionError

async def background_workflow_execution(workflow_id: str, input_data: dict):
    """Background task for workflow execution with proper error handling."""
    try:
        workflow = await get_workflow(workflow_id)
        result = await execute_workflow(workflow, input_data)
        
        # Update execution status
        await update_execution_status(workflow_id, "completed", result)
        
    except WorkflowExecutionError as e:
        # Log workflow-specific errors
        logger.error(f"Workflow execution failed: {e.message}", extra={
            "workflow_id": workflow_id,
            "error_code": e.error_code,
            "details": e.details
        })
        await update_execution_status(workflow_id, "failed", error=e.details)
        
    except Exception as e:
        # Log unexpected errors
        logger.exception(f"Unexpected error in background workflow execution")
        await update_execution_status(workflow_id, "failed", error={
            "error_type": type(e).__name__,
            "message": str(e)
        })
```

### Concurrent Operation Error Handling

```python
async def process_multiple_workflows(workflow_ids: List[str]):
    """Process multiple workflows concurrently with error handling."""
    
    async def process_single_workflow(workflow_id: str):
        try:
            return await execute_workflow_by_id(workflow_id)
        except Exception as e:
            logger.error(f"Error processing workflow {workflow_id}: {e}")
            return {"workflow_id": workflow_id, "error": str(e)}
    
    # Process workflows concurrently
    tasks = [process_single_workflow(wf_id) for wf_id in workflow_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Separate successful results from errors
    successful_results = []
    failed_results = []
    
    for result in results:
        if isinstance(result, Exception):
            failed_results.append({
                "error": str(result),
                "error_type": type(result).__name__
            })
        elif "error" in result:
            failed_results.append(result)
        else:
            successful_results.append(result)
    
    return {
        "successful": successful_results,
        "failed": failed_results,
        "total_processed": len(workflow_ids)
    }
```

## Error Handling Best Practices

### 1. Use Specific Exceptions

```python
# ❌ Don't use generic exceptions
raise Exception("Something went wrong")

# ✅ Use specific exceptions
raise ResourceNotFoundError("Workflow not found", details={"workflow_id": workflow_id})
```

### 2. Provide Helpful Error Details

```python
# ❌ Minimal error information
raise ValidationError("Invalid data")

# ✅ Detailed error information
raise ValidationError(
    message="Validation failed for workflow data",
    details={
        "field_errors": [
            {"field": "name", "message": "Name is required"},
            {"field": "nodes", "message": "At least one node is required"}
        ],
        "schema_version": "v1.0"
    }
)
```

### 3. Log Errors Appropriately

```python
# ❌ Don't log client errors as server errors
try:
    user = await get_user(user_id)
except ResourceNotFoundError as e:
    logger.error(f"User not found: {user_id}")  # This is client error, not server error
    raise

# ✅ Log appropriately based on error type
try:
    user = await get_user(user_id)
except ResourceNotFoundError as e:
    logger.warning(f"User not found: {user_id}")  # Client error - warning level
    raise
except DatabaseError as e:
    logger.error(f"Database error getting user: {e}")  # Server error - error level
    raise
```

### 4. Handle Cleanup in Error Cases

```python
async def process_file_upload(file: UploadFile):
    temp_file_path = None
    try:
        # Save uploaded file temporarily
        temp_file_path = await save_temp_file(file)
        
        # Process file
        result = await process_file(temp_file_path)
        
        # Move to permanent location
        permanent_path = await move_to_permanent_storage(temp_file_path)
        
        return {"file_path": permanent_path, "result": result}
        
    except Exception as e:
        # Clean up temporary file on error
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        if isinstance(e, (ValidationError, InvalidInputError)):
            # Re-raise client errors as-is
            raise
        else:
            # Log and wrap unexpected errors
            logger.exception("Error processing file upload")
            raise InternalServerError("File processing failed")
```

### 5. Use Context Managers for Resource Cleanup

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_transaction(db: Session):
    """Context manager for database transactions with error handling."""
    try:
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise

# Usage
async def create_workflow_with_nodes(workflow_data: dict, nodes_data: List[dict]):
    async with database_transaction(db) as tx:
        # Create workflow
        workflow = await create_workflow(workflow_data, tx)
        
        # Create nodes
        for node_data in nodes_data:
            await create_node(workflow.id, node_data, tx)
        
        return workflow
```

## Testing Error Handling

### Unit Tests for Custom Exceptions

```python
import pytest
from synapse.exceptions import ValidationError, ResourceNotFoundError

def test_validation_error_with_details():
    """Test ValidationError with detailed information."""
    details = {
        "field_errors": [
            {"field": "email", "message": "Invalid format"}
        ]
    }
    
    error = ValidationError(
        message="Validation failed",
        error_code="VALIDATION_FAILED",
        details=details
    )
    
    assert error.message == "Validation failed"
    assert error.error_code == "VALIDATION_FAILED"
    assert error.details == details

def test_resource_not_found_error():
    """Test ResourceNotFoundError default behavior."""
    error = ResourceNotFoundError("Resource not found")
    
    assert error.message == "Resource not found"
    assert error.error_code == "RESOURCE_NOT_FOUND"  # Default from class
    assert error.details == {}
```

### Integration Tests for Error Responses

```python
from fastapi.testclient import TestClient

def test_workflow_not_found_error(client: TestClient):
    """Test workflow not found returns proper error response."""
    response = client.get("/api/v1/workflows/nonexistent")
    
    assert response.status_code == 404
    
    error_data = response.json()["error"]
    assert error_data["error_code"] == "RESOURCE_NOT_FOUND"
    assert error_data["message"] == "Workflow not found"
    assert "request_id" in error_data
    assert "timestamp" in error_data

def test_validation_error_response(client: TestClient):
    """Test validation error returns proper error response."""
    invalid_data = {"name": ""}  # Invalid workflow data
    
    response = client.post("/api/v1/workflows", json=invalid_data)
    
    assert response.status_code == 400
    
    error_data = response.json()["error"]
    assert error_data["error_code"] == "VALIDATION_ERROR"
    assert "details" in error_data
```

## Performance Considerations

### 1. Avoid Expensive Operations in Error Handling

```python
# ❌ Don't perform expensive operations in exception details
raise ResourceNotFoundError(
    message="User not found",
    details={
        "all_users": await get_all_users(),  # Expensive operation
        "user_id": user_id
    }
)

# ✅ Include only necessary information
raise ResourceNotFoundError(
    message="User not found",
    details={"user_id": user_id}
)
```

### 2. Use Lazy Evaluation for Error Details

```python
def get_error_details(user_id: str) -> dict:
    """Generate error details only when needed."""
    return {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "suggestions": ["Check user ID format", "Verify user exists"]
    }

# Use lambda for lazy evaluation
raise ResourceNotFoundError(
    message="User not found",
    details=get_error_details(user_id)
)
```

This developer guide provides comprehensive examples and best practices for working with the SynapScale error handling system. Following these patterns will ensure consistent, maintainable, and user-friendly error handling throughout the application.