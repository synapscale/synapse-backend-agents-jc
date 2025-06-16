"""
Configuração otimizada do sistema
Criado por José - O melhor Full Stack do mundo
Integra com DigitalOcean PostgreSQL e todas as funcionalidades
"""
import os
import logging
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

load_dotenv()


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
        default_factory=lambda: os.getenv("DATABASE_SCHEMA", "synapscale_db"),
        description="Schema do banco de dados"
    )

    # Configurações de segurança
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", ""),
        description="Chave secreta para JWT"
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""),
        description="Chave secreta para assinatura JWT"
    )
    JWT_ALGORITHM: str = Field(
        default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"),
        description="Algoritmo de assinatura JWT"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        ),
        description="Tempo de expiração do access token em minutos"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default_factory=lambda: int(
            os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
        ),
        description="Tempo de expiração do refresh token em dias"
    )

    # Configurações do servidor
    HOST: str = Field(
        default_factory=lambda: os.getenv("HOST", "0.0.0.0"),
        description="Host do servidor"
    )
    PORT: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000")),
        description="Porta do servidor"
    )
    DEBUG: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true",
        description="Modo debug"
    )
    ENVIRONMENT: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Ambiente de execução"
    )

    # Configurações de CORS
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: (
            os.getenv("CORS_ORIGINS",
                      "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if os.getenv("CORS_ORIGINS")
            else ["http://localhost:3000", "http://127.0.0.1:3000"]
        ),
        description="Origens permitidas para CORS"
    )

    BACKEND_CORS_ORIGINS: str = Field(
        default_factory=lambda: os.getenv(
            "BACKEND_CORS_ORIGINS",
            '["http://localhost:3000", "http://127.0.0.1:3000"]'
        ),
        description="Origens permitidas para CORS (formato JSON string)"
    )

    @property
    def backend_cors_origins_list(self) -> List[str]:
        """Converte BACKEND_CORS_ORIGINS de string JSON para lista"""
        try:
            import json
            result = json.loads(self.BACKEND_CORS_ORIGINS)
            return result if isinstance(result, list) else []
        except (json.JSONDecodeError, TypeError):
            # Fallback para valores padrão do .env ou valores mínimos
            default_cors = os.getenv(
                "CORS_FALLBACK",
                '["http://localhost:3000", "http://127.0.0.1:3000"]'
            )
            try:
                result = json.loads(default_cors)
                return result if isinstance(result, list) else []
            except (json.JSONDecodeError, TypeError):
                return ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> str:
        if isinstance(v, str):
            if not v:  # String vazia
                # Busca do .env ou usa valores mínimos
                return os.getenv(
                    "CORS_FALLBACK",
                    '["http://localhost:3000", "http://127.0.0.1:3000"]'
                )
            try:
                import json
                # Tenta fazer parse para validar que é JSON válido
                json.loads(v)
                return v
            except json.JSONDecodeError:
                # Se não for JSON válido, retorna como lista com um item
                import json
                return json.dumps([v.strip()])
        if isinstance(v, list):
            import json
            return json.dumps(v)
        return str(v)

    # Configurações de logging
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Nível de logging"
    )
    LOG_FILE: str = Field(
        default_factory=lambda: os.getenv("LOG_FILE", "logs/app.log"),
        description="Arquivo de log"
    )
    LOG_FORMAT: str = Field(
        default_factory=lambda: os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        description="Formato do log (compatibilidade)"
    )

    # Configurações de upload
    MAX_FILE_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "10485760")),
        description="Tamanho máximo de arquivo em bytes"
    )
    ALLOWED_EXTENSIONS_STR: str = Field(
        default_factory=lambda: os.getenv("ALLOWED_EXTENSIONS", ".txt,.pdf,.doc,.docx,.csv,.json,.xml"),
        description="Extensões de arquivo permitidas (formato string)"
    )

    @property
    def ALLOWED_EXTENSIONS(self) -> list[str]:
        """Converte ALLOWED_EXTENSIONS_STR de string separada por vírgulas para lista"""
        if not self.ALLOWED_EXTENSIONS_STR:
            return [".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".xml"]
        # Remove espaços e filtra valores vazios
        extensions = [ext.strip() for ext in self.ALLOWED_EXTENSIONS_STR.split(",") if ext.strip()]
        return extensions if extensions else [".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".xml"]

    # Configurações de LLM
    OPENAI_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="Chave da API OpenAI"
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"),
        description="Chave da API Anthropic"
    )
    GOOGLE_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY"),
        description="Chave da API Google"
    )

    # Configurações de email
    SMTP_HOST: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_HOST"),
        description="Host SMTP"
    )
    SMTP_PORT: int = Field(
        default_factory=lambda: int(os.getenv("SMTP_PORT", "587")),
        description="Porta SMTP"
    )
    SMTP_USER: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_USER"),
        description="Usuário SMTP"
    )
    SMTP_PASSWORD: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_PASSWORD"),
        description="Senha SMTP"
    )
    EMAIL_FROM: Optional[str] = Field(
        default_factory=lambda: os.getenv("EMAIL_FROM"),
        description="Email remetente"
    )
    SMTP_USERNAME: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_USERNAME"),
        description="Usuário SMTP (compatibilidade)"
    )
    SMTP_FROM_EMAIL: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_FROM_EMAIL"),
        description="Email remetente (compatibilidade)"
    )
    SMTP_FROM_NAME: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_FROM_NAME"),
        description="Nome remetente (compatibilidade)"
    )

    # Configurações de Redis
    REDIS_URL: str = Field(
        default_factory=lambda: os.getenv(
            "REDIS_URL", "redis://localhost:6379/0"
        ),
        description="URL do Redis"
    )

    # Configurações de WebSocket
    WEBSOCKET_ENABLED: bool = Field(
        default_factory=lambda: os.getenv(
            "WEBSOCKET_ENABLED", "True"
        ).lower() == "true",
        description="WebSocket habilitado"
    )
    WEBSOCKET_PATH: str = Field(
        default_factory=lambda: os.getenv("WEBSOCKET_PATH", "/ws"),
        description="Caminho do WebSocket"
    )

    # Configurações de API
    API_V1_STR: str = Field(
        default_factory=lambda: os.getenv("API_V1_STR", "/api/v1"),
        description="Prefixo da API v1"
    )

    PROJECT_NAME: str = Field(
        default_factory=lambda: os.getenv(
            "PROJECT_NAME", "SynapScale Backend"
        ),
        description="Nome do projeto (compatibilidade)"
    )

    VERSION: str = Field(
        default_factory=lambda: os.getenv("VERSION", "1.0.0"),
        description="Versão do projeto (compatibilidade)"
    )

    UPLOAD_FOLDER: str = Field(
        default_factory=lambda: os.getenv("UPLOAD_FOLDER", "uploads"),
        description="Diretório de uploads (compatibilidade)"
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
def setup_logging() -> None:
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
    logger.info("   - Database: %s", settings.DATABASE_SCHEMA)
    logger.info("   - CORS: %s", settings.CORS_ORIGINS)
    logger.info("   - LLM Providers: %d", len(settings.get_llm_providers()))

logger.info(
    "✅ Configurações carregadas para ambiente: %s", settings.ENVIRONMENT
)

