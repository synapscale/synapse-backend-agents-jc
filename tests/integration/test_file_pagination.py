import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from synapse.api.v1.router import api_router
from synapse.db.base import get_db
from synapse.middlewares.rate_limiting import rate_limit

# Teste adicional para endpoints de arquivos
@pytest.mark.asyncio
async def test_list_files_pagination():
    """Testa a paginação na listagem de arquivos."""
    # Configuração da aplicação
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    
    # Mock para o banco de dados
    async def override_get_db():
        mock_db = AsyncMock(spec=AsyncSession)
        try:
            yield mock_db
        finally:
            pass
    
    # Mock para o rate limiting
    async def override_rate_limit():
        return None
    
    # Substituir dependências
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[rate_limit] = override_rate_limit
    
    # Configurar cliente de teste
    client = TestClient(app)
    
    # Mock para o serviço de arquivos
    with patch('synapse.services.file_service.FileService.list_user_files') as mock_list:
        # Configurar o retorno do mock
        mock_list.return_value = {
            "items": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "filename": "test.pdf",
                    "original_filename": "original.pdf",
                    "content_type": "application/pdf",
                    "file_size": 12345,
                    "created_at": "2025-05-27T14:30:00Z"
                }
            ],
            "total": 1,
            "page": 2,
            "size": 10,
            "pages": 1
        }
        
        # Executar o teste com parâmetros de paginação
        response = client.get(
            "/api/v1/files/?page=2&size=10",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 10
        assert len(data["items"]) == 1
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_list.assert_called_once()
        args, kwargs = mock_list.call_args
        assert kwargs.get("page") == 2
        assert kwargs.get("size") == 10

@pytest.mark.asyncio
async def test_upload_file_invalid_category():
    """Testa o upload de arquivo com categoria inválida."""
    # Configuração da aplicação
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    
    # Mock para o banco de dados e rate limiting
    async def override_get_db():
        mock_db = AsyncMock(spec=AsyncSession)
        try:
            yield mock_db
        finally:
            pass
    
    async def override_rate_limit():
        return None
    
    # Substituir dependências
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[rate_limit] = override_rate_limit
    
    # Configurar cliente de teste
    client = TestClient(app)
    
    # Executar o teste com categoria inválida
    with open("tests/conftest.py", "rb") as test_file:
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"category": "invalid_category"},
            headers={"Authorization": "Bearer test_token"}
        )
    
    # Verificações
    assert response.status_code == 400
    data = response.json()
    assert "Categoria inválida" in data["detail"]
