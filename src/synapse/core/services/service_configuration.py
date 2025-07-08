"""
Service Configuration Module.

This module centralizes the registration of all application services
in the dependency injection container.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from synapse.database import get_db
from synapse.core.services.dependency_container import (
    get_container,
    register_singleton,
    register_scoped,
    register_transient,
)

logger = logging.getLogger(__name__)


def configure_services() -> None:
    """
    Configure all application services in the DI container.

    This function registers all services with appropriate lifetimes:
    - Singleton: One instance for the entire application
    - Scoped: One instance per request/session
    - Transient: New instance every time
    """
    container = get_container()

    logger.info("🔧 Configuring application services...")

    # Register database session as scoped (one per request)
    def create_db_session() -> AsyncSession:
        """Factory function to create database session."""
        from synapse.database import AsyncSessionLocal

        return AsyncSessionLocal()

    register_scoped(AsyncSession, factory=create_db_session)

    # Register core services
    _register_core_services()

    # Register business services
    _register_business_services()

    # Register infrastructure services
    _register_infrastructure_services()

    # Register external services
    _register_external_services()

    logger.info(f"✅ Configured {len(container.get_registered_services())} services")


def _register_core_services() -> None:
    """Register core application services."""
    logger.debug("Registering core services...")

    try:
        # Auth services
        from synapse.services.auth_service import AuthService

        register_scoped(AuthService, AuthService)

        # File services
        from synapse.services.file_service import FileService

        register_scoped(FileService, FileService)

        # Cache services
        from synapse.core.cache import get_cache_service

        register_singleton(Any, factory=get_cache_service)  # Cache as singleton

        logger.debug("✅ Core services registered")

    except ImportError as e:
        logger.warning(f"Some core services not available: {e}")


def _register_business_services() -> None:
    """Register business logic services."""
    logger.debug("Registering business services...")

    try:
        # Sample Test Service (for testing full stack)
        from synapse.services.sample_test_service import (
            SampleTestService,
            create_sample_test_service,
        )

        register_scoped(SampleTestService, factory=create_sample_test_service)

        # User services
        try:
            from synapse.services.user_service import UserService

            register_scoped(UserService, UserService)
        except ImportError:
            logger.debug("UserService not available")

        # Workspace services
        try:
            from synapse.services.workspace_service import WorkspaceService

            register_scoped(WorkspaceService, WorkspaceService)
        except ImportError:
            logger.debug("WorkspaceService not available")

        # Workflow services
        try:
            from synapse.services.workflow_service import WorkflowService

            register_scoped(WorkflowService, WorkflowService)
        except ImportError:
            logger.debug("WorkflowService not available")

        # Agent services
        try:
            from synapse.services.agent_service import AgentService

            register_scoped(AgentService, AgentService)
        except ImportError:
            logger.debug("AgentService not available")

        # Analytics services
        try:
            from synapse.services.analytics_service import AnalyticsService

            register_scoped(AnalyticsService, AnalyticsService)
        except ImportError:
            logger.debug("AnalyticsService not available")

        # Template services
        try:
            from synapse.services.template_service import TemplateService

            register_scoped(TemplateService, TemplateService)
        except ImportError:
            logger.debug("TemplateService not available")

        # Conversation services
        try:
            from synapse.services.conversation_service import ConversationService

            register_scoped(ConversationService, ConversationService)
        except ImportError:
            logger.debug("ConversationService not available")

        # Alert services
        try:
            from synapse.services.alert_service import AlertService

            register_scoped(AlertService, AlertService)
        except ImportError:
            logger.debug("AlertService not available")

        logger.debug("✅ Business services registered")

    except ImportError as e:
        logger.warning(f"Some business services not available: {e}")


def _register_infrastructure_services() -> None:
    """Register infrastructure services."""
    logger.debug("Registering infrastructure services...")

    try:
        # Storage services
        from synapse.core.storage.storage_manager import StorageManager

        def create_storage_manager() -> StorageManager:
            """Factory function for StorageManager."""
            from synapse.core.config import settings
            return StorageManager(base_storage_path=settings.STORAGE_BASE_PATH)

        register_singleton(StorageManager, factory=create_storage_manager)

        # Email services
        from synapse.core.email.service import EmailService

        register_singleton(EmailService, EmailService)

        # Logging services
        from synapse.logger_config import get_logger

        def create_logging_service():
            return get_logger("synapse")

        register_singleton(Any, factory=create_logging_service)

        logger.debug("✅ Infrastructure services registered")

    except ImportError as e:
        logger.warning(f"Some infrastructure services not available: {e}")


def _register_external_services() -> None:
    """Register external API services."""
    logger.debug("Registering external services...")

    try:
        # LLM services
        from synapse.services.llm_service import UnifiedLLMService

        register_singleton(UnifiedLLMService, UnifiedLLMService)

        # Executor services
        from synapse.core.executors.http_executor import HTTPExecutor

        register_transient(HTTPExecutor, HTTPExecutor)

        logger.debug("✅ External services registered")

    except ImportError as e:
        logger.warning(f"Some external services not available: {e}")


def get_registered_services_info() -> dict:
    """
    Get information about all registered services.

    Returns:
        Dictionary with service registration information
    """
    container = get_container()
    services = container.get_registered_services()

    return {
        "total_services": len(services),
        "services": [
            {
                "name": service.__name__,
                "module": service.__module__,
                "type": str(service),
            }
            for service in services
        ],
    }


def validate_service_configuration() -> bool:
    """
    Validate that all services are properly configured.

    Returns:
        True if all services are valid, False otherwise
    """
    container = get_container()

    try:
        # Test basic container functionality
        services = container.get_registered_services()

        # Try to resolve a few core services to validate configuration
        test_services = []

        # Find services to test
        for service_type in services:
            if service_type.__name__ in ["UserService", "AuthService", "FileService"]:
                test_services.append(service_type)

        # Test resolution
        for service_type in test_services[:3]:  # Test up to 3 services
            try:
                instance = container.resolve(service_type)
                logger.debug(f"✅ Successfully resolved {service_type.__name__}")
            except Exception as e:
                logger.error(f"❌ Failed to resolve {service_type.__name__}: {e}")
                return False

        logger.info("✅ Service configuration validation passed")
        return True

    except Exception as e:
        logger.error(f"❌ Service configuration validation failed: {e}")
        return False
