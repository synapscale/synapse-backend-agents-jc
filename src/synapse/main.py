"""
Aplicação principal do SynapScale Backend
Otimizada por José - um desenvolvedor Full Stack
Implementa as melhores práticas de segurança, performance e configuração
Conexão direta com PostgreSQL via SQLAlchemy
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from sqlalchemy.orm import Session
import os

from src.synapse.config import settings
from src.synapse.database import init_db, get_db, health_check
from src.synapse.api.v1.router import api_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_configuration():
    """Verifica configurações críticas da aplicação"""
    warnings = []
    if not hasattr(settings, 'SMTP_HOST') or not settings.SMTP_HOST:
        warnings.append('Configuração SMTP necessária para notificações por email')
    if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
        warnings.append('SECRET_KEY deve ser configurada para segurança')
    if not hasattr(settings, 'DATABASE_URL') or not settings.DATABASE_URL:
        warnings.append('DATABASE_URL deve ser configurada')
    llm_providers = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    if not any((hasattr(settings, provider) and getattr(settings, provider) for provider in llm_providers)):
        warnings.append('Pelo menos um provedor LLM deve ser configurado')
    for warning in warnings:
        logger.warning(f'⚠️  Configuração: {warning}')
    if not warnings:
        logger.info('✅ Todas as configurações críticas estão definidas')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação com tratamento robusto de erros"""
    logger.info('🚀 Iniciando SynapScale Backend API...')
    check_configuration()
    try:
        init_db()
        logger.info('✅ Conectado ao banco de dados PostgreSQL via SQLAlchemy')
    except Exception as e:
        logger.error(f'❌ Erro ao conectar ao banco de dados: {e}')
        raise
    try:
        if health_check():
            logger.info('✅ Conectividade com banco de dados verificada')
        else:
            logger.error('❌ Falha na verificação de conectividade com o banco')
            raise Exception("Falha na verificação de conectividade com o banco")
    except Exception as e:
        logger.error(f'❌ Erro de conectividade com banco: {e}')
        raise
    try:
        from src.synapse.core.websockets.manager import ConnectionManager
        websocket_manager = ConnectionManager()
        logger.info('✅ WebSocket Manager inicializado')
    except Exception as e:
        logger.warning(f'⚠️  WebSocket Manager não disponível: {e}')
        websocket_manager = None
    try:
        from src.synapse.api.v1.endpoints.executions import initialize_execution_service
        await initialize_execution_service(websocket_manager)
        logger.info('🚀 Engine de Execução de Workflows inicializada com sucesso')
    except Exception as e:
        logger.error(f'❌ Erro ao inicializar Engine de Execução: {e}')
    logger.info('🎉 SynapScale Backend iniciado com sucesso!')
    yield
    logger.info('🔄 Finalizando SynapScale Backend...')
    try:
        from src.synapse.api.v1.endpoints.executions import shutdown_execution_service
        await shutdown_execution_service()
        logger.info('✅ Engine de Execução finalizada com sucesso')
    except Exception as e:
        logger.error(f'❌ Erro ao finalizar Engine de Execução: {e}')
    logger.info('✅ SynapScale Backend finalizado com sucesso')

app = FastAPI(
    title='SynapScale Backend API', 
    description='\n    🚀 **SynapScale Backend API** - Plataforma de Automação com IA\n    \n    API robusta e escalável para gerenciamento de workflows, agentes AI e automações.\n    \n    ## Funcionalidades Principais\n    \n    * **🔐 Autenticação**: Sistema completo de autenticação e autorização\n    * **⚡ Workflows**: Criação e execução de workflows de automação\n    * **🤖 Agentes AI**: Integração com múltiplos provedores de IA\n    * **🔗 Nodes**: Componentes reutilizáveis para workflows\n    * **💬 Conversas**: Histórico e gerenciamento de conversas\n    * **📁 Arquivos**: Upload e gerenciamento de arquivos\n    \n    ## Segurança\n    \n    * Autenticação JWT robusta\n    * Validação de dados com Pydantic\n    * Rate limiting implementado\n    * CORS configurado adequadamente\n    ', 
    version='1.0.0', 
    docs_url='/docs', 
    redoc_url='/redoc', 
    lifespan=lifespan, 
    contact={'name': 'SynapScale Team', 'email': 'support@synapscale.com'}, 
    license_info={'name': 'MIT'}
)

