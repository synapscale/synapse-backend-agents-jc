"""
Configuração unificada da aplicação SynapScale.

Este módulo centraliza todas as configurações da aplicação, carregando
valores de variáveis de ambiente definidas no arquivo .env.

Todas as configurações são validadas usando Pydantic v2.
"""

import json
import logging
import os
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from synapse.constants import FILE_CATEGORIES


def _parse_list_env(value: str | None) -> list[str]:
    """Parse environment variable to list of strings."""
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """
    Configurações da aplicação com validação.

    Todas as configurações são carregadas de variáveis de ambiente
    definidas no arquivo .env na raiz do projeto.
    """

    # ============================
    # CONFIGURAÇÕES GERAIS
    # ============================
    ENVIRONMENT: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Ambiente de execução",
    )
    DEBUG: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true",
        description="Modo debug",
    )
    PROJECT_NAME: str = Field(
        default_factory=lambda: os.getenv("PROJECT_NAME", "SynapScale Backend API"),
        description="Nome do projeto",
    )
    VERSION: str = Field(
        default_factory=lambda: os.getenv("VERSION", "2.0.0"),
        description="Versão do projeto",
    )
    API_V1_STR: str = Field(
        default_factory=lambda: os.getenv("API_V1_STR", "/api/v1"),
        description="Prefixo da API v1",
    )
    DESCRIPTION: str = Field(
        default_factory=lambda: os.getenv(
            "DESCRIPTION", "Plataforma de Automação com IA"
        ),
        description="Descrição do projeto",
    )
    SERVER_HOST: str = Field(
        default_factory=lambda: os.getenv("SERVER_HOST", "http://localhost:8000"),
        description="URL do servidor",
    )
    HOST: str = Field(
        default_factory=lambda: os.getenv("HOST", "0.0.0.0"),
        description="Host do servidor",
    )
    PORT: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000")),
        description="Porta do servidor",
    )
    SERVER_PORT: int = Field(
        default_factory=lambda: int(
            os.getenv("SERVER_PORT", os.getenv("PORT", "8000"))
        ),
        description="Porta do servidor (alias para PORT)",
    )

    # ============================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ============================
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY"),
        description="Chave secreta para JWT",
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY"),
        description="Chave secreta para assinatura JWT",
    )
    ENCRYPTION_KEY: str | None = Field(
        default_factory=lambda: os.getenv("ENCRYPTION_KEY"),
        description="Chave de criptografia para dados sensíveis (Base64)",
    )
    JWT_ALGORITHM: str = Field(
        default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"),
        description="Algoritmo de assinatura JWT",
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        description="Tempo de expiração do access token em minutos",
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        description="Tempo de expiração do refresh token em dias",
    )

    # ============================
    # CONFIGURAÇÕES DO BANCO DE DADOS
    # ============================
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL"),
        description="URL de conexão com o banco de dados",
    )
    DATABASE_SCHEMA: str = Field(
        default_factory=lambda: os.getenv("DATABASE_SCHEMA", "synapscale_db"),
        description="Schema do banco de dados",
    )
    DATABASE_POOL_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("DATABASE_POOL_SIZE", "20")),
        description="Tamanho do pool de conexões",
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default_factory=lambda: int(os.getenv("DATABASE_MAX_OVERFLOW", "30")),
        description="Overflow máximo do pool",
    )
    DATABASE_ECHO: bool = Field(
        default_factory=lambda: os.getenv("DATABASE_ECHO", "False").lower() == "true",
        description="Habilitar log SQL",
    )
    DATABASE_POOL_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("DATABASE_POOL_TIMEOUT", "30")),
        description="Timeout do pool de conexões",
    )
    DATABASE_POOL_RECYCLE: int = Field(
        default_factory=lambda: int(os.getenv("DATABASE_POOL_RECYCLE", "3600")),
        description="Tempo de reciclagem de conexões",
    )
    POSTGRES_USER: str | None = Field(
        default_factory=lambda: os.getenv("POSTGRES_USER"),
        description="Usuário PostgreSQL",
    )
    POSTGRES_PASSWORD: str | None = Field(
        default_factory=lambda: os.getenv("POSTGRES_PASSWORD"),
        description="Senha PostgreSQL",
    )
    POSTGRES_DB: str | None = Field(
        default_factory=lambda: os.getenv("POSTGRES_DB"),
        description="Nome do banco PostgreSQL",
    )

    # ============================
    # CONFIGURAÇÕES DE REDIS
    # ============================
    REDIS_URL: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_URL"), description="URL do Redis"
    )
    REDIS_PASSWORD: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_PASSWORD"),
        description="Senha do Redis",
    )
    REDIS_DB: int = Field(
        default_factory=lambda: int(os.getenv("REDIS_DB", "0")),
        description="Banco de dados do Redis",
    )

    # ============================
    # CONFIGURAÇÕES DE CORS
    # ============================
    BACKEND_CORS_ORIGINS: str = Field(
        default_factory=lambda: os.getenv(
            "BACKEND_CORS_ORIGINS", '["http://localhost:3000"]'
        ),
        description="Origens permitidas para CORS (formato JSON)",
    )
    FRONTEND_URL: str = Field(
        default_factory=lambda: os.getenv("FRONTEND_URL", "http://localhost:3000"),
        description="URL do frontend",
    )
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: (
            os.getenv("CORS_ORIGINS").split(",") if os.getenv("CORS_ORIGINS") else []
        ),
        description="Origens permitidas para CORS",
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default_factory=lambda: _parse_list_env(
            os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
        ),
        description="Métodos HTTP permitidos para CORS",
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default_factory=lambda: _parse_list_env(os.getenv("CORS_ALLOW_HEADERS", "*")),
        description="Cabeçalhos permitidos para CORS",
    )
    CORS_EXPOSE_HEADERS: list[str] = Field(
        default_factory=lambda: _parse_list_env(os.getenv("CORS_EXPOSE_HEADERS", "")),
        description="Cabeçalhos expostos pelo CORS",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower()
        == "true",
        description="Permitir credenciais no CORS",
    )
    CORS_MAX_AGE: int = Field(
        default_factory=lambda: int(os.getenv("CORS_MAX_AGE", "600")),
        description="Tempo máximo de cache para CORS",
    )

    @property
    def backend_cors_origins_list(self) -> list[str]:
        """Converte BACKEND_CORS_ORIGINS de string JSON para lista"""
        val = self.BACKEND_CORS_ORIGINS
        logger = logging.getLogger(__name__)
        if not val:
            return []
        try:
            result = json.loads(val)
            if isinstance(result, list):
                return [o.strip().rstrip("/") for o in result]
        except Exception as e:
            logger.warning(
                f"BACKEND_CORS_ORIGINS não é JSON válido: {e}. Tentando CSV."
            )
        if "," in val:
            return [o.strip().rstrip("/") for o in val.split(",") if o.strip()]
        logger.warning("BACKEND_CORS_ORIGINS não é JSON nem CSV. Usando valor bruto.")
        return [val.strip().rstrip("/")]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> str:
        """Parse CORS origins from various formats to JSON string"""
        if isinstance(v, str):
            if not v:
                return "[]"
            try:
                json.loads(v)
                return v
            except json.JSONDecodeError:
                return json.dumps([v.strip()])
        if isinstance(v, list):
            return json.dumps(v)
        return str(v)

    # ============================
    # CONFIGURAÇÕES DE LLM/IA
    # ============================
    LLM_DEFAULT_PROVIDER: str = Field(
        default_factory=lambda: os.getenv("LLM_DEFAULT_PROVIDER", "claude"),
        description="Provedor LLM padrão",
    )

    # OpenAI
    OPENAI_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="Chave da API OpenAI",
    )
    OPENAI_ORG_ID: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_ORG_ID"),
        description="ID da organização OpenAI",
    )
    OPENAI_API_BASE: str = Field(
        default_factory=lambda: os.getenv(
            "OPENAI_API_BASE", "https://api.openai.com/v1"
        ),
        description="URL base da API OpenAI",
    )
    OPENAI_API_VERSION: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_VERSION"),
        description="Versão da API OpenAI",
    )
    OPENAI_API_TYPE: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_TYPE", "openai"),
        description="Tipo da API OpenAI",
    )
    OPENAI_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("OPENAI_TIMEOUT", "60")),
        description="Timeout OpenAI",
    )
    OPENAI_MAX_RETRIES: int = Field(
        default_factory=lambda: int(os.getenv("OPENAI_MAX_RETRIES", "3")),
        description="Max retries OpenAI",
    )
    OPENAI_DEFAULT_MODEL: str = Field(
        default_factory=lambda: os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o"),
        description="Modelo OpenAI padrão",
    )

    # Outros provedores LLM
    ANTHROPIC_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"),
        description="Chave da API Anthropic",
    )
    GOOGLE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY"),
        description="Chave da API Google",
    )
    GROK_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("GROK_API_KEY"),
        description="Chave da API Grok",
    )
    DEEPSEEK_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"),
        description="Chave da API DeepSeek",
    )
    LLAMA_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("LLAMA_API_KEY"),
        description="Chave da API Llama",
    )
    HUGGINGFACE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("HUGGINGFACE_API_KEY"),
        description="Chave da API HuggingFace",
    )
    MISTRAL_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("MISTRAL_API_KEY"),
        description="Chave da API Mistral",
    )
    COHERE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("COHERE_API_KEY"),
        description="Chave da API Cohere",
    )

    # Tess
    TESS_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("TESS_API_KEY"),
        description="Chave da API Tess",
    )
    TESS_API_BASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "TESS_API_BASE_URL", "https://tess.pareto.io/api"
        ),
        description="URL base da API Tess",
    )

    # ============================
    # CONFIGURAÇÕES DE EMAIL/SMTP
    # ============================
    SMTP_HOST: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_HOST"), description="Host SMTP"
    )
    SMTP_PORT: int | None = Field(
        default_factory=lambda: (
            int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
        ),
        description="Porta SMTP",
    )
    SMTP_USERNAME: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_USERNAME"), description="Usuário SMTP"
    )
    SMTP_PASSWORD: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_PASSWORD"), description="Senha SMTP"
    )
    SMTP_FROM_EMAIL: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_FROM_EMAIL"),
        description="Email remetente",
    )
    SMTP_FROM_NAME: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_FROM_NAME"),
        description="Nome remetente",
    )
    SMTP_USE_TLS: bool = Field(
        default_factory=lambda: os.getenv("SMTP_USE_TLS", "True").lower() == "true",
        description="Usar TLS no SMTP",
    )
    EMAIL_NOTIFICATIONS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "True").lower()
        == "true",
        description="Habilitar notificações por email",
    )

    # ============================
    # CONFIGURAÇÕES DE ARMAZENAMENTO
    # ============================
    STORAGE_TYPE: str = Field(
        default_factory=lambda: os.getenv("STORAGE_TYPE", "local"),
        description="Tipo de armazenamento",
    )
    STORAGE_BASE_PATH: str = Field(
        default_factory=lambda: os.getenv("STORAGE_BASE_PATH", "./storage"),
        description="Caminho base para armazenamento",
    )
    MAX_UPLOAD_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", "52428800")),
        description="Tamanho máximo de upload",
    )
    UPLOAD_DIR: str = Field(
        default_factory=lambda: os.getenv("UPLOAD_DIR", "./uploads"),
        description="Diretório de uploads",
    )
    UPLOAD_FOLDER: str = Field(
        default_factory=lambda: os.getenv("UPLOAD_FOLDER", "./uploads"),
        description="Pasta de uploads (alias para UPLOAD_DIR)",
    )
    ALLOWED_FILE_TYPES: str = Field(
        default_factory=lambda: os.getenv("ALLOWED_FILE_TYPES", "[]"),
        description="Tipos de arquivo permitidos",
    )
    ALLOWED_EXTENSIONS: str = Field(
        default_factory=lambda: os.getenv(
            "ALLOWED_EXTENSIONS", ".pdf,.doc,.docx,.txt,.csv"
        ),
        description="Extensões permitidas",
    )
    ALLOWED_FILE_EXTENSIONS: list[str] = Field(
        default_factory=lambda: _parse_list_env(
            os.getenv("ALLOWED_FILE_EXTENSIONS", ".pdf,.doc,.docx,.txt,.csv")
        ),
        description="Lista de extensões permitidas",
    )
    MAX_FILE_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "10485760")),
        description="Tamanho máximo de arquivo",
    )

    # AWS S3
    AWS_ACCESS_KEY_ID: str | None = Field(
        default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID"),
        description="Chave de acesso AWS",
    )
    AWS_SECRET_ACCESS_KEY: str | None = Field(
        default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY"),
        description="Chave secreta AWS",
    )
    AWS_BUCKET_NAME: str | None = Field(
        default_factory=lambda: os.getenv("AWS_BUCKET_NAME"),
        description="Nome do bucket S3",
    )
    AWS_REGION: str = Field(
        default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"),
        description="Região AWS",
    )

    # Google Cloud Storage
    GCS_BUCKET_NAME: str | None = Field(
        default_factory=lambda: os.getenv("GCS_BUCKET_NAME"),
        description="Nome do bucket GCS",
    )
    GCS_CREDENTIALS_PATH: str | None = Field(
        default_factory=lambda: os.getenv("GCS_CREDENTIALS_PATH"),
        description="Caminho para credenciais GCS",
    )

    # ============================
    # CONFIGURAÇÕES DE RATE LIMITING
    # ============================
    RATE_LIMIT_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "True").lower()
        == "true",
        description="Habilitar rate limiting",
    )
    RATE_LIMIT_DEFAULT: str = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_DEFAULT", "100/minute"),
        description="Rate limit padrão",
    )
    RATE_LIMIT_FILE_UPLOAD: str = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_FILE_UPLOAD", "10/minute"),
        description="Rate limit para upload de arquivos",
    )
    RATE_LIMIT_LLM_GENERATE: str = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_LLM_GENERATE", "20/minute"),
        description="Rate limit para geração LLM",
    )
    RATE_LIMIT_AUTH: str = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_AUTH", "5/minute"),
        description="Rate limit para autenticação",
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
        description="Número de requisições permitidas",
    )
    RATE_LIMIT_WINDOW: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        description="Janela de tempo em segundos",
    )

    # ============================
    # CONFIGURAÇÕES DE WEBSOCKET
    # ============================
    WEBSOCKET_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("WEBSOCKET_ENABLED", "True").lower()
        == "true",
        description="Habilitar WebSocket",
    )
    WEBSOCKET_PATH: str = Field(
        default_factory=lambda: os.getenv("WEBSOCKET_PATH", "/ws"),
        description="Caminho do WebSocket",
    )
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(
        default_factory=lambda: int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30")),
        description="Intervalo de heartbeat",
    )
    WEBSOCKET_MAX_CONNECTIONS: int = Field(
        default_factory=lambda: int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", "1000")),
        description="Máximo de conexões WebSocket",
    )
    WEBSOCKET_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("WEBSOCKET_TIMEOUT", "300")),
        description="Timeout do WebSocket",
    )
    WS_MAX_CONNECTIONS_PER_USER: int = Field(
        default_factory=lambda: int(os.getenv("WS_MAX_CONNECTIONS_PER_USER", "5")),
        description="Máximo de conexões por usuário",
    )
    WS_MESSAGE_MAX_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("WS_MESSAGE_MAX_SIZE", "1048576")),
        description="Tamanho máximo de mensagem WebSocket",
    )
    WS_HEARTBEAT_INTERVAL: int = Field(
        default_factory=lambda: int(os.getenv("WS_HEARTBEAT_INTERVAL", "30")),
        description="Intervalo de heartbeat WebSocket",
    )

    # ============================
    # CONFIGURAÇÕES DE MONITORAMENTO
    # ============================
    SENTRY_DSN: str | None = Field(
        default_factory=lambda: os.getenv("SENTRY_DSN"), description="DSN do Sentry"
    )
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Nível de logging",
    )
    LOG_FORMAT: str = Field(
        default_factory=lambda: os.getenv("LOG_FORMAT", "json"),
        description="Formato do log",
    )
    LOG_FILE: str = Field(
        default_factory=lambda: os.getenv("LOG_FILE", "logs/synapscale.log"),
        description="Arquivo de log",
    )
    ENABLE_METRICS: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_METRICS", "True").lower() == "true",
        description="Habilitar métricas",
    )
    ENABLE_TRACING: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_TRACING", "False").lower() == "true",
        description="Habilitar tracing",
    )

    # Configurações de logging centralizado
    ENABLE_CENTRALIZED_LOGGING: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_CENTRALIZED_LOGGING", "True").lower()
        == "true",
        description="Habilitar logging centralizado",
    )
    LOKI_URL: str | None = Field(
        default_factory=lambda: os.getenv("LOKI_URL"), description="URL do Loki"
    )
    LOKI_PUSH_URL: str | None = Field(
        default_factory=lambda: os.getenv("LOKI_PUSH_URL"),
        description="URL de push do Loki",
    )
    LOG_RETENTION_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("LOG_RETENTION_DAYS", "7")),
        description="Dias de retenção de logs",
    )
    CENTRALIZED_LOG_LABELS: str = Field(
        default_factory=lambda: os.getenv(
            "CENTRALIZED_LOG_LABELS",
            '{"service":"synapscale","environment":"development"}',
        ),
        description="Labels para logs centralizados",
    )
    ENABLE_LOG_FILE_OUTPUT: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_LOG_FILE_OUTPUT", "True").lower()
        == "true",
        description="Habilitar saída para arquivo de log",
    )
    LOG_DIRECTORY: str = Field(
        default_factory=lambda: os.getenv("LOG_DIRECTORY", "logs"),
        description="Diretório de logs",
    )

    # ============================
    # CONFIGURAÇÕES DE CACHE
    # ============================
    CACHE_TTL_DEFAULT: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_DEFAULT", "300")),
        description="TTL padrão do cache",
    )
    CACHE_TTL_USER_DATA: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_USER_DATA", "900")),
        description="TTL do cache para dados de usuário",
    )
    CACHE_TTL_STATIC_DATA: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_STATIC_DATA", "3600")),
        description="TTL do cache para dados estáticos",
    )
    CACHE_TTL: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL", "3600")),
        description="TTL do cache",
    )

    # ============================
    # CONFIGURAÇÕES DE EXECUÇÃO
    # ============================
    WORKFLOW_EXECUTION_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("WORKFLOW_EXECUTION_TIMEOUT", "300")),
        description="Timeout de execução de workflow",
    )
    MAX_CONCURRENT_EXECUTIONS: int = Field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_EXECUTIONS", "10")),
        description="Máximo de execuções concorrentes",
    )
    EXECUTION_RETRY_ATTEMPTS: int = Field(
        default_factory=lambda: int(os.getenv("EXECUTION_RETRY_ATTEMPTS", "3")),
        description="Tentativas de retry de execução",
    )

    # ============================
    # CONFIGURAÇÕES DE MARKETPLACE
    # ============================
    MARKETPLACE_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("MARKETPLACE_ENABLED", "True").lower()
        == "true",
        description="Habilitar marketplace",
    )
    MARKETPLACE_APPROVAL_REQUIRED: bool = Field(
        default_factory=lambda: os.getenv(
            "MARKETPLACE_APPROVAL_REQUIRED", "True"
        ).lower()
        == "true",
        description="Exigir aprovação no marketplace",
    )
    MARKETPLACE_COMMISSION_RATE: float = Field(
        default_factory=lambda: float(os.getenv("MARKETPLACE_COMMISSION_RATE", "0.15")),
        description="Taxa de comissão do marketplace",
    )

    # ============================
    # CONFIGURAÇÕES DE NOTIFICAÇÕES
    # ============================
    NOTIFICATIONS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("NOTIFICATIONS_ENABLED", "True").lower()
        == "true",
        description="Habilitar notificações",
    )
    PUSH_NOTIFICATIONS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("PUSH_NOTIFICATIONS_ENABLED", "False").lower()
        == "true",
        description="Habilitar notificações push",
    )

    # ============================
    # CONFIGURAÇÕES DE ANALYTICS
    # ============================
    ANALYTICS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("ANALYTICS_ENABLED", "True").lower()
        == "true",
        description="Habilitar analytics",
    )
    ANALYTICS_RETENTION_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("ANALYTICS_RETENTION_DAYS", "90")),
        description="Dias de retenção de analytics",
    )

    # ============================
    # CONFIGURAÇÕES DE BACKUP
    # ============================
    BACKUP_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("BACKUP_ENABLED", "True").lower() == "true",
        description="Habilitar backup",
    )
    BACKUP_INTERVAL_HOURS: int = Field(
        default_factory=lambda: int(os.getenv("BACKUP_INTERVAL_HOURS", "24")),
        description="Intervalo de backup em horas",
    )
    BACKUP_RETENTION_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
        description="Dias de retenção de backup",
    )
    BACKUP_SCHEDULE: str = Field(
        default_factory=lambda: os.getenv("BACKUP_SCHEDULE", "0 2 * * *"),
        description="Schedule do backup (cron)",
    )

    # ============================
    # CONFIGURAÇÕES DE DESENVOLVIMENTO
    # ============================
    RELOAD_ON_CHANGE: bool = Field(
        default_factory=lambda: os.getenv("RELOAD_ON_CHANGE", "True").lower() == "true",
        description="Recarregar ao modificar código",
    )
    SHOW_DOCS: bool = Field(
        default_factory=lambda: os.getenv("SHOW_DOCS", "True").lower() == "true",
        description="Mostrar documentação",
    )
    ENABLE_PROFILING: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_PROFILING", "False").lower()
        == "true",
        description="Habilitar profiling",
    )

    # ============================
    # CONFIGURAÇÕES DE WEBHOOK
    # ============================
    WEBHOOK_SECRET: str | None = Field(
        default_factory=lambda: os.getenv("WEBHOOK_SECRET"),
        description="Chave secreta para webhooks",
    )
    WEBHOOK_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("WEBHOOK_TIMEOUT", "30")),
        description="Timeout de webhook",
    )

    # ============================
    # CONFIGURAÇÕES DE SEGURANÇA AVANÇADA
    # ============================
    ENABLE_HTTPS_REDIRECT: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_HTTPS_REDIRECT", "False").lower()
        == "true",
        description="Habilitar redirecionamento HTTPS",
    )
    SECURE_COOKIES: bool = Field(
        default_factory=lambda: os.getenv("SECURE_COOKIES", "False").lower() == "true",
        description="Usar cookies seguros",
    )
    CSRF_PROTECTION: bool = Field(
        default_factory=lambda: os.getenv("CSRF_PROTECTION", "True").lower() == "true",
        description="Habilitar proteção CSRF",
    )

    # ============================
    # CONFIGURAÇÕES DE PRODUÇÃO
    # ============================
    PROMETHEUS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("PROMETHEUS_ENABLED", "False").lower()
        == "true",
        description="Habilitar Prometheus",
    )
    HEALTH_CHECK_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("HEALTH_CHECK_ENABLED", "True").lower()
        == "true",
        description="Habilitar health check",
    )

    # ============================
    # PROPRIEDADES COMPUTADAS
    # ============================
    @property
    def FILE_CATEGORIES(self) -> dict:
        """Importa categorias de arquivo do módulo constants"""
        return FILE_CATEGORIES

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"
        json_schema_extra = {
            "example": {
                "DATABASE_URL": "postgresql://user:pass@localhost/db",
                "SECRET_KEY": "your-secret-key",
                "DEBUG": False,
            }
        }

    # ============================
    # MÉTODOS UTILITÁRIOS
    # ============================
    def get_llm_providers(self) -> dict[str, Any]:
        """Retorna configurações dos provedores LLM disponíveis"""
        providers = {}

        if self.OPENAI_API_KEY:
            providers["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "org_id": self.OPENAI_ORG_ID,
                "api_base": self.OPENAI_API_BASE,
                "api_version": self.OPENAI_API_VERSION,
                "api_type": self.OPENAI_API_TYPE,
                "timeout": self.OPENAI_TIMEOUT,
                "max_retries": self.OPENAI_MAX_RETRIES,
                "default_model": self.OPENAI_DEFAULT_MODEL,
            }

        if self.ANTHROPIC_API_KEY:
            providers["anthropic"] = {
                "api_key": self.ANTHROPIC_API_KEY,
            }

        if self.GOOGLE_API_KEY:
            providers["google"] = {
                "api_key": self.GOOGLE_API_KEY,
            }

        if self.GROK_API_KEY:
            providers["grok"] = {
                "api_key": self.GROK_API_KEY,
            }

        if self.DEEPSEEK_API_KEY:
            providers["deepseek"] = {
                "api_key": self.DEEPSEEK_API_KEY,
            }

        if self.LLAMA_API_KEY:
            providers["llama"] = {
                "api_key": self.LLAMA_API_KEY,
            }

        if self.HUGGINGFACE_API_KEY:
            providers["huggingface"] = {
                "api_key": self.HUGGINGFACE_API_KEY,
            }

        if self.MISTRAL_API_KEY:
            providers["mistral"] = {
                "api_key": self.MISTRAL_API_KEY,
            }

        if self.COHERE_API_KEY:
            providers["cohere"] = {
                "api_key": self.COHERE_API_KEY,
            }

        if self.TESS_API_KEY:
            providers["tess"] = {
                "api_key": self.TESS_API_KEY,
                "base_url": self.TESS_API_BASE_URL,
            }

        return providers

    def validate_openai_config(self) -> dict[str, Any]:
        """Valida e retorna configuração do OpenAI com formato padronizado"""
        errors = []
        warnings = []

        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY é obrigatória")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "config": {},
            }

        config = {
            "api_key": self.OPENAI_API_KEY,
            "timeout": self.OPENAI_TIMEOUT,
            "max_retries": self.OPENAI_MAX_RETRIES,
        }

        if self.OPENAI_ORG_ID:
            config["organization"] = self.OPENAI_ORG_ID

        if self.OPENAI_API_TYPE == "azure":
            if not self.OPENAI_API_BASE or not self.OPENAI_API_VERSION:
                errors.append(
                    "Para Azure OpenAI, OPENAI_API_BASE e OPENAI_API_VERSION são obrigatórios"
                )
                return {
                    "valid": False,
                    "errors": errors,
                    "warnings": warnings,
                    "config": {},
                }
            config.update(
                {
                    "azure_endpoint": self.OPENAI_API_BASE,
                    "api_version": self.OPENAI_API_VERSION,
                }
            )
        else:
            if self.OPENAI_API_BASE != "https://api.openai.com/v1":
                config["base_url"] = self.OPENAI_API_BASE

        # Validações de configuração
        if self.OPENAI_TIMEOUT < 10:
            warnings.append("OPENAI_TIMEOUT muito baixo, recomendado >= 10 segundos")

        if self.OPENAI_MAX_RETRIES > 5:
            warnings.append("OPENAI_MAX_RETRIES muito alto, pode causar lentidão")

        return {"valid": True, "errors": errors, "warnings": warnings, "config": config}

    def get_openai_client_config(self) -> dict[str, Any]:
        """Retorna configuração para cliente OpenAI"""
        validation_result = self.validate_openai_config()
        if not validation_result["valid"]:
            raise ValueError(
                f"Configuração OpenAI inválida: {validation_result['errors']}"
            )
        return validation_result["config"]

    def get_database_url(self) -> str:
        """Retorna URL do banco de dados"""
        return self.DATABASE_URL

    def get_cors_origins(self) -> list[str]:
        """Retorna lista de origens CORS permitidas"""
        return self.backend_cors_origins_list

    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.ENVIRONMENT.lower() == "development"

    def get_storage_config(self) -> dict:
        """Retorna configuração de armazenamento"""
        config = {
            "type": self.STORAGE_TYPE,
            "base_path": self.STORAGE_BASE_PATH,
            "max_upload_size": self.MAX_UPLOAD_SIZE,
        }

        if self.STORAGE_TYPE == "s3":
            config.update(
                {
                    "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
                    "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY,
                    "bucket_name": self.AWS_BUCKET_NAME,
                    "region": self.AWS_REGION,
                }
            )
        elif self.STORAGE_TYPE == "gcs":
            config.update(
                {
                    "bucket_name": self.GCS_BUCKET_NAME,
                    "credentials_path": self.GCS_CREDENTIALS_PATH,
                }
            )

        return config

    def get_email_config(self) -> dict:
        """Retorna configuração de email"""
        return {
            "smtp_host": self.SMTP_HOST,
            "smtp_port": self.SMTP_PORT,
            "smtp_username": self.SMTP_USERNAME,
            "smtp_password": self.SMTP_PASSWORD,
            "smtp_from_email": self.SMTP_FROM_EMAIL,
            "smtp_from_name": self.SMTP_FROM_NAME,
            "smtp_use_tls": self.SMTP_USE_TLS,
        }

    def get_redis_config(self) -> dict:
        """Retorna configuração do Redis"""
        return {
            "url": self.REDIS_URL,
            "password": self.REDIS_PASSWORD,
            "db": self.REDIS_DB,
        }

    def get_database_config(self) -> dict[str, Any]:
        """Retorna configuração completa do banco de dados"""
        return {
            "url": self.DATABASE_URL,
            "schema": self.DATABASE_SCHEMA,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT,
            "pool_recycle": self.DATABASE_POOL_RECYCLE,
            "echo": self.DATABASE_ECHO,
        }


