"""
Repository Pattern Implementation.

This module provides the repository pattern for data access, implementing
interfaces and concrete implementations for database operations.
"""

import logging
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Union, Sequence
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, asc, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select
from pydantic import BaseModel

from synapse.database import Base as SQLAlchemyBaseModel
from synapse.exceptions import NotFoundError, ValidationError, DatabaseError

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class IRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic repository interface for CRUD operations.

    This interface defines the contract for all repository implementations,
    ensuring consistent data access patterns across the application.
    """

    @abstractmethod
    async def create(self, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """Create a new record."""
        pass

    @abstractmethod
    async def get(self, id: Union[UUID, str, int]) -> Optional[ModelType]:
        """Get a record by ID."""
        pass

    @abstractmethod
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        **kwargs,
    ) -> List[ModelType]:
        """Get multiple records with filtering and pagination."""
        pass

    @abstractmethod
    async def update(
        self, id: Union[UUID, str, int], obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """Update a record by ID."""
        pass

    @abstractmethod
    async def delete(self, id: Union[UUID, str, int]) -> bool:
        """Delete a record by ID."""
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        pass

    @abstractmethod
    async def exists(self, id: Union[UUID, str, int]) -> bool:
        """Check if a record exists."""
        pass


class BaseRepository(IRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository implementation using SQLAlchemy.

    Provides common CRUD operations for all entity types with
    optimized queries and error handling.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: The SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
        self.logger = logging.getLogger(f"{self.__class__.__name__}({model.__name__})")

    async def create(self, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Pydantic model with data to create
            **kwargs: Additional fields to set

        Returns:
            Created model instance

        Raises:
            DatabaseError: If creation fails
            ValidationError: If validation fails
        """
        try:
            # Convert Pydantic model to dict
            if isinstance(obj_in, BaseModel):
                obj_data = obj_in.model_dump(exclude_unset=True)
            else:
                obj_data = obj_in

            # Add any additional kwargs
            obj_data.update(kwargs)

            # Create database object
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)

            self.logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
            return db_obj

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create {self.model.__name__}") from e

    async def get(self, id: Union[UUID, str, int]) -> Optional[ModelType]:
        """
        Get a record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            self.logger.error(f"Failed to get {self.model.__name__} with ID {id}: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__}") from e

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        **kwargs,
    ) -> List[ModelType]:
        """
        Get multiple records with filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field: value filters
            order_by: List of field names to order by (prefix with '-' for desc)
            **kwargs: Additional filter criteria

        Returns:
            List of model instances
        """
        try:
            query = select(self.model)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            query = query.where(getattr(self.model, field).in_(value))
                        else:
                            query = query.where(getattr(self.model, field) == value)

            # Apply additional kwargs as filters
            for field, value in kwargs.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

            # Apply ordering
            if order_by:
                for field in order_by:
                    if field.startswith("-"):
                        field_name = field[1:]
                        if hasattr(self.model, field_name):
                            query = query.order_by(
                                desc(getattr(self.model, field_name))
                            )
                    else:
                        if hasattr(self.model, field):
                            query = query.order_by(asc(getattr(self.model, field)))

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            self.logger.error(f"Failed to get multiple {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to get multiple {self.model.__name__}") from e

    async def update(
        self, id: Union[UUID, str, int], obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update a record by ID.

        Args:
            id: Record ID
            obj_in: Update data (Pydantic model or dict)

        Returns:
            Updated model instance or None if not found

        Raises:
            DatabaseError: If update fails
        """
        try:
            # Get existing object
            db_obj = await self.get(id)
            if not db_obj:
                return None

            # Convert update data to dict
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in

            # Update fields
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            await self.db.commit()
            await self.db.refresh(db_obj)

            self.logger.info(f"Updated {self.model.__name__} with ID: {id}")
            return db_obj

        except Exception as e:
            await self.db.rollback()
            self.logger.error(
                f"Failed to update {self.model.__name__} with ID {id}: {e}"
            )
            raise DatabaseError(f"Failed to update {self.model.__name__}") from e

    async def delete(self, id: Union[UUID, str, int]) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            # Check if exists
            db_obj = await self.get(id)
            if not db_obj:
                return False

            # Delete
            await self.db.delete(db_obj)
            await self.db.commit()

            self.logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return True

        except Exception as e:
            await self.db.rollback()
            self.logger.error(
                f"Failed to delete {self.model.__name__} with ID {id}: {e}"
            )
            raise DatabaseError(f"Failed to delete {self.model.__name__}") from e

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.

        Args:
            filters: Dictionary of field: value filters

        Returns:
            Number of records
        """
        try:
            query = select(func.count(self.model.id))

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            query = query.where(getattr(self.model, field).in_(value))
                        else:
                            query = query.where(getattr(self.model, field) == value)

            result = await self.db.execute(query)
            return result.scalar()

        except Exception as e:
            self.logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to count {self.model.__name__}") from e

    async def exists(self, id: Union[UUID, str, int]) -> bool:
        """
        Check if a record exists.

        Args:
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        try:
            query = select(self.model.id).where(self.model.id == id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            self.logger.error(
                f"Failed to check existence of {self.model.__name__} with ID {id}: {e}"
            )
            raise DatabaseError(
                f"Failed to check existence of {self.model.__name__}"
            ) from e

    async def get_with_relations(
        self, id: Union[UUID, str, int], relations: List[str]
    ) -> Optional[ModelType]:
        """
        Get a record with related data loaded.

        Args:
            id: Record ID
            relations: List of relationship names to load

        Returns:
            Model instance with relations loaded or None
        """
        try:
            query = select(self.model).where(self.model.id == id)

            # Add relationship loading
            for relation in relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            self.logger.error(
                f"Failed to get {self.model.__name__} with relations: {e}"
            )
            raise DatabaseError(
                f"Failed to get {self.model.__name__} with relations"
            ) from e


class UnitOfWork:
    """
    Unit of Work pattern implementation.

    Manages multiple repositories within a single database transaction,
    ensuring data consistency across multiple operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize Unit of Work.

        Args:
            db: Database session
        """
        self.db = db
        self._repositories: Dict[Type, BaseRepository] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_repository(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType] = None,
        update_schema: Type[UpdateSchemaType] = None,
    ) -> BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]:
        """
        Get or create a repository for the given model.

        Args:
            model: SQLAlchemy model class
            create_schema: Pydantic schema for create operations
            update_schema: Pydantic schema for update operations

        Returns:
            Repository instance
        """
        if model not in self._repositories:
            self._repositories[model] = BaseRepository(model, self.db)
            self.logger.debug(f"Created repository for {model.__name__}")

        return self._repositories[model]

    async def commit(self):
        """Commit the transaction."""
        await self.db.commit()
        self.logger.debug("Transaction committed")

    async def rollback(self):
        """Rollback the transaction."""
        await self.db.rollback()
        self.logger.debug("Transaction rolled back")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
