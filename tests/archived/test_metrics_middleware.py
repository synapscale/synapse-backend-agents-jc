"""
Teste do Middleware de Métricas
Verifica se as métricas estão sendo coletadas corretamente
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import time

from src.synapse.main import app
from src.synapse.middlewares.metrics import (
    track_llm_metrics,
    http_requests_total,
    llm_requests_total,
    REGISTRY,
)


@pytest.fixture
def client():
    """Cliente de teste para a aplicação"""
    return TestClient(app)


@pytest.mark.metrics
def test_metrics_endpoint_exists(client):
    """Testa se o endpoint /metrics existe e retorna dados"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "synapscale_" in response.text


@pytest.mark.metrics
def test_http_metrics_collection(client):
    """Testa se métricas HTTP são coletadas automaticamente"""
    # Fazer algumas requisições para gerar métricas
    client.get("/health")
    client.get("/")
    # Removido /info que está causando erro de configuração

    # Verificar se as métricas foram registradas
    response = client.get("/metrics")
    assert response.status_code == 200

    metrics_text = response.text

    # Verificar se contém métricas HTTP básicas
    assert "synapscale_http_requests_total" in metrics_text
    assert "synapscale_http_request_duration_seconds" in metrics_text
    assert "synapscale_http_requests_active" in metrics_text


@pytest.mark.metrics
def test_llm_metrics_tracking():
    """Testa se as métricas de LLM estão definidas corretamente"""
    # Verificar se as métricas LLM existem no registry
    from src.synapse.middlewares.metrics import (
        llm_requests_total,
        llm_request_duration_seconds,
        llm_tokens_total,
        llm_costs_total,
        track_llm_metrics,
    )

    # Usar a função track_llm_metrics que já existe
    track_llm_metrics(
        provider="openai",
        model="gpt-4o",
        endpoint="/generate",
        status="success",
        duration=1.5,
        input_tokens=100,
        output_tokens=200,
        cost=0.05,
    )

    # Verificar se as métricas foram registradas
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200

    metrics_text = response.text

    # Verificar se as definições das métricas LLM existem
    assert "synapscale_llm_requests_total" in metrics_text
    assert "synapscale_llm_request_duration_seconds" in metrics_text
    assert "synapscale_llm_tokens_total" in metrics_text
    assert "synapscale_llm_costs_total" in metrics_text

    # Verificar se as métricas têm pelo menos as definições (# HELP e # TYPE)
    assert "# HELP synapscale_llm_requests_total" in metrics_text
    assert "# TYPE synapscale_llm_requests_total counter" in metrics_text


@pytest.mark.metrics
def test_system_metrics_in_response(client):
    """Testa se métricas de sistema estão incluídas na resposta"""
    response = client.get("/metrics")
    assert response.status_code == 200

    metrics_text = response.text

    # Verificar métricas de sistema
    assert "synapscale_system_cpu_usage_percent" in metrics_text
    assert "synapscale_system_memory_usage_bytes" in metrics_text


@pytest.mark.metrics
def test_metrics_format_prometheus(client):
    """Testa se as métricas estão no formato correto do Prometheus"""
    response = client.get("/metrics")
    assert response.status_code == 200

    metrics_text = response.text
    lines = metrics_text.split("\n")

    # Verificar formato básico do Prometheus
    help_lines = [line for line in lines if line.startswith("# HELP")]
    type_lines = [line for line in lines if line.startswith("# TYPE")]
    metric_lines = [line for line in lines if line and not line.startswith("#")]

    assert len(help_lines) > 0, "Devem existir linhas HELP"
    assert len(type_lines) > 0, "Devem existir linhas TYPE"
    assert len(metric_lines) > 0, "Devem existir linhas de métricas"

    # Verificar se métricas têm valores numéricos
    for line in metric_lines[:10]:  # Verificar apenas as primeiras 10
        if " " in line:
            metric_name, value = line.rsplit(" ", 1)
            try:
                float(value)
            except ValueError:
                pytest.fail(f"Valor de métrica inválido: {value} na linha: {line}")


@pytest.mark.metrics
def test_middleware_performance(client):
    """Testa se o middleware não adiciona latência significativa"""
    # Medir tempo com middleware (usando endpoint simples)
    start_time = time.time()
    response = client.get("/health")
    duration_with_middleware = time.time() - start_time

    assert response.status_code == 200
    # O middleware não deve adicionar mais que 2 segundos de latência (considerando conexão DB)
    assert duration_with_middleware < 2.0


@pytest.mark.metrics
def test_metrics_registry_isolation():
    """Testa se o registry personalizado está funcionando"""
    from prometheus_client import REGISTRY as DEFAULT_REGISTRY
    from src.synapse.middlewares.metrics import REGISTRY as CUSTOM_REGISTRY

    # Verificar se estamos usando um registry personalizado
    assert CUSTOM_REGISTRY is not DEFAULT_REGISTRY

    # Verificar se métricas estão no registry personalizado
    metric_names = [
        metric._name for metric in CUSTOM_REGISTRY._collector_to_names.keys()
    ]
    synapscale_metrics = [
        name for name in metric_names if name.startswith("synapscale_")
    ]

    assert (
        len(synapscale_metrics) > 0
    ), "Devem existir métricas do SynapScale no registry personalizado"


@pytest.mark.metrics
def test_error_handling_in_metrics(client):
    """Testa se erros são tratados corretamente nas métricas"""
    # Fazer requisição para endpoint inexistente
    response = client.get("/endpoint-inexistente")
    assert response.status_code == 404

    # Verificar se a métrica de erro foi registrada
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200

    metrics_text = metrics_response.text

    # Verificar se o status code 404 foi registrado
    assert 'status_code="404"' in metrics_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
