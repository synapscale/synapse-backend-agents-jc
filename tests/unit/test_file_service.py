"""Testes unitários para o serviço de arquivos.

Este módulo contém testes unitários para o serviço de gerenciamento de arquivos,
verificando todas as operações principais como upload, download, listagem e remoção.
"""

import io
import os
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.synapse.core.security import SecurityValidator
from src.synapse.core.storage import StorageManager
from src.synapse.models.file import File
from src.synapse.schemas.file import FileUpdate
from src.synapse.services.file_service import FileService


@pytest.fixture
def mock_db_session():
    """Fixture para mock de sessão de banco de dados."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.delete = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_storage_manager():
    """Fixture para mock de gerenciador de armazenamento."""
    with patch("src.synapse.services.file_service.StorageManager") as mock:
        manager = mock.return_value
        manager.save_file = AsyncMock(
            return_value={
                "stored_name": "test_stored_name",
                "file_path": "/path/to/file",
                "checksum": "test_checksum",
            }
        )
        manager.get_file = AsyncMock(return_value=b"test_content")
        manager.delete_file = AsyncMock(return_value=True)
        manager.generate_download_url = AsyncMock(
            return_value="http://test-url.com/download"
        )
        yield manager


@pytest.fixture
def mock_security_validator():
    """Fixture para mock de validador de segurança."""
    with patch("src.synapse.services.file_service.SecurityValidator") as mock:
        validator = mock.return_value
        validator.validate_file_safety = AsyncMock(return_value=True)
        yield validator


@pytest.fixture
def file_service(mock_storage_manager, mock_security_validator):
    """Fixture para serviço de arquivos com mocks."""
    return FileService()


@pytest.fixture
def sample_file():
    """Fixture para arquivo de teste."""
    content = b"test file content"
    file = MagicMock(spec=UploadFile)
    file.filename = "test_file.txt"
    file.content_type = "text/plain"
    file.read = AsyncMock(return_value=content)
    return file


@pytest.fixture
def sample_db_file():
    """Fixture para objeto File do banco de dados."""
    return File(
        id=uuid.uuid4(),
        user_id="test_user",
        filename="test_file.txt",
        stored_name="test_stored_name",
        category="document",
        mime_type="text/plain",
        size="17",
        checksum="test_checksum",
        tags=["test", "example"],
        description="Test file description",
        is_public="false",
        status="completed",
        storage_path="/path/to/file",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_upload_file(
    file_service,
    mock_db_session,
    sample_file,
    mock_storage_manager,
    mock_security_validator,
):
    """Testa o upload de arquivo."""
    # Configurar mock de execute().scalars().first()
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None

    # Dados do arquivo
    file_data = FileUpdate(
        tags=["test", "example"], description="Test file description", is_public=False
    )

    # Executar upload
    result = await file_service.upload_file(
        db=mock_db_session, file=sample_file, user_id="test_user", file_data=file_data
    )

    # Verificar chamadas
    sample_file.read.assert_called_once()
    mock_security_validator.validate_file_safety.assert_called_once()
    mock_storage_manager.save_file.assert_called_once()
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    # Verificar resultado
    assert result is not None
    assert mock_db_session.add.call_args[0][0].user_id == "test_user"
    assert mock_db_session.add.call_args[0][0].filename == "test_file.txt"


@pytest.mark.asyncio
async def test_get_file(file_service, mock_db_session, sample_db_file):
    """Testa a obtenção de informações de arquivo."""
    # Configurar mock para retornar o arquivo
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = (
        sample_db_file
    )

    # Executar get_file
    result = await file_service.get_file(
        db=mock_db_session, file_id=sample_db_file.id, user_id="test_user"
    )

    # Verificar chamadas
    mock_db_session.execute.assert_called_once()

    # Verificar resultado
    assert result is not None
    assert result.id == sample_db_file.id
    assert result.user_id == "test_user"


@pytest.mark.asyncio
async def test_get_file_not_found(file_service, mock_db_session):
    """Testa a obtenção de arquivo inexistente."""
    # Configurar mock para retornar None
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None

    # Executar get_file e verificar exceção
    with pytest.raises(Exception):
        await file_service.get_file(
            db=mock_db_session, file_id=uuid.uuid4(), user_id="test_user"
        )


@pytest.mark.asyncio
async def test_list_files(file_service, mock_db_session, sample_db_file):
    """Testa a listagem de arquivos."""
    # Configurar mock para retornar lista de arquivos
    mock_db_session.execute.return_value.scalars.return_value.all.side_effect = [
        [sample_db_file.id],  # Para contagem
        [sample_db_file],  # Para listagem
    ]

    # Executar list_files
    files, total = await file_service.list_files(
        db=mock_db_session, user_id="test_user", skip=0, limit=10
    )

    # Verificar chamadas
    assert mock_db_session.execute.call_count == 2

    # Verificar resultado
    assert len(files) == 1
    assert files[0].id == sample_db_file.id
    assert total == 1


@pytest.mark.asyncio
async def test_update_file(file_service, mock_db_session, sample_db_file):
    """Testa a atualização de informações de arquivo."""
    # Configurar mock para retornar o arquivo
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = (
        sample_db_file
    )

    # Dados de atualização
    file_data = FileUpdate(
        tags=["updated", "tags"], description="Updated description", is_public=True
    )

    # Executar update_file
    result = await file_service.update_file(
        db=mock_db_session,
        file_id=sample_db_file.id,
        user_id="test_user",
        file_data=file_data,
    )

    # Verificar chamadas
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    # Verificar resultado
    assert result is not None
    assert result.tags == ["updated", "tags"]
    assert result.description == "Updated description"
    assert result.is_public == "true"


@pytest.mark.asyncio
async def test_delete_file(
    file_service, mock_db_session, sample_db_file, mock_storage_manager
):
    """Testa a remoção de arquivo."""
    # Configurar mock para retornar o arquivo
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = (
        sample_db_file
    )

    # Executar delete_file
    result = await file_service.delete_file(
        db=mock_db_session, file_id=sample_db_file.id, user_id="test_user"
    )

    # Verificar chamadas
    mock_storage_manager.delete_file.assert_called_once_with(
        category=sample_db_file.category, stored_name=sample_db_file.stored_name
    )
    mock_db_session.delete.assert_called_once_with(sample_db_file)
    mock_db_session.commit.assert_called_once()

    # Verificar resultado
    assert result is True


@pytest.mark.asyncio
async def test_generate_download_url(
    file_service, mock_db_session, sample_db_file, mock_storage_manager
):
    """Testa a geração de URL para download."""
    # Configurar mock para retornar o arquivo
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = (
        sample_db_file
    )

    # Executar generate_download_url
    result = await file_service.generate_download_url(
        db=mock_db_session, file_id=sample_db_file.id, user_id="test_user"
    )

    # Verificar chamadas
    mock_storage_manager.generate_download_url.assert_called_once_with(
        category=sample_db_file.category, stored_name=sample_db_file.stored_name
    )

    # Verificar resultado
    assert result is not None
    assert "download_url" in result
    assert "expires_at" in result
    assert result["download_url"] == "http://test-url.com/download"