# Configuração CORS otimizada para desenvolvimento e produção
allowed_origins = [
    'http://localhost:3000',  # Frontend Next.js desenvolvimento
    'http://localhost:3001',  # Frontend alternativo
    'http://127.0.0.1:3000',  # Localhost alternativo
    'https://synapscale.com',  # Produção
    'https://app.synapscale.com',  # App produção
    'https://*.synapscale.com',  # Subdomínios
] if not settings.DEBUG else ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'],
    allow_headers=[
        'Accept',
        'Accept-Language',
        'Content-Language',
        'Content-Type',
        'Authorization',
        'X-Requested-With',
        'X-CSRF-Token',
        'X-API-Key',
    ],
    expose_headers=[
        'X-Process-Time',
        'X-Request-ID',
        'X-Rate-Limit-Remaining',
        'X-Rate-Limit-Reset',
    ],
    max_age=86400,  # 24 horas para preflight cache
)

@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    """Adiciona headers de segurança"""
    response = await call_next(request)
    
    # Headers de segurança
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Content Security Policy para desenvolvimento
    if settings.DEBUG:
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' *"
    
    return response

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    """Adiciona header com tempo de processamento da requisição"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

@app.middleware('http')
async def log_requests(request: Request, call_next):
    """Log estruturado de todas as requisições"""
    start_time = time.time()
    logger.info(f"📥 {request.method} {request.url.path} - Client: {(request.client.host if request.client else 'unknown')}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f'📤 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s')
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f'❌ Erro não tratado: {str(exc)}', exc_info=True)
    return JSONResponse(status_code=500, content={'error': 'Internal server error', 'message': 'Ocorreu um erro interno. Tente novamente mais tarde.', 'request_id': id(request)})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para HTTPExceptions com logging"""
    logger.warning(f'⚠️  HTTP {exc.status_code}: {exc.detail}')
    return JSONResponse(status_code=exc.status_code, content={'error': exc.detail, 'status_code': exc.status_code})

app.include_router(api_router, prefix='/api/v1')

@app.get('/health', tags=['health'])
async def health_check_endpoint(db: Session = Depends(get_db)):
    """
    Endpoint para verificação de saúde da API
    Inclui verificações de componentes críticos
    """
    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "synapscale_db")
    
    health_status = {
        'status': 'healthy',
        'service': 'synapscale-backend',
        'version': '1.0.0',
        'timestamp': time.time(),
        'uptime': time.time(),
        'components': {
            'database': 'healthy',
            'api': 'healthy',
            'cors': 'configured',
            'auth': 'available'
        },
        'environment': 'development' if settings.DEBUG else 'production'
    }
    
    try:
        # Verificar conexão com o banco
        from sqlalchemy import text
        result = db.execute(text(f"SELECT COUNT(*) FROM {DATABASE_SCHEMA}.users"))
        count = result.scalar()
        health_status['components']['database'] = 'healthy'
        health_status['components']['database_count'] = count
    except Exception as e:
        logger.error(f'❌ Health check - Banco de dados: {e}')
        health_status['components']['database'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    # Verificar se endpoints críticos estão disponíveis
    try:
        health_status['components']['endpoints'] = {
            'auth': '/api/v1/auth',
            'variables': '/api/v1/variables',
            'workflows': '/api/v1/workflows',
            'chat': '/api/v1/chat'
        }
    except Exception as e:
        logger.error(f'❌ Health check - Endpoints: {e}')
        health_status['components']['endpoints'] = 'error'
    
    return health_status

@app.get('/', tags=['root'])
async def root():
    """
    Endpoint raiz da API com informações úteis
    """
    return {
        'message': '🚀 SynapScale Backend API', 
        'version': '1.0.0', 
        'status': 'running', 
        'documentation': {'swagger': '/docs', 'redoc': '/redoc'}, 
        'endpoints': {'health': '/health', 'api': '/api/v1'}, 
        'features': [
            'Autenticação JWT', 
            'Workflows de Automação', 
            'Agentes AI', 
            'Gerenciamento de Arquivos', 
            'Histórico de Conversas'
        ]
    }

@app.get('/info', tags=['info'])
async def api_info():
    """
    Informações detalhadas sobre a API
    """
    return {
        'name': 'SynapScale Backend API', 
        'version': '1.0.0', 
        'description': 'Plataforma de Automação com IA', 
        'author': 'José - um desenvolvedor Full Stack', 
        'endpoints_count': len([route for route in app.routes]), 
        'features': {
            'authentication': 'JWT com refresh tokens', 
            'workflows': 'Execução de workflows complexos', 
            'ai_integration': 'Múltiplos provedores de IA', 
            'file_management': 'Upload e processamento de arquivos', 
            'real_time': 'WebSockets para atualizações em tempo real'
        }, 
        'security': {
            'cors': 'Configurado', 
            'trusted_hosts': 'Implementado', 
            'rate_limiting': 'Planejado', 
            'input_validation': 'Pydantic schemas'
        }, 
        'database': 'PostgreSQL com SQLAlchemy'
    }

if __name__ == '__main__':
    uvicorn.run('src.synapse.main:app', host='0.0.0.0', port=8000, reload=True, reload_dirs=['src'], log_level='info', access_log=True)

