"""Testes de integração para endpoints de arquivos.

Este módulo contém testes de integração para os endpoints da API de arquivos,
verificando o fluxo completo desde a requisição HTTP até o banco de dados.
"""

import io
import os
import uuid
from typing import Dict, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.synapse.api.v1 import router as v1_router
from src.synapse.config import settings
from src.synapse.core.auth import create_access_token
from src.synapse.db import Base, get_db
from src.synapse.main import app as main_app
from src.synapse.models.file import File


# Configurar banco de dados em memória para testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Criar engine e sessão para testes
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


# Sobrescrever dependência de banco de dados
async def override_get_db():
    """Sobrescreve a dependência de banco de dados para testes."""
    async with TestingSessionLocal() as session:
        yield session


# Sobrescrever dependência de autenticação
async def override_get_current_user():
    """Sobrescreve a dependência de autenticação para testes."""
    return {
        "id": "test_user",
        "username": "testuser",
        "role": "user",
        "scopes": ["files:read", "files:write"],
    }


# Criar diretório temporário para armazenamento
@pytest.fixture(scope="module")
def temp_storage_dir(tmp_path_factory):
    """Cria diretório temporário para armazenamento de arquivos."""
    temp_dir = tmp_path_factory.mktemp("storage")
    # Criar subdiretórios para categorias
    for category in ["image", "video", "audio", "document", "archive"]:
        os.makedirs(os.path.join(temp_dir, category), exist_ok=True)
    return temp_dir


# Configurar aplicação para testes
@pytest.fixture
def app(temp_storage_dir):
    """Configura aplicação FastAPI para testes."""
    # Sobrescrever configurações
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.STORAGE_BASE_PATH = str(temp_storage_dir)

    # Sobrescrever dependências
    main_app.dependency_overrides[get_db] = override_get_db

    return main_app


# Cliente de teste
@pytest.fixture
def client(app):
    """Cliente de teste para a API."""
    return TestClient(app)


# Token de autenticação
@pytest.fixture
def auth_token():
    """Gera token de autenticação para testes."""
    return create_access_token(
        data={
            "sub": "test_user",
            "username": "testuser",
            "role": "user",
            "scopes": ["files:read", "files:write"],
        }
    )


# Headers de autenticação
@pytest.fixture
def auth_headers(auth_token):
    """Headers de autenticação para requisições."""
    return {"Authorization": f"Bearer {auth_token}"}


# Inicializar banco de dados para testes
@pytest.fixture(autouse=True)
async def init_test_db():
    """Inicializa banco de dados para testes."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Teste de upload de arquivo
def test_upload_file(client, auth_headers, temp_storage_dir):
    """Testa o endpoint de upload de arquivo."""
    # Preparar arquivo de teste
    file_content = b"test file content"
    files = {"file": ("test_file.txt", io.BytesIO(file_content), "text/plain")}
    data = {
        "category": "document",
        "tags": "test,example",
        "description": "Test file description",
        "is_public": "false",
    }

    # Enviar requisição
    response = client.post(
        "/api/v1/files/upload", files=files, data=data, headers=auth_headers
    )

    # Verificar resposta
    assert response.status_code == 201
    assert "file_id" in response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Arquivo enviado com sucesso"

    # Verificar se arquivo foi salvo
    file_id = response.json()["file_id"]
    return file_id


# Teste de listagem de arquivos
def test_list_files(client, auth_headers):
    """Testa o endpoint de listagem de arquivos."""
    # Primeiro fazer upload de um arquivo
    file_id = test_upload_file(client, auth_headers, None)

    # Enviar requisição de listagem
    response = client.get("/api/v1/files", headers=auth_headers)

    # Verificar resposta
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()
    assert response.json()["total"] >= 1

    # Verificar se o arquivo enviado está na lista
    found = False
    for item in response.json()["items"]:
        if item["id"] == file_id:
            found = True
            assert item["filename"] == "test_file.txt"
            assert item["category"] == "document"
            assert item["mime_type"] == "text/plain"

    assert found, "Arquivo enviado não encontrado na listagem"


# Teste de obtenção de informações de arquivo
def test_get_file(client, auth_headers):
    """Testa o endpoint de obtenção de informações de arquivo."""
    # Primeiro fazer upload de um arquivo
    file_id = test_upload_file(client, auth_headers, None)

    # Enviar requisição
    response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)

    # Verificar resposta
    assert response.status_code == 200
    assert response.json()["id"] == file_id
    assert response.json()["filename"] == "test_file.txt"
    assert response.json()["category"] == "document"
    assert response.json()["mime_type"] == "text/plain"
    assert response.json()["user_id"] == "test_user"


# Teste de geração de URL de download
def test_download_file(client, auth_headers):
    """Testa o endpoint de geração de URL para download."""
    # Primeiro fazer upload de um arquivo
    file_id = test_upload_file(client, auth_headers, None)

    # Enviar requisição
    response = client.get(f"/api/v1/files/{file_id}/download", headers=auth_headers)

    # Verificar resposta
    assert response.status_code == 200
    assert "download_url" in response.json()
    assert "expires_at" in response.json()


# Teste de atualização de informações de arquivo
def test_update_file(client, auth_headers):
    """Testa o endpoint de atualização de informações de arquivo."""
    # Primeiro fazer upload de um arquivo
    file_id = test_upload_file(client, auth_headers, None)

    # Dados de atualização
    update_data = {
        "tags": ["updated", "tags"],
        "description": "Updated description",
        "is_public": True,
    }

    # Enviar requisição
    response = client.patch(
        f"/api/v1/files/{file_id}", json=update_data, headers=auth_headers
    )

    # Verificar resposta
    assert response.status_code == 200
    assert response.json()["id"] == file_id
    assert response.json()["tags"] == ["updated", "tags"]
    assert response.json()["description"] == "Updated description"
    assert response.json()["is_public"] == True


# Teste de remoção de arquivo
def test_delete_file(client, auth_headers):
    """Testa o endpoint de remoção de arquivo."""
    # Primeiro fazer upload de um arquivo
    file_id = test_upload_file(client, auth_headers, None)

    # Enviar requisição
    response = client.delete(f"/api/v1/files/{file_id}", headers=auth_headers)

    # Verificar resposta
    assert response.status_code == 204

    # Verificar se arquivo foi removido
    get_response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
    assert get_response.status_code == 404
