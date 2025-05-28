"""
Testes de integração para os endpoints de arquivos.

Este módulo contém testes de integração para os endpoints de arquivos,
garantindo que as rotas, autenticação e fluxos completos funcionem corretamente.
"""

import pytest
import io
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.main import app
from synapse.services.file_service import FileService
from synapse.models.file import File
from synapse.core.auth.jwt import create_access_token


@pytest.fixture
def test_client():
    """Fixture para cliente de teste."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock para sessão de banco de dados."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    
    # Patch para o get_db dependency
    with patch("synapse.api.deps.get_db", return_value=session):
        yield session


@pytest.fixture
def auth_headers():
    """Fixture para headers de autenticação."""
    # Criar token de acesso para usuário de teste
    token = create_access_token(
        data={
            "sub": "test_user",
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_file_service():
    """Mock para o serviço de arquivos."""
    with patch("synapse.api.v1.endpoints.files.routes.FileService") as mock_service_class:
        mock_service = MagicMock(spec=FileService)
        mock_service_class.return_value = mock_service
        yield mock_service


@pytest.fixture
def mock_file_model():
    """Mock para modelo de arquivo."""
    file = MagicMock(spec=File)
    file.id = "123e4567-e89b-12d3-a456-426614174000"
    file.filename = "test_document.pdf"
    file.content_type = "application/pdf"
    file.size = 100
    file.path = "/storage/pdf/test_document.pdf"
    file.category = "pdf"
    file.created_at = "2025-01-01T12:00:00"
    file.updated_at = "2025-01-01T12:00:00"
    file.user_id = "test_user"
    
    # Converter para dict para serialização
    file.dict = MagicMock(return_value={
        "id": file.id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "path": file.path,
        "category": file.category,
        "created_at": file.created_at,
        "updated_at": file.updated_at,
        "user_id": file.user_id
    })
    
    return file


def test_upload_file(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de upload de arquivo."""
    # Configurar mock para o serviço
    mock_file_service.create_file = AsyncMock(return_value=mock_file_model)
    
    # Criar arquivo de teste
    test_file = io.BytesIO(b"test file content")
    
    # Fazer requisição
    response = test_client.post(
        "/api/v1/files/upload",
        files={"file": ("test_document.pdf", test_file, "application/pdf")},
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_document.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size"] == 100
    assert data["category"] == "pdf"
    
    # Verificar chamada ao serviço
    mock_file_service.create_file.assert_called_once()


def test_upload_file_unauthorized(test_client, mock_db_session):
    """Testa o endpoint de upload de arquivo sem autenticação."""
    # Criar arquivo de teste
    test_file = io.BytesIO(b"test file content")
    
    # Fazer requisição sem token
    response = test_client.post(
        "/api/v1/files/upload",
        files={"file": ("test_document.pdf", test_file, "application/pdf")}
    )
    
    # Verificar resposta
    assert response.status_code == 401


def test_get_file_by_id(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de recuperação de arquivo por ID."""
    # Configurar mock para o serviço
    mock_file_service.get_file_by_id = AsyncMock(return_value=mock_file_model)
    
    # Fazer requisição
    response = test_client.get(
        f"/api/v1/files/{mock_file_model.id}",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_file_model.id
    assert data["filename"] == mock_file_model.filename
    
    # Verificar chamada ao serviço
    mock_file_service.get_file_by_id.assert_called_once_with(
        file_id=mock_file_model.id
    )


def test_get_file_by_id_not_found(test_client, mock_db_session, auth_headers, mock_file_service):
    """Testa o endpoint de recuperação de arquivo inexistente."""
    # Configurar mock para o serviço
    mock_file_service.get_file_by_id = AsyncMock(side_effect=HTTPException(status_code=404, detail="File not found"))
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/files/nonexistent-id",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_download_file(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de download de arquivo."""
    # Configurar mock para o serviço
    mock_file_service.get_file_by_id = AsyncMock(return_value=mock_file_model)
    
    # Configurar mock para o método open
    mock_file_content = io.BytesIO(b"test file content")
    with patch("builtins.open", return_value=mock_file_content):
        # Fazer requisição
        response = test_client.get(
            f"/api/v1/files/{mock_file_model.id}/download",
            headers=auth_headers
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.headers["content-type"] == mock_file_model.content_type
        assert response.headers["content-disposition"] == f'attachment; filename="{mock_file_model.filename}"'
        
        # Verificar chamada ao serviço
        mock_file_service.get_file_by_id.assert_called_once_with(
            file_id=mock_file_model.id
        )


def test_list_files(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de listagem de arquivos."""
    # Configurar mock para o serviço
    mock_file_service.get_files = AsyncMock(return_value=([mock_file_model], 1))
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/files/",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == mock_file_model.id
    assert data["total"] == 1
    
    # Verificar chamada ao serviço
    mock_file_service.get_files.assert_called_once()
    args, kwargs = mock_file_service.get_files.call_args
    assert kwargs["skip"] == 0
    assert kwargs["limit"] == 100
    assert kwargs["user_id"] == "test_user"
    assert kwargs["category"] is None


def test_list_files_with_pagination(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de listagem de arquivos com paginação."""
    # Configurar mock para o serviço
    mock_file_service.get_files = AsyncMock(return_value=([mock_file_model], 10))
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/files/?skip=5&limit=10",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["total"] == 10
    
    # Verificar chamada ao serviço
    mock_file_service.get_files.assert_called_once()
    args, kwargs = mock_file_service.get_files.call_args
    assert kwargs["skip"] == 5
    assert kwargs["limit"] == 10


def test_list_files_with_category(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de listagem de arquivos com filtro de categoria."""
    # Configurar mock para o serviço
    mock_file_service.get_files = AsyncMock(return_value=([mock_file_model], 1))
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/files/?category=pdf",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    
    # Verificar chamada ao serviço
    mock_file_service.get_files.assert_called_once()
    args, kwargs = mock_file_service.get_files.call_args
    assert kwargs["category"] == "pdf"


def test_update_file(test_client, mock_db_session, auth_headers, mock_file_service, mock_file_model):
    """Testa o endpoint de atualização de arquivo."""
    # Configurar mock para o serviço
    mock_file_service.update_file = AsyncMock(return_value=mock_file_model)
    
    # Dados da requisição
    request_data = {
        "filename": "updated_document.pdf"
    }
    
    # Fazer requisição
    response = test_client.put(
        f"/api/v1/files/{mock_file_model.id}",
        json=request_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_file_model.id
    
    # Verificar chamada ao serviço
    mock_file_service.update_file.assert_called_once_with(
        file_id=mock_file_model.id,
        filename=request_data["filename"],
        user_id="test_user"
    )


def test_delete_file(test_client, mock_db_session, auth_headers, mock_file_service):
    """Testa o endpoint de exclusão de arquivo."""
    # Configurar mock para o serviço
    mock_file_service.delete_file = AsyncMock(return_value=True)
    
    # Fazer requisição
    response = test_client.delete(
        "/api/v1/files/123e4567-e89b-12d3-a456-426614174000",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Verificar chamada ao serviço
    mock_file_service.delete_file.assert_called_once_with(
        file_id="123e4567-e89b-12d3-a456-426614174000",
        user_id="test_user"
    )


def test_error_handling(test_client, mock_db_session, auth_headers, mock_file_service):
    """Testa o tratamento de erros nos endpoints."""
    # Configurar mock para o serviço
    mock_file_service.get_file_by_id = AsyncMock(side_effect=Exception("Erro no serviço"))
    
    # Fazer requisição
    response = test_client.get(
        "/api/v1/files/123e4567-e89b-12d3-a456-426614174000",
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Erro no serviço" in data["detail"]
