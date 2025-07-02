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
project_root = (
    _PathHelper(__file__).resolve().parents[2]
)  # .../synapse-backend-agents-jc
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
# ---------------------------------------------------------------------------------------------

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from sqlalchemy.orm import Session
from pathlib import Path
from fastapi.openapi.utils import get_openapi
from sqlalchemy import (
    text,
)  # 🆕 necessário para consultas SQL diretas no health detailed

# Importar do sistema centralizado
from synapse.core.config import settings
from synapse.database import init_db, get_db
from synapse.api.v1.api import api_router
from synapse.api.deps import get_current_user
from synapse.models.user import User
from synapse.middlewares.rate_limiting import rate_limit
from synapse.middlewares.metrics import setup_metrics_middleware
from synapse.middlewares.error_middleware import setup_error_middleware
from synapse.middlewares.tenant_middleware import TenantMiddleware
from synapse.error_handlers import setup_error_handlers, add_request_id_middleware

# Sistema de tracing distribuído
from synapse.core.tracing import (
    setup_tracing,
    instrument_fastapi,
    instrument_libraries,
    TracingMiddleware,
    get_trace_context,
)

# Configuração de logging otimizada com sistema centralizado
log_level_name = settings.LOG_LEVEL or "INFO"
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        # Adicionar FileHandler se LOG_FILE estiver configurado
        *(
            [logging.FileHandler(settings.LOG_FILE)]
            if hasattr(settings, "LOG_FILE") and settings.LOG_FILE
            else []
        ),
    ],
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
    logger.info("🚀 Iniciando SynapScale Backend API com configuração centralizada...")

    try:
        # Verificar configurações com sistema centralizado
        config_valid, config_errors = check_configuration()
        if not config_valid:
            raise Exception(f"Configurações inválidas: {config_errors}")

        # Criar diretórios necessários usando configurações centralizadas
        upload_dir = settings.UPLOAD_FOLDER or "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"📁 Diretório de uploads criado: {upload_dir}")

        # Tracing já foi configurado durante a criação da aplicação
        if settings.ENABLE_TRACING:
            logger.info("✅ Sistema de tracing distribuído já configurado")

        # Inicializar banco de dados
        await init_db()
        logger.info("✅ Banco de dados inicializado via SQLAlchemy")

        # Configurar serviços de dependency injection
        try:
            from synapse.core.services import configure_services

            configure_services()
            logger.info("✅ Sistema de serviços configurado")
        except Exception as e:
            logger.warning(f"⚠️  Sistema de serviços não disponível: {e}")

        # Verificar conectividade
        try:
            # Simple health check using SQLAlchemy
            from synapse.database import AsyncSessionLocal

            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            logger.info("✅ Conectividade com banco de dados verificada")
        except Exception as e:
            logger.error(f"❌ Falha na verificação de conectividade com o banco: {e}")
            # Em ambiente de produção (como Render), permitir inicialização mesmo sem banco
            # O banco pode estar ainda sendo provisionado
            if settings.ENVIRONMENT == "production":
                logger.warning(
                    "⚠️ Continuando em produção - banco pode estar sendo provisionado"
                )
            elif settings.is_development():
                logger.warning(
                    "⚠️ Continuando em modo desenvolvimento sem banco de dados"
                )
            else:
                raise Exception("Falha na verificação de conectividade com o banco")

    except Exception as e:
        logger.error(f"❌ Erro crítico na inicialização: {e}")
        raise

    # Inicializar componentes opcionais
    websocket_manager = None
    try:
        from synapse.core.websockets.manager import ConnectionManager

        websocket_manager = ConnectionManager()
        logger.info("✅ WebSocket Manager inicializado")
    except Exception as e:
        logger.warning(f"⚠️  WebSocket Manager não disponível: {e}")

    # Engine de Execução (pode ser desabilitada em desenvolvimento)
    execution_engine_enabled = (
        os.getenv("EXECUTION_ENGINE_ENABLED", "true").lower() == "true"
    )
    if execution_engine_enabled:
        try:
            from synapse.api.v1.endpoints.executions import initialize_execution_service

            await initialize_execution_service(websocket_manager)
            logger.info("✅ Engine de Execução de Workflows inicializada")
        except Exception as e:
            logger.warning(f"⚠️  Engine de Execução não disponível: {e}")
    else:
        logger.info(
            "⚠️  Engine de Execução desabilitada (EXECUTION_ENGINE_ENABLED=false)"
        )

    # Alert System and Background Tasks (always enabled if database is available)
    background_task_manager = None
    alert_system_enabled = os.getenv("ALERT_SYSTEM_ENABLED", "true").lower() == "true"
    if alert_system_enabled:
        try:
            from synapse.core.alerts.background_tasks import (
                background_task_manager as bg_manager,
            )

            background_task_manager = bg_manager
            await background_task_manager.start_all_tasks()
            logger.info("✅ Sistema de Alertas e Tarefas em Background inicializado")
        except Exception as e:
            logger.warning(f"⚠️  Sistema de Alertas não disponível: {e}")
    else:
        logger.info("⚠️  Sistema de Alertas desabilitado (ALERT_SYSTEM_ENABLED=false)")

    logger.info("🎉 SynapScale Backend iniciado com sucesso!")

    yield

    # Shutdown
    logger.info("🔄 Finalizando SynapScale Backend...")
    execution_engine_enabled = (
        os.getenv("EXECUTION_ENGINE_ENABLED", "true").lower() == "true"
    )
    if execution_engine_enabled:
        try:
            from synapse.api.v1.endpoints.executions import shutdown_execution_service

            await shutdown_execution_service()
            logger.info("✅ Engine de Execução finalizada")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao finalizar Engine de Execução: {e}")
    else:
        logger.info("ℹ️  Engine de Execução não estava habilitada")

    # Shutdown Alert System and Background Tasks
    if "background_task_manager" in locals() and background_task_manager:
        try:
            await background_task_manager.stop_all_tasks()
            logger.info("✅ Sistema de Alertas e Tarefas em Background finalizado")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao finalizar Sistema de Alertas: {e}")
    else:
        logger.info("ℹ️  Sistema de Alertas não estava habilitado")

    logger.info("✅ SynapScale Backend finalizado com sucesso")


