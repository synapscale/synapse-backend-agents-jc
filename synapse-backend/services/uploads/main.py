"""Aplicação principal do serviço de uploads."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .routes.uploads import router as uploads_router


class HealthResponse(BaseModel):
    """Modelo de resposta para verificação de saúde."""

    status: str
    service: str
    version: str


class StorageUsageResponse(BaseModel):
    """Modelo de resposta para uso de armazenamento."""

    used_space: int
    total_space: int
    usage_percentage: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    print("🚀 Iniciando serviço de uploads...")

    # Criar diretórios necessários
    storage_dirs = [
        "storage/image",
        "storage/video",
        "storage/audio",
        "storage/document",
        "storage/archive",
        "storage/metadata",
    ]
    for directory in storage_dirs:
        os.makedirs(directory, exist_ok=True)

    print("✅ Serviço de uploads iniciado com sucesso!")

    yield

    # Shutdown
    print("🛑 Encerrando serviço de uploads...")


# Configuração da aplicação
app = FastAPI(
    title="SynapScale Upload Service",
    description=(
        "Serviço especializado para upload, processamento e "
        "gerenciamento de arquivos"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(uploads_router, prefix="/api/v1", tags=["uploads"])


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificação de saúde do serviço."""
    return HealthResponse(status="healthy", service="uploads", version="1.0.0")


@app.get("/storage/usage", response_model=StorageUsageResponse)
async def get_storage_usage():
    """Retorna informações sobre o uso do armazenamento."""
    # Implementação simplificada
    return StorageUsageResponse(
        used_space=0, total_space=1000000000, usage_percentage=0.0  # 1GB
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
