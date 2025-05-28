import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from synapse.core.security.file_validation import validate_file
from synapse.services.file_service import FileService
from synapse.models.file import File
from synapse.core.storage.storage_manager import StorageManager

# Teste adicional para validação de arquivo
@pytest.mark.asyncio
async def test_validate_file_invalid_extension():
    """Testa se a validação rejeita arquivos com extensão não permitida."""
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.exe"
    mock_file.content_type = "application/octet-stream"
    
    with pytest.raises(HTTPException) as excinfo:
        await validate_file(mock_file, "document")
    
    assert excinfo.value.status_code == 400
    assert "Tipo de arquivo não permitido" in excinfo.value.detail

# Teste adicional para o serviço de arquivos
@pytest.mark.asyncio
async def test_file_service_get_nonexistent_file():
    """Testa se o serviço retorna erro apropriado para arquivo inexistente."""
    # Configuração
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    file_service = FileService(mock_db)
    
    # Execução e verificação
    with pytest.raises(HTTPException) as excinfo:
        await file_service.get_file("550e8400-e29b-41d4-a716-446655440000", 1)
    
    assert excinfo.value.status_code == 404
    assert "Arquivo não encontrado" in excinfo.value.detail

# Teste para verificar permissões de acesso
@pytest.mark.asyncio
async def test_file_service_unauthorized_access():
    """Testa se o serviço impede acesso não autorizado a arquivos."""
    # Configuração
    mock_file = MagicMock(spec=File)
    mock_file.id = 1
    mock_file.user_id = 2  # Diferente do user_id na requisição
    
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_file
    
    file_service = FileService(mock_db)
    
    # Execução e verificação
    with pytest.raises(HTTPException) as excinfo:
        await file_service.get_file(1, 1)  # user_id=1 tenta acessar arquivo do user_id=2
    
    assert excinfo.value.status_code == 403
    assert "Acesso não autorizado" in excinfo.value.detail

# Teste para o gerenciador de armazenamento
@pytest.mark.asyncio
async def test_storage_manager_save_file():
    """Testa se o gerenciador de armazenamento salva arquivos corretamente."""
    with patch('synapse.core.storage.storage_manager.aiofiles.open', new_callable=AsyncMock) as mock_open:
        file_mock = AsyncMock()
        file_mock.read.return_value = b"test content"
        
        storage_manager = StorageManager()
        
        # Execução
        result = await storage_manager.save_file(file_mock, "test.txt", "uploads")
        
        # Verificação
        assert result is not None
        assert "uploads" in result
        assert ".txt" in result
        mock_open.assert_called_once()
        
        # Verificar se o método write foi chamado com o conteúdo correto
        mock_file = mock_open.return_value.__aenter__.return_value
        mock_file.write.assert_called_once_with(b"test content")
