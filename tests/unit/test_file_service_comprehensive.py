"""
Testes unitários para o serviço de arquivos.

Este módulo contém testes unitários para o serviço de arquivos,
garantindo que o upload, download, listagem e exclusão funcionem corretamente.
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from fastapi import UploadFile, HTTPException
import io

from synapse.services.file_service import FileService
from synapse.models.file import File
from synapse.core.security.file_validation import validate_file_extension, validate_file_size
from synapse.config import settings


@pytest.fixture
def mock_db_session():
    """Mock para sessão de banco de dados."""
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def file_service(mock_db_session):
    """Fixture para o serviço de arquivos."""
    return FileService(mock_db_session)


@pytest.fixture
def mock_upload_file():
    """Mock para arquivo de upload."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test_document.pdf"
    file.content_type = "application/pdf"
    file.file = io.BytesIO(b"test file content")
    file.size = 100
    return file


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
    file.created_at = datetime.utcnow()
    file.updated_at = datetime.utcnow()
    file.user_id = "user123"
    return file


@pytest.mark.asyncio
async def test_create_file(file_service, mock_upload_file, mock_db_session):
    """Testa a criação de arquivo."""
    # Configurar mocks
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    # Configurar mock para o método privado _save_file
    with patch.object(file_service, "_save_file", return_value="/storage/pdf/test_document.pdf"):
        # Chamar o método
        result = await file_service.create_file(
            file=mock_upload_file,
            user_id="user123"
        )
        
        # Verificar resultado
        assert result.filename == "test_document.pdf"
        assert result.content_type == "application/pdf"
        assert result.size == 100
        assert result.path == "/storage/pdf/test_document.pdf"
        assert result.category == "pdf"
        assert result.user_id == "user123"
        
        # Verificar chamadas ao banco de dados
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_file_duplicate_name(file_service, mock_upload_file, mock_db_session):
    """Testa a criação de arquivo com nome duplicado."""
    # Configurar mock para simular arquivo existente
    existing_file = MagicMock(spec=File)
    existing_file.filename = "test_document.pdf"
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing_file
    
    # Configurar mock para o método privado _save_file
    with patch.object(file_service, "_save_file", return_value="/storage/pdf/test_document_1.pdf"):
        # Chamar o método
        result = await file_service.create_file(
            file=mock_upload_file,
            user_id="user123"
        )
        
        # Verificar que o nome foi modificado
        assert result.filename == "test_document_1.pdf"


@pytest.mark.asyncio
async def test_get_file_by_id(file_service, mock_file_model, mock_db_session):
    """Testa a recuperação de arquivo por ID."""
    # Configurar mock para simular arquivo existente
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_file_model
    
    # Chamar o método
    result = await file_service.get_file_by_id(
        file_id="123e4567-e89b-12d3-a456-426614174000"
    )
    
    # Verificar resultado
    assert result == mock_file_model


@pytest.mark.asyncio
async def test_get_file_by_id_not_found(file_service, mock_db_session):
    """Testa a recuperação de arquivo inexistente."""
    # Configurar mock para simular arquivo não encontrado
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    # Chamar o método e verificar exceção
    with pytest.raises(HTTPException) as excinfo:
        await file_service.get_file_by_id(
            file_id="nonexistent-id"
        )
    
    # Verificar código de status da exceção
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_get_files(file_service, mock_file_model, mock_db_session):
    """Testa a listagem de arquivos."""
    # Configurar mock para simular lista de arquivos
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [mock_file_model]
    mock_db_session.execute.return_value.scalar.return_value = 1  # Total count
    
    # Chamar o método
    result, total = await file_service.get_files(
        skip=0,
        limit=10,
        user_id="user123",
        category=None
    )
    
    # Verificar resultado
    assert len(result) == 1
    assert result[0] == mock_file_model
    assert total == 1


