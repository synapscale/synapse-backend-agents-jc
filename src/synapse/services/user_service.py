"""
User Service - Example Service Implementation.

This service demonstrates the complete integration of the service layer
with repository pattern, dependency injection, and error handling.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.database import get_async_db
from synapse.models.user import User
from synapse.schemas.user import UserProfileUpdate, UserProfileResponse
from synapse.core.services import BaseService, BaseRepository, get_service
from synapse.exceptions import NotFoundError, ValidationError, DatabaseError

logger = logging.getLogger(__name__)


class UserService(BaseService[User, dict, UserProfileUpdate]):
    """
    User service with complete CRUD operations and business logic.
    
    This service demonstrates:
    - Integration with repository pattern
    - Business logic separation
    - Error handling
    - Dependency injection integration
    - Async operations
    """
    
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        """
        Initialize User Service.
        
        Args:
            db: Database session from dependency injection
        """
        super().__init__(db)
        self.model = User
        self.schema_class = dict  # Will be updated with proper schema
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Initialize repository for this service
        from synapse.core.services.repository import BaseRepository
        self.repository = BaseRepository(User, db)
    
    async def create_user(
        self, 
        email: str,
        username: str,
        password: str,
        full_name: str,
        **kwargs
    ) -> User:
        """
        Create a new user with validation and business logic.
        
        Args:
            email: User email
            username: Username
            password: Plain password (will be hashed)
            full_name: User's full name
            **kwargs: Additional user fields
            
        Returns:
            Created user instance
            
        Raises:
            ValidationError: If validation fails
            DatabaseError: If creation fails
        """
        try:
            self.logger.info(f"Creating user with email: {email}")
            
            # Validate email uniqueness
            if await self.get_by_email(email):
                raise ValidationError("Email already registered")
            
            # Validate username uniqueness
            if await self.get_by_username(username):
                raise ValidationError("Username already taken")
            
            # Create user data
            user_data = {
                "email": email,
                "username": username,
                "full_name": full_name,
                **kwargs
            }
            
            # Create user instance to hash password
            user = User(**user_data)
            user.set_password(password)
            
            # Save to database
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            self.logger.info(f"User created successfully with ID: {user.id}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to create user: {e}")
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            raise DatabaseError("Failed to create user") from e
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            User instance or None if not found
        """
        try:
            users = await self.repository.get_multi(
                filters={"email": email},
                limit=1
            )
            return users[0] if users else None
            
        except Exception as e:
            self.logger.error(f"Failed to get user by email {email}: {e}")
            raise DatabaseError("Failed to get user by email") from e
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None if not found
        """
        try:
            users = await self.repository.get_multi(
                filters={"username": username},
                limit=1
            )
            return users[0] if users else None
            
        except Exception as e:
            self.logger.error(f"Failed to get user by username {username}: {e}")
            raise DatabaseError("Failed to get user by username") from e
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            email: User email
            password: Plain password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        try:
            user = await self.get_by_email(email)
            if user and user.verify_password(password):
                self.logger.info(f"User {email} authenticated successfully")
                return user
            
            self.logger.warning(f"Authentication failed for {email}")
            return None
            
        except Exception as e:
            self.logger.error(f"Authentication error for {email}: {e}")
            return None
    
    async def update_profile(
        self, 
        user_id: UUID, 
        update_data: UserProfileUpdate
    ) -> Optional[User]:
        """
        Update user profile with validation.
        
        Args:
            user_id: User ID
            update_data: Profile update data
            
        Returns:
            Updated user instance or None if not found
            
        Raises:
            ValidationError: If validation fails
            DatabaseError: If update fails
        """
        try:
            self.logger.info(f"Updating profile for user: {user_id}")
            
            # Check if user exists
            user = await self.get(user_id)
            if not user:
                raise NotFoundError(f"User with ID {user_id} not found")
            
            # Validate username uniqueness if being updated
            if update_data.username and update_data.username != user.username:
                existing_user = await self.get_by_username(update_data.username)
                if existing_user:
                    raise ValidationError("Username already taken")
            
            # Update user
            updated_user = await self.update(user_id, update_data)
            
            self.logger.info(f"Profile updated successfully for user: {user_id}")
            return updated_user
            
        except Exception as e:
            self.logger.error(f"Failed to update profile for user {user_id}: {e}")
            if isinstance(e, (NotFoundError, ValidationError, DatabaseError)):
                raise
            raise DatabaseError("Failed to update user profile") from e
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deactivated, False if not found
            
        Raises:
            DatabaseError: If deactivation fails
        """
        try:
            self.logger.info(f"Deactivating user: {user_id}")
            
            user = await self.update(user_id, {"is_active": False})
            if user:
                self.logger.info(f"User {user_id} deactivated successfully")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate user {user_id}: {e}")
            raise DatabaseError("Failed to deactivate user") from e
    
    async def get_active_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[User]:
        """
        Get list of active users with optional search.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term for username or email
            
        Returns:
            List of active users
        """
        try:
            filters = {"is_active": True}
            
            # TODO: Implement search functionality in repository
            # This would require more advanced query building
            
            users = await self.repository.get_multi(
                skip=skip,
                limit=limit,
                filters=filters,
                order_by=["-created_at"]
            )
            
            self.logger.debug(f"Retrieved {len(users)} active users")
            return users
            
        except Exception as e:
            self.logger.error(f"Failed to get active users: {e}")
            raise DatabaseError("Failed to get active users") from e
    
    async def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get user statistics and related data counts.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If query fails
        """
        try:
            user = await self.get(user_id)
            if not user:
                raise NotFoundError(f"User with ID {user_id} not found")
            
            # This is a simplified example - in a real implementation,
            # you would query related tables for actual counts
            stats = {
                "user_id": str(user_id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "workflows_count": 0,  # Would query workflow table
                "agents_count": 0,     # Would query agent table
                "conversations_count": 0,  # Would query conversation table
            }
            
            self.logger.debug(f"Generated stats for user: {user_id}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get user stats for {user_id}: {e}")
            if isinstance(e, NotFoundError):
                raise
            raise DatabaseError("Failed to get user statistics") from e


# Dependency injection function
async def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    """
    Dependency injection function for UserService.
    
    Args:
        db: Database session
        
    Returns:
        UserService instance
    """
    return UserService(db)


# Register service in DI container (this would be called in service_configuration.py)
def register_user_service():
    """Register UserService in the dependency injection container."""
    from synapse.core.services import register_scoped
    register_scoped(UserService, UserService) 