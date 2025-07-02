"""
Middleware de Multi-Tenancy
Detecta e configura o tenant atual baseado no usuário autenticado
"""

from typing import Optional
from uuid import UUID
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from synapse.core.auth.jwt import decode_token
from synapse.services.tenant_service import TenantService
from synapse.database import get_db


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware para detectar e configurar tenant automaticamente
    """

    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
        ]

    async def dispatch(self, request: Request, call_next):
        # Pular middleware para rotas excluídas
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Tentar extrair tenant_id do usuário autenticado
        tenant_id = await self._extract_tenant_from_user(request)

        if tenant_id:
            # Adicionar tenant_id ao estado da requisição
            request.state.tenant_id = tenant_id

            # Configurar tenant no serviço
            db = next(get_db())
            try:
                tenant_service = TenantService(db)
                tenant_service.set_current_tenant(tenant_id)
                request.state.tenant_service = tenant_service
            finally:
                db.close()

        response = await call_next(request)
        return response

    async def _extract_tenant_from_user(self, request: Request) -> Optional[UUID]:
        """
        Extrai tenant_id do usuário autenticado
        """
        try:
            # Extrair token do header Authorization
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None

            token = authorization.split(" ")[1]

            # Decodificar token para obter user_id
            payload = decode_token(token)
            if not payload:
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            # Buscar tenant do usuário
            db = next(get_db())
            try:
                tenant_service = TenantService(db)
                tenant = tenant_service.get_user_tenant(UUID(user_id))
                return tenant.id if tenant else None
            finally:
                db.close()

        except Exception:
            # Em caso de erro, continuar sem tenant
            return None


def get_current_tenant_id(request: Request) -> Optional[UUID]:
    """
    Função helper para obter tenant_id da requisição
    """
    return getattr(request.state, "tenant_id", None)


def get_tenant_service(request: Request) -> Optional[TenantService]:
    """
    Função helper para obter TenantService da requisição
    """
    return getattr(request.state, "tenant_service", None)


def require_tenant(request: Request) -> UUID:
    """
    Função helper que garante que existe um tenant na requisição
    """
    tenant_id = get_current_tenant_id(request)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context is required for this operation",
        )
    return tenant_id
