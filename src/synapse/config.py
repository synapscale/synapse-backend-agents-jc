"""Configurações centralizadas para o backend SynapScale.

Este módulo contém todas as configurações centralizadas do sistema,
carregadas a partir de variáveis de ambiente com valores padrão seguros.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, validator


class Settings(BaseModel):
    """Configurações da aplicação."""

    # Configurações básicas
    app_name: str = "SynapScale Backend"
    project_name: str = "SynapScale Backend"
    app_version: str = "1.0.0"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Configurações de API
    api_v1_str: str = "/api/v1"

    # Configurações de segurança
    secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    algorithm: str = "HS256"  # Alias para jwt_algorithm
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Configurações de banco de dados - usando aiosqlite para async
    database_url: str = "sqlite+aiosqlite:///./synapse.db"
    database_echo: bool = False

    # Configurações de upload e storage
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_directory: str = "./storage"
    storage_base_path: str = "./storage"
    storage_provider: str = "local"
    
    allowed_extensions: List[str] = [
        "jpg", "jpeg", "png", "gif", "bmp", "svg", "webp",
        "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm",
        "mp3", "wav", "ogg", "m4a", "flac", "aac",
        "pdf", "doc", "docx", "txt", "rtf", "odt",
        "zip", "rar", "7z", "tar", "gz", "bz2"
    ]
    
    allowed_file_categories: List[str] = ["image", "video", "audio", "document", "archive"]

    # Configurações de rate limiting
    rate_limit: int = 100
    rate_limit_per_minute: int = 100
    rate_limit_window: int = 60
    upload_rate_limit_per_minute: int = 10

    # Configurações de CORS
    backend_cors_origins: List[str] = ["*"]
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: List[str] = ["*"]

    # Configurações de Redis (opcional)
    redis_url: Optional[str] = None

    # Configurações de logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "Settings":
        """Carrega configurações das variáveis de ambiente."""
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "development"),
            secret_key=os.getenv("SECRET_KEY", secrets.token_urlsafe(32)),
            database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./synapse.db"),
            upload_directory=os.getenv("UPLOAD_DIRECTORY", "./storage"),
            storage_base_path=os.getenv("STORAGE_BASE_PATH", "./storage"),
            redis_url=os.getenv("REDIS_URL"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_v1_str=os.getenv("API_V1_STR", "/api/v1"),
            project_name=os.getenv("PROJECT_NAME", "SynapScale Backend"),
        )


# Instância global das configurações
settings = Settings.from_env()
