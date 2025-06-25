"""
Core services module.

This module contains base classes and utilities for service layer implementation.
"""

from .base_service import BaseService
from .dependency_container import (
    ServiceContainer,
    ServiceLifetime,
    ServiceDescriptor,
    get_container,
    register_singleton,
    register_scoped,
    register_transient,
    resolve,
    get_service,
)
from .repository import (
    IRepository,
    BaseRepository,
    UnitOfWork,
)
from .service_configuration import configure_services

__all__ = [
    "BaseService",
    "ServiceContainer",
    "ServiceLifetime", 
    "ServiceDescriptor",
    "get_container",
    "register_singleton",
    "register_scoped",
    "register_transient",
    "resolve",
    "get_service",
    "IRepository",
    "BaseRepository",
    "UnitOfWork",
    "configure_services",
] 