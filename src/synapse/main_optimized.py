"""
Aplicação principal otimizada do SynapScale Backend
Versão de produção com todas as funcionalidades essenciais sincronizadas
Implementa todas as melhores práticas de FastAPI, segurança e performance
"""

import logging
import time
import os
import sys
from pathlib import Path as _PathHelper
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

# --- Garantir que o pacote "synapse" seja encontrado ---
project_root = _PathHelper(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from synapse.core.config_new import settings
from synapse.database import init_db, get_db, health_check  # Usar database.py padrão
from synapse.api.v1.router import api_router
from synapse.middlewares.rate_limiting import rate_limit

# Configuração de logging otimizada
log_level_name = settings.LOG_LEVEL or "INFO"
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=log_level,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        *([logging.FileHandler(settings.LOG_FILE)] if hasattr(settings, 'LOG_FILE') and settings.LOG_FILE else [])
    ]
)
logger = logging.getLogger(__name__)

def validate_settings():
    """Validação mínima de settings para inicialização."""
    return True, []

def check_configuration():
    """Verifica configurações críticas da aplicação"""
    logger.info("🔍 Verificando configurações...")
    
    valid, errors = validate_settings()
    
    if not valid:
        logger.error("❌ Erros de configuração encontrados:")
        for error in errors:
            logger.error(f"   - {error}")
        return False, errors
    else:
        logger.info("✅ Todas as configurações validadas com sucesso")
        return True, []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info('🚀 Iniciando SynapScale Backend API (Otimizado)...')
    
    try:
        # Verificar configurações
        config_valid, config_errors = check_configuration()
        if not config_valid:
            raise Exception(f"Configurações inválidas: {config_errors}")
        
        # Criar diretórios necessários
        upload_dir = settings.UPLOAD_FOLDER or "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f'📁 Diretório de uploads criado: {upload_dir}')
        
        # Inicializar banco de dados
        init_db()
        logger.info('✅ Banco de dados inicializado')
        
        # Verificar conectividade
        if health_check():
            logger.info('✅ Conectividade com banco de dados verificada')
        else:
            logger.error('❌ Falha na verificação de conectividade com o banco')
            if settings.ENVIRONMENT == "production":
                logger.warning('⚠️ Continuando em produção - banco pode estar sendo provisionado')
            elif settings.is_development():
                logger.warning('⚠️ Continuando em modo desenvolvimento')
            else:
                raise Exception("Falha na verificação de conectividade com o banco")
        
        # Inicializar WebSocket Manager
        websocket_manager = None
        try:
            from synapse.core.websockets.manager import ConnectionManager
            websocket_manager = ConnectionManager()
            logger.info('✅ WebSocket Manager inicializado')
        except Exception as e:
            logger.warning(f'⚠️ WebSocket Manager não disponível: {e}')
        
        # Engine de Execução
        execution_engine_enabled = os.getenv('EXECUTION_ENGINE_ENABLED', 'true').lower() == 'true'
        if execution_engine_enabled:
            try:
                from synapse.api.v1.endpoints.executions import initialize_execution_service
                await initialize_execution_service(websocket_manager)
                logger.info('✅ Engine de Execução inicializada')
            except Exception as e:
                logger.warning(f'⚠️ Engine de Execução não disponível: {e}')
        
        logger.info('🎉 SynapScale Backend iniciado com sucesso!')
        
    except Exception as e:
        logger.error(f'❌ Erro crítico na inicialização: {e}')
        raise
    
    yield
    
    # Shutdown
    logger.info('🔄 Finalizando SynapScale Backend...')
    execution_engine_enabled = os.getenv('EXECUTION_ENGINE_ENABLED', 'true').lower() == 'true'
    if execution_engine_enabled:
        try:
            from synapse.api.v1.endpoints.executions import shutdown_execution_service
            await shutdown_execution_service()
            logger.info('✅ Engine de Execução finalizada')
        except Exception as e:
            logger.warning(f'⚠️ Erro ao finalizar Engine de Execução: {e}')
    
    logger.info('✅ SynapScale Backend finalizado com sucesso')

# Definição de tags para documentação
openapi_tags = [
    {"name": "system", "description": "🏠 Status do sistema e informações gerais"},
    {"name": "authentication", "description": "🔐 Autenticação e gerenciamento de sessão"},
    {"name": "workspaces", "description": "🏢 Workspaces e colaboração"},
    {"name": "workflows", "description": "⚙️ Workflows e automação"},
    {"name": "ai", "description": "🤖 IA e agentes"},
    {"name": "marketplace", "description": "🛒 Marketplace e componentes"},
    {"name": "analytics", "description": "📊 Analytics e relatórios"},
    {"name": "data", "description": "📁 Gestão de dados e arquivos"},
    {"name": "advanced", "description": "🔌 Recursos avançados"}
]

# Criar aplicação FastAPI
app = FastAPI(
    title=getattr(settings, 'PROJECT_NAME', None) or "SynapScale Backend API",
    description='''
    🚀 **SynapScale Backend API** - Plataforma de Automação com IA
    
    API robusta e escalável para gerenciamento de workflows, agentes AI e automações.
    **VERSÃO OTIMIZADA PARA PRODUÇÃO**
    
    ## Funcionalidades Principais
    
    * **🔐 Autenticação**: Sistema completo de autenticação e autorização
    * **⚡ Workflows**: Criação e execução de workflows de automação
    * **🤖 Agentes AI**: Integração com múltiplos provedores de IA
    * **🔗 Nodes**: Componentes reutilizáveis para workflows
    * **💬 Conversas**: Histórico e gerenciamento de conversas
    * **📁 Arquivos**: Upload e gerenciamento de arquivos
    
    ## Segurança
    
    * Autenticação JWT robusta
    * Rate limiting configurável
    * Headers de segurança
    * Validação de dados completa
    ''',
    version=getattr(settings, 'VERSION', None) or "2.0.0",
    openapi_tags=openapi_tags,
    docs_url=None,  # Desabilitar docs padrão para usar customizado
    redoc_url="/redoc",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
    lifespan=lifespan,
)

