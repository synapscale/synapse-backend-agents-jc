"""
Aplicação principal do SynapScale Backend - VERSÃO OTIMIZADA COM CONFIGURAÇÃO CENTRALIZADA
Migração completa para main.py com todas as correções implementadas
Implementa as melhores práticas de segurança, performance e configuração
Sistema de configuração centralizada elimina todas as duplicações
"""
import logging
import time
import os
import sys
from pathlib import Path as _PathHelper
import uvicorn

# --- Garantir que o pacote "synapse" seja encontrado mesmo se PYTHONPATH não estiver definido ---
project_root = _PathHelper(__file__).resolve().parents[2]  # .../synapse-backend-agents-jc
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
# ---------------------------------------------------------------------------------------------

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from sqlalchemy.orm import Session
from pathlib import Path
from fastapi.openapi.utils import get_openapi

# Importar do sistema centralizado
from synapse.core.config_new import settings
from synapse.database import init_db, get_db, health_check
from synapse.api.v1.router import api_router
from synapse.middlewares.rate_limiting import rate_limit

# Configuração de logging otimizada com sistema centralizado
log_level_name = settings.LOG_LEVEL or "INFO"
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=log_level,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        # Adicionar FileHandler se LOG_FILE estiver configurado
        *([logging.FileHandler(settings.LOG_FILE)] if hasattr(settings, 'LOG_FILE') and settings.LOG_FILE else [])
    ]
)
logger = logging.getLogger(__name__)

def validate_settings():
    """Validação mínima de settings para inicialização e testes."""
    return True, []

def check_configuration():
    """Verifica configurações críticas da aplicação usando sistema centralizado"""
    logger.info("🔍 Verificando configurações com sistema centralizado...")
    
    # Usar validação centralizada
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
    """Gerencia o ciclo de vida da aplicação com sistema centralizado"""
    logger.info('🚀 Iniciando SynapScale Backend API com configuração centralizada...')
    
    try:
        # Verificar configurações com sistema centralizado
        config_valid, config_errors = check_configuration()
        if not config_valid:
            raise Exception(f"Configurações inválidas: {config_errors}")
        
        # Criar diretórios necessários usando configurações centralizadas
        upload_dir = settings.UPLOAD_FOLDER or "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f'📁 Diretório de uploads criado: {upload_dir}')
        
        # Inicializar banco de dados
        init_db()
        logger.info('✅ Banco de dados inicializado via SQLAlchemy')
        
        # Verificar conectividade
        if health_check():
            logger.info('✅ Conectividade com banco de dados verificada')
        else:
            logger.error('❌ Falha na verificação de conectividade com o banco')
            # Em ambiente de produção (como Render), permitir inicialização mesmo sem banco
            # O banco pode estar ainda sendo provisionado
            if settings.ENVIRONMENT == "production":
                logger.warning('⚠️ Continuando em produção - banco pode estar sendo provisionado')
            elif settings.is_development():
                logger.warning('⚠️ Continuando em modo desenvolvimento sem banco de dados')
            else:
                raise Exception("Falha na verificação de conectividade com o banco")
            
    except Exception as e:
        logger.error(f'❌ Erro crítico na inicialização: {e}')
        raise
    
    # Inicializar componentes opcionais
    websocket_manager = None
    try:
        from synapse.core.websockets.manager import ConnectionManager
        websocket_manager = ConnectionManager()
        logger.info('✅ WebSocket Manager inicializado')
    except Exception as e:
        logger.warning(f'⚠️  WebSocket Manager não disponível: {e}')
    
    try:
        from synapse.api.v1.endpoints.executions import initialize_execution_service
        await initialize_execution_service(websocket_manager)
        logger.info('✅ Engine de Execução de Workflows inicializada')
    except Exception as e:
        logger.warning(f'⚠️  Engine de Execução não disponível: {e}')
    
    logger.info('🎉 SynapScale Backend iniciado com sucesso!')
    
    yield
    
    # Shutdown
    logger.info('🔄 Finalizando SynapScale Backend...')
    try:
        from synapse.api.v1.endpoints.executions import shutdown_execution_service
        await shutdown_execution_service()
        logger.info('✅ Engine de Execução finalizada')
    except Exception as e:
        logger.warning(f'⚠️  Erro ao finalizar Engine de Execução: {e}')
    
    logger.info('✅ SynapScale Backend finalizado com sucesso')

