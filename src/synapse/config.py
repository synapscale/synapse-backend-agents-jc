"""
Configurações completas do sistema com todas as variáveis de ambiente
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    model_config = {"extra": "allow", "env_file": ".env", "case_sensitive": True}
    
    # Configurações gerais
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")  # DEVE ser definida via env
    SERVER_HOST: str = "http://localhost:8000"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SynapScale Backend"
    VERSION: str = "2.0.0"
    
    # Banco de dados PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/synapscale_db")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")  # DEVE ser definida via env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Email SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@synapscale.com"
    SMTP_FROM_NAME: str = "SynapScale"
    SMTP_USE_TLS: bool = True
    
    # Armazenamento de arquivos
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    STORAGE_BASE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        ".pdf", ".doc", ".docx", ".txt", ".csv", ".xlsx", 
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".mp3", ".wav", ".mp4", ".avi", ".mov"
    ]
    
    # AWS S3 (se STORAGE_TYPE=s3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Google Cloud Storage (se STORAGE_TYPE=gcs)
    GCS_BUCKET_NAME: Optional[str] = None
    GCS_CREDENTIALS_PATH: Optional[str] = None
    
    # Provedores LLM
    OPENAI_API_KEY: Optional[str] = None  # Removido valor demo
    OPENAI_ORG_ID: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    LLAMA_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_FILE_UPLOAD: str = "10/minute"
    RATE_LIMIT_LLM_GENERATE: str = "20/minute"
    RATE_LIMIT_AUTH: str = "5/minute"
    
    # WebSockets
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_USER: int = 5
    WS_MESSAGE_MAX_SIZE: int = 1024 * 1024  # 1MB
    
    # Monitoramento e Logging
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    
    # Segurança
    ENABLE_HTTPS_REDIRECT: bool = False
    SECURE_COOKIES: bool = False
    CSRF_PROTECTION: bool = True
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # DEVE ser definida via env
    
    # Cache
    CACHE_TTL_DEFAULT: int = 300  # 5 minutos
    CACHE_TTL_USER_DATA: int = 900  # 15 minutos
    CACHE_TTL_STATIC_DATA: int = 3600  # 1 hora
    
    # Execução de Workflows
    WORKFLOW_EXECUTION_TIMEOUT: int = 300  # 5 minutos
    MAX_CONCURRENT_EXECUTIONS: int = 10
    EXECUTION_RETRY_ATTEMPTS: int = 3
    
    # Marketplace
    MARKETPLACE_ENABLED: bool = True
    MARKETPLACE_APPROVAL_REQUIRED: bool = True
    MARKETPLACE_COMMISSION_RATE: float = 0.15  # 15%
    
    # Notificações
    NOTIFICATIONS_ENABLED: bool = True
    EMAIL_NOTIFICATIONS_ENABLED: bool = True
    PUSH_NOTIFICATIONS_ENABLED: bool = False
    
    # Analytics
    ANALYTICS_ENABLED: bool = True
    ANALYTICS_RETENTION_DAYS: int = 90
    
    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 30
    
    # Desenvolvimento
    RELOAD_ON_CHANGE: bool = True
    SHOW_DOCS: bool = True
    ENABLE_PROFILING: bool = False
    
    def get_database_url(self) -> str:
        """Retorna URL do banco de dados formatada"""
        return self.DATABASE_URL
    
    def get_cors_origins(self) -> List[str]:
        """Retorna lista de origens CORS permitidas"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
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
                    "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro", "gemini-pro-vision"
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
                "models": ["llama-3-70b", "llama-3-8b", "llama-2-70b", "llama-2-13b"]
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
            errors.append("SECRET_KEY deve ser definida com pelo menos 32 caracteres")
        
        if not settings.JWT_SECRET_KEY or len(settings.JWT_SECRET_KEY) < 32:
            errors.append("JWT_SECRET_KEY deve ser definida com pelo menos 32 caracteres")
        
        if not settings.DATABASE_URL.startswith("postgresql"):
            errors.append("Use PostgreSQL em produção")
    
    # Validar configuração de email se notificações estão habilitadas
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            errors.append("Configuração SMTP necessária para notificações por email")
    
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

