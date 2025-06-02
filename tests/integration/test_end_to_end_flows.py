"""
Testes end-to-end para fluxos completos do backend.

Este módulo contém testes end-to-end para fluxos completos do backend,
simulando cenários reais de uso com múltiplos serviços integrados.
"""

import pytest
import io
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.synapse.main import app
from src.synapse.core.auth.jwt import create_access_token


@pytest.fixture
def test_client():
    """Fixture para cliente de teste."""
    return TestClient(app)


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
def mock_db_session():
    """Mock para sessão de banco de dados."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    
    # Patch para o get_db dependency
    with patch("synapse.api.deps.get_db", return_value=session):
        yield session


class TestEndToEndFlows:
    """Testes end-to-end para fluxos completos do backend."""
    
    def test_upload_and_analyze_document(self, test_client, auth_headers, mock_db_session):
        """
        Testa o fluxo completo de upload de documento e análise com LLM.
        
        Fluxo:
        1. Upload de um documento PDF
        2. Recuperação do documento
        3. Análise do conteúdo com LLM
        """
        # Configurar mocks para serviços
        with patch("synapse.services.file_service.FileService.create_file") as mock_create_file, \
             patch("synapse.services.file_service.FileService.get_file_by_id") as mock_get_file, \
             patch("synapse.core.llm.unified.UnifiedLLMService.generate_text") as mock_generate_text:
            
            # Mock para criação de arquivo
            mock_file = MagicMock()
            mock_file.id = "123e4567-e89b-12d3-a456-426614174000"
            mock_file.filename = "test_document.pdf"
            mock_file.content_type = "application/pdf"
            mock_file.path = "/storage/pdf/test_document.pdf"
            mock_file.dict = MagicMock(return_value={
                "id": mock_file.id,
                "filename": mock_file.filename,
                "content_type": mock_file.content_type,
                "path": mock_file.path,
                "category": "pdf",
                "size": 1024,
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-01-01T12:00:00",
                "user_id": "test_user"
            })
            mock_create_file.return_value = mock_file
            mock_get_file.return_value = mock_file
            
            # Mock para geração de texto
            mock_generate_text.return_value = {
                "text": "Este documento contém informações sobre machine learning e suas aplicações.",
                "model": "claude-3-sonnet",
                "provider": "claude",
                "tokens": {
                    "prompt": 50,
                    "completion": 20,
                    "total": 70
                },
                "processing_time": 1.5
            }
            
            # 1. Upload de documento
            test_file = io.BytesIO(b"test file content")
            upload_response = test_client.post(
                "/api/v1/files/upload",
                files={"file": ("test_document.pdf", test_file, "application/pdf")},
                headers=auth_headers
            )
            
            # Verificar resposta de upload
            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            file_id = upload_data["id"]
            
            # 2. Recuperação do documento
            get_response = test_client.get(
                f"/api/v1/files/{file_id}",
                headers=auth_headers
            )
            
            # Verificar resposta de recuperação
            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["id"] == file_id
            
            # 3. Análise do conteúdo com LLM
            analysis_request = {
                "prompt": f"Analise o conteúdo do documento {get_data['filename']} e resuma os principais pontos.",
                "provider": "claude",
                "model": "claude-3-sonnet",
                "max_tokens": 500
            }
            
            analysis_response = test_client.post(
                "/api/v1/llm/generate",
                json=analysis_request,
                headers=auth_headers
            )
            
            # Verificar resposta de análise
            assert analysis_response.status_code == 200
            analysis_data = analysis_response.json()
            assert "text" in analysis_data
            assert analysis_data["provider"] == "claude"
            
            # Verificar chamadas aos serviços
            mock_create_file.assert_called_once()
            mock_get_file.assert_called_once_with(file_id=file_id)
            mock_generate_text.assert_called_once()
    
    def test_multi_provider_llm_comparison(self, test_client, auth_headers, mock_db_session):
        """
        Testa o fluxo de comparação de respostas entre múltiplos provedores de LLM.
        
        Fluxo:
        1. Geração de texto com Claude
        2. Geração de texto com Gemini
        3. Geração de texto com OpenAI
        4. Comparação dos resultados
        """
        # Configurar mocks para serviços
        with patch("synapse.core.llm.unified.UnifiedLLMService.generate_text") as mock_generate_text:
            
            # Configurar respostas diferentes para cada chamada
            mock_generate_text.side_effect = [
                # Resposta Claude
                {
                    "text": "Resposta do Claude sobre machine learning.",
                    "model": "claude-3-sonnet",
                    "provider": "claude",
                    "tokens": {"total": 50},
                    "processing_time": 1.2
                },
                # Resposta Gemini
                {
                    "text": "Resposta do Gemini sobre machine learning.",
                    "model": "gemini-1.5-pro",
                    "provider": "gemini",
                    "tokens": {"total": 45},
                    "processing_time": 0.9
                },
                # Resposta OpenAI
                {
                    "text": "Resposta do OpenAI sobre machine learning.",
                    "model": "gpt-4o",
                    "provider": "openai",
                    "tokens": {"total": 48},
                    "processing_time": 1.0
                }
            ]
            
            # Prompt comum para todos os provedores
            prompt = "Explique o conceito de machine learning em termos simples."
            
            # 1. Geração com Claude
            claude_response = test_client.post(
                "/api/v1/llm/claude/generate",
                json={
                    "prompt": prompt,
                    "model": "claude-3-sonnet",
                    "max_tokens": 500
                },
                headers=auth_headers
            )
            
            # 2. Geração com Gemini
            gemini_response = test_client.post(
                "/api/v1/llm/gemini/generate",
                json={
                    "prompt": prompt,
                    "model": "gemini-1.5-pro",
                    "max_tokens": 500
                },
                headers=auth_headers
            )
            
            # 3. Geração com OpenAI
            openai_response = test_client.post(
                "/api/v1/llm/openai/generate",
                json={
                    "prompt": prompt,
                    "model": "gpt-4o",
                    "max_tokens": 500
                },
                headers=auth_headers
            )
            
            # Verificar respostas
            assert claude_response.status_code == 200
            assert gemini_response.status_code == 200
            assert openai_response.status_code == 200
            
            # Extrair dados
            claude_data = claude_response.json()
            gemini_data = gemini_response.json()
            openai_data = openai_response.json()
            
            # 4. Comparar resultados
            assert "Claude" in claude_data["text"]
            assert "Gemini" in gemini_data["text"]
            assert "OpenAI" in openai_data["text"]
            
            assert claude_data["provider"] == "claude"
            assert gemini_data["provider"] == "gemini"
            assert openai_data["provider"] == "openai"
            
            # Verificar chamadas ao serviço
            assert mock_generate_text.call_count == 3
    
    def test_file_management_workflow(self, test_client, auth_headers, mock_db_session):
        """
        Testa o fluxo completo de gerenciamento de arquivos.
        
        Fluxo:
        1. Upload de múltiplos arquivos
        2. Listagem e filtragem
        3. Atualização de um arquivo
        4. Download de um arquivo
        5. Exclusão de um arquivo
        """
        # Configurar mocks para serviços
        with patch("synapse.services.file_service.FileService.create_file") as mock_create_file, \
             patch("synapse.services.file_service.FileService.get_files") as mock_get_files, \
             patch("synapse.services.file_service.FileService.update_file") as mock_update_file, \
             patch("synapse.services.file_service.FileService.get_file_by_id") as mock_get_file, \
             patch("synapse.services.file_service.FileService.delete_file") as mock_delete_file, \
             patch("builtins.open", return_value=io.BytesIO(b"test file content")):
            
            # Mock para criação de arquivos
            def create_mock_file(index, ext):
                mock_file = MagicMock()
                mock_file.id = f"file-id-{index}"
                mock_file.filename = f"document_{index}.{ext}"
                mock_file.content_type = "application/pdf" if ext == "pdf" else "text/plain"
                mock_file.category = ext
                mock_file.path = f"/storage/{ext}/document_{index}.{ext}"
                mock_file.size = 1024
                mock_file.user_id = "test_user"
                mock_file.created_at = "2025-01-01T12:00:00"
                mock_file.updated_at = "2025-01-01T12:00:00"
                
                mock_file.dict = MagicMock(return_value={
                    "id": mock_file.id,
                    "filename": mock_file.filename,
                    "content_type": mock_file.content_type,
                    "category": mock_file.category,
                    "path": mock_file.path,
                    "size": mock_file.size,
                    "user_id": mock_file.user_id,
                    "created_at": mock_file.created_at,
                    "updated_at": mock_file.updated_at
                })
                
                return mock_file
            
            # Criar mocks para diferentes arquivos
            pdf_file = create_mock_file(1, "pdf")
            txt_file = create_mock_file(2, "txt")
            
            # Configurar retornos dos mocks
            mock_create_file.side_effect = [pdf_file, txt_file]
            mock_get_files.return_value = ([pdf_file, txt_file], 2)  # Todos os arquivos
            mock_get_files.side_effect = [
                ([pdf_file, txt_file], 2),  # Todos os arquivos
                ([pdf_file], 1),  # Apenas PDFs
            ]
            mock_update_file.return_value = pdf_file
            mock_get_file.return_value = pdf_file
            mock_delete_file.return_value = True
            
            # 1. Upload de múltiplos arquivos
            # Upload do primeiro arquivo (PDF)
            pdf_upload = test_client.post(
                "/api/v1/files/upload",
                files={"file": ("document_1.pdf", io.BytesIO(b"pdf content"), "application/pdf")},
                headers=auth_headers
            )
            
            # Upload do segundo arquivo (TXT)
            txt_upload = test_client.post(
                "/api/v1/files/upload",
                files={"file": ("document_2.txt", io.BytesIO(b"txt content"), "text/plain")},
                headers=auth_headers
            )
            
            # Verificar respostas de upload
            assert pdf_upload.status_code == 200
            assert txt_upload.status_code == 200
            
            pdf_data = pdf_upload.json()
            txt_data = txt_upload.json()
            
            # 2. Listagem e filtragem
            # Listar todos os arquivos
            list_all = test_client.get(
                "/api/v1/files/",
                headers=auth_headers
            )
            
            # Listar apenas PDFs
            list_pdfs = test_client.get(
                "/api/v1/files/?category=pdf",
                headers=auth_headers
            )
            
            # Verificar respostas de listagem
            assert list_all.status_code == 200
            assert list_pdfs.status_code == 200
            
            all_files = list_all.json()
            pdf_files = list_pdfs.json()
            
            assert all_files["total"] == 2
            assert len(all_files["items"]) == 2
            
            assert pdf_files["total"] == 1
            assert len(pdf_files["items"]) == 1
            assert pdf_files["items"][0]["category"] == "pdf"
            
            # 3. Atualização de um arquivo
            update_response = test_client.put(
                f"/api/v1/files/{pdf_data['id']}",
                json={"filename": "updated_document.pdf"},
                headers=auth_headers
            )
            
            # Verificar resposta de atualização
            assert update_response.status_code == 200
            
            # 4. Download de um arquivo
            download_response = test_client.get(
                f"/api/v1/files/{pdf_data['id']}/download",
                headers=auth_headers
            )
            
            # Verificar resposta de download
            assert download_response.status_code == 200
            assert download_response.headers["content-type"] == "application/pdf"
            
            # 5. Exclusão de um arquivo
            delete_response = test_client.delete(
                f"/api/v1/files/{pdf_data['id']}",
                headers=auth_headers
            )
            
            # Verificar resposta de exclusão
            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert delete_data["success"] is True
            
            # Verificar chamadas aos serviços
            assert mock_create_file.call_count == 2
            assert mock_get_files.call_count == 2
            mock_update_file.assert_called_once()
            mock_get_file.assert_called_once()
            mock_delete_file.assert_called_once()
    
    def test_authentication_and_authorization(self, test_client):
        """
        Testa o fluxo de autenticação e autorização.
        
        Fluxo:
        1. Tentativa de acesso sem token
        2. Acesso com token inválido
        3. Acesso com token expirado
        4. Acesso com token válido
        """
        # 1. Tentativa de acesso sem token
        no_token_response = test_client.get("/api/v1/files/")
        assert no_token_response.status_code == 401
        
        # 2. Acesso com token inválido
        invalid_token_headers = {"Authorization": "Bearer invalid_token"}
        invalid_token_response = test_client.get(
            "/api/v1/files/",
            headers=invalid_token_headers
        )
        assert invalid_token_response.status_code == 401
        
        # 3. Acesso com token expirado
        with patch("synapse.core.auth.jwt.decode_token", side_effect=jwt.ExpiredSignatureError):
            expired_token_headers = {"Authorization": "Bearer expired_token"}
            expired_token_response = test_client.get(
                "/api/v1/files/",
                headers=expired_token_headers
            )
            assert expired_token_response.status_code == 401
        
        # 4. Acesso com token válido
        valid_token = create_access_token(
            data={
                "sub": "test_user",
                "name": "Test User",
                "email": "test@example.com",
                "role": "user"
            }
        )
        valid_token_headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch("synapse.services.file_service.FileService.get_files", return_value=([], 0)):
            valid_token_response = test_client.get(
                "/api/v1/files/",
                headers=valid_token_headers
            )
            assert valid_token_response.status_code == 200
