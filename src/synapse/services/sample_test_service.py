"""
Sample Test Service - Demonstrates Full Service Layer Stack.

This service demonstrates the complete service layer architecture including:
- BaseService inheritance
- Repository pattern usage
- Dependency injection
- Database access through service layer
- CRUD operations
- Error handling
- Logging
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from synapse.core.services.base_service import BaseService
from synapse.core.services.repository import IRepository, BaseRepository, UnitOfWork
from synapse.models.user import User
from synapse.exceptions import ServiceError

logger = logging.getLogger(__name__)


# Pydantic schemas for the sample service
class UserCreateRequest(BaseModel):
    """Request model for creating a user."""

    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    full_name: str = Field(..., description="User's full name")
    password: str = Field(..., min_length=6, description="User password")
    bio: Optional[str] = Field(None, description="User biography")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "password": "securepassword123",
                "bio": "This is a test user for service layer demo",
            }
        }


class UserUpdateRequest(BaseModel):
    """Request model for updating a user."""

    email: Optional[str] = Field(None, description="User email address")
    username: Optional[str] = Field(None, description="Unique username")
    full_name: Optional[str] = Field(None, description="User's full name")
    bio: Optional[str] = Field(None, description="User biography")
    is_active: Optional[bool] = Field(None, description="User active status")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Updated Test User",
                "bio": "Updated biography for test user",
                "is_active": True,
            }
        }


class UserResponse(BaseModel):
    """Response model for user data."""

    id: str
    email: str
    username: str
    full_name: str
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserRepository(BaseRepository[User, UserCreateRequest, UserUpdateRequest]):
    """
    User-specific repository with custom methods.

    Demonstrates extending BaseRepository for domain-specific operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error finding user by email {email}: {e}")
            raise

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        try:
            result = await self.db.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error finding user by username {username}: {e}")
            raise

    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        try:
            result = await self.db.execute(select(User).where(User.is_active == True))
            return list(result.scalars().all())
        except Exception as e:
            self.logger.error(f"Error getting active users: {e}")
            raise

    async def count_users(self) -> int:
        """Count total number of users."""
        try:
            result = await self.db.execute(select(func.count(User.id)))
            return result.scalar() or 0
        except Exception as e:
            self.logger.error(f"Error counting users: {e}")
            raise


