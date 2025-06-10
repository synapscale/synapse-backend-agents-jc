"""
Configuração otimizada do sistema
Criado por José - um desenvolvedor Full Stack
Integra com DigitalOcean PostgreSQL e todas as funcionalidades
"""
import os
from typing import Dict, List, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import logging


class Settings(BaseSettings):
    """
    Configurações da aplicação com validação
    """
    
    # Configurações do banco de dados
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", ""),
        description="URL de conexão com o banco de dados"
    )
    DATABASE_SCHEMA: str = Field(
        default="synapscale_db",
        description="Schema do banco de dados"
    )
    
    # Configurações de segurança
    SECRET_KEY: str = Field(
        default="fallback-secret-key-change-in-production",
        description="Chave secreta para JWT"
    )
    JWT_SECRET_KEY: str = Field(
        default="fallback-jwt-secret-change-in-production",
        description="Chave secreta para assinatura JWT"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo de assinatura JWT"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Tempo de expiração do access token em minutos"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Tempo de expiração do refresh token em dias"
    )
    
    # Configurações do servidor
    HOST: str = Field(
        default="0.0.0.0",
        description="Host do servidor"
    )
    PORT: int = Field(
        default=8000,
        description="Porta do servidor"
    )
    DEBUG: bool = Field(
        default=False,
        description="Modo de debug"
    )
    ENVIRONMENT: str = Field(
        default="production",
        description="Ambiente de execução"
    )
    
    # Configurações de CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://localhost:3000"],
        description="Origens permitidas para CORS"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Configurações de upload
    MAX_FILE_SIZE: int = Field(
        default=10485760,  # 10MB
        description="Tamanho máximo de arquivo em bytes"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".xml"],
        description="Extensões de arquivo permitidas"
    )
    
    @field_validator('ALLOWED_EXTENSIONS', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',') if ext.strip()]
        return v
    
    # Configurações de LLM
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave da API OpenAI"
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave da API Anthropic"
    )
    GOOGLE_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave da API Google"
    )
    GROQ_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave da API Groq"
    )
    
    # Configurações de logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de logging"
    )
    LOG_FILE: str = Field(
        default="logs/synapse.log",
        description="Arquivo de log"
    )
    
    # Configurações de cache/Redis
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="URL do Redis"
    )
    
    # Configurações de email
    SMTP_HOST: Optional[str] = Field(
        default=None,
        description="Host SMTP"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="Porta SMTP"
    )
    SMTP_USER: Optional[str] = Field(
        default=None,
        description="Usuário SMTP"
    )
    SMTP_PASSWORD: Optional[str] = Field(
        default=None,
        description="Senha SMTP"
    )
    
    # Configurações de WebSocket
    WS_ENDPOINT: str = Field(
        default="/ws",
        description="Endpoint WebSocket"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def get_llm_providers(self) -> Dict[str, bool]:
        """
        Retorna os provedores de LLM disponíveis
        """
        providers = {}
        
        if self.OPENAI_API_KEY:
            providers["openai"] = True
        if self.ANTHROPIC_API_KEY:
            providers["anthropic"] = True
        if self.GOOGLE_API_KEY:
            providers["google"] = True
        if self.GROQ_API_KEY:
            providers["groq"] = True
        
        # Adicionar provedor mock para desenvolvimento
        if self.ENVIRONMENT == "development":
            providers["mock"] = True
        
        return providers
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Retorna configurações específicas do banco de dados
        """
        return {
            "url": self.DATABASE_URL,
            "schema": self.DATABASE_SCHEMA,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600
        }


# Instância global das configurações
settings = Settings()


# Configurar logging baseado nas configurações
def setup_logging():
    """
    Configura o sistema de logging
    """
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler()
        ]
    )


# Configurar logging na importação
setup_logging()

# Log das configurações carregadas
logger = logging.getLogger(__name__)

if settings.ENVIRONMENT == "development":
    logger.info("🔧 Configurações de desenvolvimento carregadas")
    logger.info(f"   - Database: {settings.DATABASE_SCHEMA}")
    logger.info(f"   - Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"   - Debug: {settings.DEBUG}")
