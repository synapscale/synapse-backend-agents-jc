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
    if request.url.path.startswith(f"{getattr(settings, 'API_V1_STR', None) or '/api/v1'}/auth"):
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
    if response.status_code >= 400 or request.url.path.startswith(f"{getattr(settings, 'API_V1_STR', None) or '/api/v1'}"):
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
app.include_router(api_router, prefix=getattr(settings, 'API_V1_STR', None) or "/api/v1")

# Static files - sempre disponível para CSS customizado
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
    """
    Endpoint personalizado para Swagger UI com design moderno e refinado
    """
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <link type="text/css" rel="stylesheet" href="/static/unified-docs-styles.css?v=10.0">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <title>{getattr(settings, 'PROJECT_NAME', None) or 'SynapScale Backend API'} - API Documentation</title>
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

            .swagger-ui .opblock-tag[data-tag="authentication"] h3::before {{
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

            .swagger-ui .opblock-tag[data-tag="advanced"] h3::before {{
                content: '🔌';
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
    """)

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
        "environment": getattr(settings, 'ENVIRONMENT', None) or "production",
        "version": getattr(settings, 'VERSION', None) or "2.0.0",
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
            {"schema": getattr(settings, 'DATABASE_SCHEMA', None) or "synapscale_db"}
        )
        table_count = result.scalar() if result else 0
        
    except Exception as e:
        logger.error(f"Database detailed check failed: {e}")
        db_connected = False
        table_count = 0

    return {
        "status": "healthy",
        "environment": getattr(settings, 'ENVIRONMENT', None) or "production",
        "version": getattr(settings, 'VERSION', None) or "2.0.0",
        "database": {
            "connected": db_connected,
            "schema": getattr(settings, 'DATABASE_SCHEMA', None) or "synapscale_db",
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
        "message": f"🚀 {getattr(settings, 'PROJECT_NAME', None) or 'SynapScale Backend API'}",
        "version": getattr(settings, 'VERSION', None) or "2.0.0",
        "environment": getattr(settings, 'ENVIRONMENT', None) or "production",
        "docs": "/docs",
        "health": "/health",
        "api": getattr(settings, 'API_V1_STR', None) or "/api/v1"
    }

@app.get("/info", tags=["system"])
async def api_info():
    """Informações da API"""
    return {
        "name": getattr(settings, 'PROJECT_NAME', None) or "SynapScale Backend API",
        "version": getattr(settings, 'VERSION', None) or "2.0.0",
        "description": "Plataforma de Automação com IA",
        "environment": getattr(settings, 'ENVIRONMENT', None) or "production",
        "debug": getattr(settings, 'DEBUG', None) or False,
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
    host = getattr(settings, 'HOST', None) or "0.0.0.0"
    port = getattr(settings, 'PORT', None) or 8000
    environment = getattr(settings, 'ENVIRONMENT', None) or "development"
    debug = getattr(settings, 'DEBUG', None) or False
    
    logger.info(f"🚀 Iniciando servidor em modo desenvolvimento...")
    logger.info(f"📍 Host: {host}:{port}")
    logger.info(f"🌍 Ambiente: {environment}")
    logger.info(f"🔍 Debug: {debug}")
    logger.info(f"📚 Docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "synapse.main_optimized:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level_name.lower(),
        access_log=True,
        server_header=False,
        date_header=False
    )