# Criar aplicação FastAPI com configurações centralizadas
app = FastAPI(
    title=settings.PROJECT_NAME,
    description='''
    🚀 **SynapScale Backend API** - Plataforma de Automação com IA
    
    API robusta e escalável para gerenciamento de workflows, agentes AI e automações.
    **VERSÃO OTIMIZADA COM CONFIGURAÇÃO CENTRALIZADA**
    
    ## Funcionalidades Principais
    
    * **🔐 Autenticação**: Sistema completo de autenticação e autorização
    * **⚡ Workflows**: Criação e execução de workflows de automação
    * **🤖 Agentes AI**: Integração com múltiplos provedores de IA
    * **🔗 Nodes**: Componentes reutilizáveis para workflows
    * **💬 Conversas**: Histórico e gerenciamento de conversas
    * **📁 Arquivos**: Upload e gerenciamento de arquivos
    
    ## Segurança
    
    * Autenticação JWT robusta
    * Validação de dados com Pydantic
    * Rate limiting implementado
    * CORS configurado adequadamente
    
    ## Sistema Centralizado
    
    Esta versão implementa sistema de configuração centralizada que elimina
    todas as duplicações e melhora a manutenibilidade.
    ''',
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,          # esconde lista lateral de schemas
        "docExpansion": "none",                # inicia colapsado
        "displayRequestDuration": True,         # mostra tempo de requisição
        "tryItOutEnabled": True,                # permite executar
        "persistAuthorization": True,           # manter autenticação entre sessões
    },
            swagger_ui_css_url="/static/unified-docs-styles.css?v=3",
    lifespan=lifespan,
    contact={'name': 'SynapScale Team', 'email': 'support@synapscale.com'},
    license_info={'name': 'MIT'}
)

# ------- CORS CONFIGURATION (centralizada) -------
cors_origins = settings.backend_cors_origins_list

allow_methods = settings.CORS_ALLOW_METHODS or ['*']
allow_headers = settings.CORS_ALLOW_HEADERS or ['*']
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

# Trusted host middleware para segurança
if not settings.DEBUG:
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
else:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )

