#!/usr/bin/env python3
"""
Script to update the OpenAPI specification with custom error schemas.

This script adds our custom error response schemas to the OpenAPI specification
and updates error responses to use the new standardized format.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def get_error_schemas() -> Dict[str, Any]:
    """Get the custom error schemas to add to OpenAPI spec."""
    return {
        "ErrorResponse": {
            "type": "object",
            "required": ["error"],
            "properties": {
                "error": {
                    "$ref": "#/components/schemas/ErrorDetail"
                }
            },
            "title": "ErrorResponse",
            "description": "Standard error response format for all API errors"
        },
        "ErrorDetail": {
            "type": "object",
            "required": ["error_code", "message", "timestamp", "path", "method", "request_id"],
            "properties": {
                "error_code": {
                    "type": "string",
                    "title": "Error Code",
                    "description": "Unique identifier for the error type",
                    "example": "RESOURCE_NOT_FOUND"
                },
                "message": {
                    "type": "string",
                    "title": "Message",
                    "description": "Human-readable error message",
                    "example": "The requested resource was not found"
                },
                "details": {
                    "type": "object",
                    "title": "Details",
                    "description": "Additional error-specific information",
                    "example": {"resource_id": "123", "resource_type": "workflow"}
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "title": "Timestamp",
                    "description": "ISO 8601 timestamp when the error occurred",
                    "example": "2024-01-15T10:30:00Z"
                },
                "path": {
                    "type": "string",
                    "title": "Path",
                    "description": "API endpoint path where the error occurred",
                    "example": "/api/v1/workflows/123"
                },
                "method": {
                    "type": "string",
                    "title": "Method",
                    "description": "HTTP method used in the request",
                    "example": "GET"
                },
                "request_id": {
                    "type": "string",
                    "title": "Request ID",
                    "description": "Unique identifier for request tracking",
                    "example": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            },
            "title": "ErrorDetail",
            "description": "Detailed error information"
        },
        "ValidationErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "ValidationErrorResponse",
            "description": "Error response for validation failures",
            "example": {
                "error": {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Validation failed for request data",
                    "details": {
                        "field_errors": [
                            {"field": "email", "message": "Invalid email format"},
                            {"field": "password", "message": "Password must be at least 8 characters"}
                        ]
                    },
                    "timestamp": "2024-01-15T10:30:00Z",
                    "path": "/api/v1/auth/register",
                    "method": "POST",
                    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            }
        },
        "AuthenticationErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "AuthenticationErrorResponse", 
            "description": "Error response for authentication failures",
            "example": {
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
        },
        "AuthorizationErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "AuthorizationErrorResponse",
            "description": "Error response for authorization failures",
            "example": {
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
        },
        "ResourceNotFoundErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "ResourceNotFoundErrorResponse",
            "description": "Error response for resource not found",
            "example": {
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
        },
        "ResourceConflictErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "ResourceConflictErrorResponse",
            "description": "Error response for resource conflicts",
            "example": {
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
        },
        "RateLimitErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "RateLimitErrorResponse",
            "description": "Error response for rate limit exceeded",
            "example": {
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
        },
        "InternalServerErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "InternalServerErrorResponse",
            "description": "Error response for internal server errors",
            "example": {
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
        },
        "ExternalServiceErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/ErrorResponse"}
            ],
            "title": "ExternalServiceErrorResponse",
            "description": "Error response for external service errors",
            "example": {
                "error": {
                    "error_code": "LLM_PROVIDER_ERROR",
                    "message": "LLM provider service unavailable",
                    "details": {
                        "provider": "openai",
                        "service_status": "timeout",
                        "retry_suggested": True
                    },
                    "timestamp": "2024-01-15T10:30:00Z",
                    "path": "/api/v1/llm/generate",
                    "method": "POST",
                    "request_id": "req_901m2345-m67j-90l1-i234-204492952888"
                }
            }
        }
    }

def get_error_response_definitions() -> Dict[str, Any]:
    """Get error response definitions for different HTTP status codes."""
    return {
        "400": {
            "description": "Bad Request - Validation or input error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "401": {
            "description": "Unauthorized - Authentication required or failed",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/AuthenticationErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "403": {
            "description": "Forbidden - Insufficient permissions",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/AuthorizationErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "404": {
            "description": "Not Found - Resource does not exist",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ResourceNotFoundErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "409": {
            "description": "Conflict - Resource already exists or conflict",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ResourceConflictErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "422": {
            "description": "Unprocessable Entity - Request validation failed",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "429": {
            "description": "Too Many Requests - Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/RateLimitErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                },
                "Retry-After": {
                    "description": "Seconds to wait before retrying",
                    "schema": {"type": "integer"}
                }
            }
        },
        "500": {
            "description": "Internal Server Error - Unexpected server error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/InternalServerErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        "502": {
            "description": "Bad Gateway - External service error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ExternalServiceErrorResponse"}
                }
            },
            "headers": {
                "X-Request-ID": {
                    "description": "Unique request identifier for tracking",
                    "schema": {"type": "string"}
                }
            }
        }
    }

def update_openapi_spec(spec_file: Path, output_file: Path = None) -> None:
    """Update OpenAPI specification with custom error schemas."""
    
    if not spec_file.exists():
        print(f"Error: OpenAPI spec file not found: {spec_file}")
        sys.exit(1)
    
    # Load existing OpenAPI spec
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in OpenAPI spec: {e}")
        sys.exit(1)
    
    # Ensure components and schemas sections exist
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    
    # Add custom error schemas
    error_schemas = get_error_schemas()
    spec['components']['schemas'].update(error_schemas)
    
    # Update API info to mention error handling
    if 'info' not in spec:
        spec['info'] = {}
    
    spec['info']['description'] = spec['info'].get('description', '') + """

