"""
Configurações completas do sistema com todas as variáveis de ambiente
"""
from typing import List, Optional
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()


class Settings:
    def __init__(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = os.getenv("DEBUG", "True") == "True"
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.SERVER_HOST = os.getenv("SERVER_HOST", "http://localhost:8000")
        self.API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "SynapScale Backend")
        self.VERSION = os.getenv("VERSION", "2.0.0")

        # Banco de dados PostgreSQL
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://username:password@localhost:5432/synapscale_db",
        )
        self.DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "synapscale_db")
        self.DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 20))
        self.DATABASE_MAX_OVERFLOW = int(
            os.getenv("DATABASE_MAX_OVERFLOW", 30)
        )
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False") == "True"

        # Redis
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.REDIS_DB = int(os.getenv("REDIS_DB", 0))

        # JWT
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        )
        self.JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(
            os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7)
        )

        # CORS
        self.BACKEND_CORS_ORIGINS = (
            os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
            if os.getenv("BACKEND_CORS_ORIGINS")
            else []
        )

        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")

        # Claude
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

        # Gemini
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        # Grok
        self.GROK_API_KEY = os.getenv("GROK_API_KEY")

        # DeepSeek
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

        # Llama
        self.LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")

        # Storage
        self.STORAGE_TYPE = os.getenv(
            "STORAGE_TYPE", "local"  # local, s3, gcs
        )
        self.MAX_UPLOAD_SIZE = int(
            os.getenv("MAX_UPLOAD_SIZE", 52428800)  # 50MB
        )
        self.ALLOWED_FILE_TYPES = os.getenv(
            "ALLOWED_FILE_TYPES",
            ".pdf,.doc,.docx,.txt,.csv,.xlsx,.jpg,.jpeg,.png,.gif,.bmp,.webp,.mp3,.wav,.mp4,.avi,.mov",
        ).split(",")

        self.STORAGE_BASE_PATH = os.getenv(
            "STORAGE_BASE_PATH"
        )
        self.AWS_ACCESS_KEY_ID = os.getenv(
            "AWS_ACCESS_KEY_ID"
        )
        self.AWS_SECRET_ACCESS_KEY = os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.AWS_BUCKET_NAME = os.getenv(
            "AWS_BUCKET_NAME"
        )
        self.AWS_REGION = os.getenv(
            "AWS_REGION"
        )
        self.GCS_BUCKET_NAME = os.getenv(
            "GCS_BUCKET_NAME"
        )
        self.GCS_CREDENTIALS_PATH = os.getenv(
            "GCS_CREDENTIALS_PATH"
        )

        # SMTP
        self.SMTP_HOST = os.getenv(
            "SMTP_HOST"
        )
        self.SMTP_PORT = os.getenv(
            "SMTP_PORT"
        )
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SMTP_FROM_EMAIL = os.getenv(
            "SMTP_FROM_EMAIL", "noreply@synapscale.com"
        )
        self.SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "SynapScale")
        self.SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True") == "True"

        # Segurança
        self.ENABLE_HTTPS_REDIRECT = os.getenv(
            "ENABLE_HTTPS_REDIRECT", "False"
        ) == "True"
        self.SECURE_COOKIES = os.getenv("SECURE_COOKIES", "False") == "True"
        self.CSRF_PROTECTION = os.getenv("CSRF_PROTECTION", "True") == "True"
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

        self.CACHE_TTL_DEFAULT = int(
            os.getenv("CACHE_TTL_DEFAULT", 300)  # 5 minutos
        )
        self.CACHE_TTL_USER_DATA = int(
            os.getenv("CACHE_TTL_USER_DATA", 900)  # 15 minutos
        )
        self.CACHE_TTL_STATIC_DATA = int(
            os.getenv("CACHE_TTL_STATIC_DATA", 3600)  # 1 hora
        )

        self.WORKFLOW_EXECUTION_TIMEOUT = int(
            os.getenv("WORKFLOW_EXECUTION_TIMEOUT", 300)  # 5 minutos
        )
        self.MAX_CONCURRENT_EXECUTIONS = int(
            os.getenv("MAX_CONCURRENT_EXECUTIONS", 10)
        )
        self.EXECUTION_RETRY_ATTEMPTS = int(
            os.getenv("EXECUTION_RETRY_ATTEMPTS", 3)
        )

        self.MARKETPLACE_ENABLED = os.getenv(
            "MARKETPLACE_ENABLED", "True"
        ) == "True"
        self.MARKETPLACE_APPROVAL_REQUIRED = os.getenv(
            "MARKETPLACE_APPROVAL_REQUIRED", "True"
        ) == "True"
        self.MARKETPLACE_COMMISSION_RATE = float(
            os.getenv("MARKETPLACE_COMMISSION_RATE", 0.15)  # 15%
        )

        self.NOTIFICATIONS_ENABLED = os.getenv(
            "NOTIFICATIONS_ENABLED", "True"
        ) == "True"
        self.EMAIL_NOTIFICATIONS_ENABLED = os.getenv(
            "EMAIL_NOTIFICATIONS_ENABLED", "True"
        ) == "True"
        self.PUSH_NOTIFICATIONS_ENABLED = os.getenv(
            "PUSH_NOTIFICATIONS_ENABLED", "False"
        ) == "True"

        self.ANALYTICS_ENABLED = os.getenv(
            "ANALYTICS_ENABLED", "True"
        ) == "True"
        self.ANALYTICS_RETENTION_DAYS = int(
            os.getenv("ANALYTICS_RETENTION_DAYS", 90)
        )

        self.BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "True") == "True"
        self.BACKUP_INTERVAL_HOURS = int(
            os.getenv("BACKUP_INTERVAL_HOURS", 24)
        )
        self.BACKUP_RETENTION_DAYS = int(
            os.getenv("BACKUP_RETENTION_DAYS", 30)
        )

        self.ENABLE_PROFILING = os.getenv(
            "ENABLE_PROFILING", "False"
        ) == "True"

        # Atributos ausentes adicionados
        self.RELOAD_ON_CHANGE = os.getenv(
            "RELOAD_ON_CHANGE", "False"
        ) == "True"
        self.SHOW_DOCS = os.getenv(
            "SHOW_DOCS", "True"
        ) == "True"

    def get_database_url(self) -> str:
        """Retorna URL do banco de dados formatada"""
        return self.DATABASE_URL

    def get_cors_origins(self) -> List[str]:
        """Retorna lista de origens CORS permitidas"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [
                origin.strip()
                for origin in self.BACKEND_CORS_ORIGINS.split(",")
            ]
        return self.BACKEND_CORS_ORIGINS

    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.ENVIRONMENT.lower() == "development"

    def get_llm_providers(self) -> dict:
        """Retorna configuração dos provedores LLM disponíveis"""
        providers = {}

        if self.OPENAI_API_KEY:
            providers["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "org_id": self.OPENAI_ORG_ID,
                "models": [
                    "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
                    "gpt-3.5-turbo-16k", "text-davinci-003"
                ]
            }

        if self.CLAUDE_API_KEY:
            providers["claude"] = {
                "api_key": self.CLAUDE_API_KEY,
                "models": [
                    "claude-3-opus-20240229", "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307", "claude-2.1", "claude-2.0"
                ]
            }

        if self.GEMINI_API_KEY:
            providers["gemini"] = {
                "api_key": self.GEMINI_API_KEY,
                "models": [
                    "gemini-1.5-pro",
                    "gemini-1.5-flash",
                    "gemini-pro",
                    "gemini-pro-vision",
                ]
            }

        if self.GROK_API_KEY:
            providers["grok"] = {
                "api_key": self.GROK_API_KEY,
                "models": ["grok-1"]
            }

        if self.DEEPSEEK_API_KEY:
            providers["deepseek"] = {
                "api_key": self.DEEPSEEK_API_KEY,
                "models": ["deepseek-chat", "deepseek-coder"]
            }

        if self.LLAMA_API_KEY:
            providers["llama"] = {
                "api_key": self.LLAMA_API_KEY,
                "models": [
                    "llama-3-70b",
                    "llama-3-8b",
                    "llama-2-70b",
                    "llama-2-13b",
                ]
            }

        return providers

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


# Instância global das configurações
settings = Settings()


# Validações de configuração
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

        if not settings.DATABASE_URL.startswith("postgresql"):
            errors.append("Use PostgreSQL em produção")

    # Validar configuração de email se notificações estão habilitadas
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            errors.append(
                "Configuração SMTP necessária para notificações por email"
            )

    # Validar pelo menos um provedor LLM
    if not any([
        settings.OPENAI_API_KEY,
        settings.CLAUDE_API_KEY,
        settings.GEMINI_API_KEY,
        settings.GROK_API_KEY,
        settings.DEEPSEEK_API_KEY,
        settings.LLAMA_API_KEY
    ]):
        errors.append("Pelo menos um provedor LLM deve ser configurado")

    if errors:
        raise ValueError(f"Erros de configuração: {'; '.join(errors)}")


# Executar validação na importação
try:
    validate_settings()
except ValueError as e:
    if settings.is_production():
        raise e
    else:
        print(f"Aviso: {e}")

# Configurações específicas por ambiente
if settings.is_development():
    # Configurações de desenvolvimento
    settings.DATABASE_ECHO = True
    settings.RELOAD_ON_CHANGE = True
    settings.SHOW_DOCS = True
elif settings.is_production():
    # Configurações de produção
    settings.DEBUG = False
    settings.DATABASE_ECHO = False
    settings.RELOAD_ON_CHANGE = False
    settings.SECURE_COOKIES = True
    settings.ENABLE_HTTPS_REDIRECT = True

