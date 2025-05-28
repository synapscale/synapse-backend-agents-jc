"""
Testes unitários para o módulo de configuração.

Este módulo contém testes unitários para o módulo de configuração,
garantindo que as variáveis de ambiente sejam carregadas corretamente.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from synapse.config import Settings


@pytest.fixture
def mock_env_vars():
    """Mock para variáveis de ambiente."""
    env_vars = {
        "SECRET_KEY": "test_secret_key",
        "SERVER_NAME": "Test Server",
        "SERVER_HOST": "http://testserver",
        "PROJECT_NAME": "TestProject",
        "API_V1_STR": "/api/v1",
        "ENVIRONMENT": "testing",
        "LOG_LEVEL": "DEBUG",
        "BACKEND_CORS_ORIGINS": "http://localhost,http://example.com",
        "SQLALCHEMY_DATABASE_URI": "sqlite+aiosqlite:///./test.db",
        "CLAUDE_API_KEY": "test_claude_key",
        "GEMINI_API_KEY": "test_gemini_key",
        "GROK_API_KEY": "test_grok_key",
        "DEEPSEEK_API_KEY": "test_deepseek_key",
        "TESS_API_KEY": "test_tess_key",
        "TESS_API_BASE_URL": "https://test.tess.api",
        "OPENAI_API_KEY": "test_openai_key",
        "LLAMA_API_KEY": "test_llama_key",
        "LLAMA_API_BASE_URL": "https://test.llama.api",
        "LLM_DEFAULT_PROVIDER": "test_provider",
        "LLM_ENABLE_CACHE": "true",
        "LLM_CACHE_TTL": "1800",
        "UPLOAD_DIR": "./test_uploads",
        "MAX_UPLOAD_SIZE": "10485760",
        "ALLOWED_EXTENSIONS": "pdf,txt,jpg",
        "STORAGE_BASE_PATH": "./test_storage",
        "STORAGE_PROVIDER": "test_storage",
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_DEFAULT": "50/minute",
        "RATE_LIMIT_FILE_UPLOAD": "5/minute",
        "RATE_LIMIT_LLM_GENERATE": "10/minute",
        "REDIS_URL": "redis://localhost:6379/1",
        "RATE_LIMIT": "50",
        "RATE_LIMIT_WINDOW": "1800"
    }
    return env_vars


def test_settings_load_from_env(mock_env_vars):
    """Testa se as configurações são carregadas corretamente das variáveis de ambiente."""
    with patch.dict(os.environ, mock_env_vars):
        settings = Settings()
        
        # Verificar valores carregados
        assert settings.SECRET_KEY == "test_secret_key"
        assert settings.SERVER_NAME == "Test Server"
        assert str(settings.SERVER_HOST) == "http://testserver"
        assert settings.PROJECT_NAME == "TestProject"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.ENVIRONMENT == "testing"
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.BACKEND_CORS_ORIGINS_STR == "http://localhost,http://example.com"
        assert settings.SQLALCHEMY_DATABASE_URI == "sqlite+aiosqlite:///./test.db"
        assert settings.CLAUDE_API_KEY == "test_claude_key"
        assert settings.GEMINI_API_KEY == "test_gemini_key"
        assert settings.GROK_API_KEY == "test_grok_key"
        assert settings.DEEPSEEK_API_KEY == "test_deepseek_key"
        assert settings.TESS_API_KEY == "test_tess_key"
        assert settings.TESS_API_BASE_URL == "https://test.tess.api"
        assert settings.OPENAI_API_KEY == "test_openai_key"
        assert settings.LLAMA_API_KEY == "test_llama_key"
        assert settings.LLAMA_API_BASE_URL == "https://test.llama.api"
        assert settings.LLM_DEFAULT_PROVIDER == "test_provider"
        assert settings.LLM_ENABLE_CACHE is True
        assert settings.LLM_CACHE_TTL == 1800
        assert settings.UPLOAD_DIR == "./test_uploads"
        assert settings.MAX_UPLOAD_SIZE == 10485760
        assert settings.ALLOWED_EXTENSIONS_STR == "pdf,txt,jpg"
        assert settings.STORAGE_BASE_PATH == "./test_storage"
        assert settings.STORAGE_PROVIDER == "test_storage"
        assert settings.RATE_LIMIT_ENABLED is True
        assert settings.RATE_LIMIT_DEFAULT == "50/minute"
        assert settings.RATE_LIMIT_FILE_UPLOAD == "5/minute"
        assert settings.RATE_LIMIT_LLM_GENERATE == "10/minute"
        assert settings.REDIS_URL == "redis://localhost:6379/1"
        assert settings.RATE_LIMIT == 50
        assert settings.RATE_LIMIT_WINDOW == 1800


def test_settings_default_values():
    """Testa se os valores padrão são usados quando as variáveis de ambiente não estão definidas."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        
        # Verificar valores padrão
        assert settings.SERVER_NAME == "SynapScale API"
        assert str(settings.SERVER_HOST) == "http://localhost"
        assert settings.PROJECT_NAME == "SynapScale"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.ENVIRONMENT == "development"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.BACKEND_CORS_ORIGINS_STR == "*"
        assert settings.SQLALCHEMY_DATABASE_URI == "sqlite+aiosqlite:///./synapse.db"
        assert settings.LLM_DEFAULT_PROVIDER == "claude"
        assert settings.LLM_ENABLE_CACHE is True
        assert settings.LLM_CACHE_TTL == 3600
        assert settings.UPLOAD_DIR == "./uploads"
        assert settings.MAX_UPLOAD_SIZE == 50 * 1024 * 1024
        assert settings.ALLOWED_EXTENSIONS_STR == "pdf,doc,docx,txt,csv,xls,xlsx,jpg,jpeg,png"
        assert settings.STORAGE_BASE_PATH == "./storage"
        assert settings.STORAGE_PROVIDER == "local"
        assert settings.RATE_LIMIT_ENABLED is True
        assert settings.RATE_LIMIT_DEFAULT == "100/minute"
        assert settings.RATE_LIMIT_FILE_UPLOAD == "10/minute"
        assert settings.RATE_LIMIT_LLM_GENERATE == "20/minute"
        assert settings.REDIS_URL == "redis://localhost:6379/0"
        assert settings.RATE_LIMIT == 100
        assert settings.RATE_LIMIT_WINDOW == 3600


def test_backend_cors_origins_property():
    """Testa a propriedade BACKEND_CORS_ORIGINS."""
    # Teste com múltiplas origens
    with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": "http://localhost,http://example.com"}):
        settings = Settings()
        assert settings.BACKEND_CORS_ORIGINS == ["http://localhost", "http://example.com"]
    
    # Teste com wildcard
    with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": "*"}):
        settings = Settings()
        assert settings.BACKEND_CORS_ORIGINS == ["*"]
    
    # Teste com espaços extras
    with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": "http://localhost, http://example.com"}):
        settings = Settings()
        assert settings.BACKEND_CORS_ORIGINS == ["http://localhost", "http://example.com"]


def test_allowed_extensions_property():
    """Testa a propriedade ALLOWED_EXTENSIONS."""
    # Teste com múltiplas extensões
    with patch.dict(os.environ, {"ALLOWED_EXTENSIONS": "pdf,txt,jpg"}):
        settings = Settings()
        assert settings.ALLOWED_EXTENSIONS == ["pdf", "txt", "jpg"]
    
    # Teste com espaços extras
    with patch.dict(os.environ, {"ALLOWED_EXTENSIONS": "pdf, txt, jpg"}):
        settings = Settings()
        assert settings.ALLOWED_EXTENSIONS == ["pdf", "txt", "jpg"]
