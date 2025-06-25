"""Sistema de tracing distribuído usando OpenTelemetry para SynapScale.

Este módulo implementa tracing distribuído com propagação de contexto,
spans customizados para operações críticas e integração com logs.
"""

import logging
import os
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Optional, Union

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from synapse.core.config_new import settings

logger = logging.getLogger(__name__)

# Global tracer instance
tracer = None
propagator = TraceContextTextMapPropagator()


class TracingConfig:
    """Configuração do sistema de tracing."""
    
    def __init__(self):
        self.service_name = "synapscale-backend"
        self.service_version = "1.0.0"
        self.environment = settings.ENVIRONMENT
        self.enabled = settings.ENABLE_TRACING
        
        # Configurações de exporters
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        self.console_exporter = os.getenv("CONSOLE_EXPORTER", "false").lower() == "true"
        
        # Configurações de sampling
        self.sample_rate = float(os.getenv("TRACE_SAMPLE_RATE", "1.0"))


def setup_tracing() -> None:
    """Configura o sistema de tracing distribuído."""
    global tracer
    
    config = TracingConfig()
    
    if not config.enabled:
        logger.info("Tracing distribuído desabilitado")
        return
    
    # Configurar resource
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: config.service_name,
        ResourceAttributes.SERVICE_VERSION: config.service_version,
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: config.environment,
    })
    
    # Configurar provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    
    # Configurar exporters
    exporters = []
    
    # Console exporter (para desenvolvimento)
    if config.console_exporter:
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        provider.add_span_processor(console_processor)
        exporters.append("console")
    
    # Jaeger exporter
    try:
        jaeger_exporter = JaegerExporter(
            endpoint=config.jaeger_endpoint,
        )
        jaeger_processor = BatchSpanProcessor(jaeger_exporter)
        provider.add_span_processor(jaeger_processor)
        exporters.append("jaeger")
    except Exception as e:
        logger.warning(f"Falha ao configurar Jaeger exporter: {e}")
    
    # OTLP exporter
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=config.otlp_endpoint,
            insecure=True,
        )
        otlp_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(otlp_processor)
        exporters.append("otlp")
    except Exception as e:
        logger.warning(f"Falha ao configurar OTLP exporter: {e}")
    
    # Obter tracer global
    tracer = trace.get_tracer(__name__)
    
    logger.info(f"Tracing distribuído configurado com exporters: {', '.join(exporters)}")


def instrument_fastapi(app) -> None:
    """Instrumenta aplicação FastAPI com OpenTelemetry."""
    if not settings.ENABLE_TRACING:
        return
    
    try:
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="health,metrics,docs,redoc,openapi.json",
        )
        logger.info("FastAPI instrumentado com OpenTelemetry")
    except Exception as e:
        logger.error(f"Erro ao instrumentar FastAPI: {e}")


def instrument_libraries() -> None:
    """Instrumenta bibliotecas com OpenTelemetry."""
    if not settings.ENABLE_TRACING:
        return
    
    try:
        # Instrumentar HTTPX
        HTTPXClientInstrumentor().instrument()
        
        # Instrumentar Redis
        RedisInstrumentor().instrument()
        
        # Instrumentar SQLAlchemy
        SQLAlchemyInstrumentor().instrument()
        
        logger.info("Bibliotecas instrumentadas com OpenTelemetry")
    except Exception as e:
        logger.error(f"Erro ao instrumentar bibliotecas: {e}")


@contextmanager
def create_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    set_status_on_exception: bool = True
):
    """Context manager para criar spans personalizados."""
    if not tracer:
        yield None
        return
    
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        try:
            yield span
        except Exception as e:
            if set_status_on_exception:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise


