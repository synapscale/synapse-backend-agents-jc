"""Configuração de logging unificada para o backend SynapScale.

Este módulo integra as melhores funcionalidades de logging estruturado,
mantendo compatibilidade total com o código existente.

MIGRAÇÃO GRADUAL:
- Mantém interface existente para compatibilidade
- Adiciona funcionalidades avançadas opcionais
- Permite evolução sem quebrar código existente
"""

import json
import logging
import logging.handlers
import sys
import time
import traceback
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from synapse.core.config import settings


class ErrorTracker:
    """Sistema de rastreamento de erros integrado."""

    def __init__(self):
        self.error_counts = {}
        self.error_patterns = {}
        self.critical_errors = []
        self.start_time = time.time()

    def track_error(self, error_type: str, endpoint: str, details: Dict[str, Any]):
        """Registra um erro para análise."""

        # Contar erros por tipo
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1

        # Contar erros por endpoint
        if endpoint not in self.error_patterns:
            self.error_patterns[endpoint] = {}
        if error_type not in self.error_patterns[endpoint]:
            self.error_patterns[endpoint][error_type] = 0
        self.error_patterns[endpoint][error_type] += 1

        # Registrar erros críticos
        if details.get("level") == "CRITICAL" or details.get("status_code", 0) >= 500:
            self.critical_errors.append(
                {
                    "timestamp": time.time(),
                    "error_type": error_type,
                    "endpoint": endpoint,
                    "details": details,
                }
            )

            # Manter apenas os últimos 100 erros críticos
            if len(self.critical_errors) > 100:
                self.critical_errors = self.critical_errors[-100:]

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de erro."""

        uptime = time.time() - self.start_time
        total_errors = sum(self.error_counts.values())

        return {
            "uptime": uptime,
            "total_errors": total_errors,
            "error_rate": total_errors / uptime if uptime > 0 else 0,
            "error_counts_by_type": self.error_counts.copy(),
            "error_patterns_by_endpoint": self.error_patterns.copy(),
            "critical_errors_count": len(self.critical_errors),
            "recent_critical_errors": (
                self.critical_errors[-5:] if self.critical_errors else []
            ),
        }


# Instância global do tracker
error_tracker = ErrorTracker()


class UnifiedJSONFormatter(logging.Formatter):
    """Formatador unificado que combina as melhores funcionalidades."""

    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log como JSON estruturado."""

        # Dados básicos do log
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adicionar informações de contexto se disponíveis
        context_fields = [
            "request_id",
            "user_id",
            "endpoint_category",
            "url",
            "method",
            "status_code",
            "process_time",
            "error_type",
            "error_count",
        ]

        for field in context_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        # Adicionar exceção se existir
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Adicionar stack trace customizado se existir
        if hasattr(record, "traceback"):
            log_data["traceback"] = record.traceback

        # Adicionar outros atributos extras
        excluded_attrs = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "id",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "traceback",
        } | set(context_fields)

        for key, value in record.__dict__.items():
            if key not in excluded_attrs:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)


