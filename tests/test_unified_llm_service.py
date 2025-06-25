"""
Unit tests for UnifiedLLMService.

This module contains comprehensive tests for the UnifiedLLMService class,
testing all methods with various scenarios including success cases,
error cases, and edge cases.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from synapse.services.llm_service import UnifiedLLMService, get_llm_service
from synapse.models.llm import LLM
from synapse.exceptions import (
    ModelNotFoundError,
    ProviderNotFoundError,
    LLMDatabaseError,
    DatabaseError
)


class TestUnifiedLLMService:
    """Test suite for UnifiedLLMService."""

    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Create a mock database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        return mock_session

    @pytest_asyncio.fixture
    async def llm_service(self, mock_db_session):
        """Create a UnifiedLLMService instance with mocked dependencies."""
        return UnifiedLLMService(mock_db_session)

    @pytest_asyncio.fixture
    def sample_llm_data(self):
        """Sample LLM data for testing."""
        return {
            "id": str(uuid4()),
            "name": "gpt-4",
            "provider": "openai",
            "model_version": "gpt-4-0613",
            "display_name": "OpenAI GPT-4",
            "cost_per_token_input": 0.00003,
            "cost_per_token_output": 0.00006,
            "cost_per_1k_tokens_input": 0.03,
            "cost_per_1k_tokens_output": 0.06,
            "max_tokens_supported": 8192,
            "supports_function_calling": True,
            "supports_vision": False,
            "supports_streaming": True,
            "context_window": 8192,
            "is_active": True,
            "llm_metadata": {},
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }

    @pytest_asyncio.fixture
    def mock_llm_model(self, sample_llm_data):
        """Create a mock LLM model."""
        mock_model = Mock()
        mock_model.to_dict.return_value = sample_llm_data
        mock_model.display_name = sample_llm_data["display_name"]
        mock_model.id = UUID(sample_llm_data["id"])
        mock_model.name = sample_llm_data["name"]
        mock_model.provider = sample_llm_data["provider"]
        return mock_model

    # Test get_available_models
    @pytest.mark.asyncio
    async def test_get_available_models_success(self, llm_service, mock_llm_model):
        """Test getting available models successfully."""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_llm_model]
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.get_available_models()

        # Assertions
        assert len(result) == 1
        assert result[0]["name"] == "gpt-4"
        assert result[0]["provider"] == "openai"
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_models_with_provider_filter(self, llm_service, mock_llm_model):
        """Test getting available models with provider filter."""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_llm_model]
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method with provider filter
        result = await llm_service.get_available_models(provider="openai")

        # Assertions
        assert len(result) == 1
        assert result[0]["provider"] == "openai"
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_models_empty_result(self, llm_service):
        """Test getting available models when none are found."""
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.get_available_models()

        # Assertions
        assert result == []
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_models_database_error(self, llm_service):
        """Test handling database error in get_available_models."""
        # Mock database error
        llm_service.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        # Execute method and expect exception
        with pytest.raises(DatabaseError):
            await llm_service.get_available_models()

    # Test get_available_providers
    @pytest.mark.asyncio
    async def test_get_available_providers_success(self, llm_service):
        """Test getting available providers successfully."""
        # Mock database query result with correct return format
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = ["openai", "claude", "gemini"]
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.get_available_providers()

        # Assertions
        assert "openai" in result
        assert "claude" in result
        assert "gemini" in result
        assert len(result) == 3
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_providers_database_error(self, llm_service):
        """Test handling database error in get_available_providers."""
        # Mock database error
        llm_service.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        # Execute method and expect exception
        with pytest.raises(DatabaseError):
            await llm_service.get_available_providers()

    # Test validate_model_provider
    @pytest.mark.asyncio
    async def test_validate_model_provider_valid(self, llm_service, mock_llm_model):
        """Test validating a valid model/provider combination."""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_llm_model
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.validate_model_provider("gpt-4", "openai")

        # Assertions
        assert result is True
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_model_provider_invalid(self, llm_service):
        """Test validating an invalid model/provider combination."""
        # Mock database query result (no model found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.validate_model_provider("invalid-model", "invalid-provider")

        # Assertions
        assert result is False
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_model_provider_database_error(self, llm_service):
        """Test handling database error in validate_model_provider."""
        # Mock database error
        llm_service.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        # Execute method (should not raise, just return False)
        result = await llm_service.validate_model_provider("gpt-4", "openai")

        # Assertions
        assert result is False

    # Test get_model_details
    @pytest.mark.asyncio
    async def test_get_model_details_success(self, llm_service, mock_llm_model, sample_llm_data):
        """Test getting model details successfully."""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_llm_model
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        llm_id = UUID(sample_llm_data["id"])
        result = await llm_service.get_model_details(llm_id)

        # Assertions
        assert result["id"] == sample_llm_data["id"]
        assert result["name"] == "gpt-4"
        assert result["provider"] == "openai"
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_model_details_not_found(self, llm_service):
        """Test getting details for non-existent model."""
        # Mock database query result (no model found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method and expect exception
        llm_id = uuid4()
        with pytest.raises(ModelNotFoundError):
            await llm_service.get_model_details(llm_id)

    @pytest.mark.asyncio
    async def test_get_model_details_database_error(self, llm_service):
        """Test handling database error in get_model_details."""
        # Mock database error
        llm_service.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        # Execute method and expect exception
        llm_id = uuid4()
        with pytest.raises(LLMDatabaseError):
            await llm_service.get_model_details(llm_id)

    # Test get_model_by_provider_and_name
    @pytest.mark.asyncio
    async def test_get_model_by_provider_and_name_found(self, llm_service, mock_llm_model, sample_llm_data):
        """Test getting model by provider and name when found."""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_llm_model
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.get_model_by_provider_and_name("openai", "gpt-4")

        # Assertions
        assert result is not None
        assert result["name"] == "gpt-4"
        assert result["provider"] == "openai"
        llm_service.db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_model_by_provider_and_name_not_found(self, llm_service):
        """Test getting model by provider and name when not found."""
        # Mock database query result (no model found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        llm_service.db.execute = AsyncMock(return_value=mock_result)

        # Execute method
        result = await llm_service.get_model_by_provider_and_name("invalid", "invalid")

        # Assertions
        assert result is None
        llm_service.db.execute.assert_called_once()

    # Test get_llm_service dependency function
    def test_get_llm_service_dependency(self):
        """Test the dependency injection function."""
        # Mock database session
        mock_db = Mock(spec=AsyncSession)
        
        # Execute function
        service = get_llm_service(db=mock_db)
        
        # Assertions
        assert isinstance(service, UnifiedLLMService)
        assert service.db == mock_db


class TestUnifiedLLMServiceIntegration:
    """Integration tests for UnifiedLLMService."""

    @pytest_asyncio.fixture
    async def llm_service_with_real_session(self):
        """Create service with a more realistic mock session."""
        mock_session = AsyncMock(spec=AsyncSession)
        return UnifiedLLMService(mock_session)

    @pytest_asyncio.fixture
    def mock_llm_model(self):
        """Create a mock LLM model for integration tests."""
        sample_data = {
            "id": str(uuid4()),
            "name": "gpt-4",
            "provider": "openai",
            "model_version": "gpt-4-0613",
            "display_name": "OpenAI GPT-4",
        }
        mock_model = Mock()
        mock_model.to_dict.return_value = sample_data
        mock_model.display_name = sample_data["display_name"]
        mock_model.id = UUID(sample_data["id"])
        mock_model.name = sample_data["name"]
        mock_model.provider = sample_data["provider"]
        return mock_model

    @pytest.mark.asyncio
    async def test_service_initialization(self, llm_service_with_real_session):
        """Test that the service initializes correctly."""
        service = llm_service_with_real_session
        
        # Check that service has the expected attributes
        assert hasattr(service, 'db')
        assert hasattr(service, 'logger')
        # Logger name is 'UnifiedLLMService' not the full module path
        assert service.logger.name == 'UnifiedLLMService'

    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(self, llm_service_with_real_session, mock_llm_model):
        """Test a sequence of operations to ensure state consistency."""
        service = llm_service_with_real_session
        
        # Mock database responses for multiple operations
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_llm_model]
        mock_result.scalar_one_or_none.return_value = mock_llm_model
        service.db.execute = AsyncMock(return_value=mock_result)
        
        # Execute multiple operations
        models = await service.get_available_models()
        providers = await service.get_available_providers()
        is_valid = await service.validate_model_provider("gpt-4", "openai")
        
        # Assertions
        assert len(models) == 1
        assert is_valid is True
        assert service.db.execute.call_count == 3 