class SampleTestService(BaseService[User, UserCreateRequest, UserUpdateRequest]):
    """
    Sample Test Service demonstrating full service layer architecture.

    This service extends BaseService and demonstrates:
    - Dependency injection through constructor
    - Repository pattern usage
    - Custom business logic methods
    - Error handling and logging
    - Integration with UnitOfWork pattern
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the sample test service.

        Args:
            session: Database session injected via dependency injection
        """
        # Initialize repository
        repository = UserRepository(session)

        # Initialize base service with repository
        super().__init__(repository, User, UserCreateRequest, UserUpdateRequest)

        self.session = session
        self.user_repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug("SampleTestService initialized")

    async def create_user(self, user_data: UserCreateRequest) -> UserResponse:
        """
        Create a new user with business logic validation.

        Args:
            user_data: User creation data

        Returns:
            Created user response

        Raises:
            ServiceError: If user creation fails
        """
        self.logger.info(f"Creating user with email: {user_data.email}")

        try:
            # Check if user already exists
            existing_user = await self.user_repository.find_by_email(user_data.email)
            if existing_user:
                raise ServiceError(f"User with email {user_data.email} already exists")

            existing_username = await self.user_repository.find_by_username(
                user_data.username
            )
            if existing_username:
                raise ServiceError(
                    f"User with username {user_data.username} already exists"
                )

            # Create user instance
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                bio=user_data.bio,
                is_active=True,
                is_verified=False,
                is_superuser=False,
            )

            # Set password using model method
            user.set_password(user_data.password)

            # Save using repository
            created_user = await self.user_repository.create(user)

            self.logger.info(f"User created successfully with ID: {created_user.id}")

            return UserResponse.model_validate(created_user)

        except ServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating user: {e}")
            raise ServiceError(f"Failed to create user: {str(e)}")

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User response or None if not found
        """
        self.logger.debug(f"Getting user by ID: {user_id}")

        try:
            user = await self.user_repository.get(user_id)
            if user:
                return UserResponse.model_validate(user)
            return None

        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {e}")
            raise ServiceError(f"Failed to get user: {str(e)}")

    async def update_user(
        self, user_id: UUID, update_data: UserUpdateRequest
    ) -> Optional[UserResponse]:
        """
        Update user with business logic validation.

        Args:
            user_id: User UUID
            update_data: Update data

        Returns:
            Updated user response or None if not found
        """
        self.logger.info(f"Updating user: {user_id}")

        try:
            # Get existing user
            user = await self.user_repository.get(user_id)
            if not user:
                return None

            # Validate unique constraints if updating email/username
            if update_data.email and update_data.email != user.email:
                existing = await self.user_repository.find_by_email(update_data.email)
                if existing:
                    raise ServiceError(f"Email {update_data.email} already in use")

            if update_data.username and update_data.username != user.username:
                existing = await self.user_repository.find_by_username(
                    update_data.username
                )
                if existing:
                    raise ServiceError(
                        f"Username {update_data.username} already in use"
                    )

            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            updated_user = await self.user_repository.update(user_id, update_dict)

            if updated_user:
                self.logger.info(f"User updated successfully: {user_id}")
                return UserResponse.model_validate(updated_user)

            return None

        except ServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {e}")
            raise ServiceError(f"Failed to update user: {str(e)}")

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete user (soft delete by marking as inactive).

        Args:
            user_id: User UUID

        Returns:
            True if deleted successfully, False if not found
        """
        self.logger.info(f"Deleting user: {user_id}")

        try:
            # Implement soft delete by deactivating user
            result = await self.user_repository.update(user_id, {"is_active": False})

            if result:
                self.logger.info(f"User soft deleted successfully: {user_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}")
            raise ServiceError(f"Failed to delete user: {str(e)}")

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user responses
        """
        self.logger.debug(f"Getting users with skip={skip}, limit={limit}")

        try:
            users = await self.user_repository.get_multi(skip=skip, limit=limit)
            return [UserResponse.model_validate(user) for user in users]

        except Exception as e:
            self.logger.error(f"Error getting all users: {e}")
            raise ServiceError(f"Failed to get users: {str(e)}")

    async def get_active_users(self) -> List[UserResponse]:
        """
        Get all active users.

        Returns:
            List of active user responses
        """
        self.logger.debug("Getting active users")

        try:
            users = await self.user_repository.get_active_users()
            return [UserResponse.model_validate(user) for user in users]

        except Exception as e:
            self.logger.error(f"Error getting active users: {e}")
            raise ServiceError(f"Failed to get active users: {str(e)}")

    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user statistics demonstrating complex business logic.

        Returns:
            Dictionary with user statistics
        """
        self.logger.debug("Getting user statistics")

        try:
            async with UnitOfWork(self.session) as uow:
                total_users = await self.user_repository.count_users()
                active_users = await self.user_repository.get_active_users()
                active_count = len(active_users)

                stats = {
                    "total_users": total_users,
                    "active_users": active_count,
                    "inactive_users": total_users - active_count,
                    "activation_rate": (
                        round((active_count / total_users * 100), 2)
                        if total_users > 0
                        else 0
                    ),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                self.logger.info(f"User statistics generated: {stats}")
                return stats

        except Exception as e:
            self.logger.error(f"Error getting user statistics: {e}")
            raise ServiceError(f"Failed to get user statistics: {str(e)}")

    async def test_transaction_rollback(self, user_data: UserCreateRequest) -> str:
        """
        Test method to demonstrate transaction rollback functionality.

        This method intentionally fails after creating a user to test rollback.

        Args:
            user_data: User creation data

        Returns:
            Status message

        Raises:
            ServiceError: Always fails to demonstrate rollback
        """
        self.logger.info("Testing transaction rollback")

        try:
            async with UnitOfWork(self.session) as uow:
                # Create user
                user = User(
                    email=user_data.email,
                    username=user_data.username,
                    full_name=user_data.full_name,
                    bio=user_data.bio,
                )
                user.set_password(user_data.password)

                created_user = await self.user_repository.create(user)

                # Intentionally fail to test rollback
                raise ServiceError("Intentional failure to test transaction rollback")

        except ServiceError as e:
            self.logger.info(f"Transaction rolled back successfully: {e}")
            return f"Transaction rollback test completed: {str(e)}"
        except Exception as e:
            self.logger.error(f"Unexpected error in rollback test: {e}")
            raise ServiceError(f"Rollback test failed: {str(e)}")


# Factory function for dependency injection
def create_sample_test_service(session: AsyncSession) -> SampleTestService:
    """
    Factory function to create SampleTestService instance.

    This function works with the dependency injection container by
    receiving the database session as a parameter.

    Args:
        session: Database session injected by DI container

    Returns:
        SampleTestService instance
    """
    return SampleTestService(session)
