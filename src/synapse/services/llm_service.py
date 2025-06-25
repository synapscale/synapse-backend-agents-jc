"""
Unified LLM Service - Central service for accessing LLM data from database.

This service provides a unified interface for accessing LLM models and providers
stored in the database, replacing hardcoded enums and static configurations.
"""

import logging
import time
from typing import Optional, List, Dict, Any
from uuid import UUID
from functools import wraps

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from synapse.database import get_db
from synapse.models.llm import LLM
from synapse.exceptions import (
    NotFoundError, 
    ValidationError, 
    DatabaseError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidModelProviderCombinationError,
    LLMDatabaseError
)

# Sistema de tracing distribuído
from synapse.core.tracing import trace_operation, trace_database_operation

logger = logging.getLogger(__name__)


def log_performance(operation_name: str):
    """Decorator to log performance metrics for service operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            operation_id = f"{operation_name}_{id(self)}"
            
            try:
                self.logger.debug(f"Starting operation: {operation_name} [ID: {operation_id}]")
                result = await func(self, *args, **kwargs)
                
                duration = time.time() - start_time
                self.logger.info(
                    f"Operation completed successfully: {operation_name} "
                    f"[Duration: {duration:.3f}s] [ID: {operation_id}]"
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(
                    f"Operation failed: {operation_name} "
                    f"[Duration: {duration:.3f}s] [Error: {type(e).__name__}: {str(e)}] "
                    f"[ID: {operation_id}]"
                )
                raise
        return wrapper
    return decorator


class UnifiedLLMService:
    """
    Unified LLM Service for accessing LLM data from database.
    
    This service provides a central interface for:
    - Fetching available models and providers from database
    - Validating model/provider combinations
    - Getting detailed model information
    - Replacing hardcoded enum-based data with dynamic database queries
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize Unified LLM Service.
        
        Args:
            db: Async database session
        """
        self.db = db
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @trace_database_operation("select", table="llms")
    @log_performance("get_available_models")
    async def get_available_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of available LLM models from database.
        
        Args:
            provider: Optional provider filter (e.g., 'openai', 'claude')
            
        Returns:
            List of model dictionaries with complete information
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            self.logger.debug(f"Getting available models for provider: {provider}")
            
            # Build query for active models
            stmt = select(LLM).where(LLM.is_active == True)
            
            # Apply provider filter if specified
            if provider:
                stmt = stmt.where(LLM.provider == provider)
            
            # Execute query and convert to dictionaries
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            model_list = [model.to_dict() for model in models]
            
            self.logger.info(f"Found {len(model_list)} available models")
            return model_list
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while getting available models: {e}")
            raise LLMDatabaseError("Failed to fetch available models from database") from e
        except Exception as e:
            self.logger.error(f"Unexpected error while getting available models: {e}")
            raise DatabaseError("Failed to fetch available models") from e
    
    @trace_database_operation("select", table="llms")
    @log_performance("get_available_providers")
    async def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers from database.
        
        Returns:
            List of unique provider names
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            self.logger.debug("Getting available providers")
            
            # Query distinct providers from active models using modern SQLAlchemy syntax
            stmt = select(LLM.provider).filter(
                LLM.is_active == True
            ).distinct()
            
            result = await self.db.execute(stmt)
            providers = result.scalars().all()
            
            # Filter out None values
            provider_list = [provider for provider in providers if provider]
            
            self.logger.info(f"Found {len(provider_list)} available providers: {provider_list}")
            return provider_list
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while getting available providers: {e}")
            raise LLMDatabaseError("Failed to fetch available providers from database") from e
        except Exception as e:
            self.logger.error(f"Unexpected error while getting available providers: {e}")
            raise DatabaseError("Failed to fetch available providers") from e
    
    @trace_database_operation("select", table="llms")
    @log_performance("validate_model_provider")
    async def validate_model_provider(self, model_name: str, provider: str) -> bool:
        """
        Validate if a model/provider combination exists and is active.
        
        Args:
            model_name: Name of the model to validate
            provider: Provider name to validate
            
        Returns:
            True if combination is valid and active, False otherwise
        """
        try:
            self.logger.debug(f"Validating model '{model_name}' for provider '{provider}'")
            
            # Query for exact match of active model/provider combination
            stmt = select(LLM).filter(
                and_(
                    LLM.name == model_name,
                    LLM.provider == provider,
                    LLM.is_active == True
                )
            )
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            is_valid = model is not None
            self.logger.debug(f"Model/provider validation result: {is_valid}")
            return is_valid
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while validating model/provider: {e}")
            # Return False on database error to be safe
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error while validating model/provider: {e}")
            # Return False on error to be safe
            return False
    
    @trace_database_operation("select", table="llms")
    @log_performance("get_model_details")
    async def get_model_details(self, llm_id: UUID) -> Dict[str, Any]:
        """
        Get detailed information for a specific LLM by ID.
        
        Args:
            llm_id: UUID of the LLM model
            
        Returns:
            Dictionary with complete model information
            
        Raises:
            NotFoundError: If model with given ID is not found
            DatabaseError: If database query fails
        """
        try:
            self.logger.debug(f"Getting model details for ID: {llm_id}")
            
            # Query for specific model by ID
            stmt = select(LLM).filter(LLM.id == llm_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                self.logger.warning(f"LLM model with ID {llm_id} not found in database")
                raise ModelNotFoundError(f"LLM model with ID {llm_id} not found", 
                                        details={"llm_id": str(llm_id)})
            
            model_dict = model.to_dict()
            self.logger.info(f"Retrieved model details for: {model.display_name}")
            return model_dict
            
        except ModelNotFoundError:
            # Re-raise ModelNotFoundError as-is
            raise
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while getting model details: {e}")
            raise LLMDatabaseError("Failed to fetch model details from database") from e
        except Exception as e:
            self.logger.error(f"Unexpected error while getting model details: {e}")
            raise DatabaseError("Failed to fetch model details") from e
    
    @trace_database_operation("select", table="llms")
    @log_performance("get_model_by_provider_and_name")
    async def get_model_by_provider_and_name(self, provider: str, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model details by provider and model name.
        
        Args:
            provider: Provider name (e.g., 'openai', 'claude')
            model_name: Model name (e.g., 'gpt-4', 'claude-3-sonnet')
            
        Returns:
            Model dictionary if found, None otherwise
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            self.logger.debug(f"Getting model '{model_name}' for provider '{provider}'")
            
            # Query for model by provider and name
            stmt = select(LLM).filter(
                and_(
                    LLM.provider == provider,
                    LLM.name == model_name,
                    LLM.is_active == True
                )
            )
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                model_dict = model.to_dict()
                self.logger.info(f"Found model: {model.display_name}")
                return model_dict
            
            self.logger.debug(f"Model '{model_name}' not found for provider '{provider}'")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get model by provider and name: {e}")
            raise DatabaseError("Failed to fetch model by provider and name") from e
    
    @trace_database_operation("select", table="llms")
    @log_performance("get_cheapest_model")
    async def get_cheapest_model(self, provider: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the cheapest available model (based on input token cost).
        
        Args:
            provider: Optional provider filter
            
        Returns:
            Cheapest model dictionary if found, None otherwise
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            self.logger.debug(f"Getting cheapest model for provider: {provider}")
            
            # Start with active models query
            stmt = select(LLM).filter(LLM.is_active == True)
            
            # Add provider filter if specified
            if provider:
                stmt = stmt.filter(LLM.provider == provider)
            
            # Order by input cost (ascending) to get cheapest first
            stmt = stmt.order_by(LLM.cost_per_token_input.asc())
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                model_dict = model.to_dict()
                self.logger.info(f"Found cheapest model: {model.display_name}")
                return model_dict
            
            self.logger.debug("No cheapest model found")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get cheapest model: {e}")
            raise DatabaseError("Failed to fetch cheapest model") from e
    
    @trace_database_operation("select", table="llms")
    @log_performance("get_models_with_capabilities")
    async def get_models_with_capabilities(self, **capabilities) -> List[Dict[str, Any]]:
        """
        Get models filtered by specific capabilities.
        
        Args:
            **capabilities: Capability filters (e.g., supports_vision=True, supports_function_calling=True)
            
        Returns:
            List of models matching the capability criteria
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            self.logger.debug(f"Getting models with capabilities: {capabilities}")
            
            # Start with active models query
            stmt = select(LLM).filter(LLM.is_active == True)
            
            # Apply capability filters
            for capability, value in capabilities.items():
                if hasattr(LLM, capability):
                    stmt = stmt.filter(getattr(LLM, capability) == value)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            model_list = [model.to_dict() for model in models]
            
            self.logger.info(f"Found {len(model_list)} models with specified capabilities")
            return model_list
            
        except Exception as e:
            self.logger.error(f"Failed to get models with capabilities: {e}")
            raise DatabaseError("Failed to fetch models with capabilities") from e


# Dependency injection function
def get_llm_service(db: AsyncSession = Depends(get_db)) -> UnifiedLLMService:
    """
    Dependency injection function for UnifiedLLMService.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        UnifiedLLMService instance
    """
    return UnifiedLLMService(db)


def register_llm_service():
    """
    Register the LLM service for dependency injection.
    This function can be used for service registration if needed.
    """
    logger.info("LLM Service registered successfully")
    return True 


# Export main classes and functions
__all__ = [
    "UnifiedLLMService",
    "LLMService",  # Alias for compatibility
    "get_llm_service",
    "register_llm_service",
]

# Alias for backward compatibility
LLMService = UnifiedLLMService 