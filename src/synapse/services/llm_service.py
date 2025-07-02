"""
Unified LLM Service - Central service for accessing LLM data from database.

This service provides a unified interface for:
- Fetching available models and providers from database
- Managing user-specific API keys via user_variables
- Real LLM generation with multiple providers
- Replacing hardcoded enum-based data with dynamic database queries
"""

import logging
import time
from typing import Optional, List, Dict, Any
from uuid import UUID
from functools import wraps

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, select, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from synapse.database import get_async_db
from synapse.models.llm import LLM
from synapse.models.user_variable import UserVariable
from synapse.exceptions import (
    NotFoundError,
    ValidationError,
    DatabaseError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidModelProviderCombinationError,
    LLMDatabaseError,
)

# Sistema de tracing distribuído
from synapse.core.tracing import trace_operation, trace_database_operation

# Import for real LLM functionality
try:
    import openai
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from synapse.core.config import settings

logger = logging.getLogger(__name__)


class LLMResponse:
    """Response class for LLM operations"""

    def __init__(
        self,
        content: str,
        model: str,
        provider: str,
        usage: dict = None,
        metadata: dict = None,
    ):
        self.content = content
        self.model = model
        self.provider = provider
        self.usage = usage or {}
        self.metadata = metadata or {}


def log_performance(operation_name: str):
    """Decorator to log performance metrics for service operations."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            operation_id = f"{operation_name}_{id(self)}"

            try:
                self.logger.debug(
                    f"Starting operation: {operation_name} [ID: {operation_id}]"
                )
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
    Unified LLM Service for accessing LLM data from database and real LLM operations.

    This service provides a central interface for:
    - Fetching available models and providers from database
    - Managing user-specific API keys via user_variables
    - Real LLM text generation with multiple providers
    - Validating model/provider combinations
    - Getting detailed model information
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize Unified LLM Service.

        Args:
            db: Async database session
        """
        self.db = db
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.settings = settings
        self._initialize_llm_clients()

    def _initialize_llm_clients(self):
        """Initialize LLM provider clients"""
        self.clients = {}
        self.providers = {}

        # OpenAI
        if OPENAI_AVAILABLE and self.settings.OPENAI_API_KEY:
            try:
                self.clients["openai"] = AsyncOpenAI(
                    api_key=self.settings.OPENAI_API_KEY
                )
                self.providers["openai"] = {
                    "name": "OpenAI",
                    "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                    "available": True,
                }
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.providers["openai"] = {"available": False, "error": str(e)}

        # Anthropic
        if ANTHROPIC_AVAILABLE and self.settings.ANTHROPIC_API_KEY:
            try:
                self.clients["anthropic"] = anthropic.AsyncAnthropic(
                    api_key=self.settings.ANTHROPIC_API_KEY
                )
                self.providers["anthropic"] = {
                    "name": "Anthropic",
                    "models": [
                        "claude-3-opus-20240229",
                        "claude-3-sonnet-20240229",
                        "claude-3-haiku-20240307",
                    ],
                    "available": True,
                }
                logger.info("Anthropic provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
                self.providers["anthropic"] = {"available": False, "error": str(e)}

        # Google
        if GOOGLE_AVAILABLE and self.settings.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=self.settings.GOOGLE_API_KEY)
                self.providers["google"] = {
                    "name": "Google",
                    "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                    "available": True,
                }
                logger.info("Google provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google: {e}")
                self.providers["google"] = {"available": False, "error": str(e)}

    # === USER API KEYS MANAGEMENT ===

    def get_user_api_key(
        self, db_sync: Session, user_id, provider: str
    ) -> Optional[str]:
        """
        Get user-specific API key from user_variables table.

        Args:
            db_sync: Synchronous database session
            user_id: User UUID
            provider: Provider name (openai, anthropic, google, etc.)

        Returns:
            Decrypted API key or None if not found
        """
        try:
            provider_key_mapping = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "claude": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "gemini": "GOOGLE_API_KEY",
                "grok": "GROK_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "llama": "LLAMA_API_KEY",
            }

            key_name = provider_key_mapping.get(provider.lower())
            if not key_name:
                self.logger.warning(f"Provider {provider} not supported")
                return None

            user_variable = (
                db_sync.query(UserVariable)
                .filter(
                    UserVariable.user_id == user_id,
                    UserVariable.key == key_name,
                    UserVariable.category.in_(["api_keys", "ai"]),
                    UserVariable.is_active == True,
                )
                .first()
            )

            if user_variable:
                return user_variable.get_decrypted_value()

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting user API key for {user_id}/{provider}: {e}"
            )
            return None

    def create_or_update_user_api_key(
        self, db_sync: Session, user_id, provider: str, api_key: str
    ) -> bool:
        """
        Create or update user API key in user_variables.

        Args:
            db_sync: Synchronous database session
            user_id: User UUID
            provider: Provider name
            api_key: API key to store

        Returns:
            True if successful
        """
        try:
            provider_key_mapping = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "grok": "GROK_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "llama": "LLAMA_API_KEY",
            }

            key_name = provider_key_mapping.get(provider.lower())
            if not key_name:
                return False

            existing_variable = (
                db_sync.query(UserVariable)
                .filter(
                    UserVariable.user_id == user_id,
                    UserVariable.key == key_name,
                    UserVariable.category == "api_keys",
                )
                .first()
            )

            if existing_variable:
                existing_variable.set_encrypted_value(api_key)
                existing_variable.is_active = True
            else:
                new_variable = UserVariable(
                    user_id=user_id,
                    key=key_name,
                    category="api_keys",
                    description=f"API key for {provider.title()} provider",
                    is_active=True,
                )
                new_variable.set_encrypted_value(api_key)
                db_sync.add(new_variable)

            db_sync.commit()
            return True

        except Exception as e:
            self.logger.error(f"Error creating/updating user API key: {e}")
            db_sync.rollback()
            return False

    def list_user_api_keys(self, db_sync: Session, user_id) -> List[Dict[str, Any]]:
        """
        List all user API keys from user_variables.

        Args:
            db_sync: Synchronous database session
            user_id: User UUID

        Returns:
            List of API key information
        """
        try:
            provider_key_mapping = {
                "OPENAI_API_KEY": "openai",
                "ANTHROPIC_API_KEY": "anthropic",
                "GOOGLE_API_KEY": "google",
                "GROK_API_KEY": "grok",
                "DEEPSEEK_API_KEY": "deepseek",
                "LLAMA_API_KEY": "llama",
            }

            api_key_variables = (
                db_sync.query(UserVariable)
                .filter(
                    UserVariable.user_id == user_id,
                    UserVariable.category == "api_keys",
                    UserVariable.is_active == True,
                )
                .all()
            )

            result = []
            for variable in api_key_variables:
                provider = provider_key_mapping.get(variable.key)
                if provider:
                    result.append(
                        {
                            "provider": provider,
                            "key_name": variable.key,
                            "description": variable.description,
                            "created_at": (
                                variable.created_at.isoformat()
                                if variable.created_at
                                else None
                            ),
                            "updated_at": (
                                variable.updated_at.isoformat()
                                if variable.updated_at
                                else None
                            ),
                            "has_value": bool(variable.encrypted_value),
                        }
                    )

            return result

        except Exception as e:
            self.logger.error(f"Error listing user API keys for {user_id}: {e}")
            return []

    def delete_user_api_key(self, db_sync: Session, user_id, provider: str) -> bool:
        """
        Delete user API key from user_variables.

        Args:
            db_sync: Synchronous database session
            user_id: User UUID
            provider: Provider name

        Returns:
            True if successful
        """
        try:
            provider_key_mapping = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "grok": "GROK_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "llama": "LLAMA_API_KEY",
            }

            key_name = provider_key_mapping.get(provider.lower())
            if not key_name:
                return False

            variable = (
                db_sync.query(UserVariable)
                .filter(
                    UserVariable.user_id == user_id,
                    UserVariable.key == key_name,
                    UserVariable.category == "api_keys",
                )
                .first()
            )

            if variable:
                db_sync.delete(variable)
                db_sync.commit()
                return True

            return False

        except Exception as e:
            self.logger.error(
                f"Error deleting user API key for {user_id}/{provider}: {e}"
            )
            db_sync.rollback()
            return False

    # === REAL LLM GENERATION ===

    async def generate_text_for_user(
        self,
        prompt: str,
        user_id,
        db_sync: Session,
        model: str = None,
        provider: str = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using user-specific API key or fallback to system key.

        Args:
            prompt: Text prompt
            user_id: User UUID
            db_sync: Synchronous database session
            model: Model name
            provider: Provider name
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated text
        """
        if not provider:
            provider = getattr(self.settings, "LLM_DEFAULT_PROVIDER", "openai")

        # Try user-specific API key first
        user_api_key = self.get_user_api_key(db_sync, user_id, provider)

        if user_api_key:
            self.logger.info(f"Using user-specific API key for {user_id}/{provider}")
            return await self._generate_with_custom_key(
                prompt, provider, model, user_api_key, **kwargs
            )
        else:
            # Fallback to system API key
            self.logger.info(f"Using system API key for {provider}")
            return await self.generate_text(prompt, model, provider, **kwargs)

    async def chat_completion_for_user(
        self,
        messages: list,
        user_id,
        db: Session,
        model: str = None,
        provider: str = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate chat completion using user-specific API key or fallback to system key.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: User UUID
            db: Database session (synchronous)
            model: Model name
            provider: Provider name
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated text
        """
        if not provider:
            provider = getattr(self.settings, "LLM_DEFAULT_PROVIDER", "openai")

        # Try user-specific API key first
        user_api_key = self.get_user_api_key(db, user_id, provider)

        if user_api_key:
            self.logger.info(
                f"Using user-specific API key for chat completion {user_id}/{provider}"
            )
            return await self._chat_completion_with_custom_key(
                messages, provider, model, user_api_key, **kwargs
            )
        else:
            # Fallback to system API key
            self.logger.info(f"Using system API key for chat completion {provider}")
            return await self.chat_completion(messages, model, provider, **kwargs)

    async def generate_text(
        self,
        prompt: str,
        model: str = None,
        provider: str = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using system API keys.

        Args:
            prompt: Text prompt
            model: Model name
            provider: Provider name
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated text
        """
        if not provider:
            provider = getattr(self.settings, "LLM_DEFAULT_PROVIDER", "openai")

        if not model:
            model = self._get_default_model(provider)

        if provider == "openai" and self.providers.get("openai", {}).get("available"):
            return await self._generate_openai(prompt, model, **kwargs)
        elif provider == "anthropic" and self.providers.get("anthropic", {}).get(
            "available"
        ):
            return await self._generate_anthropic(prompt, model, **kwargs)
        elif provider == "google" and self.providers.get("google", {}).get("available"):
            return await self._generate_google(prompt, model, **kwargs)
        else:
            # Mock response if provider not available
            return LLMResponse(
                content=f"Provider {provider} not available. Mock response for: {prompt[:50]}...",
                model=model or "mock-model",
                provider=provider or "mock",
                usage={"tokens": 100},
                metadata={"mock": True, "reason": "provider_not_available"},
            )

    async def chat_completion(
        self,
        messages: list,
        model: str = None,
        provider: str = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate chat completion using system API keys.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name
            provider: Provider name
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated text
        """
        if not provider:
            provider = getattr(self.settings, "LLM_DEFAULT_PROVIDER", "openai")

        if not model:
            model = self._get_default_model(provider)

        if provider == "openai" and self.providers.get("openai", {}).get("available"):
            return await self._chat_completion_openai(messages, model, **kwargs)
        elif provider == "anthropic" and self.providers.get("anthropic", {}).get(
            "available"
        ):
            return await self._chat_completion_anthropic(messages, model, **kwargs)
        elif provider == "google" and self.providers.get("google", {}).get("available"):
            return await self._chat_completion_google(messages, model, **kwargs)
        else:
            # Mock response if provider not available
            last_message = messages[-1] if messages else {"content": "No messages"}
            return LLMResponse(
                content=f"Provider {provider} not available. Mock response for: {last_message.get('content', '')[:50]}...",
                model=model or "mock-model",
                provider=provider or "mock",
                usage={"tokens": 100},
                metadata={"mock": True, "reason": "provider_not_available"},
            )

    async def _generate_with_custom_key(
        self, prompt: str, provider: str, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate text using custom API key"""
        if not model:
            model = self._get_default_model(provider)

        try:
            if provider == "openai":
                return await self._generate_openai_with_key(
                    prompt, model, api_key, **kwargs
                )
            elif provider == "anthropic":
                return await self._generate_anthropic_with_key(
                    prompt, model, api_key, **kwargs
                )
            elif provider == "google":
                return await self._generate_google_with_key(
                    prompt, model, api_key, **kwargs
                )
            else:
                return LLMResponse(
                    content=f"Provider {provider} not supported for custom keys. Mock response.",
                    model=model,
                    provider=provider,
                    usage={"tokens": 100},
                    metadata={"mock": True, "reason": "provider_not_supported"},
                )
        except Exception as e:
            self.logger.error(f"Error generating with custom key ({provider}): {e}")
            raise Exception(f"Error in text generation: {str(e)}")

    async def _generate_openai(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using OpenAI with system key"""
        try:
            client = self.clients["openai"]
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={"finish_reason": response.choices[0].finish_reason},
            )
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _generate_openai_with_key(
        self, prompt: str, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate text using OpenAI with custom key"""
        try:
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "user_api_key": True,
                },
            )
        except Exception as e:
            self.logger.error(f"OpenAI API error with custom key: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _generate_anthropic(
        self, prompt: str, model: str, **kwargs
    ) -> LLMResponse:
        """Generate text using Anthropic with system key"""
        # Placeholder implementation
        return LLMResponse(
            content=f"[Anthropic] Mock response for: {prompt[:50]}...",
            model=model,
            provider="anthropic",
            usage={"tokens": 100},
            metadata={"mock": True, "reason": "implementation_pending"},
        )

    async def _generate_anthropic_with_key(
        self, prompt: str, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate text using Anthropic with custom key"""
        # Placeholder implementation
        return LLMResponse(
            content=f"[Anthropic Custom] Mock response for: {prompt[:50]}...",
            model=model,
            provider="anthropic",
            usage={"tokens": 100},
            metadata={
                "mock": True,
                "user_api_key": True,
                "reason": "implementation_pending",
            },
        )

    async def _generate_google(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using Google with system key"""
        # Placeholder implementation
        return LLMResponse(
            content=f"[Google] Mock response for: {prompt[:50]}...",
            model=model,
            provider="google",
            usage={"tokens": 100},
            metadata={"mock": True, "reason": "implementation_pending"},
        )

    async def _generate_google_with_key(
        self, prompt: str, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate text using Google with custom key"""
        # Placeholder implementation
        return LLMResponse(
            content=f"[Google Custom] Mock response for: {prompt[:50]}...",
            model=model,
            provider="google",
            usage={"tokens": 100},
            metadata={
                "mock": True,
                "user_api_key": True,
                "reason": "implementation_pending",
            },
        )

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-sonnet-20240229",
            "google": "gemini-1.5-pro",
        }
        return defaults.get(provider, "gpt-4o")

    # === DATABASE OPERATIONS (EXISTING) ===

    @trace_database_operation("select", table="llms")
    @log_performance("get_available_models")
    async def get_available_models(
        self, provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
            raise LLMDatabaseError(
                "Failed to fetch available models from database"
            ) from e
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
            stmt = select(LLM.provider).where(LLM.is_active == True).distinct()

            result = await self.db.execute(stmt)
            providers = result.scalars().all()

            # Filter out None values
            provider_list = [provider for provider in providers if provider]

            self.logger.info(
                f"Found {len(provider_list)} available providers: {provider_list}"
            )
            return provider_list

        except SQLAlchemyError as e:
            self.logger.error(f"Database error while getting available providers: {e}")
            raise LLMDatabaseError(
                "Failed to fetch available providers from database"
            ) from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting available providers: {e}"
            )
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
            self.logger.debug(
                f"Validating model '{model_name}' for provider '{provider}'"
            )

            # Query for exact match of active model/provider combination
            stmt = select(LLM).where(
                and_(
                    LLM.name == model_name,
                    LLM.provider == provider,
                    LLM.is_active == True,
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
            stmt = select(LLM).where(LLM.id == llm_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                self.logger.warning(f"LLM model with ID {llm_id} not found in database")
                raise ModelNotFoundError(
                    f"LLM model with ID {llm_id} not found",
                    details={"llm_id": str(llm_id)},
                )

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
    async def get_model_by_provider_and_name(
        self, provider: str, model_name: str
    ) -> Optional[Dict[str, Any]]:
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
            stmt = select(LLM).where(
                and_(
                    LLM.provider == provider,
                    LLM.name == model_name,
                    LLM.is_active == True,
                )
            )

            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                model_dict = model.to_dict()
                self.logger.info(f"Found model: {model.display_name}")
                return model_dict

            self.logger.debug(
                f"Model '{model_name}' not found for provider '{provider}'"
            )
            return None

        except Exception as e:
            self.logger.error(f"Failed to get model by provider and name: {e}")
            raise DatabaseError("Failed to fetch model by provider and name") from e

    @trace_database_operation("select", table="llms")
    @log_performance("get_cheapest_model")
    async def get_cheapest_model(
        self, provider: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
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
            stmt = select(LLM).where(LLM.is_active == True)

            # Add provider filter if specified
            if provider:
                stmt = stmt.where(LLM.provider == provider)

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
    async def get_models_with_capabilities(
        self, **capabilities
    ) -> List[Dict[str, Any]]:
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
            stmt = select(LLM).where(LLM.is_active == True)

            # Apply capability filters
            for capability, value in capabilities.items():
                if hasattr(LLM, capability):
                    stmt = stmt.where(getattr(LLM, capability) == value)

            result = await self.db.execute(stmt)
            models = result.scalars().all()
            model_list = [model.to_dict() for model in models]

            self.logger.info(
                f"Found {len(model_list)} models with specified capabilities"
            )
            return model_list

        except Exception as e:
            self.logger.error(f"Failed to get models with capabilities: {e}")
            raise DatabaseError("Failed to fetch models with capabilities") from e

    async def _chat_completion_with_custom_key(
        self, messages: list, provider: str, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using custom API key"""
        if not model:
            model = self._get_default_model(provider)

        try:
            if provider == "openai":
                return await self._chat_completion_openai_with_key(
                    messages, model, api_key, **kwargs
                )
            elif provider == "anthropic":
                return await self._chat_completion_anthropic_with_key(
                    messages, model, api_key, **kwargs
                )
            elif provider == "google":
                return await self._chat_completion_google_with_key(
                    messages, model, api_key, **kwargs
                )
            else:
                last_message = messages[-1] if messages else {"content": "No messages"}
                return LLMResponse(
                    content=f"Provider {provider} not supported for custom keys. Mock response.",
                    model=model,
                    provider=provider,
                    usage={"tokens": 100},
                    metadata={"mock": True, "reason": "provider_not_supported"},
                )
        except Exception as e:
            self.logger.error(
                f"Error generating chat completion with custom key ({provider}): {e}"
            )
            raise Exception(f"Error in chat completion: {str(e)}")

    async def _chat_completion_openai(
        self, messages: list, model: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using OpenAI with system key"""
        try:
            client = self.clients["openai"]
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={"finish_reason": response.choices[0].finish_reason},
            )
        except Exception as e:
            self.logger.error(f"OpenAI chat completion API error: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _chat_completion_openai_with_key(
        self, messages: list, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using OpenAI with custom key"""
        try:
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "user_api_key": True,
                },
            )
        except Exception as e:
            self.logger.error(f"OpenAI chat completion API error with custom key: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _chat_completion_anthropic(
        self, messages: list, model: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Anthropic with system key"""
        # Placeholder implementation
        last_message = messages[-1] if messages else {"content": "No messages"}
        return LLMResponse(
            content=f"[Anthropic] Mock chat response for: {last_message.get('content', '')[:50]}...",
            model=model,
            provider="anthropic",
            usage={"tokens": 100},
            metadata={"mock": True, "reason": "implementation_pending"},
        )

    async def _chat_completion_anthropic_with_key(
        self, messages: list, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Anthropic with custom key"""
        # Placeholder implementation
        last_message = messages[-1] if messages else {"content": "No messages"}
        return LLMResponse(
            content=f"[Anthropic Custom] Mock chat response for: {last_message.get('content', '')[:50]}...",
            model=model,
            provider="anthropic",
            usage={"tokens": 100},
            metadata={
                "mock": True,
                "user_api_key": True,
                "reason": "implementation_pending",
            },
        )

    async def _chat_completion_google(
        self, messages: list, model: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Google with system key"""
        # Placeholder implementation
        last_message = messages[-1] if messages else {"content": "No messages"}
        return LLMResponse(
            content=f"[Google] Mock chat response for: {last_message.get('content', '')[:50]}...",
            model=model,
            provider="google",
            usage={"tokens": 100},
            metadata={"mock": True, "reason": "implementation_pending"},
        )

    async def _chat_completion_google_with_key(
        self, messages: list, model: str, api_key: str, **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Google with custom key"""
        # Placeholder implementation
        last_message = messages[-1] if messages else {"content": "No messages"}
        return LLMResponse(
            content=f"[Google Custom] Mock chat response for: {last_message.get('content', '')[:50]}...",
            model=model,
            provider="google",
            usage={"tokens": 100},
            metadata={
                "mock": True,
                "user_api_key": True,
                "reason": "implementation_pending",
            },
        )


# Dependency injection function
def get_llm_service(db: AsyncSession = Depends(get_async_db)) -> UnifiedLLMService:
    """
    Dependency injection function for UnifiedLLMService.

    Args:
        db: Database session from dependency injection

    Returns:
        UnifiedLLMService instance (database-backed, NOT mocked)
    """
    # Return the database-backed UnifiedLLMService from this file, not the mocked one
    return UnifiedLLMService(db)


# Direct access function (not for dependency injection)
def get_llm_service_direct() -> UnifiedLLMService:
    """
    Direct access function for UnifiedLLMService (not for FastAPI dependency injection).
    Creates a new database session internally.

    Returns:
        UnifiedLLMService instance with its own database session
    """
    from synapse.database import AsyncSessionLocal

    db = AsyncSessionLocal()
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
    "get_llm_service_direct",
    "register_llm_service",
]

# Alias for backward compatibility
LLMService = UnifiedLLMService