class UnifiedLogger:
    """Logger unificado que combina funcionalidades básicas e avançadas."""

    def __init__(self, name: str = "synapse"):
        self.logger = logging.getLogger(name)
        self._setup_handlers()

    def _setup_handlers(self):
        """Configura handlers baseado no ambiente."""

        # Limpar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)

        # Formatador baseado no ambiente
        if settings.ENVIRONMENT == "production":
            formatter = UnifiedJSONFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handlers de arquivo em produção ou se configurado
        if (
            settings.ENVIRONMENT == "production"
            or os.getenv("ENABLE_FILE_LOGGING", "false").lower() == "true"
        ):
            self._setup_file_handlers()

        # Configurar nível
        log_level_name = settings.LOG_LEVEL or "INFO"
        log_level = getattr(logging, log_level_name, logging.INFO)
        self.logger.setLevel(log_level)

    def _setup_file_handlers(self):
        """Configura handlers de arquivo para produção."""

        # Criar diretório de logs
        def _get_log_directory():
            """Lazy loading para evitar import circular com fallback seguro"""
            try:
                from synapse.core.config import settings
                return Path(settings.LOG_DIRECTORY)
            except ImportError:
                # Fallback seguro se houver problema circular
                return Path("logs")
        
        log_dir = _get_log_directory()
        log_dir.mkdir(exist_ok=True)

        # Handler principal
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "synapse.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setFormatter(UnifiedJSONFormatter())
        self.logger.addHandler(file_handler)

        # Handler para erros
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "synapse_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(UnifiedJSONFormatter())
        self.logger.addHandler(error_handler)

    # Métodos de logging básicos para compatibilidade
    def debug(self, message: str, *args, **kwargs):
        """Log de debug."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log de informação."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log de aviso."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log de erro."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log crítico."""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log de exceção (inclui traceback)."""
        self.logger.exception(message, *args, **kwargs)

    def log_error(
        self, error: Exception, request=None, context: Optional[Dict[str, Any]] = None
    ):
        """Log de erro com contexto detalhado."""

        error_type = error.__class__.__name__
        endpoint = str(request.url) if request else "unknown"

        extra = {
            "error_type": error_type,
            "traceback": traceback.format_exc(),
        }

        if request:
            extra.update(
                {
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "url": str(request.url),
                    "method": request.method,
                    "endpoint_category": getattr(
                        request.state, "endpoint_category", "unknown"
                    ),
                }
            )

        if context:
            extra.update(context)

        # Registrar no tracker
        error_tracker.track_error(error_type, endpoint, extra)

        # Log do erro
        self.logger.error(f"Error occurred: {error}", extra=extra, exc_info=True)


# Instância global unificada
_unified_logger = UnifiedLogger()


def setup_logging() -> None:
    """Configura o sistema de logging unificado.

    Esta função mantém compatibilidade com o código existente
    enquanto configura o sistema avançado.
    """
    # Configurar nível de log baseado no ambiente
    log_level_name = settings.LOG_LEVEL or "INFO"
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Criar handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)

    # Definir formatador baseado no ambiente
    if settings.ENVIRONMENT == "production":
        formatter = UnifiedJSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configurar loggers específicos
    for logger_name, logger_level in [
        ("uvicorn", log_level),
        ("uvicorn.access", log_level),
        ("sqlalchemy.engine", logging.WARNING),
        ("alembic", logging.INFO),
    ]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)

    # Log inicial
    logging.info(
        f"Logging unificado configurado: nível={settings.LOG_LEVEL or 'INFO'}, "
        f"ambiente={settings.ENVIRONMENT}",
    )


def get_logger(name: str = None) -> UnifiedLogger:
    """Obtém um logger configurado para o módulo especificado.

    UNIFICADO: Agora retorna UnifiedLogger com todas as funcionalidades avançadas
    mantendo 100% de compatibilidade com código existente.

    Args:
        name: Nome do módulo ou componente

    Returns:
        UnifiedLogger com funcionalidades completas (ErrorTracker, JSON, etc.)
    """
    if name:
        return UnifiedLogger(name)
    return _unified_logger


def get_error_stats() -> Dict[str, Any]:
    """Retorna estatísticas de erro do sistema.

    NOVA FUNCIONALIDADE: Para monitoramento e análise.
    """
    return error_tracker.get_stats()


class RequestContextFilter(logging.Filter):
    """Filtro para adicionar contexto de requisição aos logs."""

    def __init__(self, request_id: str | None = None, user_id: str | None = None):
        """Inicializa o filtro com IDs de requisição e usuário.

        Args:
            request_id: ID único da requisição (opcional)
            user_id: ID do usuário (opcional)
        """
        super().__init__()
        self.request_id = request_id
        self.user_id = user_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Adiciona contexto ao registro de log.

        Args:
            record: Registro de log

        Returns:
            True para permitir o registro
        """
        if self.request_id:
            record.request_id = self.request_id

        if self.user_id:
            record.user_id = self.user_id

        return True
