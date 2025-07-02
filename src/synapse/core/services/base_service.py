"""
Base Service Layer Implementation.

This module provides the foundation for all service classes in the application,
implementing common CRUD operations, error handling, and patterns.
"""

import logging
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Union
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from fastapi import Depends, HTTPException, status

from synapse.database import get_db
from synapse.core.services.repository import IRepository, BaseRepository, UnitOfWork
from synapse.exceptions import (
    NotFoundError,
    ValidationError,
    DatabaseError,
    not_found_exception,
    validation_exception,
)

# Type variables for generic implementation
TModel = TypeVar("TModel")  # SQLAlchemy model type
TCreate = TypeVar("TCreate", bound=BaseModel)  # Pydantic create schema type
TUpdate = TypeVar("TUpdate", bound=BaseModel)  # Pydantic update schema type

logger = logging.getLogger(__name__)


class BaseService(Generic[TModel, TCreate, TUpdate]):
    """
    Base service class providing common CRUD operations and patterns.

    This class should be extended by all service classes to maintain
    consistency across the application.

    Type Parameters:
        TModel: SQLAlchemy model type for database operations
        TCreate: Pydantic create schema type for request validation
        TUpdate: Pydantic update schema type for request validation
    """

    def __init__(
        self,
        repository: IRepository = None,
        model_class: Type[TModel] = None,
        create_schema: Type[TCreate] = None,
        update_schema: Type[TUpdate] = None,
    ):
        """
        Initialize the base service.

        Args:
            repository: Repository instance for database operations
            model_class: SQLAlchemy model class
            create_schema: Pydantic schema for creation
            update_schema: Pydantic schema for updates
        """
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

        # Store type information
        self.model_class: Type[TModel] = model_class
        self.create_schema: Type[TCreate] = create_schema
        self.update_schema: Type[TUpdate] = update_schema

        # Database session (available through repository)
        self.db = repository.db if repository else None

    def _log_operation(self, operation: str, details: str = ""):
        """Log service operations for monitoring and debugging."""
        self.logger.info(f"{operation} - {details}")

    def _log_error(self, operation: str, error: Exception, details: str = ""):
        """Log service errors for monitoring and debugging."""
        self.logger.error(f"{operation} failed - {details}: {str(error)}")

    async def get(self, id: Any) -> Optional[TModel]:
        """
        Get entity by ID.

        Args:
            id: Entity identifier

        Returns:
            Entity if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            self._log_operation("GET", f"id={id}")

            if not self.repository:
                raise DatabaseError("Repository not initialized")

            return await self.repository.get(id)

        except Exception as e:
            self._log_error("GET", e, f"id={id}")
            raise DatabaseError(f"Failed to retrieve entity: {str(e)}")

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[TModel]:
        """
        Get entity by a specific field.

        Args:
            field_name: Name of the field to search by
            field_value: Value to search for

        Returns:
            Entity if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
            ValidationError: If field doesn't exist
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation("GET_BY_FIELD", f"{field_name}={field_value}")

            filters = {field_name: field_value}
            results = await self.repository.get_multi(filters=filters, limit=1)

            return results[0] if results else None

        except Exception as e:
            self._log_error("GET_BY_FIELD", e, f"{field_name}={field_value}")
            raise DatabaseError(f"Failed to retrieve entity by {field_name}: {str(e)}")

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        include_relations: Optional[List[str]] = None,
    ) -> List[TModel]:
        """
        Get list of entities with filtering, ordering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            order_by: Field to order by (prefix with '-' for descending)
            include_relations: List of relations to include

        Returns:
            List of entities

        Raises:
            DatabaseError: If database operation fails
            ValidationError: If invalid parameters provided
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation(
                "LIST", f"skip={skip}, limit={limit}, filters={filters}"
            )

            # Validate limit
            if limit > 1000:
                raise validation_exception("Limit cannot exceed 1000")

            return await self.repository.get_multi(
                skip=skip, limit=limit, filters=filters, order_by=order_by
            )

        except ValidationError:
            raise
        except Exception as e:
            self._log_error("LIST", e, f"skip={skip}, limit={limit}")
            raise DatabaseError(f"Failed to list entities: {str(e)}")

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.

        Args:
            filters: Dictionary of field filters

        Returns:
            Number of entities matching filters

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation("COUNT", f"filters={filters}")

            return await self.repository.count(filters=filters)

        except Exception as e:
            self._log_error("COUNT", e, f"filters={filters}")
            raise DatabaseError(f"Failed to count entities: {str(e)}")

    async def create(self, obj_in: Union[TCreate, Dict[str, Any]]) -> TModel:
        """
        Create new entity.

        Args:
            obj_in: Entity data (Pydantic model or dict)

        Returns:
            Created entity

        Raises:
            DatabaseError: If database operation fails
            ValidationError: If data validation fails
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation("CREATE", f"data={type(obj_in)}")

            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.dict(exclude_unset=True)

            result = await self.repository.create(obj_data)
            self._log_operation(
                "CREATE_SUCCESS", f"id={getattr(result, 'id', 'unknown')}"
            )

            return result

        except Exception as e:
            self._log_error("CREATE", e)
            raise DatabaseError(f"Failed to create entity: {str(e)}")

    async def update(
        self, id: Any, obj_in: Union[TUpdate, Dict[str, Any]]
    ) -> Optional[TModel]:
        """
        Update entity.

        Args:
            id: Entity identifier
            obj_in: Update data (Pydantic model or dict)

        Returns:
            Updated entity if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation("UPDATE", f"id={id}")

            # Prepare update data
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)

            result = await self.repository.update(id, update_data)
            if result:
                self._log_operation("UPDATE_SUCCESS", f"id={id}")
            else:
                self._log_operation("UPDATE_NOT_FOUND", f"id={id}")

            return result

        except Exception as e:
            self._log_error("UPDATE", e, f"id={id}")
            raise DatabaseError(f"Failed to update entity: {str(e)}")

    async def delete(self, id: Any) -> bool:
        """
        Delete entity.

        Args:
            id: Entity identifier

        Returns:
            True if entity was deleted, False if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation("DELETE", f"id={id}")

            deleted = await self.repository.delete(id)
            if deleted:
                self._log_operation("DELETE_SUCCESS", f"id={id}")
            else:
                self._log_operation("DELETE_NOT_FOUND", f"id={id}")

            return deleted

        except Exception as e:
            self._log_error("DELETE", e, f"id={id}")
            raise DatabaseError(f"Failed to delete entity: {str(e)}")

    async def exists(self, id: Any) -> bool:
        """
        Check if entity exists.

        Args:
            id: Entity identifier

        Returns:
            True if entity exists, False otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if not self.repository:
                raise DatabaseError("Repository not initialized")

            self._log_operation("EXISTS", f"id={id}")

            entity = await self.repository.get(id)
            return entity is not None

        except Exception as e:
            self._log_error("EXISTS", e, f"id={id}")
            raise DatabaseError(f"Failed to check entity existence: {str(e)}")

    def validate_create_schema(self, data: Dict[str, Any]) -> TCreate:
        """
        Validate data against the create schema.

        Args:
            data: Data to validate

        Returns:
            Validated Pydantic model instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            if not self.create_schema:
                raise ValidationError("Create schema not defined")
            return self.create_schema(**data)
        except Exception as e:
            raise validation_exception(f"Create schema validation failed: {str(e)}")

    def validate_update_schema(self, data: Dict[str, Any]) -> TUpdate:
        """
        Validate data against the update schema.

        Args:
            data: Data to validate

        Returns:
            Validated Pydantic model instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            if not self.update_schema:
                raise ValidationError("Update schema not defined")
            return self.update_schema(**data)
        except Exception as e:
            raise validation_exception(f"Update schema validation failed: {str(e)}")
