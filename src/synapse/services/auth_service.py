"""
Auth Service - Authentication and authorization service.

This service provides authentication and authorization functionality
by wrapping the UserService authentication methods.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.database import get_async_db
from synapse.models.user import User
from synapse.core.services import BaseService
from synapse.services.user_service import UserService

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """
    Authentication service that wraps UserService authentication functionality.
    
    This service provides a dedicated interface for authentication operations
    while delegating the actual user management to UserService.
    """

    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        """
        Initialize Auth Service.

        Args:
            db: Database session from dependency injection
        """
        super().__init__(db)
        self.user_service = UserService(db)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password.

        Args:
            email: User email
            password: Plain password

        Returns:
            User instance if authentication successful, None otherwise
        """
        try:
            self.logger.info(f"Authenticating user: {email}")
            user = await self.user_service.authenticate(email, password)
            
            if user:
                self.logger.info(f"Authentication successful for user: {email}")
                return user
            else:
                self.logger.warning(f"Authentication failed for user: {email}")
                return None
                
        except Exception as e:
            self.logger.error(f"Authentication error for {email}: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        return await self.user_service.get_by_email(email)

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        return await self.user_service.get(user_id)

    async def verify_user_permissions(self, user_id: UUID, required_permissions: list = None) -> bool:
        """
        Verify user permissions (placeholder implementation).

        Args:
            user_id: User ID
            required_permissions: List of required permissions

        Returns:
            True if user has required permissions, False otherwise
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
                
            # Basic permission check - user must be active
            if not user.is_active:
                return False
                
            # TODO: Implement proper permission checking logic
            # For now, all active users have basic permissions
            return True
            
        except Exception as e:
            self.logger.error(f"Permission verification error for user {user_id}: {e}")
            return False


async def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    """
    Dependency function to get AuthService instance.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    return AuthService(db)


def register_auth_service():
    """Register auth service for dependency injection."""
    from synapse.core.services import register_scoped
    register_scoped(AuthService, AuthService) 