"""
Dependency Injection Container.

This module implements a dependency injection container for managing
service instances and their lifetimes throughout the application.
"""

import logging
from typing import Dict, Type, TypeVar, Callable, Any, Optional, List
from enum import Enum
from abc import ABC, abstractmethod
import inspect
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from synapse.database import get_db

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime enums."""
    
    SINGLETON = "singleton"  # One instance for the entire application
    SCOPED = "scoped"        # One instance per request/session
    TRANSIENT = "transient"  # New instance every time


class ServiceDescriptor:
    """Describes how a service should be registered and created."""
    
    def __init__(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.SCOPED,
        dependencies: Optional[List[Type]] = None,
    ):
        """
        Initialize service descriptor.
        
        Args:
            service_type: The service interface or class type
            implementation_type: The concrete implementation type
            factory: Factory function to create the service
            lifetime: Service lifetime
            dependencies: List of dependency types
        """
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.lifetime = lifetime
        self.dependencies = dependencies or []
        
        # Validate configuration
        if not factory and not implementation_type:
            raise ValueError("Either implementation_type or factory must be provided")


class ServiceContainer:
    """
    Dependency injection container for managing service instances.
    
    Supports singleton, scoped, and transient lifetimes with automatic
    dependency resolution.
    """
    
    def __init__(self):
        """Initialize the service container."""
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def register_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> 'ServiceContainer':
        """
        Register a service with singleton lifetime.
        
        Args:
            service_type: Service interface type
            implementation_type: Implementation type
            factory: Factory function
            
        Returns:
            Self for chaining
        """
        return self._register(
            service_type,
            implementation_type,
            factory,
            ServiceLifetime.SINGLETON
        )
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> 'ServiceContainer':
        """
        Register a service with scoped lifetime.
        
        Args:
            service_type: Service interface type
            implementation_type: Implementation type
            factory: Factory function
            
        Returns:
            Self for chaining
        """
        return self._register(
            service_type,
            implementation_type,
            factory,
            ServiceLifetime.SCOPED
        )
    
    def register_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> 'ServiceContainer':
        """
        Register a service with transient lifetime.
        
        Args:
            service_type: Service interface type
            implementation_type: Implementation type
            factory: Factory function
            
        Returns:
            Self for chaining
        """
        return self._register(
            service_type,
            implementation_type,
            factory,
            ServiceLifetime.TRANSIENT
        )
    
    def _register(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]],
        factory: Optional[Callable[..., T]],
        lifetime: ServiceLifetime,
    ) -> 'ServiceContainer':
        """Internal method to register services."""
        dependencies = self._extract_dependencies(implementation_type or factory)
        
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=lifetime,
            dependencies=dependencies,
        )
        
        self._services[service_type] = descriptor
        self.logger.debug(f"Registered {service_type.__name__} with {lifetime.value} lifetime")
        
        return self
    
    def _extract_dependencies(self, target: Any) -> List[Type]:
        """Extract dependency types from constructor or factory function."""
        if target is None:
            return []
            
        try:
            if inspect.isclass(target):
                sig = inspect.signature(target.__init__)
                parameters = list(sig.parameters.values())[1:]  # Skip 'self'
            else:
                sig = inspect.signature(target)
                parameters = list(sig.parameters.values())
            
            dependencies = []
            for param in parameters:
                if param.annotation != inspect.Parameter.empty:
                    # Include AsyncSession and other important dependencies
                    # Skip only basic types that shouldn't be injected
                    if param.annotation not in [str, int, bool, dict, list]:
                        dependencies.append(param.annotation)
                        
            return dependencies
            
        except Exception as e:
            self.logger.warning(f"Could not extract dependencies from {target}: {e}")
            return []
    
    def resolve(self, service_type: Type[T], scope_id: Optional[str] = None) -> T:
        """
        Resolve a service instance.
        
        Args:
            service_type: Type of service to resolve
            scope_id: Scope identifier for scoped services
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._services[service_type]
        
        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._resolve_singleton(descriptor)
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._resolve_scoped(descriptor, scope_id or "default")
        else:  # TRANSIENT
            return self._create_instance(descriptor)
    
    def _resolve_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """Resolve singleton service."""
        if descriptor.service_type not in self._singletons:
            instance = self._create_instance(descriptor)
            self._singletons[descriptor.service_type] = instance
            self.logger.debug(f"Created singleton instance of {descriptor.service_type.__name__}")
        
        return self._singletons[descriptor.service_type]
    
    def _resolve_scoped(self, descriptor: ServiceDescriptor, scope_id: str) -> Any:
        """Resolve scoped service."""
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}
        
        scope = self._scoped_instances[scope_id]
        
        if descriptor.service_type not in scope:
            instance = self._create_instance(descriptor)
            scope[descriptor.service_type] = instance
            self.logger.debug(
                f"Created scoped instance of {descriptor.service_type.__name__} "
                f"for scope {scope_id}"
            )
        
        return scope[descriptor.service_type]
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new service instance."""
        try:
            # Resolve dependencies by parameter name
            resolved_deps = {}
            
            if descriptor.factory:
                # For factory functions, map parameter names to resolved dependencies
                sig = inspect.signature(descriptor.factory)
                for param_name, param in sig.parameters.items():
                    if param.annotation != inspect.Parameter.empty and param.annotation in self._services:
                        resolved_deps[param_name] = self.resolve(param.annotation)
                
                # Use factory function
                return descriptor.factory(**resolved_deps)
            else:
                # For constructors, map parameter names to resolved dependencies
                sig = inspect.signature(descriptor.implementation_type.__init__)
                for param_name, param in list(sig.parameters.items())[1:]:  # Skip 'self'
                    if param.annotation != inspect.Parameter.empty and param.annotation in self._services:
                        resolved_deps[param_name] = self.resolve(param.annotation)
                
                # Use constructor
                return descriptor.implementation_type(**resolved_deps)
                
        except Exception as e:
            self.logger.error(f"Failed to create instance of {descriptor.service_type.__name__}: {e}")
            raise
    
    def clear_scope(self, scope_id: str) -> None:
        """Clear a specific scope."""
        if scope_id in self._scoped_instances:
            del self._scoped_instances[scope_id]
            self.logger.debug(f"Cleared scope {scope_id}")
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def get_registered_services(self) -> List[Type]:
        """Get list of all registered service types."""
        return list(self._services.keys())
    
    @asynccontextmanager
    async def scope(self, scope_id: Optional[str] = None):
        """
        Create a scoped context for service resolution.
        
        Args:
            scope_id: Unique identifier for the scope
            
        Yields:
            Scope context
        """
        import uuid
        
        if scope_id is None:
            scope_id = str(uuid.uuid4())
        
        try:
            self.logger.debug(f"Creating scope {scope_id}")
            yield scope_id
        finally:
            self.clear_scope(scope_id)
            self.logger.debug(f"Disposed scope {scope_id}")


# Global service container instance
_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container instance."""
    return _container