# -------- CORS CONFIGURATION --------
cors_origins = settings.backend_cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[],
    max_age=600,
)

# Security middleware
if not settings.DEBUG:
    cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS")
    trusted_hosts = ["*"]  # Simplificado para produção
    if cors_origins_env:
        try:
            if cors_origins_env.strip().startswith("["):
                import json as _json
                trusted_hosts = _json.loads(cors_origins_env)
            else:
                trusted_hosts = [h.strip() for h in cors_origins_env.split(",") if h.strip()]
            
            def clean_host(host):
                host = host.strip()
                if host.startswith("http://"):
                    host = host[len("http://"):]
                elif host.startswith("https://"):
                    host = host[len("https://"):]
                return host.rstrip("/")
            
            trusted_hosts = [clean_host(h) for h in trusted_hosts]
        except Exception as e:
            logger.error(f"Erro ao processar BACKEND_CORS_ORIGINS: {e}")
            trusted_hosts = ["*"]
    
    try:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
    except Exception as e:
        logger.error(f"Erro ao adicionar TrustedHostMiddleware: {e}")
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Middlewares essenciais
@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware('http')
async def log_auth_requests(request: Request, call_next):
    """Log de requisições de autenticação para debugging"""
    if request.url.path.startswith(f"{settings.API_V1_STR}/auth"):
        logger.info(f"🔐 Auth request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

@app.middleware('http')
async def log_requests(request: Request, call_next):
    """Log básico de requisições"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log apenas para endpoints importantes ou erros
    if response.status_code >= 400 or request.url.path.startswith(f"{settings.API_V1_STR}"):
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
    
    return response

@app.middleware('http')
async def rate_limit_middleware(request: Request, call_next):
    return await rate_limit(max_requests=100, window_seconds=60)(call_next)(request)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "http_error"}
    )

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static files (apenas em debug)
if settings.DEBUG:
    static_dir = _PathHelper(__file__).resolve().parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Adicionar informações de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Aplicar segurança globalmente (exceto para endpoints públicos)
    public_paths = ["/", "/health", "/health/detailed", "/docs", "/redoc", "/openapi.json"]
    for path in openapi_schema["paths"]:
        if path not in public_paths:
            for method in openapi_schema["paths"][path]:
                if method != "options":
                    openapi_schema["paths"][path][method]["security"] = [{"HTTPBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Endpoints customizados
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Documentation",
        swagger_ui_parameters=app.swagger_ui_parameters,
    )

# Health checks
@app.get("/health", tags=["system"])
async def health_check(db: Session = Depends(get_db)):
    """Health check básico"""
    try:
        # Teste básico de conectividade usando SQLAlchemy text()
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "database": db_status,
        "timestamp": time.time()
    }

@app.get("/health/detailed", tags=["system"])
async def detailed_health_check(db: Session = Depends(get_db)):
    """Health check detalhado"""
    try:
        # Teste de conectividade
        db.execute(text("SELECT 1"))
        db_connected = True
        
        # Contar tabelas usando SQLAlchemy text() com parâmetros seguros
        result = db.execute(
            text("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = :schema"),
            {"schema": settings.DATABASE_SCHEMA}
        )
        table_count = result.scalar() if result else 0
        
    except Exception as e:
        logger.error(f"Database detailed check failed: {e}")
        db_connected = False
        table_count = 0

    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "database": {
            "connected": db_connected,
            "schema": settings.DATABASE_SCHEMA,
            "tables": table_count,
        },
        "llm_providers": {
            "openai": bool(getattr(settings, 'OPENAI_API_KEY', None)),
            "anthropic": bool(getattr(settings, 'ANTHROPIC_API_KEY', None)),
            "google": bool(getattr(settings, 'GOOGLE_API_KEY', None)),
            "groq": bool(getattr(settings, 'GROQ_API_KEY', None)),
        },
        "features": {
            "file_upload": True,
            "websocket": True,
            "analytics": True,
        },
        "timestamp": time.time()
    }

@app.get("/", tags=["system"])
async def root():
    """Endpoint raiz"""
    return {
        "message": f"🚀 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_STR
    }

@app.get("/info", tags=["system"])
async def api_info():
    """Informações da API"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Plataforma de Automação com IA",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "features": {
            "authentication": True,
            "workflows": True,
            "ai_agents": True,
            "marketplace": True,
            "analytics": True,
            "websockets": True,
            "file_upload": True
        },
        "api_version": "v1",
        "openapi": "/openapi.json",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    logger.info(f"🚀 Iniciando servidor em modo desenvolvimento...")
    logger.info(f"📍 Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔍 Debug: {settings.DEBUG}")
    logger.info(f"📚 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    
    uvicorn.run(
        "synapse.main_optimized:app",
        host=settings.HOST or "0.0.0.0",
        port=settings.PORT or 8000,
        reload=settings.DEBUG,
        log_level=log_level_name.lower(),
        access_log=True,
        server_header=False,
        date_header=False
    )