# Tags da API reorganizadas - ESTRUTURA FINAL SIMPLIFICADA E CONSOLIDADA
openapi_tags = [
    # 🏠 SISTEMA
    {
        "name": "system",
        "description": "⚙️ Status do sistema, saúde e informações gerais",
    },
    # 🔐 AUTENTICAÇÃO (CONSOLIDADO)
    {
        "name": "authentication", 
        "description": "🔐 Autenticação completa: login, registro, JWT, usuários e permissões",
    },
    # 🤖 INTELIGÊNCIA ARTIFICIAL (CONSOLIDADO)
    {
        "name": "ai",
        "description": "🤖 IA completa: LLM, conversas, feedback e integrações multimodais",
    },
    # 🎯 AGENTES (CONSOLIDADO)
    {
        "name": "agents",
        "description": "🎯 Agentes completos: configurações, ferramentas, modelos, ACL e métricas",
    },
    # ⚙️ WORKFLOWS E AUTOMAÇÃO
    {
        "name": "workflows",
        "description": "⚙️ Workflows completos: criação, nós, execuções e automação",
    },
    # 📊 ANALYTICS
    {
        "name": "analytics",
        "description": "📊 Analytics completo: métricas, dashboards, usage e insights",
    },
    # 💾 GESTÃO DE DADOS (CONSOLIDADO)
    {
        "name": "data",
        "description": "💾 Dados completos: arquivos, uploads, variáveis, tags e workspace",
    },
    # 🏢 FUNCIONALIDADES EMPRESARIAIS (CONSOLIDADO)
    {
        "name": "enterprise",
        "description": "🏢 Enterprise completo: RBAC, features, pagamentos e compliance",
    },
    # 🛒 MARKETPLACE
    {
        "name": "marketplace",
        "description": "🛒 Marketplace: templates, componentes e transações",
    },
    # 👨‍💼 ADMINISTRAÇÃO
    {
        "name": "admin",
        "description": "👨‍💼 Administração: migrações, configurações e gestão do sistema",
    },
    # ⚠️ DEPRECATED
    {
        "name": "deprecated",
        "description": "⚠️ Endpoints legados mantidos para compatibilidade",
    },
]

