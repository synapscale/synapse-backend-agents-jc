"""
Módulo de teste isolado para validação de arquivos e tratamento de erros
"""
import pytest
import os
import tempfile
import magic
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from typing import Dict, Any, Optional, List

# Criar uma aplicação FastAPI de teste
app = FastAPI()

# Configurações de teste
ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"],
    "document": ["application/pdf", "application/msword", "text/plain", "text/markdown"],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg"],
    "video": ["video/mp4", "video/webm"],
    "archive": ["application/zip", "application/x-tar", "application/gzip"]
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Classe de validação de conteúdo
class ContentValidator:
    @staticmethod
    def validate_mime_type(content_type: str, allowed_categories: Optional[List[str]] = None) -> bool:
        """Valida se o tipo MIME é permitido."""
        if allowed_categories:
            # Verificar apenas nas categorias especificadas
            allowed_mimes = []
            for category in allowed_categories:
                if category in ALLOWED_MIME_TYPES:
                    allowed_mimes.extend(ALLOWED_MIME_TYPES[category])
            
            return content_type in allowed_mimes
        else:
            # Verificar em todas as categorias
            return any(content_type in mimes for mimes in ALLOWED_MIME_TYPES.values())
    
    @staticmethod
    def validate_file_size(size: int, max_size: int = MAX_FILE_SIZE) -> bool:
        """Valida se o tamanho do arquivo está dentro do limite."""
        return size <= max_size
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Valida e sanitiza o nome do arquivo."""
        import re
        # Remover caracteres potencialmente perigosos
        sanitized = re.sub(r'[^\w\-\.]', '_', filename)
        
        # Garantir que o nome não comece com ponto (arquivos ocultos)
        if sanitized.startswith('.'):
            sanitized = f"file_{sanitized}"
        
        return sanitized

# Função para verificar arquivo
async def validate_file(file_content: bytes, filename: str, max_size: int = MAX_FILE_SIZE):
    """Valida o conteúdo e metadados do arquivo."""
    # Verificar se o arquivo está vazio
    if not file_content:
        return JSONResponse(
            status_code=400,
            content={"detail": "Arquivo vazio"}
        )
    
    # Verificar tamanho do arquivo
    file_size = len(file_content)
    if not ContentValidator.validate_file_size(file_size, max_size):
        # Garantir que a resposta seja 413 Entity Too Large
        return JSONResponse(
            status_code=413,
            content={"detail": f"Arquivo muito grande. Tamanho máximo permitido: {max_size} bytes"}
        )
    
    # Verificar tipo MIME
    mime = magic.Magic(mime=True)
    content_type = mime.from_buffer(file_content[:1024])
    
    if not ContentValidator.validate_mime_type(content_type):
        return JSONResponse(
            status_code=400,
            content={"detail": f"Tipo de arquivo não permitido: {content_type}"}
        )
    
    # Validar nome do arquivo
    safe_filename = ContentValidator.validate_filename(filename)
    
    # Retornar metadados validados
    return {
        "filename": safe_filename,
        "content_type": content_type,
        "size": file_size,
        "is_valid": True
    }

# Rota de teste para validação de arquivo
@app.post("/test-upload")
async def test_upload_endpoint(file: UploadFile = File(...)):
    # Ler conteúdo do arquivo
    content = await file.read()
    
    # Validar arquivo usando o limite padrão
    result = await validate_file(content, file.filename)
    
    # Se for uma resposta de erro, retorná-la diretamente
    if isinstance(result, JSONResponse):
        return result
    
    # Caso contrário, retornar sucesso
    return {"message": "Arquivo válido", "metadata": result}

# Rota específica para teste de arquivo grande
@app.post("/test-upload-size-limit")
async def test_upload_size_limit(file: UploadFile = File(...)):
    content = await file.read()
    # Usar um limite explícito de 100 bytes
    result = await validate_file(content, file.filename, max_size=100)
    if isinstance(result, JSONResponse):
        return result
    return {"message": "Arquivo válido", "metadata": result}

# Cliente de teste
client = TestClient(app)

# Testes
def test_valid_image_upload():
    """Testa upload de imagem válida."""
    # Criar arquivo de imagem PNG válido
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        # Cabeçalho PNG mínimo
        temp.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
        temp_path = temp.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/test-upload",
                files={"file": ("test.png", f, "image/png")}
            )
        
        assert response.status_code == 200
        assert "Arquivo válido" in response.json()["message"]
        assert response.json()["metadata"]["content_type"] == "image/png"
        assert response.json()["metadata"]["is_valid"] is True
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_empty_file_upload():
    """Testa upload de arquivo vazio."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        # Arquivo vazio
        temp_path = temp.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/test-upload",
                files={"file": ("empty.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "Arquivo vazio" in response.json()["detail"]
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_invalid_mime_type():
    """Testa upload de arquivo com tipo MIME não permitido."""
    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as temp:
        # Conteúdo de arquivo executável simulado
        temp.write(b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00')
        temp_path = temp.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/test-upload",
                files={"file": ("test.exe", f, "application/x-msdownload")}
            )
        
        assert response.status_code == 400
        assert "Tipo de arquivo não permitido" in response.json()["detail"]
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_oversized_file():
    """Testa upload de arquivo muito grande."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        # Criar arquivo maior que o limite
        temp.write(b'A' * 200)  # 200 bytes
        temp_path = temp.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/test-upload-size-limit",
                files={"file": ("large.txt", f, "text/plain")}
            )
        
        assert response.status_code == 413
        assert "Arquivo muito grande" in response.json()["detail"]
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_filename_sanitization():
    """Testa sanitização de nomes de arquivo."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        # Conteúdo de texto simples
        temp.write(b'Hello, world!')
        temp_path = temp.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/test-upload",
                files={"file": ("malicious;file.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        assert "malicious_file.txt" == response.json()["metadata"]["filename"]
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_hidden_file():
    """Testa upload de arquivo oculto."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        # Conteúdo de texto simples
        temp.write(b'Hello, world!')
        temp_path = temp.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/test-upload",
                files={"file": (".hidden.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        assert response.json()["metadata"]["filename"].startswith("file_")
        assert ".hidden.txt" in response.json()["metadata"]["filename"]
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