def register_singleton(
    service_type: Type[T],
    implementation_type: Optional[Type[T]] = None,
    factory: Optional[Callable[..., T]] = None,
) -> ServiceContainer:
    """Register a singleton service in the global container."""
    return _container.register_singleton(service_type, implementation_type, factory)


def register_scoped(
    service_type: Type[T],
    implementation_type: Optional[Type[T]] = None,
    factory: Optional[Callable[..., T]] = None,
) -> ServiceContainer:
    """Register a scoped service in the global container."""
    return _container.register_scoped(service_type, implementation_type, factory)


def register_transient(
    service_type: Type[T],
    implementation_type: Optional[Type[T]] = None,
    factory: Optional[Callable[..., T]] = None,
) -> ServiceContainer:
    """Register a transient service in the global container."""
    return _container.register_transient(service_type, implementation_type, factory)


def resolve(service_type: Type[T], scope_id: Optional[str] = None) -> T:
    """Resolve a service from the global container."""
    return _container.resolve(service_type, scope_id)


def get_service(service_type: Type[T]) -> Callable[..., T]:
    """
    FastAPI dependency function to resolve services.
    
    Usage:
        @app.get("/example")
        def endpoint(service: MyService = Depends(get_service(MyService))):
            return service.do_something()
    """
    def dependency() -> T:
        return resolve(service_type)
    
    return dependency 