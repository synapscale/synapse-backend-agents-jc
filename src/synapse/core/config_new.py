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
        default_factory=lambda: os.getenv("DATABASE_SCHEMA"),
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

    # Configurações de LLM
    LLM_DEFAULT_PROVIDER: str | None = Field(
        default_factory=lambda: os.getenv("LLM_DEFAULT_PROVIDER", "openai"),
        description="Provedor LLM padrão"
    )
    OPENAI_API_KEY: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="Chave da API OpenAI"
    )
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

    # Configurações de Redis
    REDIS_URL: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_URL"),
        description="URL do Redis"
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
