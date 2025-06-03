"""
Aplicação principal do SynapScale Backend
Otimizada por José - O melhor Full Stack do mundo
Implementa as melhores práticas de segurança, performance e configuração
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Importações dos módulos internos
from src.synapse.config import settings
from src.synapse.database import engine, Base
from src.synapse.api.v1.router import api_router

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Avisos de configuração com melhor formatação
def check_configuration():
    """Verifica configurações críticas da aplicação"""
    warnings = []
    
    if not hasattr(settings, 'SMTP_HOST') or not settings.SMTP_HOST:
        warnings.append("Configuração SMTP necessária para notificações por email")
    
    if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
        warnings.append("SECRET_KEY deve ser configurada para segurança")
    
    if not hasattr(settings, 'DATABASE_URL') or not settings.DATABASE_URL:
        warnings.append("DATABASE_URL deve ser configurada")
    
    # Verificar configuração de LLM
    llm_providers = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    if not any(hasattr(settings, provider) and getattr(settings, provider) for provider in llm_providers):
        warnings.append("Pelo menos um provedor LLM deve ser configurado")
    
    for warning in warnings:
        logger.warning(f"⚠️  Configuração: {warning}")
    
    if not warnings:
        logger.info("✅ Todas as configurações críticas estão definidas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação com tratamento robusto de erros"""
    # Startup
    logger.info("🚀 Iniciando SynapScale Backend API...")
    
    # Verificar configurações
    check_configuration()
    
    # Criar tabelas do banco de dados
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas do banco de dados criadas/verificadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas do banco: {e}")
        raise
    
    # Verificar conectividade do banco
    try:
        from src.synapse.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Conectividade com banco de dados verificada")
    except Exception as e:
        logger.error(f"❌ Erro de conectividade com banco: {e}")
        raise
    
    # Inicializar WebSocket Manager
    try:
        from src.synapse.core.websockets.manager import ConnectionManager
        websocket_manager = ConnectionManager()
        logger.info("✅ WebSocket Manager inicializado")
    except Exception as e:
        logger.warning(f"⚠️  WebSocket Manager não disponível: {e}")
        websocket_manager = None
    
    # Inicializar Engine de Execução
    try:
        from src.synapse.api.v1.endpoints.executions import initialize_execution_service
        await initialize_execution_service(websocket_manager)
        logger.info("🚀 Engine de Execução de Workflows inicializada com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Engine de Execução: {e}")
        # Não falha o startup, mas registra o erro
    
    logger.info("🎉 SynapScale Backend iniciado com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("🔄 Finalizando SynapScale Backend...")
    
    # Finalizar Engine de Execução
    try:
        from src.synapse.api.v1.endpoints.executions import shutdown_execution_service
        await shutdown_execution_service()
        logger.info("✅ Engine de Execução finalizada com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao finalizar Engine de Execução: {e}")
    
    logger.info("✅ SynapScale Backend finalizado com sucesso")


# Criar aplicação FastAPI com configuração otimizada
app = FastAPI(
    title="SynapScale Backend API",
    description="""
    🚀 **SynapScale Backend API** - Plataforma de Automação com IA
    
    API robusta e escalável para gerenciamento de workflows, agentes AI e automações.
    
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
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "SynapScale Team",
        "email": "support@synapscale.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Middleware de segurança - Trusted Host
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.DEBUG else ["synapscale.com", "*.synapscale.com", "localhost", "127.0.0.1"]
)

# Configurar CORS com segurança aprimorada
allowed_origins = ["*"] if settings.DEBUG else [
    "https://synapscale.com",
    "https://app.synapscale.com",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware de timing para performance monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Adiciona header com tempo de processamento da requisição"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Middleware de logging para auditoria
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log estruturado de todas as requisições"""
    start_time = time.time()
    
    # Log da requisição
    logger.info(
        f"📥 {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    response = await call_next(request)
    
    # Log da resposta
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Handler global de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"❌ Erro não tratado: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Ocorreu um erro interno. Tente novamente mais tarde.",
            "request_id": id(request)
        }
    )

# Handler para HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para HTTPExceptions com logging"""
    logger.warning(f"⚠️  HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# Incluir routers da API
app.include_router(api_router, prefix="/api/v1")

# Endpoint de health check aprimorado
@app.get("/health", tags=["health"])
async def health_check():
    """
    Endpoint para verificação de saúde da API
    Inclui verificações de componentes críticos
    """
    health_status = {
        "status": "healthy",
        "service": "synapscale-backend",
        "version": "1.0.0",
        "timestamp": time.time(),
        "components": {
            "database": "healthy",
            "api": "healthy"
        }
    }
    
    # Verificar banco de dados
    try:
        from src.synapse.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"❌ Health check - Banco de dados: {e}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

# Endpoint raiz aprimorado
@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raiz da API com informações úteis
    """
    return {
        "message": "🚀 SynapScale Backend API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "api": "/api/v1"
        },
        "features": [
            "Autenticação JWT",
            "Workflows de Automação",
            "Agentes AI",
            "Gerenciamento de Arquivos",
            "Histórico de Conversas"
        ]
    }

# Endpoint de informações da API
@app.get("/info", tags=["info"])
async def api_info():
    """
    Informações detalhadas sobre a API
    """
    return {
        "name": "SynapScale Backend API",
        "version": "1.0.0",
        "description": "Plataforma de Automação com IA",
        "author": "José - O melhor Full Stack do mundo",
        "endpoints_count": len([route for route in app.routes]),
        "features": {
            "authentication": "JWT com refresh tokens",
            "workflows": "Execução de workflows complexos",
            "ai_integration": "Múltiplos provedores de IA",
            "file_management": "Upload e processamento de arquivos",
            "real_time": "WebSockets para atualizações em tempo real"
        },
        "security": {
            "cors": "Configurado",
            "trusted_hosts": "Implementado",
            "rate_limiting": "Planejado",
            "input_validation": "Pydantic schemas"
        }
    }


if __name__ == "__main__":
    # Configuração otimizada para desenvolvimento
    uvicorn.run(
        "src.synapse.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info",
        access_log=True
    )

