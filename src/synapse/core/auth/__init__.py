# /workspaces/synapse-backend-agents-jc/src/synapse/core/auth/__init__.py

"""
Authentication Module - Clean Final Architecture

This module provides unified authentication functionality:
- JWT token management via jwt_manager
- Password hashing utilities
- User password verification via User.verify_password() method
"""

# JWT functions and manager (recommended approach)
from .jwt import (
    jwt_manager,           # Main JWT manager instance (RECOMMENDED)
    create_access_token,   # Utility function
    create_refresh_token,  # Utility function  
    verify_token,          # Utility function
)

# Password utilities
from .password import (
    get_password_hash,     # For password hashing
    # Note: verify_password() removed - use User.verify_password() method
)

__all__ = [
    # JWT management (use jwt_manager for consistency)
    "jwt_manager",
    "create_access_token", 
    "create_refresh_token",
    "verify_token",
    # Password utilities
    "get_password_hash",
]

# AUTHENTICATION USAGE GUIDE:
#
# ✅ CORRECT USAGE:
# - Password verification: user.verify_password(password)
# - JWT operations: jwt_manager.create_access_token(data)
# - Dependencies: from synapse.api.deps import get_current_user
#
# ❌ DEPRECATED (removed):
# - verify_password() standalone function
# - JWT functions from core.security
