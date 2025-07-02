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

# === IMPORTAÇÕES OPCIONAIS COM FALLBACKS ===

# OpenTelemetry Core
try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    # Fallbacks quando OpenTelemetry não está disponível
    trace = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None
    ConsoleSpanExporter = None
    ResourceAttributes = None
    Status = None
    StatusCode = None
    TraceContextTextMapPropagator = None
    OPENTELEMETRY_AVAILABLE = False

# Exporters Opcionais
JAEGER_AVAILABLE = False
OTLP_AVAILABLE = False
JaegerExporter = None
OTLPSpanExporter = None

if OPENTELEMETRY_AVAILABLE:
    try:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        JAEGER_AVAILABLE = True
    except ImportError:
        JaegerExporter = None

    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        OTLP_AVAILABLE = True
    except ImportError:
        OTLPSpanExporter = None

# Instrumentação Opcional
FASTAPI_INSTRUMENTATION_AVAILABLE = False
HTTPX_INSTRUMENTATION_AVAILABLE = False
REDIS_INSTRUMENTATION_AVAILABLE = False
SQLALCHEMY_INSTRUMENTATION_AVAILABLE = False

FastAPIInstrumentor = None
HTTPXClientInstrumentor = None
RedisInstrumentor = None
SQLAlchemyInstrumentor = None

if OPENTELEMETRY_AVAILABLE:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FASTAPI_INSTRUMENTATION_AVAILABLE = True
    except ImportError:
        pass

    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPX_INSTRUMENTATION_AVAILABLE = True
    except ImportError:
        pass

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        REDIS_INSTRUMENTATION_AVAILABLE = True
    except ImportError:
        pass

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLALCHEMY_INSTRUMENTATION_AVAILABLE = True
    except ImportError:
        pass

from synapse.core.config import settings

logger = logging.getLogger(__name__)

# === GERENCIAMENTO DE ESTADO GLOBAL ===

class TracingState:
    """Gerencia o estado global do sistema de tracing de forma thread-safe."""
    
    def __init__(self):
        self.tracer = None
        self.propagator = None
        self.initialized = False
        self.enabled = False
    
    def is_ready(self) -> bool:
        """Verifica se o tracing está pronto para uso."""
        return OPENTELEMETRY_AVAILABLE and self.initialized and self.enabled
    
    def reset(self):
        """Reseta o estado do tracing."""
        self.tracer = None
        self.propagator = None
        self.initialized = False
        self.enabled = False

# Instância global do estado
_tracing_state = TracingState()

# === CONFIGURAÇÃO ===

class TracingConfig:
    """Configuração do sistema de tracing."""

    def __init__(self):
        self.service_name = "synapscale-backend"
        self.service_version = "1.0.0"
        self.environment = settings.ENVIRONMENT
        self.enabled = settings.ENABLE_TRACING

        # Configurações de exporters
        self.jaeger_endpoint = os.getenv(
            "JAEGER_ENDPOINT", "http://localhost:14268/api/traces"
        )
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        self.console_exporter = os.getenv("CONSOLE_EXPORTER", "false").lower() == "true"

        # Configurações de sampling
        self.sample_rate = float(os.getenv("TRACE_SAMPLE_RATE", "1.0"))

# === INICIALIZAÇÃO ===

def setup_tracing() -> bool:
    """
    Configura o sistema de tracing distribuído.
    
    Returns:
        bool: True se configurado com sucesso, False caso contrário
    """
    global _tracing_state

    if not OPENTELEMETRY_AVAILABLE:
        logger.info("OpenTelemetry não está disponível - tracing desabilitado")
        return False

    config = TracingConfig()

    if not config.enabled:
        logger.info("Tracing distribuído desabilitado por configuração")
        return False

    try:
        # Configurar resource
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: config.service_name,
                ResourceAttributes.SERVICE_VERSION: config.service_version,
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: config.environment,
            }
        )

        # Configurar provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        
        # Configurar propagator
        _tracing_state.propagator = TraceContextTextMapPropagator()

        # Configurar exporters
        exporters = []

        # Console exporter (para desenvolvimento)
        if config.console_exporter:
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            provider.add_span_processor(console_processor)
            exporters.append("console")

        # Jaeger exporter (apenas se endpoint estiver configurado)
        if JAEGER_AVAILABLE and config.jaeger_endpoint and config.jaeger_endpoint != "http://localhost:14268/api/traces":
            try:
                # Usar collector_endpoint (versões recentes) ou endpoint (versões antigas)
                jaeger_exporter = JaegerExporter(
                    collector_endpoint=config.jaeger_endpoint,
                )
                jaeger_processor = BatchSpanProcessor(jaeger_exporter)
                provider.add_span_processor(jaeger_processor)
                exporters.append("jaeger")
            except TypeError:
                # Fallback para versões antigas do OpenTelemetry
                try:
                    jaeger_exporter = JaegerExporter(
                        endpoint=config.jaeger_endpoint,
                    )
                    jaeger_processor = BatchSpanProcessor(jaeger_exporter)
                    provider.add_span_processor(jaeger_processor)
                    exporters.append("jaeger")
                except Exception as e:
                    logger.warning(f"Falha ao configurar Jaeger exporter (fallback): {e}")
            except Exception as e:
                logger.warning(f"Falha ao configurar Jaeger exporter: {e}")
        else:
            logger.debug("Jaeger exporter não disponível ou não configurado")

        # OTLP exporter (apenas se endpoint estiver configurado)
        if OTLP_AVAILABLE and config.otlp_endpoint and config.otlp_endpoint != "http://localhost:4317":
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
        else:
            logger.debug("OTLP exporter não disponível ou não configurado")

        # Obter tracer global
        _tracing_state.tracer = trace.get_tracer(__name__)
        _tracing_state.initialized = True
        _tracing_state.enabled = True

        logger.info(
            f"Tracing distribuído configurado com exporters: {', '.join(exporters) or 'nenhum'}"
        )
        return True

    except Exception as e:
        logger.error(f"Erro ao configurar tracing distribuído: {e}")
        _tracing_state.reset()
        return False