def setup_logging() -> None:
    """Configura o sistema de logging da aplicação"""
    import sys

    settings = get_settings()

    # Configuração básica do logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Formato do log
    if settings.LOG_FORMAT == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Handler para arquivo (se habilitado)
    handlers = [console_handler]

    if settings.ENABLE_LOG_FILE_OUTPUT and settings.LOG_FILE:
        import os

        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        handlers.append(file_handler)

    # Configuração do root logger
    logging.basicConfig(level=log_level, handlers=handlers, force=True)

    # Configuração específica para bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DATABASE_ECHO else logging.WARNING
    )


def validate_settings():
    """Valida as configurações críticas da aplicação"""
    settings = get_settings()

    # Validações críticas
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY é obrigatória")

    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY é obrigatória")

    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL é obrigatória")

    # Validações condicionais
    if settings.STORAGE_TYPE == "s3":
        if not all(
            [
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY,
                settings.AWS_BUCKET_NAME,
            ]
        ):
            raise ValueError(
                "Para STORAGE_TYPE=s3, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY e AWS_BUCKET_NAME são obrigatórios"
            )

    if settings.STORAGE_TYPE == "gcs":
        if not all([settings.GCS_BUCKET_NAME, settings.GCS_CREDENTIALS_PATH]):
            raise ValueError(
                "Para STORAGE_TYPE=gcs, GCS_BUCKET_NAME e GCS_CREDENTIALS_PATH são obrigatórios"
            )

    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        if not all(
            [
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            ]
        ):
            raise ValueError(
                "Para email habilitado, configurações SMTP são obrigatórias"
            )


# Instância global das configurações
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Retorna a instância global das configurações.

    Usa o padrão Singleton para garantir que as configurações
    sejam carregadas apenas uma vez durante a execução da aplicação.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Instância global para importação direta
settings = get_settings()
