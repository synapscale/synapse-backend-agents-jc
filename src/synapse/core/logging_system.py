"""Sistema de logging estruturado avançado para SynapScale.

Este módulo implementa logging estruturado com captura detalhada de erros,
contexto de requisições, métricas e integração com sistemas de monitoramento.
"""

import json
import logging
import logging.handlers
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from fastapi import Request


class StructuredFormatter(logging.Formatter):
    """Formatter para logging estruturado em JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log em estrutura JSON."""
        
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar informações extras se disponíveis
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
            
        if hasattr(record, "endpoint_category"):
            log_data["endpoint_category"] = record.endpoint_category
            
        if hasattr(record, "url"):
            log_data["url"] = record.url
            
        if hasattr(record, "method"):
            log_data["method"] = record.method
            
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
            
        if hasattr(record, "process_time"):
            log_data["process_time"] = record.process_time
            
        if hasattr(record, "error_type"):
            log_data["error_type"] = record.error_type
            
        if hasattr(record, "error_count"):
            log_data["error_count"] = record.error_count
            
        if hasattr(record, "traceback"):
            log_data["traceback"] = record.traceback
            
        # Adicionar stack trace para erros
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ErrorTracker:
    """Classe para rastrear e analisar erros."""
    
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
            self.critical_errors.append({
                "timestamp": time.time(),
                "error_type": error_type,
                "endpoint": endpoint,
                "details": details
            })
            
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
            "recent_critical_errors": self.critical_errors[-5:] if self.critical_errors else []
        }


# Instância global do tracker
error_tracker = ErrorTracker()


class SystemLogFilter(logging.Filter):
    """Filter for system-level events for centralized logging."""
    
    def filter(self, record):
        """Filter system-level log records."""
        system_modules = [
            'synapse.main',
            'synapse.core.tracing',
            'synapse.core.config',
            'synapse.database',
            'synapse.middlewares',
            'uvicorn',
            'sqlalchemy.engine'
        ]
        
        return any(module in record.name for module in system_modules)


class LLMLogFilter(logging.Filter):
    """Filter for LLM-related events for centralized logging."""
    
    def filter(self, record):
        """Filter LLM-related log records."""
        llm_modules = [
            'synapse.services.llm',
            'synapse.api.v1.endpoints.llm',
            'synapse.core.llm'
        ]
        
        # Check if it's an LLM module or has LLM-related attributes
        is_llm_module = any(module in record.name for module in llm_modules)
        has_llm_attributes = hasattr(record, 'endpoint_category') and 'llm' in getattr(record, 'endpoint_category', '').lower()
        
        return is_llm_module or has_llm_attributes


class SynapScaleLogger:
    """Logger principal do SynapScale com funcionalidades avançadas."""
    
    def __init__(self, name: str = "synapse"):
        self.logger = logging.getLogger(name)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configura os handlers de logging."""
        
        # Limpar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo (produção) - Centralized logging compatible
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Main application log for Loki consumption
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "synapse.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # Handler para erros críticos
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "synapse_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        # Centralized logging - System log for infrastructure events
        system_handler = logging.handlers.RotatingFileHandler(
            log_dir / "system.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        system_handler.setFormatter(StructuredFormatter())
        system_handler.addFilter(SystemLogFilter())  # Only system-level events
        self.logger.addHandler(system_handler)
        
        # Centralized logging - LLM operations log
        llm_handler = logging.handlers.RotatingFileHandler(
            log_dir / "llm_operations.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        llm_handler.setFormatter(StructuredFormatter())
        llm_handler.addFilter(LLMLogFilter())  # Only LLM-related events
        self.logger.addHandler(llm_handler)
        
        # Configurar nível
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    def log_error(self, error: Exception, request: Optional[Request] = None, 
                  context: Optional[Dict[str, Any]] = None):
        """Log de erro com contexto detalhado."""
        
        error_type = error.__class__.__name__
        endpoint = str(request.url) if request else "unknown"
        
        extra = {
            "error_type": error_type,
            "traceback": traceback.format_exc(),
        }
        
        if request:
            extra.update({
                "request_id": getattr(request.state, "request_id", "unknown"),
                "url": str(request.url),
                "method": request.method,
                "endpoint_category": getattr(request.state, "endpoint_category", "unknown"),
            })
        
        if context:
            extra.update(context)
        
        # Registrar no tracker
        error_tracker.track_error(error_type, endpoint, extra)
        
        # Log do erro
        self.logger.error(f"Error occurred: {error}", extra=extra, exc_info=True)


# Instância global do logger
synapse_logger = SynapScaleLogger()


def get_logger(name: str = None) -> SynapScaleLogger:
    """Retorna uma instância do logger SynapScale."""
    if name:
        return SynapScaleLogger(name)
    return synapse_logger


def get_error_stats() -> Dict[str, Any]:
    """Retorna estatísticas de erro do sistema."""
    return error_tracker.get_stats()


def get_logging_service() -> SynapScaleLogger:
    """Factory function to get the logging service for dependency injection."""
    return synapse_logger 