def shutdown_tracing():
    """Finaliza o sistema de tracing."""
    global _tracing_state
    
    if _tracing_state.is_ready():
        try:
            # Força flush de spans pendentes
            if OPENTELEMETRY_AVAILABLE and trace.get_tracer_provider():
                provider = trace.get_tracer_provider()
                if hasattr(provider, 'force_flush'):
                    provider.force_flush(timeout_millis=5000)
            logger.info("Tracing distribuído finalizado")
        except Exception as e:
            logger.warning(f"Erro ao finalizar tracing: {e}")
    
    _tracing_state.reset()

# === INSTRUMENTAÇÃO ===

def instrument_fastapi(app) -> bool:
    """
    Instrumenta aplicação FastAPI com OpenTelemetry.
    
    Returns:
        bool: True se instrumentado com sucesso
    """
    if not _tracing_state.is_ready():
        logger.debug("Tracing não disponível - instrumentação FastAPI ignorada")
        return False

    if not FASTAPI_INSTRUMENTATION_AVAILABLE:
        logger.debug("FastAPI instrumentation não disponível")
        return False

    try:
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="health,metrics,docs,redoc,openapi.json",
        )
        logger.info("FastAPI instrumentado com OpenTelemetry")
        return True
    except Exception as e:
        logger.error(f"Erro ao instrumentar FastAPI: {e}")
        return False

def instrument_libraries() -> bool:
    """
    Instrumenta bibliotecas com OpenTelemetry.
    
    Returns:
        bool: True se pelo menos uma biblioteca foi instrumentada
    """
    if not _tracing_state.is_ready():
        logger.debug("Tracing não disponível - instrumentação de bibliotecas ignorada")
        return False

    instrumented = []

    try:
        # Instrumentar HTTPX
        if HTTPX_INSTRUMENTATION_AVAILABLE:
            HTTPXClientInstrumentor().instrument()
            instrumented.append("HTTPX")

        # Instrumentar Redis
        if REDIS_INSTRUMENTATION_AVAILABLE:
            RedisInstrumentor().instrument()
            instrumented.append("Redis")

        # Instrumentar SQLAlchemy
        if SQLALCHEMY_INSTRUMENTATION_AVAILABLE:
            SQLAlchemyInstrumentor().instrument()
            instrumented.append("SQLAlchemy")

        if instrumented:
            logger.info(f"Bibliotecas instrumentadas: {', '.join(instrumented)}")
            return True
        else:
            logger.debug("Nenhuma biblioteca disponível para instrumentação")
            return False

    except Exception as e:
        logger.error(f"Erro ao instrumentar bibliotecas: {e}")
        return False

# === SPANS E CONTEXTO ===

@contextmanager
def create_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    set_status_on_exception: bool = True,
):
    """Context manager para criar spans personalizados."""
    if not _tracing_state.is_ready():
        yield None
        return

    with _tracing_state.tracer.start_as_current_span(name) as span:
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

# === DECORATORS ===

