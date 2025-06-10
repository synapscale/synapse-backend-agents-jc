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
        default="postgresql://doadmin:AVNS_DDsc3wHcfGgbX_USTUt@db-banco-dados-automacoes-do-user-13851907-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require",
        description="URL de conexão com o banco de dados"
    )
    DATABASE_SCHEMA: str = Field(
        default="synapscale_db",
        description="Schema do banco de dados"
    )
    
    # Configurações de segurança
    SECRET_KEY: str = Field(
        default="",  # DEVE ser definida via variável de ambiente
        description="Chave secreta para JWT"
    )
    JWT_SECRET_KEY: str = Field(
        default="",  # DEVE ser definida via variável de ambiente
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
        default=True,
        description="Modo debug"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Ambiente de execução"
    )
    
    # Configurações de CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Origens permitidas para CORS"
    )
    
    # Configurações de logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de logging"
    )
    LOG_FILE: str = Field(
        default="logs/app.log",
        description="Arquivo de log"
    )
    
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
    EMAIL_FROM: Optional[str] = Field(
        default=None,
        description="Email remetente"
    )
    
    # Configurações de Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL do Redis"
    )
    
    # Configurações de WebSocket
    WEBSOCKET_ENABLED: bool = Field(
        default=True,
        description="WebSocket habilitado"
    )
    WEBSOCKET_PATH: str = Field(
        default="/ws",
        description="Caminho do WebSocket"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def get_llm_providers(self) -> Dict[str, Any]:
        """
        Retorna provedores LLM configurados
        """
        providers = {}
        
        if self.OPENAI_API_KEY:
            providers["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            }
        
        if self.ANTHROPIC_API_KEY:
            providers["anthropic"] = {
                "api_key": self.ANTHROPIC_API_KEY,
                "models": ["claude-3-sonnet", "claude-3-opus"]
            }
        
        if self.GOOGLE_API_KEY:
            providers["google"] = {
                "api_key": self.GOOGLE_API_KEY,
                "models": ["gemini-pro", "gemini-pro-vision"]
            }
        
        # Adicionar provedor mock para desenvolvimento
        if not providers:
            providers["mock"] = {
                "api_key": "mock-key",
                "models": ["mock-model"]
            }
        
        return providers
    
    def get_database_config(self) -> Dict[str, Any]:
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
    logger.info(f"   - CORS: {settings.CORS_ORIGINS}")
    logger.info(f"   - LLM Providers: {len(settings.get_llm_providers())}")

logger.info(f"✅ Configurações carregadas para ambiente: {settings.ENVIRONMENT}")