# Criar aplicação FastAPI com configurações centralizadas
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    🚀 **SynapScale Backend API** - Plataforma de Automação com IA
    
    API robusta e escalável para gerenciamento de workflows, agentes AI e automações.
    **VERSÃO OTIMIZADA COM CONFIGURAÇÃO CENTRALIZADA E LLM UNIFICADO**
    
    ## Funcionalidades Principais
    
    * **🔐 Autenticação**: Sistema completo de autenticação e autorização
    * **⚡ Workflows**: Criação e execução de workflows de automação
    * **🤖 LLM Unificado**: Integração centralizada com OpenAI, Anthropic, Google e outros provedores
    * **🤖 Agentes AI**: Automação inteligente com múltiplos provedores
    * **🔗 Nodes**: Componentes reutilizáveis para workflows
    * **💬 Conversas**: Histórico e gerenciamento de conversas
    * **📁 Arquivos**: Upload e gerenciamento de arquivos
    
    ## Sistema LLM Unificado
    
    * **Endpoints Centralizados**: Todos em `/llm/*` para facilitar integração
    * **Multi-Provider**: OpenAI, Anthropic, Google, Meta e mais
    * **Cache Inteligente**: Redis para otimização de performance
    * **Gestão de Tokens**: Controle preciso de uso e custos
    * **Validação de DB**: Validação em tempo real dos modelos disponíveis
    
    ## Segurança
    
    * Autenticação JWT robusta
    * Validação de dados com Pydantic
    * Rate limiting implementado
    * CORS configurado adequadamente
    
    ## Sistema Centralizado
    
    Esta versão implementa sistema de configuração centralizada que elimina
    todas as duplicações e melhora a manutenibilidade.
    """,
    version=settings.VERSION,
    docs_url=None,  # Desabilitar docs padrão para usar custom
    redoc_url="/redoc",
    openapi_tags=openapi_tags,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # esconde lista lateral de schemas
        "docExpansion": "none",  # inicia colapsado
        "displayRequestDuration": True,  # mostra tempo de requisição
        "tryItOutEnabled": True,  # permite executar
        "persistAuthorization": True,  # manter autenticação entre sessões
    },
    swagger_ui_init_oauth=None,
    swagger_ui_css_url=None,
    lifespan=lifespan,
    contact={"name": "SynapScale Team", "email": "support@synapscale.com"},
    license_info={"name": "MIT"},
)

# ------- CORS CONFIGURATION (centralizada) -------
cors_origins = settings.backend_cors_origins_list

allow_methods = settings.CORS_ALLOW_METHODS or ["*"]
allow_headers = settings.CORS_ALLOW_HEADERS or ["*"]
expose_headers = settings.CORS_EXPOSE_HEADERS or []
allow_credentials = (
    settings.CORS_ALLOW_CREDENTIALS
    if settings.CORS_ALLOW_CREDENTIALS is not None
    else True
)
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
                trusted_hosts = [
                    h.strip() for h in cors_origins_env.split(",") if h.strip()
                ]

            # Ajuste automático: remover protocolo e barras finais
            def clean_host(host):
                host = host.strip()
                if host.startswith("http://"):
                    host = host[len("http://") :]
                elif host.startswith("https://"):
                    host = host[len("https://") :]
                return host.rstrip("/")

            trusted_hosts = [clean_host(h) for h in trusted_hosts]
        except Exception as e:
            logger.error(
                f"Erro ao processar BACKEND_CORS_ORIGINS para TrustedHostMiddleware: {e}"
            )
            trusted_hosts = ["*"]
    else:
        trusted_hosts = ["*"]
    try:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts,
        )
    except Exception as e:
        logger.error(
            f"Erro ao adicionar TrustedHostMiddleware com hosts {trusted_hosts}: {e}"
        )
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


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Adiciona headers de segurança"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Adiciona tempo de processamento no header"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_auth_requests(request: Request, call_next):
    """Log de requisições de autenticação para debug"""

    # Se for uma requisição para a API, log dos headers de autenticação
    if request.url.path.startswith("/api/v1/"):
        auth_header = request.headers.get("authorization")
        if auth_header:
            logger.debug(f"Auth header presente: {auth_header[:20]}...")
        else:
            logger.debug(f"Sem auth header - Path: {request.url.path}")

    response = await call_next(request)
    return response


@app.middleware("http")
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


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Limite padrão: 100 requisições por 60 segundos
    return await rate_limit(max_requests=100, window_seconds=60)(call_next)(request)


# Configurar middleware de métricas para monitoramento
setup_metrics_middleware(app)

# CRÍTICO: Adicionar middleware de tenant ANTES dos outros middlewares
app.add_middleware(TenantMiddleware)

# Configurar middleware para adicionar request ID
app.middleware("http")(add_request_id_middleware)

# Configurar middleware de interceptação de erros
setup_error_middleware(app)

# Configurar handlers de erro globais
setup_error_handlers(app)

# Configurar tracing distribuído
if settings.ENABLE_TRACING:
    # Configurar tracing antes de instrumentar
    setup_tracing()
    instrument_libraries()
    
    # Adicionar middleware de tracing
    app.add_middleware(TracingMiddleware)
    # Instrumentar FastAPI
    instrument_fastapi(app)
    logger.info("✅ FastAPI instrumentado com OpenTelemetry")


@app.get("/health", tags=["system"])
async def health_check_endpoint(db: Session = Depends(get_db)):
    """
    Verificação de saúde da aplicação com detalhes completos
    """
    try:
        # Verificar banco de dados
        try:
            db.execute(text("SELECT 1"))
            db_healthy = True
        except Exception:
            db_healthy = False

        # Informações básicas
        health_info = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": time.time(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": {
                "status": "connected" if db_healthy else "disconnected",
                "url": (
                    settings.DATABASE_URL.split("@")[-1]
                    if "@" in settings.DATABASE_URL
                    else "not_configured"
                ),
            },
            "services": {
                "api": "running",
                "database": "connected" if db_healthy else "disconnected",
            },
            "system": {
                "uptime": time.time(),  # Seria melhor ter o tempo real de uptime
                "memory_usage": "not_monitored",
                "cpu_usage": "not_monitored",
            },
        }

        # Verificar serviços opcionais
        try:
            from synapse.core.websockets.manager import ConnectionManager

            health_info["services"]["websockets"] = "available"
        except ImportError:
            health_info["services"]["websockets"] = "not_available"

        # Adicionar estatísticas de erro
        try:
            from synapse.middlewares.error_middleware import get_error_stats

            health_info["error_stats"] = get_error_stats()
        except ImportError:
            health_info["error_stats"] = "not_available"

        return health_info

    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e), "timestamp": time.time()},
        )


@app.get("/health/detailed", tags=["system"])
async def detailed_health_check(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Health check detalhado com estatísticas de banco e provedores"""
    try:
        # Testar conectividade básica ao banco
        db.execute(text("SELECT 1"))
        db_connected = True

        # Contar tabelas no schema informado (fallback para default)
        schema_name = getattr(settings, "DATABASE_SCHEMA", None) or "public"
        try:
            result = db.execute(
                text(
                    "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = :schema"
                ),
                {"schema": schema_name},
            )
            table_count = result.scalar() if result else 0
        except Exception as e:
            logger.warning(f"Não foi possível contar tabelas: {e}")
            table_count = 0

    except Exception as e:
        logger.error(f"Database detailed check failed: {e}")
        db_connected = False
        table_count = 0

    return {
        "status": "healthy" if db_connected else "degraded",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "database": {
            "connected": db_connected,
            "schema": schema_name,
            "tables": table_count,
        },
        "llm_providers": {
            "openai": bool(getattr(settings, "OPENAI_API_KEY", None)),
            "anthropic": bool(getattr(settings, "ANTHROPIC_API_KEY", None)),
            "google": bool(getattr(settings, "GOOGLE_API_KEY", None)),
            "groq": bool(getattr(settings, "GROQ_API_KEY", None)),
        },
        "features": {
            "file_upload": True,
            "websocket": True,
            "analytics": True,
        },
        "timestamp": time.time(),
    }