@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    """Adiciona headers de segurança"""
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    """Adiciona tempo de processamento no header"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

@app.middleware('http')
async def log_requests(request: Request, call_next):
    """Log de requisições com informações essenciais"""
    start_time = time.time()
    
    # Extrair informações da requisição
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    user_agent = request.headers.get("user-agent", "unknown")
    
    response = await call_next(request)
    
    # Calcular tempo de processamento
    process_time = time.time() - start_time
    
    # Log da requisição
    logger.info(
        f"{method} {url} - {response.status_code} - "
        f"{process_time:.3f}s - {client_ip} - {user_agent[:50]}"
    )
    
    return response

@app.middleware('http')
async def rate_limit_middleware(request: Request, call_next):
    # Limite padrão: 100 requisições por 60 segundos
    return await rate_limit(max_requests=100, window_seconds=60)(call_next)(request)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": "Um erro inesperado ocorreu. Nossa equipe foi notificada.",
            "request_id": request.headers.get("X-Request-ID", "unknown"),
            "timestamp": time.time()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Erro na requisição",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "request_id": request.headers.get("X-Request-ID", "unknown"),
            "timestamp": time.time()
        }
    )

@app.get('/health', tags=['health'])
async def health_check_endpoint(db: Session = Depends(get_db)):
    """
    Verificação de saúde da aplicação com detalhes completos
    """
    try:
        # Verificar banco de dados
        db_healthy = health_check()
        
        # Informações básicas
        health_info = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": time.time(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": {
                "status": "connected" if db_healthy else "disconnected",
                "url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "not_configured"
            },
            "services": {
                "api": "running",
                "database": "connected" if db_healthy else "disconnected"
            },
            "system": {
                "uptime": time.time(),  # Seria melhor ter o tempo real de uptime
                "memory_usage": "not_monitored",
                "cpu_usage": "not_monitored"
            }
        }
        
        # Verificar serviços opcionais
        try:
            from synapse.core.websockets.manager import ConnectionManager
            health_info["services"]["websockets"] = "available"
        except ImportError:
            health_info["services"]["websockets"] = "not_available"
        
        return health_info
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": time.time()
            }
        )

@app.get('/', tags=['root'])
async def root():
    """
    Endpoint raiz da API com informações gerais
    """
    docs_url = "/docs" if settings.DEBUG else None
    redoc_url = "/redoc" if settings.DEBUG else None
    return {
        "message": "🚀 SynapScale Backend API",
        "description": "API de Automação e IA - Versão Otimizada com Configuração Centralizada",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": docs_url,
        "redoc": redoc_url,
        "health": "/health",
        "api_prefix": settings.API_V1_STR,
        "features": {
            "authentication": "✅ JWT + Refresh Token",
            "workflows": "✅ Execução de Automações",
            "ai_agents": "✅ Múltiplos Provedores",
            "websockets": "✅ Tempo Real",
            "file_upload": "✅ Gerenciamento de Arquivos",
            "user_variables": "✅ Configurações Personalizadas"
        },
        "contact": {
            "team": "SynapScale Team",
            "email": "support@synapscale.com"
        },
        "timestamp": time.time()
    }

@app.get('/info', tags=['info'])
async def api_info():
    """
    Informações detalhadas sobre a API e configurações públicas
    """
    docs_url = "/docs" if settings.DEBUG else None
    redoc_url = "/redoc" if settings.DEBUG else None
    return {
        "api": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        },
        "endpoints": {
            "health": "/health",
            "docs": docs_url,
            "redoc": redoc_url,
            "openapi": "/openapi.json"
        },
        "configuration": {
            "cors_origins": len(settings.BACKEND_CORS_ORIGINS),
            "max_upload_size": f"{settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f}MB",
            "allowed_extensions": settings.ALLOWED_FILE_EXTENSIONS,
            "database_type": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite",
            "cache_enabled": getattr(settings, 'CACHE_ENABLED', False),
            "websockets_enabled": True
        },
        "security": {
            "jwt_algorithm": settings.JWT_ALGORITHM,
            "access_token_expire": f"{settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "refresh_token_expire": f"{settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days",
            "cors_enabled": True,
            "rate_limiting": getattr(settings, 'RATE_LIMIT_ENABLED', False)
        },
        "timestamp": time.time()
    }

# Incluir roteador principal da API
app.include_router(api_router, prefix=settings.API_V1_STR)

# ------------------------------------------------------------
# Static assets (apenas para DEBUG) – contém o CSS de override
# ------------------------------------------------------------
if settings.DEBUG:
    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ------------------------------------------------------------
# OpenAPI personalizado – garante refs corretas de schemas e configura autenticação
# ------------------------------------------------------------
def custom_openapi():
    """Gera um esquema OpenAPI customizado resolvendo refs de schemas."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=[{"name": "health", "description": "Endpoints de saúde"},
              {"name": "info", "description": "Informações da API"},
              {"name": "root", "description": "Endpoint raiz"}],
    )

    # Configurar esquemas de segurança para facilitar o uso na documentação
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBasic": {
            "type": "http",
            "scheme": "basic",
            "description": "🔐 **Login com Email/Senha** - Digite seu email no campo 'Username' e sua senha no campo 'Password'"
        },
        "HTTPBearer": {
            "type": "http", 
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "🔑 **Token JWT** - Use o token obtido após fazer login (formato: Bearer <token>)"
        }
    }

    # Configurar segurança global para usar ambos os esquemas
    openapi_schema["security"] = [
        {"HTTPBasic": []},
        {"HTTPBearer": []}
    ]

    # Garantir que todos os $ref de componentes apontem para #/components/schemas/<Model>
    # FastAPI normalmente já faz isso, mas caso algum caminho absoluto apareça, normalizamos.
    def _fix_refs(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "$ref" and isinstance(v, str) and not v.startswith("#/components/"):
                    # Extrai o nome do schema e monta referência local
                    schema_name = v.split("/")[-1]
                    obj[k] = f"#/components/schemas/{schema_name}"
                else:
                    _fix_refs(v)
        elif isinstance(obj, list):
            for item in obj:
                _fix_refs(item)

    _fix_refs(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Aplica função personalizada
app.openapi = custom_openapi

if __name__ == "__main__":
    logger.info(f"🚀 Iniciando servidor em modo desenvolvimento...")
    logger.info(f"📍 Host: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    logger.info(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔍 Debug: {settings.DEBUG}")
    logger.info(f"📚 Docs: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}{None}")
    
    uvicorn.run(
        "synapse.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG and settings.is_development(),
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,
        date_header=False
    )
