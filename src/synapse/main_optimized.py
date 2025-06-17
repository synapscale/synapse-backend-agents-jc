"""
Aplicação principal otimizada do SynapScale Backend
Criado por José - um desenvolvedor Full Stack
Implementa todas as melhores práticas de FastAPI, segurança e performance
"""

import logging
import time
import os
import sys
from pathlib import Path as _PathHelper
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import uvicorn

from synapse.core.config_new import settings
from .core.database_new import (
    test_database_connection,
    get_database_info,
    init_database,
)
from .api.v1.router import api_router
from synapse.middlewares.rate_limiting import rate_limit

# Configure logging
log_level_name = settings.LOG_LEVEL or "INFO"
logging.basicConfig(
    level=getattr(logging, log_level_name, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        (
            logging.FileHandler(settings.LOG_FILE)
            if settings.LOG_FILE
            else logging.StreamHandler()
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Avisar se LOG_LEVEL não foi definido explicitamente
if settings.LOG_LEVEL is None:
    logger.warning("LOG_LEVEL não definido – usando INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🚀 Starting Synapse Backend...")

    # Check database connection
    if not test_database_connection():
        raise Exception("Failed to connect to database")

    # Initialize database
    if not init_database():
        raise Exception("Failed to initialize database")

    # Create upload directory, exige definição explícita
    if settings.UPLOAD_FOLDER is None:
        raise RuntimeError("UPLOAD_FOLDER deve ser definido nas variáveis de ambiente")
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    # Create logs directory
    if settings.LOG_FILE:
        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

    logger.info("✅ Backend started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Synapse Backend...")


# Create FastAPI application
app = FastAPI(
    title="Synapse Backend Agents JC",
    description="Backend for AI automation platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
    swagger_ui_css_url="/static/swagger-overrides.css?v=2" if settings.DEBUG else None,
    lifespan=lifespan,
)

# -------- CORS CONFIGURATION centralizada --------
cors_origins = settings.backend_cors_origins_list
allow_methods = settings.CORS_ALLOW_METHODS or ["*"]
allow_headers = settings.CORS_ALLOW_HEADERS or ["*"]
expose_headers = settings.CORS_EXPOSE_HEADERS or []
allow_credentials = settings.CORS_ALLOW_CREDENTIALS if settings.CORS_ALLOW_CREDENTIALS is not None else True
max_age = settings.CORS_MAX_AGE or 600

logger.debug(
    "CORS: origins=%s methods=%s headers=%s expose=%s credentials=%s max_age=%s",
    cors_origins,
    allow_methods,
    allow_headers,
    expose_headers,
    allow_credentials,
    max_age,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    expose_headers=expose_headers,
    max_age=max_age,
)

# Security middleware
if not settings.DEBUG:
    # Usar BACKEND_CORS_ORIGINS como fonte para allowed_hosts
    cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS")
    trusted_hosts = None
    if cors_origins_env:
        try:
            if cors_origins_env.strip().startswith("["):
                import json as _json
                trusted_hosts = _json.loads(cors_origins_env)
            else:
                trusted_hosts = [h.strip() for h in cors_origins_env.split(",") if h.strip()]
            # Ajuste automático: remover protocolo e barras finais
            def clean_host(host):
                host = host.strip()
                if host.startswith("http://"):
                    host = host[len("http://"):]
                elif host.startswith("https://"):
                    host = host[len("https://"):]
                return host.rstrip("/")
            trusted_hosts = [clean_host(h) for h in trusted_hosts]
        except Exception as e:
            logger.error(f"Erro ao processar BACKEND_CORS_ORIGINS para TrustedHostMiddleware: {e}")
            trusted_hosts = ["*"]
    else:
        trusted_hosts = ["*"]
    try:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts,
        )
    except Exception as e:
        logger.error(f"Erro ao adicionar TrustedHostMiddleware com hosts {trusted_hosts}: {e}")
        # Tentar ajuste extra: permitir todos
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],
        )

# Include API routers
app.include_router(api_router, prefix="/api/v1")

# Static mount for CSS (debug only)
if settings.DEBUG:
    static_dir = _PathHelper(__file__).resolve().parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Health checks
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check"""
    db_info = get_database_info()

    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "database": {
            "connected": db_info is not None,
            "schema": settings.DATABASE_SCHEMA,
            "tables": db_info["table_count"] if db_info else 0,
        },
        "llm_providers": {
            "openai": bool(settings.OPENAI_API_KEY),
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "google": bool(settings.GOOGLE_API_KEY),
            "groq": bool(settings.GROQ_API_KEY),
        },
        "features": {
            "file_upload": True,
            "websocket": True,
            "analytics": True,
        },
    }


@app.get("/health/db")
async def database_health_check():
    """Database specific health check"""
    if test_database_connection():
        db_info = get_database_info()
        return {
            "status": "healthy",
            "database": db_info,
        }
    else:
        raise HTTPException(status_code=503, detail="Database connection failed")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Synapse Backend Agents JC",
        "version": "1.0.0",
        "docs": (
            "/docs" if settings.DEBUG else "Documentation available only in development"
        ),
    }


@app.middleware('http')
async def rate_limit_middleware(request, call_next):
    # Limite padrão: 100 requisições por 60 segundos
    return await rate_limit(max_requests=100, window_seconds=60)(call_next)(request)


if __name__ == "__main__":
    host = settings.HOST or "0.0.0.0"
    port = settings.PORT or 8000
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.DEBUG,
        log_level=log_level_name.lower(),
    )
