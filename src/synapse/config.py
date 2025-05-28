"""
Configurações para o SynapScale Backend.

Este módulo define as configurações globais para o backend,
carregando variáveis de ambiente e definindo valores padrão.
"""
import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações do aplicativo carregadas de variáveis de ambiente.
    """
    # Configurações gerais
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SERVER_NAME: str = "SynapScale API"
    SERVER_HOST: AnyHttpUrl = Field(default="http://localhost")
    PROJECT_NAME: str = "SynapScale"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # CORS - Definido como string para evitar problemas de parse
    BACKEND_CORS_ORIGINS_STR: str = Field(default="*", alias="BACKEND_CORS_ORIGINS")
    
    # Configurações de banco de dados
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./synapse.db"
    
    # Configurações de LLM
    CLAUDE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    TESS_API_KEY: Optional[str] = None
    TESS_API_BASE_URL: str = "https://tess.pareto.io/api"
    OPENAI_API_KEY: Optional[str] = None
    LLAMA_API_KEY: Optional[str] = None
    LLAMA_API_BASE_URL: str = "https://llama.developer.meta.com/api/v1"
    LLM_DEFAULT_PROVIDER: str = "claude"
    LLM_ENABLE_CACHE: bool = True
    LLM_CACHE_TTL: int = 3600  # 1 hora
    
    # Configurações de upload de arquivos
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS_STR: str = Field(
        default="pdf,doc,docx,txt,csv,xls,xlsx,jpg,jpeg,png", 
        alias="ALLOWED_EXTENSIONS"
    )
    
    # Configurações de armazenamento
    STORAGE_BASE_PATH: str = Field(default="./storage", alias="STORAGE_BASE_PATH")
    STORAGE_PROVIDER: str = Field(default="local", alias="STORAGE_PROVIDER")
    
    # Configurações de rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_FILE_UPLOAD: str = "10/minute"
    RATE_LIMIT_LLM_GENERATE: str = "20/minute"
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hora em segundos
    
    # Configuração para pydantic-settings
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )
    
    # Propriedades para converter strings em listas
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Converte a string de origens CORS em uma lista."""
        if self.BACKEND_CORS_ORIGINS_STR == "*":
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS_STR.split(",")]
    
    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        """Converte a string de extensões permitidas em uma lista."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS_STR.split(",")]


# Instância global de configurações
settings = Settings()