def trace_operation(
    operation_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True
):
    """Decorator para adicionar tracing automático a funções."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not tracer:
                return await func(*args, **kwargs)
            
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            span_attributes = attributes or {}
            span_attributes.update({
                "function.name": func.__name__,
                "function.module": func.__module__,
            })
            
            with create_span(span_name, span_attributes, record_exception) as span:
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("operation.duration", duration)
                        span.set_attribute("operation.status", "success")
                    
                    return result
                    
                except Exception as e:
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("operation.duration", duration)
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not tracer:
                return func(*args, **kwargs)
            
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            span_attributes = attributes or {}
            span_attributes.update({
                "function.name": func.__name__,
                "function.module": func.__module__,
            })
            
            with create_span(span_name, span_attributes, record_exception) as span:
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("operation.duration", duration)
                        span.set_attribute("operation.status", "success")
                    
                    return result
                    
                except Exception as e:
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("operation.duration", duration)
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                    raise
        
        # Detectar se é função async ou sync
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def trace_llm_operation(
    provider: str,
    model: str,
    operation: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    cost: Optional[float] = None
):
    """Decorator específico para operações LLM."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attributes = {
                "llm.provider": provider,
                "llm.model": model,
                "llm.operation": operation,
            }
            
            if input_tokens is not None:
                attributes["llm.input_tokens"] = input_tokens
            if output_tokens is not None:
                attributes["llm.output_tokens"] = output_tokens
            if cost is not None:
                attributes["llm.cost"] = cost
            
            with create_span(f"llm.{operation}", attributes) as span:
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("llm.duration", duration)
                        span.set_attribute("llm.status", "success")
                        
                        # Tentar extrair informações do resultado
                        if isinstance(result, dict):
                            if "usage" in result:
                                usage = result["usage"]
                                if "prompt_tokens" in usage:
                                    span.set_attribute("llm.actual_input_tokens", usage["prompt_tokens"])
                                if "completion_tokens" in usage:
                                    span.set_attribute("llm.actual_output_tokens", usage["completion_tokens"])
                                if "total_tokens" in usage:
                                    span.set_attribute("llm.total_tokens", usage["total_tokens"])
                    
                    return result
                    
                except Exception as e:
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("llm.duration", duration)
                        span.set_attribute("llm.status", "error")
                        span.set_attribute("llm.error", str(e))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attributes = {
                "llm.provider": provider,
                "llm.model": model,
                "llm.operation": operation,
            }
            
            if input_tokens is not None:
                attributes["llm.input_tokens"] = input_tokens
            if output_tokens is not None:
                attributes["llm.output_tokens"] = output_tokens
            if cost is not None:
                attributes["llm.cost"] = cost
            
            with create_span(f"llm.{operation}", attributes) as span:
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("llm.duration", duration)
                        span.set_attribute("llm.status", "success")
                    
                    return result
                    
                except Exception as e:
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("llm.duration", duration)
                        span.set_attribute("llm.status", "error")
                        span.set_attribute("llm.error", str(e))
                    raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def trace_database_operation(
    operation: str,
    table: Optional[str] = None,
    query: Optional[str] = None
):
    """Decorator específico para operações de banco de dados."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attributes = {
                "db.operation": operation,
            }
            
            if table:
                attributes["db.table"] = table
            if query:
                attributes["db.query"] = query[:100]  # Limitar tamanho da query
            
            with create_span(f"db.{operation}", attributes) as span:
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("db.duration", duration)
                        span.set_attribute("db.status", "success")
                        
                        # Tentar obter número de registros afetados
                        if hasattr(result, 'rowcount'):
                            span.set_attribute("db.rows_affected", result.rowcount)
                    
                    return result
                    
                except Exception as e:
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("db.duration", duration)
                        span.set_attribute("db.status", "error")
                        span.set_attribute("db.error", str(e))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attributes = {
                "db.operation": operation,
            }
            
            if table:
                attributes["db.table"] = table
            if query:
                attributes["db.query"] = query[:100]
            
            with create_span(f"db.{operation}", attributes) as span:
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("db.duration", duration)
                        span.set_attribute("db.status", "success")
                    
                    return result
                    
                except Exception as e:
                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("db.duration", duration)
                        span.set_attribute("db.status", "error")
                        span.set_attribute("db.error", str(e))
                    raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_current_trace_id() -> Optional[str]:
    """Obtém o trace ID atual para correlação com logs."""
    if not tracer:
        return None
    
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        trace_id = current_span.get_span_context().trace_id
        return format(trace_id, '032x')
    
    return None


def get_current_span_id() -> Optional[str]:
    """Obtém o span ID atual para correlação com logs."""
    if not tracer:
        return None
    
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        span_id = current_span.get_span_context().span_id
        return format(span_id, '016x')
    
    return None


def add_span_attribute(key: str, value: Any) -> None:
    """Adiciona atributo ao span atual."""
    if not tracer:
        return
    
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        current_span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
    """Adiciona evento ao span atual."""
    if not tracer:
        return
    
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        current_span.add_event(name, attributes or {})


def inject_trace_context(headers: Dict[str, str]) -> Dict[str, str]:
    """Injeta contexto de trace em headers HTTP."""
    if not tracer:
        return headers
    
    propagator.inject(headers)
    return headers


def extract_trace_context(headers: Dict[str, str]) -> None:
    """Extrai contexto de trace de headers HTTP."""
    if not tracer:
        return
    
    context = propagator.extract(headers)
    if context:
        trace.set_span_in_context(trace.get_current_span(), context)


class TracingMiddleware:
    """Middleware para adicionar informações de tracing aos logs."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extrair contexto de trace dos headers
        headers = dict(scope.get("headers", []))
        string_headers = {
            key.decode(): value.decode() 
            for key, value in headers.items()
        }
        extract_trace_context(string_headers)
        
        # Adicionar trace ID ao contexto da requisição
        trace_id = get_current_trace_id()
        span_id = get_current_span_id()
        
        if trace_id:
            # Adicionar ao scope para uso posterior
            scope["trace_id"] = trace_id
            scope["span_id"] = span_id
        
        await self.app(scope, receive, send)


# Função de conveniência para uso em logs
def get_trace_context() -> Dict[str, Optional[str]]:
    """Retorna contexto de trace para uso em logs."""
    return {
        "trace_id": get_current_trace_id(),
        "span_id": get_current_span_id(),
    }


# Inicialização automática se habilitado
if settings.ENABLE_TRACING:
    setup_tracing()
    instrument_libraries() 