@app.get("/", tags=["system"])
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
            "user_variables": "✅ Configurações Personalizadas",
        },
        "contact": {"team": "SynapScale Team", "email": "support@synapscale.com"},
        "timestamp": time.time(),
    }


@app.get("/info", tags=["system"])
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
            "debug": settings.DEBUG,
        },
        "endpoints": {
            "health": "/health",
            "docs": docs_url,
            "redoc": redoc_url,
            "openapi": "/openapi.json",
        },
        "configuration": {
            "cors_origins": len(settings.BACKEND_CORS_ORIGINS),
            "max_upload_size": f"{settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f}MB",
            "allowed_extensions": settings.ALLOWED_FILE_EXTENSIONS,
            "database_type": (
                "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite"
            ),
            "cache_enabled": getattr(settings, "CACHE_ENABLED", False),
            "websockets_enabled": True,
        },
        "security": {
            "jwt_algorithm": settings.JWT_ALGORITHM,
            "access_token_expire": f"{settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "refresh_token_expire": f"{settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days",
            "cors_enabled": True,
            "rate_limiting": getattr(settings, "RATE_LIMIT_ENABLED", False),
        },
        "timestamp": time.time(),
    }


# Endpoints específicos para corrigir 404s
@app.post("/current-url", tags=["system"])
async def get_current_url(request: Request):
    """
    Retorna a URL atual da requisição
    """
    return {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "timestamp": time.time()
    }