## Error Handling

This API implements a comprehensive error handling system that provides consistent, structured error responses across all endpoints. All errors follow a standardized format with detailed error information, request tracking, and proper HTTP status codes.

### Error Response Format

All error responses follow this structure:

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

### Error Codes

The API uses specific error codes for different error types:

- `VALIDATION_ERROR`: Input validation failures
- `AUTHENTICATION_FAILED`: Invalid credentials
- `INSUFFICIENT_PERMISSIONS`: Access denied
- `RESOURCE_NOT_FOUND`: Resource doesn't exist
- `RESOURCE_CONFLICT`: Resource conflicts
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INTERNAL_SERVER_ERROR`: Unexpected server errors
- `LLM_PROVIDER_ERROR`: External LLM service errors

### Request Tracking

Every error response includes a unique `request_id` and is also provided in the `X-Request-ID` header for request tracking and debugging.

For more details, see the [Error Handling Documentation](docs/api/error_handling.md).
"""
    
    # Add common error responses to paths (optional - would make spec very verbose)
    # This is commented out to avoid making the spec too large
    # error_responses = get_error_response_definitions()
    # for path_item in spec.get('paths', {}).values():
    #     for method_data in path_item.values():
    #         if isinstance(method_data, dict) and 'responses' in method_data:
    #             # Add common error responses
    #             for status_code, response_def in error_responses.items():
    #                 if status_code not in method_data['responses']:
    #                     method_data['responses'][status_code] = response_def
    
    # Write updated spec
    output_path = output_file or spec_file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated OpenAPI specification: {output_path}")
        print(f"Added {len(error_schemas)} custom error schemas")
    except Exception as e:
        print(f"Error writing updated OpenAPI spec: {e}")
        sys.exit(1)

def main():
    """Main function to update OpenAPI specification."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update OpenAPI specification with custom error schemas"
    )
    parser.add_argument(
        "spec_file",
        help="Path to the OpenAPI specification file",
        default="current_openapi.json",
        nargs="?"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (defaults to input file)",
        type=Path
    )
    parser.add_argument(
        "--backup",
        help="Create backup of original file",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    spec_file = Path(args.spec_file)
    
    # Create backup if requested
    if args.backup and spec_file.exists():
        backup_file = spec_file.with_suffix(f"{spec_file.suffix}.backup")
        backup_file.write_text(spec_file.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"Created backup: {backup_file}")
    
    # Update specification
    update_openapi_spec(spec_file, args.output)

if __name__ == "__main__":
    main() 