"""Aplicação principal do backend SynapScale.

Este módulo configura e inicializa a aplicação FastAPI, incluindo
middlewares, rotas, documentação e ciclo de vida.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from .api.v1 import router as v1_router
from .config import settings
from .db import init_db
from .logging import setup_logging
from .middlewares import setup_rate_limiting

# Configurar logging
setup_logging()

# Logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação.
    
    Args:
        app: Aplicação FastAPI
    """
    # Startup
    logger.info("🚀 Iniciando serviço de uploads...")
    
    # Inicializar banco de dados
    await init_db()
    
    # Criar diretórios necessários
    os.makedirs(settings.storage_base_path, exist_ok=True)
    for category in settings.allowed_file_categories:
        os.makedirs(os.path.join(settings.storage_base_path, category), exist_ok=True)
    
    logger.info("✅ Serviço de uploads inicializado com sucesso")
    
    yield
    
    # Shutdown
    logger.info("👋 Encerrando serviço de uploads...")


# Criar aplicação
app = FastAPI(
    title=settings.project_name,
    description="API para gerenciamento de uploads de arquivos",
    version=settings.version,
    docs_url=None,  # Desabilitar Swagger UI padrão
    redoc_url=None,  # Desabilitar ReDoc padrão
    lifespan=lifespan,
)

# Configurar CORS
origins = settings.backend_cors_origins
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS configurado com origens: {origins}")

# Configurar rate limiting
setup_rate_limiting(app)


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Middleware para logging de requisições.
    
    Args:
        request: Requisição HTTP
        call_next: Próxima função na cadeia de middlewares
        
    Returns:
        Resposta HTTP
    """
    path = request.url.path
    method = request.method
    
    # Não logar requisições de health check
    if path == "/health" or path == "/":
        return await call_next(request)
    
    logger.info(f"{method} {path}")
    
    # Processar requisição
    response = await call_next(request)
    
    logger.info(f"{method} {path} - {response.status_code}")
    return response


# Rotas de documentação personalizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Endpoint para Swagger UI personalizado.
    
    Returns:
        HTML do Swagger UI
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Endpoint para ReDoc personalizado.
    
    Returns:
        HTML do ReDoc
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


# Personalizar schema OpenAPI
def custom_openapi():
    """Personaliza o schema OpenAPI.
    
    Returns:
        Schema OpenAPI personalizado
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Adicionar componentes de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Aplicar segurança globalmente
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Rota de health check
@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint para verificação de saúde da aplicação.
    
    Returns:
        Status da aplicação
    """
    return {"status": "ok", "version": settings.version}


# Rota raiz
@app.get("/", tags=["root"])
async def root():
    """Endpoint raiz da aplicação.
    
    Returns:
        Informações básicas da API
    """
    return {
        "name": settings.project_name,
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Incluir rotas da API v1
app.include_router(v1_router, prefix=settings.api_v1_str)

# Log de inicialização
logger.info(
    f"Aplicação {settings.project_name} v{settings.version} "
    f"configurada no ambiente {settings.environment}"
)
