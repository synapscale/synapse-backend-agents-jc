"""
Configuração otimizada do sistema
Criado por José - O melhor Full Stack do mundo
Integra com DigitalOcean PostgreSQL e todas as funcionalidades
"""
import json
import logging
import os
from typing import Any
import sys

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_list_env(value: str | None) -> list[str]:
    """Converte variável de ambiente em lista.

    Aceita:
    • JSON list em string: '["GET", "POST"]'
    • Lista separada por vírgula: 'GET,POST,PUT'
    Retorna lista vazia se value é None ou string vazia.
    """
    if not value:
        return []
    value = value.strip()
    if not value:
        return []
    try:
        if value.startswith("["):
            import json as _json
            parsed = _json.loads(value)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
    except Exception:
        pass
    # Fallback para separação por vírgula
    return [v.strip() for v in value.split(',') if v.strip()]


class Settings(BaseSettings):
    """
    Configurações da aplicação com validação
    """

    # Configurações do banco de dados
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL"),
        description="URL de conexão com o banco de dados"
    )
    DATABASE_SCHEMA: str = Field(
        default_factory=lambda: os.getenv("DATABASE_SCHEMA", "synapscale_db"),
        description="Schema do banco de dados"
    )

    # Configurações de segurança
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY"),
        description="Chave secreta para JWT"
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY"),
        description="Chave secreta para assinatura JWT"
    )
    JWT_ALGORITHM: str | None = Field(
        default_factory=lambda: os.getenv("JWT_ALGORITHM"),
        description="Algoritmo de assinatura JWT"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int | None = Field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")) if os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES") else None,
        description="Tempo de expiração do access token em minutos"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int | None = Field(
        default_factory=lambda: int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS")) if os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS") else None,
        description="Tempo de expiração do refresh token em dias"
    )
    
    # CHAVE DE CRIPTOGRAFIA CRÍTICA (FALTAVA!)
    ENCRYPTION_KEY: str | None = Field(
        default_factory=lambda: os.getenv("ENCRYPTION_KEY"),
        description="Chave de criptografia para dados sensíveis (Base64)"
    )

    # Configurações do servidor
    HOST: str | None = Field(
        default_factory=lambda: os.getenv("HOST"),
        description="Host do servidor"
    )
    PORT: int | None = Field(
        default_factory=lambda: int(os.getenv("PORT")) if os.getenv("PORT") else None,
        description="Porta do servidor"
    )
    DEBUG: bool | None = Field(
        default_factory=lambda: os.getenv("DEBUG") and os.getenv("DEBUG").lower() == "true",
        description="Modo debug"
    )
    ENVIRONMENT: str | None = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT"),
        description="Ambiente de execução"
    )

    # Configurações de CORS
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: (
            os.getenv("CORS_ORIGINS").split(",") if os.getenv("CORS_ORIGINS") else []
        ),
        description="Origens permitidas para CORS"
    )

    BACKEND_CORS_ORIGINS: str = Field(
        default_factory=lambda: os.getenv("BACKEND_CORS_ORIGINS"),
        description="Origens permitidas para CORS (formato JSON string)"
    )

    # --- Novas opções de CORS ---
    CORS_ALLOW_METHODS: list[str] = Field(
        default_factory=lambda: _parse_list_env(os.getenv("BACKEND_CORS_ALLOW_METHODS")),
        description="Métodos HTTP permitidos"
    )

    CORS_ALLOW_HEADERS: list[str] = Field(
        default_factory=lambda: _parse_list_env(os.getenv("BACKEND_CORS_ALLOW_HEADERS")),
        description="Headers permitidos"
    )

    CORS_EXPOSE_HEADERS: list[str] = Field(
        default_factory=lambda: _parse_list_env(os.getenv("BACKEND_CORS_EXPOSE_HEADERS")),
        description="Headers expostos ao navegador"
    )

    CORS_ALLOW_CREDENTIALS: bool | None = Field(
        default_factory=lambda: (env_val := os.getenv("BACKEND_CORS_ALLOW_CREDENTIALS")) and env_val.lower() == "true",
        description="Se cookies/credenciais são permitidas"
    )

    CORS_MAX_AGE: int | None = Field(
        default_factory=lambda: int(os.getenv("BACKEND_CORS_MAX_AGE")) if os.getenv("BACKEND_CORS_MAX_AGE") else None,
        description="Tempo de cache do pre-flight em segundos"
    )

    @property
    def backend_cors_origins_list(self) -> list[str]:
        """Converte BACKEND_CORS_ORIGINS de string JSON ou CSV para lista"""
        val = self.BACKEND_CORS_ORIGINS
        logger = logging.getLogger(__name__)
        if not val:
            return []
        try:
            result = json.loads(val)
            if isinstance(result, list):
                return [o.strip().rstrip("/") for o in result]
        except Exception as e:
            logger.warning(f"BACKEND_CORS_ORIGINS não é JSON válido: {e}. Tentando CSV.")
        if "," in val:
            return [o.strip().rstrip("/") for o in val.split(",") if o.strip()]
        logger.warning("BACKEND_CORS_ORIGINS não é JSON nem CSV. Usando valor bruto.")
        return [val.strip().rstrip("/")]

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> str:
        """Parse CORS origins from various formats to JSON string"""
        if isinstance(v, str):
            if not v:  # String vazia
                # Se string vazia, retorna lista vazia em formato json
                return "[]"
            try:
                # Tenta fazer parse para validar que é JSON válido
                json.loads(v)
                return v
            except json.JSONDecodeError:
                # Se não for JSON válido, retorna como lista com um item
                return json.dumps([v.strip()])
        if isinstance(v, list):
            return json.dumps(v)
        return str(v)

    # Configurações de logging
    LOG_LEVEL: str | None = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL"),
        description="Nível de logging"
    )
    LOG_FILE: str | None = Field(
        default_factory=lambda: os.getenv("LOG_FILE"),
        description="Arquivo de log"
    )
    LOG_FORMAT: str | None = Field(
        default_factory=lambda: os.getenv("LOG_FORMAT"),
        description="Formato do log (compatibilidade)"
    )

    # Configurações de upload
    MAX_FILE_SIZE: int | None = Field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE")) if os.getenv("MAX_FILE_SIZE") else None,
        description="Tamanho máximo de arquivo em bytes"
    )
    ALLOWED_EXTENSIONS_STR: str | None = Field(
        default_factory=lambda: os.getenv("ALLOWED_EXTENSIONS"),
        description="Extensões de arquivo permitidas (formato string)"
    )

    @property
    def ALLOWED_EXTENSIONS(self) -> list[str]:
        """Converte ALLOWED_EXTENSIONS_STR para lista"""
        extensions_str = self.ALLOWED_EXTENSIONS_STR
        if not extensions_str:
            return [".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".xml"]

        # Remove espaços e filtra valores vazios
        extensions = [
            ext.strip()
            for ext in extensions_str.split(",")
            if ext.strip()
        ]
        return extensions

    @property
    def ALLOWED_FILE_EXTENSIONS(self) -> list[str]:
        """Alias para ALLOWED_EXTENSIONS para compatibilidade"""
        return self.ALLOWED_EXTENSIONS

    # Configurações de LLM
    LLM_DEFAULT_PROVIDER: str | None = Field(
        default_factory=lambda: os.getenv("LLM_DEFAULT_PROVIDER", "openai"),
        description="Provedor LLM padrão"
    )
    
    # Enhanced OpenAI Configuration
    OPENAI_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="Chave da API OpenAI"
    )
    OPENAI_ORG_ID: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_ORG_ID"),
        description="ID da organização OpenAI"
    )
    OPENAI_API_BASE: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        description="URL base da API OpenAI"
    )
    OPENAI_API_VERSION: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_VERSION"),
        description="Versão da API OpenAI (para Azure OpenAI)"
    )
    OPENAI_API_TYPE: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_TYPE", "openai"),
        description="Tipo da API OpenAI (openai ou azure)"
    )
    OPENAI_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("OPENAI_TIMEOUT", "60")),
        description="Timeout em segundos para requisições OpenAI"
    )
    OPENAI_MAX_RETRIES: int = Field(
        default_factory=lambda: int(os.getenv("OPENAI_MAX_RETRIES", "3")),
        description="Número máximo de tentativas para requisições OpenAI"
    )
    OPENAI_DEFAULT_MODEL: str = Field(
        default_factory=lambda: os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o"),
        description="Modelo OpenAI padrão"
    )
    
    # Other LLM Providers
    ANTHROPIC_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"),
        description="Chave da API Anthropic"
    )
    CLAUDE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("CLAUDE_API_KEY"),
        description="Chave da API Claude (alias para Anthropic)"
    )
    GOOGLE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY"),
        description="Chave da API Google"
    )
    GEMINI_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY"),
        description="Chave da API Gemini (alias para Google)"
    )
    GROK_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("GROK_API_KEY"),
        description="Chave da API Grok"
    )
    DEEPSEEK_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"),
        description="Chave da API DeepSeek"
    )
    LLAMA_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("LLAMA_API_KEY"),
        description="Chave da API Llama"
    )
    
    # Mais APIs LLM que faltavam
    HUGGINGFACE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("HUGGINGFACE_API_KEY"),
        description="Chave da API HuggingFace"
    )
    MISTRAL_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("MISTRAL_API_KEY"),
        description="Chave da API Mistral"
    )
    COHERE_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("COHERE_API_KEY"),
        description="Chave da API Cohere"
    )
    
    # Configurações específicas para Tess
    TESS_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("TESS_API_KEY"),
        description="Chave da API Tess"
    )
    TESS_API_BASE_URL: str | None = Field(
        default_factory=lambda: os.getenv("TESS_API_BASE_URL", "https://tess.pareto.io/api"),
        description="URL base da API Tess"
    )

    # Configurações de email
    SMTP_HOST: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_HOST"),
        description="Host SMTP"
    )
    SMTP_PORT: int | None = Field(
        default_factory=lambda: int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None,
        description="Porta SMTP"
    )
    SMTP_USER: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_USER"),
        description="Usuário SMTP"
    )
    SMTP_PASSWORD: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_PASSWORD"),
        description="Senha SMTP"
    )
    EMAIL_FROM: str | None = Field(
        default_factory=lambda: os.getenv("EMAIL_FROM"),
        description="Email remetente"
    )
    SMTP_USERNAME: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_USERNAME"),
        description="Usuário SMTP (compatibilidade)"
    )
    SMTP_FROM_EMAIL: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_FROM_EMAIL"),
        description="Email remetente (compatibilidade)"
    )
    SMTP_FROM_NAME: str | None = Field(
        default_factory=lambda: os.getenv("SMTP_FROM_NAME"),
        description="Nome remetente (compatibilidade)"
    )
    SMTP_USE_TLS: bool = Field(
        default_factory=lambda: os.getenv("SMTP_USE_TLS", "True") == "True",
        description="Usar TLS no SMTP"
    )

    # Configurações de Redis
    REDIS_URL: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_URL"),
        description="URL do Redis"
    )
    REDIS_PASSWORD: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_PASSWORD"),
        description="Senha do Redis"
    )
    REDIS_DB: int = Field(
        default_factory=lambda: int(os.getenv("REDIS_DB", "0")),
        description="Banco de dados do Redis"
    )

    # Configurações de WebSocket
    WEBSOCKET_ENABLED: bool | None = Field(
        default_factory=lambda: os.getenv("WEBSOCKET_ENABLED") and os.getenv("WEBSOCKET_ENABLED").lower() == "true",
        description="WebSocket habilitado"
    )
    WEBSOCKET_PATH: str | None = Field(
        default_factory=lambda: os.getenv("WEBSOCKET_PATH"),
        description="Caminho do WebSocket"
    )

    # Configurações de API
    API_V1_STR: str | None = Field(
        default_factory=lambda: os.getenv("API_V1_STR"),
        description="Prefixo da API v1"
    )

    PROJECT_NAME: str | None = Field(
        default_factory=lambda: os.getenv("PROJECT_NAME"),
        description="Nome do projeto (compatibilidade)"
    )

    VERSION: str | None = Field(
        default_factory=lambda: os.getenv("VERSION"),
        description="Versão do projeto (compatibilidade)"
    )

    UPLOAD_FOLDER: str | None = Field(
        default_factory=lambda: os.getenv("UPLOAD_FOLDER"),
        description="Diretório de uploads (compatibilidade)"
    )
    
    # Configurações de Armazenamento que faltavam
    STORAGE_TYPE: str = Field(
        default_factory=lambda: os.getenv("STORAGE_TYPE", "local"),
        description="Tipo de armazenamento (local, s3, gcs)"
    )
    STORAGE_BASE_PATH: str = Field(
        default_factory=lambda: os.getenv("STORAGE_BASE_PATH", "./storage"),
        description="Caminho base para armazenamento local"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", "52428800")),
        description="Tamanho máximo de upload em bytes"
    )
    ALLOWED_FILE_TYPES: str = Field(
        default_factory=lambda: os.getenv("ALLOWED_FILE_TYPES", '[]'),
        description="Tipos de arquivo permitidos (JSON)"
    )
    
    # AWS S3 (se STORAGE_TYPE=s3)
    AWS_ACCESS_KEY_ID: str | None = Field(
        default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID"),
        description="Chave de acesso AWS"
    )
    AWS_SECRET_ACCESS_KEY: str | None = Field(
        default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY"),
        description="Chave secreta AWS"
    )
    AWS_BUCKET_NAME: str | None = Field(
        default_factory=lambda: os.getenv("AWS_BUCKET_NAME"),
        description="Nome do bucket S3"
    )
    AWS_REGION: str = Field(
        default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"),
        description="Região AWS"
    )
    
    # Google Cloud Storage (se STORAGE_TYPE=gcs)
    GCS_BUCKET_NAME: str | None = Field(
        default_factory=lambda: os.getenv("GCS_BUCKET_NAME"),
        description="Nome do bucket GCS"
    )
    GCS_CREDENTIALS_PATH: str | None = Field(
        default_factory=lambda: os.getenv("GCS_CREDENTIALS_PATH"),
        description="Caminho para credenciais GCS"
    )
    
    # Configurações de Segurança Avançada
    ENABLE_HTTPS_REDIRECT: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_HTTPS_REDIRECT", "False") == "True",
        description="Habilitar redirecionamento HTTPS"
    )
    SECURE_COOKIES: bool = Field(
        default_factory=lambda: os.getenv("SECURE_COOKIES", "False") == "True",
        description="Usar cookies seguros"
    )
    CSRF_PROTECTION: bool = Field(
        default_factory=lambda: os.getenv("CSRF_PROTECTION", "True") == "True",
        description="Habilitar proteção CSRF"
    )
    
    # Configurações de Cache que faltavam
    CACHE_TTL_DEFAULT: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_DEFAULT", "300")),
        description="TTL padrão do cache"
    )
    CACHE_TTL_USER_DATA: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_USER_DATA", "900")),
        description="TTL do cache para dados de usuário"
    )
    CACHE_TTL_STATIC_DATA: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_STATIC_DATA", "3600")),
        description="TTL do cache para dados estáticos"
    )
    
    # Configurações de Execução
    WORKFLOW_EXECUTION_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("WORKFLOW_EXECUTION_TIMEOUT", "300")),
        description="Timeout de execução de workflow"
    )
    MAX_CONCURRENT_EXECUTIONS: int = Field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_EXECUTIONS", "10")),
        description="Máximo de execuções concorrentes"
    )
    EXECUTION_RETRY_ATTEMPTS: int = Field(
        default_factory=lambda: int(os.getenv("EXECUTION_RETRY_ATTEMPTS", "3")),
        description="Tentativas de retry de execução"
    )
    
    # Configurações de Marketplace
    MARKETPLACE_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("MARKETPLACE_ENABLED", "True") == "True",
        description="Habilitar marketplace"
    )
    MARKETPLACE_APPROVAL_REQUIRED: bool = Field(
        default_factory=lambda: os.getenv("MARKETPLACE_APPROVAL_REQUIRED", "True") == "True",
        description="Exigir aprovação no marketplace"
    )
    MARKETPLACE_COMMISSION_RATE: float = Field(
        default_factory=lambda: float(os.getenv("MARKETPLACE_COMMISSION_RATE", "0.15")),
        description="Taxa de comissão do marketplace"
    )
    
    # Configurações de Notificações
    NOTIFICATIONS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("NOTIFICATIONS_ENABLED", "True") == "True",
        description="Habilitar notificações"
    )
    EMAIL_NOTIFICATIONS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "True") == "True",
        description="Habilitar notificações por email"
    )
    PUSH_NOTIFICATIONS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("PUSH_NOTIFICATIONS_ENABLED", "False") == "True",
        description="Habilitar notificações push"
    )
    
    # Configurações de Analytics
    ANALYTICS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("ANALYTICS_ENABLED", "True") == "True",
        description="Habilitar analytics"
    )
    ANALYTICS_RETENTION_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("ANALYTICS_RETENTION_DAYS", "90")),
        description="Dias de retenção de analytics"
    )
    
    # Configurações de Backup
    BACKUP_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("BACKUP_ENABLED", "True") == "True",
        description="Habilitar backup"
    )
    BACKUP_INTERVAL_HOURS: int = Field(
        default_factory=lambda: int(os.getenv("BACKUP_INTERVAL_HOURS", "24")),
        description="Intervalo de backup em horas"
    )
    BACKUP_RETENTION_DAYS: int = Field(
        default_factory=lambda: int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
        description="Dias de retenção de backup"
    )
    
    # Configurações de Desenvolvimento
    RELOAD_ON_CHANGE: bool = Field(
        default_factory=lambda: os.getenv("RELOAD_ON_CHANGE", "True") == "True",
        description="Recarregar ao modificar código"
    )
    SHOW_DOCS: bool = Field(
        default_factory=lambda: os.getenv("SHOW_DOCS", "True") == "True",
        description="Mostrar documentação"
    )
    ENABLE_PROFILING: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_PROFILING", "False") == "True",
        description="Habilitar profiling"
    )
    
    # Configurações de Monitoramento
    SENTRY_DSN: str | None = Field(
        default_factory=lambda: os.getenv("SENTRY_DSN"),
        description="DSN do Sentry"
    )
    ENABLE_METRICS: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_METRICS", "True") == "True",
        description="Habilitar métricas"
    )
    ENABLE_TRACING: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_TRACING", "False") == "True",
        description="Habilitar tracing"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Permite campos extras do .env
        json_schema_extra = {
            "example": {
                "key": "value"
            }
        }

    def get_llm_providers(self) -> dict[str, Any]:
        """
        Retorna configuração consolidada dos provedores LLM
        
        Returns:
            dict: Dicionário com configurações dos provedores
        """
        providers = {}
        
        # OpenAI
        if self.OPENAI_API_KEY:
            providers["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "organization": self.OPENAI_ORG_ID,
                "api_base": self.OPENAI_API_BASE,
                "api_version": self.OPENAI_API_VERSION,
                "api_type": self.OPENAI_API_TYPE,
                "timeout": self.OPENAI_TIMEOUT,
                "max_retries": self.OPENAI_MAX_RETRIES,
                "default_model": self.OPENAI_DEFAULT_MODEL,
                "available": True
            }
        
        # Anthropic/Claude
        anthropic_key = self.ANTHROPIC_API_KEY or self.CLAUDE_API_KEY
        if anthropic_key:
            providers["anthropic"] = {
                "api_key": anthropic_key,
                "available": True
            }
        
        # Google/Gemini
        google_key = self.GOOGLE_API_KEY or self.GEMINI_API_KEY
        if google_key:
            providers["google"] = {
                "api_key": google_key,
                "available": True
            }
        
        # Outros provedores
        for provider in ["grok", "deepseek", "llama", "huggingface", "mistral", "cohere"]:
            key_attr = f"{provider.upper()}_API_KEY"
            api_key = getattr(self, key_attr, None)
            if api_key:
                providers[provider] = {
                    "api_key": api_key,
                    "available": True
                }
        
        # Tess
        if self.TESS_API_KEY:
            providers["tess"] = {
                "api_key": self.TESS_API_KEY,
                "api_base": self.TESS_API_BASE_URL,
                "available": True
            }
        
        return providers

    def validate_openai_config(self) -> dict[str, Any]:
        """
        Valida a configuração do OpenAI
        
        Returns:
            dict: Resultado da validação com status e mensagens
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validar API Key
        if not self.OPENAI_API_KEY:
            validation_result["valid"] = False
            validation_result["errors"].append("OPENAI_API_KEY é obrigatório")
        elif not self.OPENAI_API_KEY.startswith("sk-"):
            validation_result["warnings"].append("OPENAI_API_KEY deve começar com 'sk-' para APIs padrão do OpenAI")
        
        # Validar Organization ID (opcional mas recomendado)
        if self.OPENAI_ORG_ID and not self.OPENAI_ORG_ID.startswith("org-"):
            validation_result["warnings"].append("OPENAI_ORG_ID deve começar com 'org-'")
        
        # Validar API Base URL
        if not self.OPENAI_API_BASE.startswith("http"):
            validation_result["valid"] = False
            validation_result["errors"].append("OPENAI_API_BASE deve ser uma URL válida")
        
        # Validar API Type
        if self.OPENAI_API_TYPE not in ["openai", "azure"]:
            validation_result["valid"] = False
            validation_result["errors"].append("OPENAI_API_TYPE deve ser 'openai' ou 'azure'")
        
        # Validar Azure-specific settings
        if self.OPENAI_API_TYPE == "azure":
            if not self.OPENAI_API_VERSION:
                validation_result["valid"] = False
                validation_result["errors"].append("OPENAI_API_VERSION é obrigatório para Azure OpenAI")
            if "azure" not in self.OPENAI_API_BASE.lower():
                validation_result["warnings"].append("OPENAI_API_BASE deveria conter 'azure' para Azure OpenAI")
        
        # Validar timeout e retry settings
        if self.OPENAI_TIMEOUT <= 0:
            validation_result["valid"] = False
            validation_result["errors"].append("OPENAI_TIMEOUT deve ser maior que 0")
        
        if self.OPENAI_MAX_RETRIES < 0:
            validation_result["valid"] = False
            validation_result["errors"].append("OPENAI_MAX_RETRIES deve ser maior ou igual a 0")
        
        return validation_result

    def get_openai_client_config(self) -> dict[str, Any]:
        """
        Retorna configuração otimizada para cliente OpenAI
        
        Returns:
            dict: Configuração do cliente OpenAI
        """
        config = {
            "api_key": self.OPENAI_API_KEY,
            "timeout": self.OPENAI_TIMEOUT,
            "max_retries": self.OPENAI_MAX_RETRIES,
        }
        
        # Adicionar organization se disponível
        if self.OPENAI_ORG_ID:
            config["organization"] = self.OPENAI_ORG_ID
        
        # Configurações específicas para Azure
        if self.OPENAI_API_TYPE == "azure":
            config["azure_endpoint"] = self.OPENAI_API_BASE
            config["api_version"] = self.OPENAI_API_VERSION
        else:
            # Configurações para OpenAI padrão
            if self.OPENAI_API_BASE != "https://api.openai.com/v1":
                config["base_url"] = self.OPENAI_API_BASE
        
        return config

    def get_database_url(self) -> str:
        """Retorna URL do banco de dados formatada"""
        return self.DATABASE_URL

    def get_cors_origins(self) -> list[str]:
        """Retorna lista de origens CORS permitidas"""
        return self.backend_cors_origins_list

    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.ENVIRONMENT and self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.ENVIRONMENT and self.ENVIRONMENT.lower() == "development"
    
    def get_storage_config(self) -> dict:
        """Retorna configuração de armazenamento"""
        config = {
            "type": self.STORAGE_TYPE,
            "max_size": self.MAX_UPLOAD_SIZE,
            "allowed_types": self.ALLOWED_FILE_TYPES
        }

        if self.STORAGE_TYPE == "local":
            config["base_path"] = self.STORAGE_BASE_PATH
        elif self.STORAGE_TYPE == "s3":
            config.update({
                "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY,
                "bucket_name": self.AWS_BUCKET_NAME,
                "region": self.AWS_REGION
            })
        elif self.STORAGE_TYPE == "gcs":
            config.update({
                "bucket_name": self.GCS_BUCKET_NAME,
                "credentials_path": self.GCS_CREDENTIALS_PATH
            })

        return config

    def get_email_config(self) -> dict:
        """Retorna configuração de email"""
        return {
            "host": self.SMTP_HOST,
            "port": self.SMTP_PORT,
            "username": self.SMTP_USERNAME,
            "password": self.SMTP_PASSWORD,
            "from_email": self.SMTP_FROM_EMAIL,
            "from_name": self.SMTP_FROM_NAME,
            "use_tls": self.SMTP_USE_TLS
        }

    def get_redis_config(self) -> dict:
        """Retorna configuração do Redis"""
        return {
            "url": self.REDIS_URL,
            "password": self.REDIS_PASSWORD,
            "db": self.REDIS_DB
        }

    def get_database_config(self) -> dict[str, Any]:
        """
        Retorna configuração do banco de dados
        """
        return {
            "url": self.DATABASE_URL,
            "schema": self.DATABASE_SCHEMA,
            "echo": self.DEBUG,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 3600
        }


# Instância global das configurações
settings = Settings()


# Configurar logging baseado nas configurações
def setup_logging() -> None:
    """
    Configura o sistema de logging
    """
    log_file = settings.LOG_FILE or "logs/app.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Corrige o formato do log se estiver como 'json'
    log_format = settings.LOG_FORMAT
    if log_format == "json":
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif not log_format:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, (settings.LOG_LEVEL or "INFO"), logging.INFO),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


# Configurar logging na importação
setup_logging()

# Log das configurações carregadas
logger = logging.getLogger(__name__)

if settings.ENVIRONMENT == "development":
    logger.info("🔧 Configurações de desenvolvimento carregadas")
    logger.info("   - Database: %s", settings.DATABASE_SCHEMA)
    logger.info("   - CORS: %s", settings.CORS_ORIGINS)
    logger.info("   - LLM Providers: %d", len(settings.get_llm_providers()))

logger.info(
    "✅ Configurações carregadas para ambiente: %s", settings.ENVIRONMENT
)

# Detecta se está rodando Alembic ou testes
IS_ALEMBIC = "alembic" in sys.argv[0] or "alembic" in " ".join(sys.argv)
IS_TEST = "pytest" in sys.argv[0] or "pytest" in " ".join(sys.argv)

if IS_ALEMBIC or IS_TEST:
    REQUIRED_ENV_VARS = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "DATABASE_SCHEMA",
    ]
else:
    REQUIRED_ENV_VARS = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "DATABASE_SCHEMA",
        "UPLOAD_FOLDER",
        "BACKEND_CORS_ORIGINS",
        "HOST",
        "PORT",
        "ENVIRONMENT",
        "DEBUG",
    ]
_missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if _missing:
    raise RuntimeError(f"Variáveis de ambiente obrigatórias ausentes: {', '.join(_missing)}")

# Validações de configuração CRÍTICAS
def validate_settings():
    """Valida configurações críticas"""
    errors = []

    # Validar chaves secretas em produção
    if settings.is_production():
        if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
            errors.append(
                "SECRET_KEY deve ser definida com pelo menos 32 caracteres"
            )

        if not settings.JWT_SECRET_KEY or len(settings.JWT_SECRET_KEY) < 32:
            errors.append(
                "JWT_SECRET_KEY deve ser definida com pelo menos 32 caracteres"
            )

        if not settings.DATABASE_URL or not settings.DATABASE_URL.startswith("postgresql"):
            errors.append("Use PostgreSQL em produção")

        # Validar chave de criptografia (essencial para API keys de usuário)
        if not settings.ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY deve ser definida para criptografia de API keys de usuários")

    # Validar configuração de email se notificações estão habilitadas
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            if settings.is_production():
                # Em produção, desabilita notificações por email se SMTP não configurado
                print("⚠️  Aviso: SMTP não configurado. Notificações por email desabilitadas automaticamente.")
                settings.EMAIL_NOTIFICATIONS_ENABLED = False
            else:
                errors.append(
                    "Configuração SMTP necessária para notificações por email"
                )

    # Validação da ENCRYPTION_KEY (também em desenvolvimento para evitar erros silenciosos)
    if settings.ENCRYPTION_KEY:
        import base64
        import binascii
        try:
            decoded_key = base64.b64decode(settings.ENCRYPTION_KEY)
            if len(decoded_key) != 32:
                errors.append("ENCRYPTION_KEY deve ter 32 bytes quando decodificada (256-bits)")
        except (binascii.Error, ValueError):
            errors.append("ENCRYPTION_KEY não é um Base-64 válido")

    # Aviso sobre provedores LLM (não obrigatório devido ao sistema de API keys por usuário)
    if not any([
        settings.OPENAI_API_KEY,
        settings.CLAUDE_API_KEY,
        settings.GEMINI_API_KEY,
        settings.GROK_API_KEY,
        settings.DEEPSEEK_API_KEY,
        settings.LLAMA_API_KEY
    ]):
        # Apenas aviso, não erro crítico - usuários podem configurar suas próprias API keys
        print("⚠️  Aviso: Nenhuma API key global configurada. Sistema funcionará com API keys específicas de usuários.")

    if errors:
        raise ValueError(f"Erros de configuração: {'; '.join(errors)}")

# Executar validação na importação
try:
    validate_settings()
except ValueError as e:
    if settings.is_production():
        # Em produção, falha apenas por erros críticos (não por falta de API keys LLM)
        print(f"❌ Erro crítico de configuração: {e}")
        raise e
    else:
        print(f"⚠️  Aviso de configuração: {e}")

# Configurações específicas por ambiente
if settings.is_development():
    # Configurações de desenvolvimento
    settings.RELOAD_ON_CHANGE = True
    settings.SHOW_DOCS = True
elif settings.is_production():
    # Configurações de produção
    settings.DEBUG = False
    settings.RELOAD_ON_CHANGE = False
    settings.SECURE_COOKIES = True
    settings.ENABLE_HTTPS_REDIRECT = True
