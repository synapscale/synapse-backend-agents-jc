"""
Middleware de Métricas para Monitoramento e Observabilidade
Coleta métricas de API, LLM, e sistema para Prometheus/Grafana
"""
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
import psutil
import logging

logger = logging.getLogger(__name__)

# Registry personalizado para evitar conflitos
REGISTRY = CollectorRegistry()

# ========================================
# MÉTRICAS GERAIS DA API
# ========================================

# Contador de requisições HTTP
http_requests_total = Counter(
    'synapscale_http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

# Histograma de latência HTTP
http_request_duration_seconds = Histogram(
    'synapscale_http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Gauge de requisições ativas
http_requests_active = Gauge(
    'synapscale_http_requests_active',
    'Número de requisições HTTP ativas',
    registry=REGISTRY
)

# ========================================
# MÉTRICAS ESPECÍFICAS DE LLM
# ========================================

# Contador de chamadas LLM
llm_requests_total = Counter(
    'synapscale_llm_requests_total',
    'Total de chamadas para LLM',
    ['provider', 'model', 'endpoint', 'status'],
    registry=REGISTRY
)

# Histograma de latência LLM
llm_request_duration_seconds = Histogram(
    'synapscale_llm_request_duration_seconds',
    'Duração das chamadas LLM em segundos',
    ['provider', 'model'],
    registry=REGISTRY
)

# Contador de tokens processados
llm_tokens_total = Counter(
    'synapscale_llm_tokens_total',
    'Total de tokens processados',
    ['provider', 'model', 'type'],  # type: input, output
    registry=REGISTRY
)

# Contador de custos LLM
llm_costs_total = Counter(
    'synapscale_llm_costs_total',
    'Custo total das chamadas LLM em USD',
    ['provider', 'model'],
    registry=REGISTRY
)

# ========================================
# MÉTRICAS DE SISTEMA
# ========================================

# Gauge de uso de CPU
system_cpu_usage = Gauge(
    'synapscale_system_cpu_usage_percent',
    'Uso de CPU do sistema em porcentagem',
    registry=REGISTRY
)

# Gauge de uso de memória
system_memory_usage = Gauge(
    'synapscale_system_memory_usage_bytes',
    'Uso de memória do sistema em bytes',
    registry=REGISTRY
)

# Gauge de conexões de banco de dados
database_connections_active = Gauge(
    'synapscale_database_connections_active',
    'Número de conexões ativas no banco de dados',
    registry=REGISTRY
)

# ========================================
# MÉTRICAS DE NEGÓCIO
# ========================================

# Contador de usuários ativos
users_active_total = Gauge(
    'synapscale_users_active_total',
    'Número total de usuários ativos',
    registry=REGISTRY
)

# Contador de workspaces
workspaces_total = Gauge(
    'synapscale_workspaces_total',
    'Número total de workspaces',
    registry=REGISTRY
)

# Contador de execuções de workflow
workflow_executions_total = Counter(
    'synapscale_workflow_executions_total',
    'Total de execuções de workflow',
    ['status'],
    registry=REGISTRY
)


class MetricsMiddleware:
    """Middleware para coleta automática de métricas"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Incrementar requisições ativas
        http_requests_active.inc()
        
        # Capturar dados da requisição
        method = request.method
        path = self._get_route_path(request)
        start_time = time.time()
        
        try:
            # Processar requisição
            response = await call_next(request)
            status_code = str(response.status_code)
            
        except Exception as e:
            # Em caso de erro, registrar como 500
            status_code = "500"
            logger.error(f"Erro no middleware de métricas: {e}")
            raise
            
        finally:
            # Calcular duração
            duration = time.time() - start_time
            
            # Registrar métricas
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Decrementar requisições ativas
            http_requests_active.dec()
            
        return response
    
    def _get_route_path(self, request: Request) -> str:
        """Extrai o path da rota (sem parâmetros dinâmicos)"""
        try:
            for route in self.app.routes:
                if isinstance(route, APIRoute):
                    match, _ = route.matches(request)
                    if match.name == "full_match":
                        return route.path
            return request.url.path
        except:
            return request.url.path


def track_llm_metrics(
    provider: str,
    model: str,
    endpoint: str,
    status: str,
    duration: float,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost: float = 0.0
):
    """
    Função auxiliar para registrar métricas específicas de LLM
    Deve ser chamada nos endpoints de LLM após cada chamada
    """
    # Registrar chamada LLM
    llm_requests_total.labels(
        provider=provider,
        model=model,
        endpoint=endpoint,
        status=status
    ).inc()
    
    # Registrar duração
    llm_request_duration_seconds.labels(
        provider=provider,
        model=model
    ).observe(duration)
    
    # Registrar tokens
    if input_tokens > 0:
        llm_tokens_total.labels(
            provider=provider,
            model=model,
            type="input"
        ).inc(input_tokens)
    
    if output_tokens > 0:
        llm_tokens_total.labels(
            provider=provider,
            model=model,
            type="output"
        ).inc(output_tokens)
    
    # Registrar custo
    if cost > 0:
        llm_costs_total.labels(
            provider=provider,
            model=model
        ).inc(cost)


def update_system_metrics():
    """
    Atualiza métricas de sistema
    Deve ser chamada periodicamente (ex: a cada 30 segundos)
    """
    try:
        # Uso de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)
        
        # Uso de memória
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.used)
        
    except Exception as e:
        logger.error(f"Erro ao atualizar métricas de sistema: {e}")


async def metrics_endpoint(request: Request) -> Response:
    """
    Endpoint /metrics para exposição das métricas no formato Prometheus
    """
    try:
        # Atualizar métricas de sistema antes de expor
        update_system_metrics()
        
        # Gerar métricas no formato Prometheus
        metrics_data = generate_latest(REGISTRY)
        
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar métricas: {e}")
        return Response(
            content="# Erro ao gerar métricas\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )


def setup_metrics_middleware(app: FastAPI):
    """
    Configura o middleware de métricas na aplicação FastAPI
    """
    # Adicionar middleware
    app.middleware("http")(MetricsMiddleware(app))
    
    # Adicionar endpoint de métricas
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])
    
    logger.info("Middleware de métricas configurado com sucesso")


# ========================================
# FUNÇÕES AUXILIARES PARA USO NOS ENDPOINTS
# ========================================

def increment_workflow_execution(status: str):
    """Incrementa contador de execuções de workflow"""
    workflow_executions_total.labels(status=status).inc()


def set_active_users_count(count: int):
    """Define número de usuários ativos"""
    users_active_total.set(count)


def set_workspaces_count(count: int):
    """Define número total de workspaces"""
    workspaces_total.set(count)


def set_database_connections(count: int):
    """Define número de conexões ativas no banco"""
    database_connections_active.set(count)


# ========================================
# DECORATOR PARA MÉTRICAS AUTOMÁTICAS
# ========================================

def track_endpoint_metrics(endpoint_name: str = None):
    """
    Decorator para rastrear métricas automaticamente em funções
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            name = endpoint_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
                
            except Exception as e:
                status = "error"
                logger.error(f"Erro em {name}: {e}")
                raise
                
            finally:
                duration = time.time() - start_time
                # Aqui você pode adicionar métricas específicas se necessário
                
        return wrapper
    return decorator 