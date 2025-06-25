from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
import logging

from synapse.api.v1.api import api_router
from synapse.core.config_new import settings
from synapse.middlewares.metrics import MetricsMiddleware
from synapse.middlewares.rate_limiting import RateLimiterMiddleware
from synapse.middlewares.error_middleware import ErrorInterceptionMiddleware
from synapse.middlewares.logging import request_logging_middleware
from synapse.database import engine, Base

# Configurar logging
logger = logging.getLogger("synapse.app")

# Criar a aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middlewares
app.add_middleware(ErrorInterceptionMiddleware)
app.middleware("http")(request_logging_middleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Incluir o router principal da API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Tratamento de erros de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Endpoint raiz
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API SynapScale",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }

# Inicialização do banco de dados
@app.on_event("startup")
async def startup():
    # Criar tabelas no banco de dados
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Integrar Memory Bank se estiver habilitado
    if os.getenv("ENABLE_MEMORY_BANK", "").lower() == "true":
        try:
            from synapse.api.v1.memory_bank_integration import setup_memory_bank
            
            logger.info("Configurando integração com Memory Bank...")
            success = setup_memory_bank(app)
            
            if success:
                logger.info("Memory Bank integrado com sucesso!")
            else:
                logger.warning("Falha ao integrar Memory Bank. Continuando sem Memory Bank.")
                
        except ImportError:
            logger.warning("Módulo Memory Bank não encontrado. Continuando sem Memory Bank.")
        except Exception as e:
            logger.error(f"Erro ao configurar Memory Bank: {e}")
