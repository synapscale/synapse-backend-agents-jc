import shutil
import os

# Definir diretório de uploads isolado para os testes
os.environ["UPLOAD_DIR"] = "/tmp/test_uploads"

# Limpar o diretório de uploads antes dos testes
def pytest_sessionstart(session):
    upload_dir = "/tmp/test_uploads"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
import pytest
import os
import json
import jwt
import sys
from datetime import datetime, timedelta
from fastapi.testclient import TestClient




# Definir variáveis de ambiente ANTES de importar o app
TEST_SECRET_KEY = "test_secret_key"
TEST_UPLOAD_DIR = "/tmp/test_uploads"
os.environ["SECRET_KEY"] = TEST_SECRET_KEY
os.environ["UPLOAD_DIR"] = TEST_UPLOAD_DIR
os.environ["MAX_FILE_SIZE"] = "5242880"
os.environ["RATE_LIMIT_MAX_REQUESTS"] = "3"
os.environ["RATE_LIMIT_WINDOW"] = "60"

# Adicionar o diretório raiz ao path para permitir imports absolutos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from services.uploads.main import app

# Configurações de teste
TEST_USER_ID = "test_user_123"
TEST_USERNAME = "testuser"
TEST_UPLOAD_DIR = "/tmp/test_uploads"
TEST_SECRET_KEY = "test_secret_key"

# Configurar ambiente de teste
os.environ["UPLOAD_DIR"] = TEST_UPLOAD_DIR
os.environ["SECRET_KEY"] = TEST_SECRET_KEY
os.environ["MAX_FILE_SIZE"] = "5242880"  # 5MB

# Cliente de teste
client = TestClient(app)