@pytest.mark.asyncio
async def test_get_files_with_category(file_service, mock_file_model, mock_db_session):
    """Testa a listagem de arquivos com filtro de categoria."""
    # Configurar mock para simular lista de arquivos
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [mock_file_model]
    mock_db_session.execute.return_value.scalar.return_value = 1  # Total count
    
    # Chamar o método
    result, total = await file_service.get_files(
        skip=0,
        limit=10,
        user_id="user123",
        category="pdf"
    )
    
    # Verificar resultado
    assert len(result) == 1
    assert result[0] == mock_file_model
    assert total == 1


@pytest.mark.asyncio
async def test_update_file(file_service, mock_file_model, mock_db_session):
    """Testa a atualização de arquivo."""
    # Configurar mock para simular arquivo existente
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_file_model
    
    # Chamar o método
    result = await file_service.update_file(
        file_id="123e4567-e89b-12d3-a456-426614174000",
        filename="updated_document.pdf",
        user_id="user123"
    )
    
    # Verificar resultado
    assert result.filename == "updated_document.pdf"
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_file_not_found(file_service, mock_db_session):
    """Testa a atualização de arquivo inexistente."""
    # Configurar mock para simular arquivo não encontrado
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    # Chamar o método e verificar exceção
    with pytest.raises(HTTPException) as excinfo:
        await file_service.update_file(
            file_id="nonexistent-id",
            filename="updated_document.pdf",
            user_id="user123"
        )
    
    # Verificar código de status da exceção
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_file(file_service, mock_file_model, mock_db_session):
    """Testa a exclusão de arquivo."""
    # Configurar mock para simular arquivo existente
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_file_model
    
    # Configurar mock para o método privado _remove_file
    with patch.object(file_service, "_remove_file", return_value=True):
        # Chamar o método
        result = await file_service.delete_file(
            file_id="123e4567-e89b-12d3-a456-426614174000",
            user_id="user123"
        )
        
        # Verificar resultado
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_file_model)
        mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_file_not_found(file_service, mock_db_session):
    """Testa a exclusão de arquivo inexistente."""
    # Configurar mock para simular arquivo não encontrado
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    # Chamar o método e verificar exceção
    with pytest.raises(HTTPException) as excinfo:
        await file_service.delete_file(
            file_id="nonexistent-id",
            user_id="user123"
        )
    
    # Verificar código de status da exceção
    assert excinfo.value.status_code == 404


def test_validate_file_extension_valid():
    """Testa a validação de extensão de arquivo válida."""
    # Configurar mock para settings
    with patch("synapse.core.security.file_validation.settings") as mock_settings:
        mock_settings.ALLOWED_EXTENSIONS = ["pdf", "txt", "jpg"]
        
        # Testar extensões válidas
        assert validate_file_extension("document.pdf") is True
        assert validate_file_extension("notes.txt") is True
        assert validate_file_extension("image.jpg") is True


def test_validate_file_extension_invalid():
    """Testa a validação de extensão de arquivo inválida."""
    # Configurar mock para settings
    with patch("synapse.core.security.file_validation.settings") as mock_settings:
        mock_settings.ALLOWED_EXTENSIONS = ["pdf", "txt", "jpg"]
        
        # Testar extensões inválidas
        assert validate_file_extension("script.js") is False
        assert validate_file_extension("data.csv") is False
        assert validate_file_extension("noextension") is False


def test_validate_file_size_valid():
    """Testa a validação de tamanho de arquivo válido."""
    # Configurar mock para settings
    with patch("synapse.core.security.file_validation.settings") as mock_settings:
        mock_settings.MAX_UPLOAD_SIZE = 1024 * 1024  # 1 MB
        
        # Testar tamanhos válidos
        assert validate_file_size(1000) is True  # 1 KB
        assert validate_file_size(1024 * 1024) is True  # 1 MB exato


def test_validate_file_size_invalid():
    """Testa a validação de tamanho de arquivo inválido."""
    # Configurar mock para settings
    with patch("synapse.core.security.file_validation.settings") as mock_settings:
        mock_settings.MAX_UPLOAD_SIZE = 1024 * 1024  # 1 MB
        
        # Testar tamanho inválido
        assert validate_file_size(1024 * 1024 + 1) is False  # 1 MB + 1 byte
        assert validate_file_size(2 * 1024 * 1024) is False  # 2 MB