def trace_operation(
    operation_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
):
    """Decorator para adicionar tracing automático a funções."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _tracing_state.is_ready():
                return await func(*args, **kwargs)

            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            span_attributes = attributes or {}
            span_attributes.update(
                {
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                }
            )

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
            if not _tracing_state.is_ready():
                return func(*args, **kwargs)

            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            span_attributes = attributes or {}
            span_attributes.update(
                {
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                }
            )

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
    cost: Optional[float] = None,
):
    """Decorator específico para operações de LLM."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _tracing_state.is_ready():
                return await func(*args, **kwargs)

            span_name = f"llm.{provider}.{operation}"
            attributes = {
                "llm.provider": provider,
                "llm.model": model,
                "llm.operation": operation,
            }

            if input_tokens:
                attributes["llm.input_tokens"] = input_tokens
            if output_tokens:
                attributes["llm.output_tokens"] = output_tokens
            if cost:
                attributes["llm.cost"] = cost

            with create_span(span_name, attributes) as span:
                start_time = time.time()

                try:
                    result = await func(*args, **kwargs)

                    if span:
                        duration = time.time() - start_time
                        span.set_attribute("llm.duration", duration)
                        span.set_attribute("llm.status", "success")

                        # Tentar extrair tokens e custo do resultado
                        if hasattr(result, "usage"):
                            usage = result.usage
                            if hasattr(usage, "prompt_tokens"):
                                span.set_attribute("llm.actual_input_tokens", usage.prompt_tokens)
                            if hasattr(usage, "completion_tokens"):
                                span.set_attribute("llm.actual_output_tokens", usage.completion_tokens)
                            if hasattr(usage, "total_tokens"):
                                span.set_attribute("llm.total_tokens", usage.total_tokens)

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
            if not _tracing_state.is_ready():
                return func(*args, **kwargs)

            span_name = f"llm.{provider}.{operation}"
            attributes = {
                "llm.provider": provider,
                "llm.model": model,
                "llm.operation": operation,
            }

            if input_tokens:
                attributes["llm.input_tokens"] = input_tokens
            if output_tokens:
                attributes["llm.output_tokens"] = output_tokens
            if cost:
                attributes["llm.cost"] = cost

            with create_span(span_name, attributes) as span:
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
    operation: str, table: Optional[str] = None, query: Optional[str] = None
):
    """Decorator específico para operações de banco de dados."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _tracing_state.is_ready():
                return await func(*args, **kwargs)

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
                        if hasattr(result, "rowcount"):
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
            if not _tracing_state.is_ready():
                return func(*args, **kwargs)

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

# === UTILITÁRIOS ===

def get_current_trace_id() -> Optional[str]:
    """Obtém o trace ID atual para correlação com logs."""
    if not _tracing_state.is_ready():
        return None

    try:
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            trace_id = current_span.get_span_context().trace_id
            return format(trace_id, "032x")
    except Exception:
        pass

    return None

def get_current_span_id() -> Optional[str]:
    """Obtém o span ID atual para correlação com logs."""
    if not _tracing_state.is_ready():
        return None

    try:
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            span_id = current_span.get_span_context().span_id
            return format(span_id, "016x")
    except Exception:
        pass

    return None

def add_span_attribute(key: str, value: Any) -> None:
    """Adiciona atributo ao span atual."""
    if not _tracing_state.is_ready():
        return

    try:
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.set_attribute(key, value)
    except Exception:
        pass

def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
    """Adiciona evento ao span atual."""
    if not _tracing_state.is_ready():
        return

    try:
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.add_event(name, attributes or {})
    except Exception:
        pass

def inject_trace_context(headers: Dict[str, str]) -> Dict[str, str]:
    """Injeta contexto de trace em headers HTTP."""
    if not _tracing_state.is_ready() or not _tracing_state.propagator:
        return headers

    try:
        _tracing_state.propagator.inject(headers)
    except Exception:
        pass

    return headers

def extract_trace_context(headers: Dict[str, str]) -> None:
    """Extrai contexto de trace de headers HTTP."""
    if not _tracing_state.is_ready() or not _tracing_state.propagator:
        return

    try:
        context = _tracing_state.propagator.extract(headers)
        if context:
            trace.set_span_in_context(trace.get_current_span(), context)
    except Exception:
        pass

# === MIDDLEWARE ===

class TracingMiddleware:
    """Middleware para adicionar informações de tracing aos logs."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extrair contexto de trace dos headers se tracing estiver ativo
        if _tracing_state.is_ready():
            headers = dict(scope.get("headers", []))
            string_headers = {
                key.decode(): value.decode() for key, value in headers.items()
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

# === CONVENIÊNCIA ===

def get_trace_context() -> Dict[str, Optional[str]]:
    """Retorna contexto de trace para uso em logs."""
    return {
        "trace_id": get_current_trace_id(),
        "span_id": get_current_span_id(),
    }

def is_tracing_enabled() -> bool:
    """Verifica se o tracing está habilitado e funcionando."""
    return _tracing_state.is_ready()

def get_tracing_info() -> Dict[str, Any]:
    """Retorna informações sobre o estado do tracing."""
    return {
        "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
        "jaeger_available": JAEGER_AVAILABLE,
        "otlp_available": OTLP_AVAILABLE,
        "fastapi_instrumentation_available": FASTAPI_INSTRUMENTATION_AVAILABLE,
        "initialized": _tracing_state.initialized,
        "enabled": _tracing_state.enabled,
        "ready": _tracing_state.is_ready(),
    }