@app.get("/.identity", tags=["system"])
async def get_identity():
    """
    Retorna informações de identidade do serviço
    """
    return {
        "service": "synapscale",
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
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
    # Forçar regeneração do schema (remover cache)
    app.openapi_schema = None

    # Debug: verificar se openapi_tags está correto
    print(f"DEBUG: openapi_tags tem {len(openapi_tags)} tags")
    for tag in openapi_tags:
        if "llm" in tag["name"]:
            print(f"DEBUG: Tag LLM encontrada: {tag}")

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=openapi_tags,
    )

    # Configurar esquemas de segurança para facilitar o uso na documentação
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "🔑 **Token JWT** - Obtenha um token através do endpoint /auth/login ou /auth/docs-login",
        },
        "HTTPBasic": {
            "type": "http",
            "scheme": "basic",
            "description": "🔐 **Login Direto** - Digite seu email no campo 'Username' e sua senha no campo 'Password'",
        },
    }

    # Configurar segurança global para aceitar AMBOS os esquemas
    # Isso permite que o usuário escolha qualquer um no modal de autorização
    openapi_schema["security"] = [{"HTTPBearer": []}, {"HTTPBasic": []}]

    # Garantir que todos os $ref de componentes apontem para #/components/schemas/<Model>
    # FastAPI normalmente já faz isso, mas caso algum caminho absoluto apareça, normalizamos.
    def _fix_refs(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if (
                    k == "$ref"
                    and isinstance(v, str)
                    and not v.startswith("#/components/")
                ):
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


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Endpoint personalizado para Swagger UI com design moderno e refinado
    """
    return HTMLResponse(
        content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <link type="text/css" rel="stylesheet" href="/static/unified-docs-styles.css?v=8.0">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <title>{settings.PROJECT_NAME} - API Documentation</title>
        <style>
            /* Design System - Cores e Variáveis */
            :root {{
                --primary-color: #3b82f6;
                --primary-hover: #2563eb;
                --secondary-color: #10b981;
                --background: #f8fafc;
                --card-background: #ffffff;
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --border-color: #e2e8f0;
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                --radius-md: 8px;
                --radius-lg: 12px;
                --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }}

            /* Base Styles */
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: var(--background);
                color: var(--text-primary);
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }}

            /* Swagger UI Container */
            .swagger-ui {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem;
            }}

            /* Info Section - Header */
            .swagger-ui .info {{
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 3rem 2rem;
                border-radius: var(--radius-lg);
                margin-bottom: 2rem;
                box-shadow: var(--shadow-lg);
            }}

            .swagger-ui .info .title {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}

            .swagger-ui .info .title small.version-stamp {{
                background: rgba(255,255,255,0.2);
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.9rem;
                margin-left: 1rem;
                backdrop-filter: blur(10px);
            }}

            .swagger-ui .info .markdown p {{
                font-size: 1.1rem;
                opacity: 0.95;
                max-width: 800px;
            }}

            /* Category Sections - Blocos Pais */
            .swagger-ui .opblock-tag-section {{
                background: var(--card-background);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                margin: 2rem 0;
                padding: 1.5rem;
                border: 1px solid var(--border-color);
                transition: var(--transition);
                position: relative;
                overflow: hidden;
            }}

            .swagger-ui .opblock-tag-section::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                border-radius: var(--radius-lg) var(--radius-lg) 0 0;
            }}

            .swagger-ui .opblock-tag-section:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }}

            /* Category Headers */
            .swagger-ui .opblock-tag {{
                background: transparent !important;
                border: none !important;
                padding: 1rem 0 !important;
                margin-bottom: 1rem !important;
                border-bottom: 1px solid var(--border-color) !important;
            }}

            .swagger-ui .opblock-tag h3 {{
                color: var(--text-primary) !important;
                font-size: 1.5rem !important;
                font-weight: 600 !important;
                margin: 0 !important;
                display: flex;
                align-items: center;
                gap: 1rem;
            }}

            /* Category Icons */
            .swagger-ui .opblock-tag[data-tag="system"] h3::before {{
                content: '🏠';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="auth"] h3::before {{
                content: '🔐';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #f97316, #fb923c);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="workspaces"] h3::before {{
                content: '🏢';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #10b981, #34d399);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="workflows"] h3::before {{
                content: '⚙️';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #3b82f6, #60a5fa);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="ai"] h3::before {{
                content: '🤖';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #ec4899, #f472b6);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="marketplace"] h3::before {{
                content: '🛒';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #8b5cf6, #a78bfa);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="analytics"] h3::before {{
                content: '📊';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #06b6d4, #22d3ee);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="data"] h3::before {{
                content: '📁';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #f59e0b, #fbbf24);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            .swagger-ui .opblock-tag[data-tag="admin"] h3::before {{
                content: '👑';
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #ef4444, #f87171);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: var(--shadow-sm);
            }}

            /* Endpoints dentro das categorias */
            .swagger-ui .opblock {{
                margin: 0.75rem 0;
                border-radius: var(--radius-md);
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow-sm);
                transition: var(--transition);
                overflow: hidden;
            }}

            .swagger-ui .opblock:hover {{
                transform: translateX(4px);
                box-shadow: var(--shadow-md);
            }}

            /* HTTP Method Colors */
            .swagger-ui .opblock.opblock-get {{
                border-left: 4px solid #3b82f6;
            }}

            .swagger-ui .opblock.opblock-post {{
                border-left: 4px solid #10b981;
            }}

            .swagger-ui .opblock.opblock-put {{
                border-left: 4px solid #f59e0b;
            }}

            .swagger-ui .opblock.opblock-delete {{
                border-left: 4px solid #ef4444;
            }}

            .swagger-ui .opblock.opblock-patch {{
                border-left: 4px solid #8b5cf6;
            }}

            /* Method Badges */
            .swagger-ui .opblock .opblock-summary-method {{
                border-radius: var(--radius-md);
                font-weight: 600;
                font-size: 0.875rem;
                min-width: 80px;
                text-align: center;
            }}

            /* Buttons */
            .swagger-ui .btn {{
                border-radius: var(--radius-md);
                font-weight: 500;
                transition: var(--transition);
                border: none;
                cursor: pointer;
            }}

            .swagger-ui .btn.execute {{
                background: var(--primary-color);
                color: white;
                padding: 0.5rem 1rem;
            }}

            .swagger-ui .btn.execute:hover {{
                background: var(--primary-hover);
                transform: translateY(-1px);
                box-shadow: var(--shadow-md);
            }}

            /* Authorization */
            .swagger-ui .auth-wrapper .authorize {{
                background: var(--primary-color);
                color: white;
                border: none;
                border-radius: var(--radius-md);
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: var(--transition);
            }}

            .swagger-ui .auth-wrapper .authorize:hover {{
                background: var(--primary-hover);
                transform: translateY(-1px);
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                .swagger-ui {{
                    padding: 1rem;
                }}

                .swagger-ui .info {{
                    padding: 2rem 1rem;
                }}

                .swagger-ui .info .title {{
                    font-size: 2rem;
                }}

                .swagger-ui .opblock-tag-section {{
                    padding: 1rem;
                }}

                .swagger-ui .opblock-tag h3 {{
                    font-size: 1.25rem !important;
                }}

                .swagger-ui .opblock-tag h3::before {{
                    width: 32px;
                    height: 32px;
                    font-size: 16px;
                }}
            }}

            /* Animations */
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}

            .swagger-ui .opblock-tag-section {{
                animation: fadeInUp 0.6s ease-out;
            }}

            /* Staggered animation for multiple sections */
            .swagger-ui .opblock-tag-section:nth-child(1) {{ animation-delay: 0.1s; }}
            .swagger-ui .opblock-tag-section:nth-child(2) {{ animation-delay: 0.2s; }}
            .swagger-ui .opblock-tag-section:nth-child(3) {{ animation-delay: 0.3s; }}
            .swagger-ui .opblock-tag-section:nth-child(4) {{ animation-delay: 0.4s; }}
            .swagger-ui .opblock-tag-section:nth-child(5) {{ animation-delay: 0.5s; }}
            .swagger-ui .opblock-tag-section:nth-child(6) {{ animation-delay: 0.6s; }}
            .swagger-ui .opblock-tag-section:nth-child(7) {{ animation-delay: 0.7s; }}
            .swagger-ui .opblock-tag-section:nth-child(8) {{ animation-delay: 0.8s; }}
            .swagger-ui .opblock-tag-section:nth-child(9) {{ animation-delay: 0.9s; }}

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {{
                :root {{
                    --background: #0f172a;
                    --card-background: #1e293b;
                    --text-primary: #f1f5f9;
                    --text-secondary: #94a3b8;
                    --border-color: #334155;
                }}
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            const ui = SwaggerUIBundle({{
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                layout: 'BaseLayout',
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                defaultModelsExpandDepth: -1,
                docExpansion: 'none',
                displayRequestDuration: true,
                tryItOutEnabled: true,
                persistAuthorization: true,
                oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                syntaxHighlight: {{
                    activate: true,
                    theme: 'agate'
                }},
                tagsSorter: 'alpha',
                operationsSorter: 'alpha'
            }});
        </script>
    </body>
    </html>
    """
    )


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
        date_header=False,
    )
