"""
Legacy Endpoint Tracking Middleware

Este middleware rastreia o uso de endpoints LLM legados e adiciona headers de depreciação
para facilitar a migração para os novos endpoints unificados.
"""

import time
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from synapse.database import get_db
from synapse.logger_config import get_logger
from synapse.core.config import settings

logger = get_logger(__name__)
import random


class LegacyEndpointTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para rastrear uso de endpoints legados e gerenciar a migração gradual.

    Funcionalidades:
    - Rastreia uso de endpoints LLM legados
    - Adiciona headers de depreciação
    - Implementa redirecionamento gradual
    - Coleta métricas para dashboard de migração
    """

    # Mapeamento de endpoints legados para novos endpoints
    LEGACY_ENDPOINT_MAPPING = {
        "/api/v1/openai/models": "/api/v1/llm/models?provider=openai",
        "/api/v1/openai/generate": "/api/v1/llm/generate",
        "/api/v1/openai/chat": "/api/v1/llm/chat",
        "/api/v1/anthropic/models": "/api/v1/llm/models?provider=anthropic",
        "/api/v1/anthropic/generate": "/api/v1/llm/generate",
        "/api/v1/anthropic/chat": "/api/v1/llm/chat",
        "/api/v1/google/models": "/api/v1/llm/models?provider=google",
        "/api/v1/google/generate": "/api/v1/llm/generate",
        "/api/v1/google/chat": "/api/v1/llm/chat",
    }

    # Fases de migração com configurações
    MIGRATION_PHASES = {
        "phase_1": {
            "name": "Compatibilidade Total",
            "start_date": "2024-01-01",
            "redirect_probability": 0.0,
            "warning_level": "info",
        },
        "phase_2": {
            "name": "Incentivo à Migração",
            "start_date": "2024-04-01",
            "redirect_probability": 0.1,
            "warning_level": "warning",
        },
        "phase_3": {
            "name": "Deprecação Ativa",
            "start_date": "2024-07-01",
            "redirect_probability": 0.5,
            "warning_level": "urgent",
        },
        "phase_4": {
            "name": "Remoção Final",
            "start_date": "2024-10-01",
            "redirect_probability": 1.0,
            "warning_level": "final",
        },
    }

    def __init__(self, app):
        super().__init__(app)
        self.tracking_enabled = getattr(settings, "LEGACY_TRACKING_ENABLED", True)
        self.migration_phase = self._get_current_migration_phase()

    async def dispatch(self, request: Request, call_next):
        """Processa a requisição e aplica tracking/headers de depreciação."""

        # Verifica se é um endpoint legacy
        if not self._is_legacy_endpoint(request.url.path):
            return await call_next(request)

        # Coleta informações da requisição
        user_info = await self._extract_user_info(request)

        # Determina se deve redirecionar
        should_redirect = self._should_redirect_request(request, user_info)

        if should_redirect:
            return self._create_redirect_response(request)

        # Processa normalmente e adiciona headers
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Adiciona headers de depreciação
        self._add_deprecation_headers(response, request.url.path)

        # Registra o uso legacy (async em background)
        if self.tracking_enabled:
            self._track_legacy_usage(request, user_info, process_time)

        return response

    def _is_legacy_endpoint(self, path: str) -> bool:
        """Verifica se o endpoint é legacy."""
        return any(
            path.startswith(legacy_path.split("?")[0])
            for legacy_path in self.LEGACY_ENDPOINT_MAPPING.keys()
        )

    async def _extract_user_info(self, request: Request) -> Dict[str, Any]:
        """Extrai informações do usuário da requisição."""
        try:
            # Tenta extrair user_id do token JWT se disponível
            auth_header = request.headers.get("authorization", "")
            user_id = None

            # Lógica simplificada - em produção usar JWT decoder apropriado
            if auth_header.startswith("Bearer "):
                # Aqui você implementaria a decodificação do JWT
                # Por agora, usar um placeholder
                user_id = "extracted_from_jwt"

            return {
                "user_id": user_id,
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "referer": request.headers.get("referer"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoint": request.url.path,
                "method": request.method,
                "query_params": str(request.query_params),
            }
        except Exception as e:
            logger.warning(f"Erro ao extrair informações do usuário: {e}")
            return {
                "user_id": None,
                "ip_address": "unknown",
                "user_agent": "unknown",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoint": request.url.path,
                "method": request.method,
            }

    def _get_current_migration_phase(self) -> str:
        """Determina a fase atual de migração baseada na data."""
        current_date = datetime.now().strftime("%Y-%m-%d")

        for phase_id, config in reversed(list(self.MIGRATION_PHASES.items())):
            if current_date >= config["start_date"]:
                return phase_id

        return "phase_1"  # Default

    def _should_redirect_request(self, request: Request, user_info: Dict) -> bool:
        """Determina se a requisição deve ser redirecionada."""

        # Nunca redirecionar requests OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return False

        # Obter configuração da fase atual
        phase_config = self.MIGRATION_PHASES.get(self.migration_phase, {})
        redirect_probability = phase_config.get("redirect_probability", 0.0)

        # Se probabilidade é 0, nunca redirecionar
        if redirect_probability == 0.0:
            return False

        # Se probabilidade é 1.0, sempre redirecionar
        if redirect_probability >= 1.0:
            return True

        # Usar random baseado no user_id para consistência
        seed_value = hash(user_info.get("user_id", "anonymous")) % 1000
        return (seed_value / 1000.0) < redirect_probability

    def _create_redirect_response(self, request: Request) -> RedirectResponse:
        """Cria resposta de redirecionamento para o novo endpoint."""

        legacy_path = request.url.path
        new_path = self.LEGACY_ENDPOINT_MAPPING.get(legacy_path)

        if not new_path:
            # Fallback: tentar mapear genericamente
            if "/openai/" in legacy_path:
                new_path = legacy_path.replace("/openai/", "/llm/")
            elif "/anthropic/" in legacy_path:
                new_path = legacy_path.replace("/anthropic/", "/llm/")
            elif "/google/" in legacy_path:
                new_path = legacy_path.replace("/google/", "/llm/")
            else:
                new_path = "/api/v1/llm/"

        # Preservar query parameters
        if request.query_params:
            new_path += f"?{request.query_params}"

        response = RedirectResponse(
            url=new_path, status_code=307  # Preserva método HTTP e body
        )

        # Adicionar headers informativos
        response.headers["X-Migration-Redirect"] = "true"
        response.headers["X-Legacy-Endpoint"] = legacy_path
        response.headers["X-New-Endpoint"] = new_path
        response.headers["X-Migration-Phase"] = self.migration_phase

        self._add_deprecation_headers(response, legacy_path)

        logger.info(f"Redirecionando endpoint legacy {legacy_path} para {new_path}")

        return response

    def _add_deprecation_headers(self, response: Response, legacy_path: str):
        """Adiciona headers de depreciação à resposta."""

        phase_config = self.MIGRATION_PHASES.get(self.migration_phase, {})
        warning_level = phase_config.get("warning_level", "info")

        # Headers padrão de depreciação
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2024-12-31T23:59:59Z"
        response.headers["Link"] = (
            '</docs/llm-migration-guide>; rel="alternate"; title="Migration Guide"'
        )

        # Header de warning específico por fase
        warning_messages = {
            "info": "This endpoint is deprecated. Please migrate to /llm/* endpoints. See docs.synapscale.com/llm-migration",
            "warning": "This endpoint will be removed soon. Please migrate to /llm/* endpoints immediately.",
            "urgent": "URGENT: This endpoint will be removed in 30 days. Migrate to /llm/* endpoints now!",
            "final": "This endpoint has been removed. Please use /llm/* endpoints only.",
        }

        warning_message = warning_messages.get(warning_level, warning_messages["info"])
        response.headers["Warning"] = f'299 - "{warning_message}"'

        # Headers informativos adicionais
        response.headers["X-Legacy-Endpoint"] = "true"
        response.headers["X-Migration-Phase"] = self.migration_phase
        response.headers["X-Migration-Guide"] = (
            "https://docs.synapscale.com/llm-migration"
        )
        response.headers["X-New-Endpoint"] = self.LEGACY_ENDPOINT_MAPPING.get(
            legacy_path, "/api/v1/llm/"
        )

    def _track_legacy_usage(
        self, request: Request, user_info: Dict, process_time: float
    ):
        """Registra o uso de endpoint legacy para métricas."""

        try:
            # Em uma implementação completa, isso seria salvo no banco de dados
            # Por agora, apenas log estruturado

            usage_data = {
                "event_type": "legacy_endpoint_usage",
                "timestamp": user_info["timestamp"],
                "user_id": user_info.get("user_id"),
                "endpoint": user_info["endpoint"],
                "method": user_info["method"],
                "ip_address": user_info["ip_address"],
                "user_agent": user_info["user_agent"],
                "migration_phase": self.migration_phase,
                "process_time": process_time,
                "referer": user_info.get("referer"),
                "query_params": user_info.get("query_params"),
            }

            # Log estruturado para coleta de métricas
            logger.info(
                "Legacy endpoint usage tracked",
                extra={"legacy_usage": usage_data, "structured_log": True},
            )

            # TODO: Implementar salvamento em banco de dados
            # await self._save_to_database(usage_data)

            # TODO: Implementar métricas Prometheus
            # self._update_prometheus_metrics(usage_data)

        except Exception as e:
            logger.error(f"Erro ao rastrear uso legacy: {e}")

    async def _save_to_database(self, usage_data: Dict):
        """Salva dados de uso no banco de dados (implementação futura)."""
        # TODO: Implementar salvamento em tabela legacy_usage
        pass

    def _update_prometheus_metrics(self, usage_data: Dict):
        """Atualiza métricas Prometheus (implementação futura)."""
        # TODO: Implementar métricas Prometheus para dashboard
        pass


# Função helper para configurar o middleware
def setup_legacy_tracking_middleware(app):
    """Configura o middleware de tracking de endpoints legacy."""

    if getattr(settings, "LEGACY_TRACKING_ENABLED", True):
        app.add_middleware(LegacyEndpointTrackingMiddleware)
        logger.info("Legacy endpoint tracking middleware habilitado")
    else:
        logger.info("Legacy endpoint tracking middleware desabilitado")


# Funções utilitárias para dashboard
def get_current_migration_phase() -> str:
    """Retorna a fase atual de migração."""
    middleware = LegacyEndpointTrackingMiddleware(None)
    return middleware.migration_phase


def get_migration_phase_info() -> Dict[str, Any]:
    """Retorna informações detalhadas da fase atual."""
    middleware = LegacyEndpointTrackingMiddleware(None)
    phase_id = middleware.migration_phase
    phase_config = middleware.MIGRATION_PHASES.get(phase_id, {})

    return {
        "current_phase": phase_id,
        "phase_name": phase_config.get("name", "Unknown"),
        "redirect_probability": phase_config.get("redirect_probability", 0.0),
        "warning_level": phase_config.get("warning_level", "info"),
        "start_date": phase_config.get("start_date", "unknown"),
    }
