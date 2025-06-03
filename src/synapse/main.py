"""
Aplicação principal do SynapScale Backend
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importações dos módulos internos
from src.synapse.config import settings
from src.synapse.database import engine, Base
from src.synapse.api.v1.router import api_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Avisos de configuração
if not hasattr(settings, 'SMTP_HOST') or not settings.SMTP_HOST:
    logger.warning("Aviso: Erros de configuração: Configuração SMTP necessária para notificações por email")

logger.warning("Aviso: Erros de configuração: Pelo menos um provedor LLM deve ser configurado")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação SynapScale...")
    
    # Criar tabelas do banco de dados
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados criadas/verificadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas do banco: {e}")
    
    yield
    
    # Shutdown
    logger.info("Finalizando aplicação SynapScale...")


# Criar aplicação FastAPI
app = FastAPI(
    title="SynapScale Backend API",
    description="API Backend para o SynapScale - Plataforma de Agentes AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers da API
app.include_router(api_router, prefix="/api/v1")

# Endpoint de health check
@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return {
        "status": "healthy",
        "service": "synapscale-backend",
        "version": "1.0.0"
    }

# Endpoint raiz
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "SynapScale Backend API",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.synapse.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