# Funções auxiliares
def create_test_token(user_id=TEST_USER_ID, username=TEST_USERNAME, scopes=None):
    """Cria um token JWT de teste."""
    if scopes is None:
        scopes = ["uploads:read", "uploads:write"]
    
    payload = {
        "sub": user_id,
        "username": username,
        "role": "user",
        "scopes": scopes,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")

def setup_test_env():
    """Configura o ambiente de teste."""
    # Criar diretórios necessários
    os.makedirs(TEST_UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(TEST_UPLOAD_DIR, "metadata"), exist_ok=True)
    os.makedirs(os.path.join(TEST_UPLOAD_DIR, "image"), exist_ok=True)
    os.makedirs(os.path.join(TEST_UPLOAD_DIR, "document"), exist_ok=True)

def cleanup_test_env():
    """Limpa o ambiente de teste."""
    import shutil
    if os.path.exists(TEST_UPLOAD_DIR):
        shutil.rmtree(TEST_UPLOAD_DIR)

# Fixtures
@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Configura e limpa o ambiente antes e depois de cada teste."""
    setup_test_env()
    yield
    cleanup_test_env()

@pytest.fixture
def auth_headers():
    """Retorna cabeçalhos de autenticação para os testes."""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def read_only_headers():
    """Retorna cabeçalhos com permissão apenas de leitura."""
    token = create_test_token(scopes=["uploads:read"])
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_image():
    """Cria uma imagem de teste."""
    image_path = os.path.join(TEST_UPLOAD_DIR, "test_image.png")
    
    # Criar uma imagem PNG simples
    with open(image_path, "wb") as f:
        # Cabeçalho PNG mínimo
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    
    return image_path

@pytest.fixture
def test_text_file():
    """Cria um arquivo de documento de teste (PDF mínimo válido)."""
    pdf_path = os.path.join(TEST_UPLOAD_DIR, "test_file.pdf")
    # PDF mínimo válido
    pdf_bytes = b'%PDF-1.1\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\nstartxref\n0\n%%EOF\n'
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    return pdf_path

# Testes
def test_health_check():
    """Testa o endpoint de verificação de saúde."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "uploads"

def test_upload_without_auth():
    """Testa upload sem autenticação."""
    response = client.post("/uploads/", files={"file": ("test.txt", "conteúdo de teste")})
    assert response.status_code == 401

def test_upload_with_read_only_scope(read_only_headers, test_text_file):
    """Testa upload com escopo apenas de leitura."""
    with open(test_text_file, "rb") as f:
        response = client.post(
            "/uploads/",
            files={"file": ("test.txt", f)},
            headers=read_only_headers
        )
    assert response.status_code == 403

def test_successful_upload(auth_headers, test_image):
    """Testa upload bem-sucedido de imagem."""
    with open(test_image, "rb") as f:
        response = client.post(
            "/uploads/",
            files={"file": ("test.png", f)},
            data={"description": "Imagem de teste", "tags": "teste,imagem"},
            headers=auth_headers
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.png"
    assert data["category"] == "image"
    assert "file_id" in data
    assert "url" in data
    
    # Verificar se o arquivo foi salvo
    file_id = data["file_id"]
    metadata_path = os.path.join(TEST_UPLOAD_DIR, "metadata", f"{file_id}.json")
    assert os.path.exists(metadata_path)

def test_upload_invalid_file(auth_headers):
    """Testa upload de arquivo inválido."""
    # Criar um arquivo com extensão de imagem mas conteúdo de texto
    invalid_file_path = os.path.join(TEST_UPLOAD_DIR, "invalid.png")
    with open(invalid_file_path, "w") as f:
        f.write("Este não é um arquivo PNG válido")
    
    with open(invalid_file_path, "rb") as f:
        response = client.post(
            "/uploads/",
            files={"file": ("invalid.png", f)},
            headers=auth_headers
        )
    
    # Deve falhar na validação de tipo MIME
    assert response.status_code == 400
    assert "Tipo de arquivo não permitido" in response.json()["detail"]

def test_upload_empty_file(auth_headers):
    """Testa upload de arquivo vazio."""
    empty_file_path = os.path.join(TEST_UPLOAD_DIR, "empty.txt")
    with open(empty_file_path, "w") as f:
        pass  # Arquivo vazio
    
    with open(empty_file_path, "rb") as f:
        response = client.post(
            "/uploads/",
            files={"file": ("empty.txt", f)},
            headers=auth_headers
        )
    
    assert response.status_code == 400
    assert "Arquivo vazio" in response.json()["detail"]

def test_list_uploads_without_auth():
    """Testa listagem sem autenticação."""
    response = client.get("/uploads/")
    assert response.status_code == 401

def test_list_uploads_empty(auth_headers):
    """Testa listagem de uploads vazia."""
    response = client.get("/uploads/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_list_uploads_with_files(auth_headers, test_image, test_text_file):
    """Testa listagem de uploads com arquivos."""
    # Fazer upload de dois arquivos
    with open(test_image, "rb") as f:
        client.post(
            "/uploads/",
            files={"file": ("test.png", f)},
            headers=auth_headers
        )
    
    with open(test_text_file, "rb") as f:
        client.post(
            "/uploads/",
            files={"file": ("test.pdf", f)},
            headers=auth_headers
        )
    
    # Listar todos os uploads
    response = client.get("/uploads/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verificar se os arquivos estão na resposta
    filenames = [item["filename"] for item in data]
    assert "test.png" in filenames
    assert "test.pdf" in filenames

def test_list_uploads_with_category_filter(auth_headers, test_image, test_text_file):
    """Testa listagem de uploads com filtro de categoria."""
    # Fazer upload de dois arquivos
    with open(test_image, "rb") as f:
        client.post(
            "/uploads/",
            files={"file": ("test.png", f)},
            headers=auth_headers
        )
    
    with open(test_text_file, "rb") as f:
        client.post(
            "/uploads/",
            files={"file": ("test.pdf", f)},
            headers=auth_headers
        )
    
    # Listar apenas imagens
    response = client.get("/uploads/?category=image", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "test.png"
    
    # Listar apenas documentos
    response = client.get("/uploads/?category=document", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "test.pdf"

def test_get_upload_by_id(auth_headers, test_image):
    """Testa obtenção de um upload específico por ID."""
    # Fazer upload de um arquivo
    with open(test_image, "rb") as f:
        response = client.post(
            "/uploads/",
            files={"file": ("test.png", f)},
            headers=auth_headers
        )
    
    file_id = response.json()["file_id"]
    
    # Obter o arquivo por ID
    response = client.get(f"/uploads/{file_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["file_id"] == file_id
    assert data["filename"] == "test.png"

def test_get_nonexistent_upload(auth_headers):
    """Testa obtenção de um upload inexistente."""
    response = client.get("/uploads/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404

def test_delete_upload(auth_headers, test_image):
    """Testa exclusão de um upload."""
    # Fazer upload de um arquivo
    with open(test_image, "rb") as f:
        response = client.post(
            "/uploads/",
            files={"file": ("test.png", f)},
            headers=auth_headers
        )
    
    file_id = response.json()["file_id"]
    
    # Excluir o arquivo
    response = client.delete(f"/uploads/{file_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Arquivo excluído com sucesso"
    
    # Verificar se o arquivo foi excluído
    response = client.get(f"/uploads/{file_id}", headers=auth_headers)
    assert response.status_code == 404

def test_rate_limiting(auth_headers, test_image):
    """Testa o rate limiting."""
    # Configurar um rate limiter mais restritivo para o teste (antes de qualquer requisição)
    import sys
    sys.path.append('/home/ubuntu/synapse-backend')
    from services.uploads.utils.security import RateLimiter
    RateLimiter.max_requests = 3
    RateLimiter.window = 60

    # Fazer múltiplos uploads em sequência
    for i in range(5):
        with open(test_image, "rb") as f:
            response = client.post(
                "/uploads/",
                files={"file": (f"test{i}.png", f)},
                headers={**auth_headers, "X-Forwarded-For": "1.2.3.4"}
            )
        if i < 3:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert "Muitas requisições" in response.json()["detail"]
            break

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
