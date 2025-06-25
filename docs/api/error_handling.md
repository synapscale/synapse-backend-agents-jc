# SynapScale Error Handling System

## Overview

The SynapScale API implements a comprehensive error handling system that provides consistent, informative, and structured error responses across all endpoints. This system ensures that clients receive standardized error information that can be easily parsed and handled programmatically.

## Key Features

- **Standardized Error Format**: All errors follow a consistent JSON structure
- **Request Tracking**: Every error includes a unique request ID for debugging
- **Detailed Context**: Errors include timestamp, HTTP method, path, and user context
- **Structured Logging**: All errors are logged with appropriate severity levels
- **Custom Exception Hierarchy**: Domain-specific exceptions for different error scenarios
- **Global Exception Handling**: Centralized error processing for consistent responses

## Error Response Format

All API errors return a standardized JSON response with the following structure:

```json
{
  "error": {
    "error_code": "string",
    "message": "string", 
    "details": {},
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/endpoint",
    "method": "POST",
    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### Response Headers

All error responses include:
- `X-Request-ID`: Unique identifier for request tracking and debugging

## Custom Exception Hierarchy

### Base Exception: `SynapseBaseException`

All custom exceptions inherit from `SynapseBaseException`, which provides:

```python
class SynapseBaseException(Exception):
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.default_error_code
        self.details = details or {}
```

### Domain-Specific Exceptions

#### Authentication & Authorization
- **`AuthenticationError`**: Invalid credentials, expired tokens
- **`AuthorizationError`**: Insufficient permissions, access denied
- **`TokenExpiredError`**: JWT tokens that have expired

#### Resource Management
- **`ResourceNotFoundError`**: Requested resources that don't exist
- **`ResourceConflictError`**: Conflicts during resource creation/updates
- **`ResourceLimitExceededError`**: Rate limits, quota exceeded

#### Validation & Input
- **`ValidationError`**: Input validation failures
- **`InvalidInputError`**: Malformed or invalid input data

#### Business Logic
- **`WorkflowExecutionError`**: Workflow processing failures
- **`NodeExecutionError`**: Individual node execution errors
- **`TemplateError`**: Template-related errors

#### External Services
- **`ExternalServiceError`**: Third-party service integration failures
- **`LLMProviderError`**: LLM provider communication errors

#### System & Infrastructure
- **`DatabaseError`**: Database operation failures
- **`ConfigurationError`**: System configuration issues
- **`InternalServerError`**: Unexpected system errors

## HTTP Status Code Mapping

| Exception Type | HTTP Status | Error Code | Description |
|---------------|-------------|------------|-------------|
| `ValidationError` | 400 | `VALIDATION_ERROR` | Invalid input data |
| `InvalidInputError` | 400 | `INVALID_INPUT` | Malformed request data |
| `AuthenticationError` | 401 | `AUTHENTICATION_FAILED` | Invalid credentials |
| `TokenExpiredError` | 401 | `TOKEN_EXPIRED` | Expired authentication token |
| `AuthorizationError` | 403 | `INSUFFICIENT_PERMISSIONS` | Access denied |
| `ResourceNotFoundError` | 404 | `RESOURCE_NOT_FOUND` | Resource doesn't exist |
| `ResourceConflictError` | 409 | `RESOURCE_CONFLICT` | Resource conflict |
| `ResourceLimitExceededError` | 429 | `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `InternalServerError` | 500 | `INTERNAL_SERVER_ERROR` | System error |
| `DatabaseError` | 500 | `DATABASE_ERROR` | Database operation failed |
| `ExternalServiceError` | 502 | `EXTERNAL_SERVICE_ERROR` | Third-party service error |
| `LLMProviderError` | 502 | `LLM_PROVIDER_ERROR` | LLM service error |

## Error Response Examples

### 400 - Validation Error
```json
{
  "error": {
    "error_code": "VALIDATION_ERROR",
    "message": "Validation failed for request data",
    "details": {
      "field_errors": [
        {
          "field": "email",
          "message": "Invalid email format"
        },
        {
          "field": "password", 
          "message": "Password must be at least 8 characters"
        }
      ]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/auth/register",
    "method": "POST",
    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### 401 - Authentication Error
```json
{
  "error": {
    "error_code": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials provided",
    "details": {
      "reason": "username_or_password_incorrect"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/auth/login",
    "method": "POST",
    "request_id": "req_234f5678-f90c-23e4-b567-537725285111"
  }
}
```

### 403 - Authorization Error
```json
{
  "error": {
    "error_code": "INSUFFICIENT_PERMISSIONS",
    "message": "Access denied: insufficient permissions",
    "details": {
      "required_permission": "workflow:delete",
      "user_permissions": ["workflow:read", "workflow:create"]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/workflows/123",
    "method": "DELETE",
    "request_id": "req_345g6789-g01d-34f5-c678-648836396222"
  }
}
```

### 404 - Resource Not Found
```json
{
  "error": {
    "error_code": "RESOURCE_NOT_FOUND", 
    "message": "Workflow not found",
    "details": {
      "resource_type": "workflow",
      "resource_id": "wf_nonexistent123"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/workflows/wf_nonexistent123",
    "method": "GET",
    "request_id": "req_456h7890-h12e-45g6-d789-759947407333"
  }
}
```

### 409 - Resource Conflict
```json
{
  "error": {
    "error_code": "RESOURCE_CONFLICT",
    "message": "Email address already registered",
    "details": {
      "conflict_field": "email",
      "conflict_value": "user@example.com"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/auth/register",
    "method": "POST",
    "request_id": "req_567i8901-i23f-56h7-e890-860058518444"
  }
}
```

### 422 - Pydantic Validation Error
```json
{
  "error": {
    "error_code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "validation_errors": [
        {
          "loc": ["body", "workflow_data", "name"],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/workflows",
    "method": "POST",
    "request_id": "req_678j9012-j34g-67i8-f901-971169629555"
  }
}
```

### 429 - Rate Limit Exceeded
```json
{
  "error": {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "3600s",
      "retry_after": 1800
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/llm/generate",
    "method": "POST",
    "request_id": "req_789k0123-k45h-78j9-g012-082270730666"
  }
}
```

### 500 - Internal Server Error
```json
{
  "error": {
    "error_code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "error_type": "DatabaseConnectionError"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/workflows",
    "method": "GET",
    "request_id": "req_890l1234-l56i-89k0-h123-193381841777"
  }
}
```

### 502 - External Service Error
```json
{
  "error": {
    "error_code": "LLM_PROVIDER_ERROR",
    "message": "LLM provider service unavailable",
    "details": {
      "provider": "openai",
      "service_status": "timeout",
      "retry_suggested": true
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/llm/generate",
    "method": "POST",
    "request_id": "req_901m2345-m67j-90l1-i234-204492952888"
  }
}
```

## Global Exception Handlers

The system includes specialized handlers for different exception types:

### Custom Exception Handlers
- **SynapseBaseException Handler**: Processes all custom domain exceptions
- **HTTPException Handler**: Handles FastAPI HTTP exceptions
- **RequestValidationError Handler**: Processes FastAPI request validation errors
- **PydanticValidationError Handler**: Handles Pydantic model validation errors

### System Exception Handlers
- **SQLAlchemyError Handler**: Database-related errors
- **ValueError/TypeError Handler**: Python built-in type errors
- **KeyError/AttributeError Handler**: Missing attributes/keys
- **NotImplementedError Handler**: Unimplemented functionality
- **Generic Exception Handler**: Fallback for unexpected errors

## Logging Integration

All errors are logged with structured information:

```python
logger.error(
    f"Error processing request",
    extra={
        "error_code": error_code,
        "error_type": type(exc).__name__,
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
        "user_id": getattr(request.state, "user_id", None),
        "details": error_details
    }
)
```

### Log Levels
- **WARNING**: Client errors (4xx status codes)
- **ERROR**: Server errors (5xx status codes)  
- **INFO**: Request processing information

## Request ID Middleware

Every request receives a unique identifier for tracking:

```python
# Request ID generation
request_id = f"req_{uuid.uuid4()}"

# Added to request state
request.state.request_id = request_id

# Included in response headers
headers["X-Request-ID"] = request_id
```

## Error Handler Setup

The error handling system is initialized in the main application:

```python
from synapse.error_handlers import setup_error_handlers

app = FastAPI()
setup_error_handlers(app)
```

This registers all exception handlers with the FastAPI application.

## Best Practices for API Clients

### Error Handling
1. **Always check HTTP status codes** before processing responses
2. **Parse the error object** from the response body for detailed information
3. **Use request_id** for support requests and debugging
4. **Implement retry logic** for 5xx errors with exponential backoff
5. **Handle rate limiting** by respecting retry_after values

### Example Client Code (Python)
```python
import requests
import time

def make_api_request(url, data=None):
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        
        # Parse error response
        error_data = response.json().get("error", {})
        error_code = error_data.get("error_code")
        message = error_data.get("message")
        request_id = error_data.get("request_id")
        
        # Handle specific error types
        if response.status_code == 401:
            # Handle authentication error
            refresh_token()
            return make_api_request(url, data)  # Retry
        
        elif response.status_code == 429:
            # Handle rate limiting
            retry_after = error_data.get("details", {}).get("retry_after", 60)
            time.sleep(retry_after)
            return make_api_request(url, data)  # Retry
        
        elif response.status_code >= 500:
            # Handle server errors with exponential backoff
            time.sleep(2 ** attempt)
            return make_api_request(url, data)  # Retry
        
        else:
            # Handle client errors
            raise APIError(f"Request failed: {message}", error_code, request_id)
            
    except requests.RequestException as e:
        # Handle network errors
        raise NetworkError(f"Network error: {e}")
```

## Monitoring and Debugging

### Request Tracking
- Use `X-Request-ID` header to track requests across logs
- Include request ID in support tickets for faster debugging
- Monitor error rates by error code and endpoint

### Error Metrics
- Track error rates by HTTP status code
- Monitor specific error codes for business logic issues
- Set up alerts for high error rates or new error types

### Log Analysis
- Search logs by request ID for complete request trace
- Filter by error codes to identify patterns
- Monitor user-specific error patterns for targeted support

## Security Considerations

### Error Information Disclosure
- Error messages are sanitized to prevent information leakage
- Internal error details are logged but not exposed to clients
- Stack traces are never included in API responses
- Database errors are abstracted to prevent schema disclosure

### Rate Limiting
- Error responses respect rate limiting to prevent abuse
- Failed authentication attempts are tracked and limited
- Detailed error information may be reduced under high load

## Testing Error Scenarios

The error handling system includes comprehensive test coverage:

```python
# Example test cases
def test_authentication_error():
    """Test authentication error response format"""
    
def test_validation_error_with_details():
    """Test validation error with field-specific details"""
    
def test_rate_limit_error():
    """Test rate limiting error response"""
    
def test_internal_server_error():
    """Test internal server error handling"""
```

## Migration Guide

### Updating Client Code
When migrating to the new error handling system:

1. **Update error parsing logic** to use the new `error` object structure
2. **Handle new error codes** that provide more specific error information  
3. **Implement request ID tracking** for better debugging
4. **Update retry logic** to handle new error response format
5. **Test error scenarios** to ensure proper handling

### Backward Compatibility
The new error handling system maintains compatibility with existing error response expectations while providing enhanced error information.